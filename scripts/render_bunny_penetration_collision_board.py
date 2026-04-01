#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


@dataclass
class DetectorCase:
    case_name: str
    summary_path: Path
    scene_npz_path: Path
    rigid_shape: str
    sim_frame_dt_s: float
    first_force_contact_frame_index: int | None
    clip_end_frame_index: int
    camera_pos: np.ndarray
    camera_pitch: float
    camera_yaw: float
    camera_fov: float
    particle_q: np.ndarray
    body_q: np.ndarray
    penalty_force: np.ndarray
    total_force: np.ndarray
    force_contact_mask: np.ndarray
    mesh_vertices_local: np.ndarray
    mesh_render_edges: np.ndarray
    box_half_extents: np.ndarray
    board_clip_duration_s: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render the final bunny penetration 2x2 board from saved detector bundles and scene artifacts."
    )
    parser.add_argument("--box-detector-summary", type=Path, required=True)
    parser.add_argument("--bunny-detector-summary", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--board-fps", type=float, default=30.0)
    parser.add_argument("--post-contact-seconds", type=float, default=1.0)
    parser.add_argument("--force-percentile", type=float, default=98.0)
    parser.add_argument("--max-arrow-world-len", type=float, default=0.035)
    parser.add_argument("--panel-width", type=int, default=960)
    parser.add_argument("--panel-height", type=int, default=540)
    parser.add_argument("--first-frame-png", type=Path, default=None)
    return parser.parse_args()


def _font(size: int, *, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=max(10, int(size)))
        except Exception:
            continue
    return ImageFont.load_default()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _color_lerp(c0: tuple[int, int, int], c1: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    alpha = float(np.clip(t, 0.0, 1.0))
    return tuple(
        int(round((1.0 - alpha) * float(a) + alpha * float(b)))
        for a, b in zip(c0, c1, strict=True)
    )


def _spectrum_color(value_01: float) -> tuple[int, int, int]:
    anchors = [
        (0.00, (43, 86, 183)),
        (0.20, (59, 154, 211)),
        (0.40, (101, 214, 170)),
        (0.60, (245, 232, 116)),
        (0.80, (247, 140, 75)),
        (1.00, (190, 18, 54)),
    ]
    x = float(np.clip(value_01, 0.0, 1.0))
    for idx in range(len(anchors) - 1):
        x0, c0 = anchors[idx]
        x1, c1 = anchors[idx + 1]
        if x <= x1:
            local = 0.0 if x1 <= x0 else (x - x0) / (x1 - x0)
            return _color_lerp(c0, c1, local)
    return anchors[-1][1]


def _camera_basis_from_pitch_yaw(pitch_deg: float, yaw_deg: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pitch = math.radians(float(pitch_deg))
    yaw = math.radians(float(yaw_deg))
    forward = np.asarray(
        [
            math.cos(pitch) * math.cos(yaw),
            math.cos(pitch) * math.sin(yaw),
            math.sin(pitch),
        ],
        dtype=np.float32,
    )
    forward /= max(float(np.linalg.norm(forward)), 1.0e-8)
    world_up = np.asarray([0.0, 0.0, 1.0], dtype=np.float32)
    right = np.cross(forward, world_up).astype(np.float32, copy=False)
    if float(np.linalg.norm(right)) <= 1.0e-8:
        right = np.asarray([1.0, 0.0, 0.0], dtype=np.float32)
    right /= max(float(np.linalg.norm(right)), 1.0e-8)
    up = np.cross(right, forward).astype(np.float32, copy=False)
    up /= max(float(np.linalg.norm(up)), 1.0e-8)
    return forward, right, up


def _project_points_to_screen(
    points_world: np.ndarray,
    *,
    cam_pos: np.ndarray,
    pitch_deg: float,
    yaw_deg: float,
    fov_deg: float,
    width: int,
    height: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    forward, right, up = _camera_basis_from_pitch_yaw(pitch_deg, yaw_deg)
    rel = np.asarray(points_world, dtype=np.float32) - np.asarray(cam_pos, dtype=np.float32)[None, :]
    z = rel @ forward
    valid = z > 1.0e-6
    px = np.full((rel.shape[0],), np.nan, dtype=np.float32)
    py = np.full((rel.shape[0],), np.nan, dtype=np.float32)
    if np.any(valid):
        x = rel[valid] @ right
        y = rel[valid] @ up
        aspect = float(width) / max(float(height), 1.0)
        tan_half = max(math.tan(math.radians(float(fov_deg)) * 0.5), 1.0e-6)
        ndc_x = x / (z[valid] * tan_half * aspect)
        ndc_y = y / (z[valid] * tan_half)
        px[valid] = (ndc_x * 0.5 + 0.5) * float(width)
        py[valid] = (0.5 - ndc_y * 0.5) * float(height)
    return px, py, valid


def _box_edges(half_extents: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    hx, hy, hz = [float(v) for v in np.asarray(half_extents, dtype=np.float32).ravel()]
    vertices = np.asarray(
        [
            [-hx, -hy, -hz],
            [-hx, -hy, hz],
            [-hx, hy, -hz],
            [-hx, hy, hz],
            [hx, -hy, -hz],
            [hx, -hy, hz],
            [hx, hy, -hz],
            [hx, hy, hz],
        ],
        dtype=np.float32,
    )
    edges = np.asarray(
        [
            [0, 1], [0, 2], [0, 4],
            [1, 3], [1, 5],
            [2, 3], [2, 6],
            [3, 7],
            [4, 5], [4, 6],
            [5, 7],
            [6, 7],
        ],
        dtype=np.int32,
    )
    return vertices, edges


def _quat_to_rotmat_xyzw(quat_xyzw: np.ndarray) -> np.ndarray:
    x, y, z, w = [float(v) for v in np.asarray(quat_xyzw, dtype=np.float32).reshape(4)]
    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z
    return np.asarray(
        [
            [1.0 - 2.0 * (yy + zz), 2.0 * (xy - wz), 2.0 * (xz + wy)],
            [2.0 * (xy + wz), 1.0 - 2.0 * (xx + zz), 2.0 * (yz - wx)],
            [2.0 * (xz - wy), 2.0 * (yz + wx), 1.0 - 2.0 * (xx + yy)],
        ],
        dtype=np.float32,
    )


def _load_case(summary_path: Path, case_name: str, post_contact_seconds: float) -> DetectorCase:
    summary = _load_json(summary_path.expanduser().resolve())
    npz = np.load(Path(summary["npz_path"]).expanduser().resolve())
    scene = np.load(Path(summary["scene_npz_path"]).expanduser().resolve())
    sim_frame_dt = float(summary["sim_frame_dt_s"])
    first_force_contact_frame = summary.get("first_force_contact_frame_index")
    if first_force_contact_frame is None:
        clip_end_frame = int(np.asarray(npz["frame_indices"], dtype=np.int32)[-1])
    else:
        clip_end_frame = min(
            int(np.asarray(npz["frame_indices"], dtype=np.int32)[-1]),
            int(first_force_contact_frame) + int(round(float(post_contact_seconds) / max(sim_frame_dt, 1.0e-12))),
        )
    case_summary = _load_json(Path(summary["scene_npz_path"]).with_name(Path(summary["scene_npz_path"]).name.replace("_scene.npz", "_summary.json")))
    return DetectorCase(
        case_name=case_name,
        summary_path=summary_path.expanduser().resolve(),
        scene_npz_path=Path(summary["scene_npz_path"]).expanduser().resolve(),
        rigid_shape=str(scene["rigid_shape_kind"]).strip(),
        sim_frame_dt_s=sim_frame_dt,
        first_force_contact_frame_index=first_force_contact_frame,
        clip_end_frame_index=int(clip_end_frame),
        camera_pos=np.asarray(case_summary.get("camera_pos", [-0.95, 0.85, 0.78]), dtype=np.float32),
        camera_pitch=float(case_summary.get("camera_pitch", -10.0)),
        camera_yaw=float(case_summary.get("camera_yaw", -40.0)),
        camera_fov=float(case_summary.get("camera_fov", 55.0)),
        particle_q=np.asarray(npz["particle_q"], dtype=np.float32),
        body_q=np.asarray(npz["body_q"], dtype=np.float32),
        penalty_force=np.asarray(npz["penalty_force"], dtype=np.float32),
        total_force=np.asarray(npz["total_force"], dtype=np.float32),
        force_contact_mask=np.asarray(npz["force_contact_mask"], dtype=np.bool_),
        geom_contact_mask=np.zeros_like(np.asarray(npz["force_contact_mask"], dtype=np.bool_)),
        mesh_vertices_local=np.asarray(scene["rigid_mesh_vertices_local"], dtype=np.float32),
        mesh_render_edges=np.asarray(scene["rigid_mesh_render_edges"], dtype=np.int32),
        box_half_extents=np.asarray(scene["rigid_box_half_extents"], dtype=np.float32),
        board_clip_duration_s=float(clip_end_frame + 1) * sim_frame_dt,
    )


def _case_force_cap(case_a: DetectorCase, case_b: DetectorCase, force_mode: str, percentile: float) -> float:
    arrays = []
    for case in (case_a, case_b):
        vectors = case.penalty_force if force_mode == "penalty" else case.total_force
        mask = np.asarray(case.force_contact_mask, dtype=np.bool_)
        if np.any(mask):
            arrays.append(np.linalg.norm(vectors[mask], axis=1).astype(np.float32, copy=False))
    if not arrays:
        return 1.0
    concat = np.concatenate(arrays, axis=0)
    return max(float(np.percentile(concat, float(percentile))), 1.0e-6)


def _draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float], color: tuple[int, int, int, int], width: int) -> None:
    draw.line((start[0], start[1], end[0], end[1]), fill=color, width=width)
    dx = float(end[0] - start[0])
    dy = float(end[1] - start[1])
    norm = math.hypot(dx, dy)
    if norm <= 1.0e-6:
        return
    ux = dx / norm
    uy = dy / norm
    px = -uy
    py = ux
    head_len = max(10.0, float(width) * 2.8)
    head_w = max(5.0, float(width) * 1.5)
    p1 = (end[0] - ux * head_len + px * head_w, end[1] - uy * head_len + py * head_w)
    p2 = (end[0] - ux * head_len - px * head_w, end[1] - uy * head_len - py * head_w)
    draw.polygon([end, p1, p2], fill=color)


def _render_case_panel(
    *,
    case: DetectorCase,
    sim_frame_index: int,
    force_mode: str,
    force_cap: float,
    panel_width: int,
    panel_height: int,
    max_arrow_world_len: float,
    hold: bool,
) -> np.ndarray:
    canvas = Image.new("RGB", (panel_width, panel_height), (243, 239, 229))
    draw = ImageDraw.Draw(canvas, mode="RGBA")
    particle_q = np.asarray(case.particle_q[sim_frame_index], dtype=np.float32)
    body_q = np.asarray(case.body_q[sim_frame_index], dtype=np.float32)
    vectors = np.asarray(case.penalty_force if force_mode == "penalty" else case.total_force, dtype=np.float32)[sim_frame_index]
    mask = np.asarray(case.force_contact_mask[sim_frame_index], dtype=np.bool_)
    magnitudes = np.linalg.norm(vectors, axis=1).astype(np.float32, copy=False)

    px, py, valid = _project_points_to_screen(
        particle_q,
        cam_pos=case.camera_pos,
        pitch_deg=case.camera_pitch,
        yaw_deg=case.camera_yaw,
        fov_deg=case.camera_fov,
        width=panel_width,
        height=panel_height,
    )
    inside = valid & np.isfinite(px) & np.isfinite(py) & (px >= 0.0) & (px < float(panel_width)) & (py >= 0.0) & (py < float(panel_height))
    for x, y in zip(px[inside], py[inside], strict=False):
        draw.ellipse((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=(196, 168, 92, 190))

    if body_q.shape[0] > 0:
        body_pos = body_q[0, :3].astype(np.float32, copy=False)
        body_quat = body_q[0, 3:7].astype(np.float32, copy=False)
        rot = _quat_to_rotmat_xyzw(body_quat)
        if case.rigid_shape == "box":
            local_vertices, edges = _box_edges(case.box_half_extents)
            rigid_vertices = local_vertices @ rot.T + body_pos[None, :]
        else:
            rigid_vertices = case.mesh_vertices_local @ rot.T + body_pos[None, :]
            edges = case.mesh_render_edges
        rpx, rpy, rvalid = _project_points_to_screen(
            rigid_vertices,
            cam_pos=case.camera_pos,
            pitch_deg=case.camera_pitch,
            yaw_deg=case.camera_yaw,
            fov_deg=case.camera_fov,
            width=panel_width,
            height=panel_height,
        )
        for edge in np.asarray(edges, dtype=np.int32).tolist():
            a = int(edge[0])
            b = int(edge[1])
            if not (rvalid[a] and rvalid[b]):
                continue
            draw.line((float(rpx[a]), float(rpy[a]), float(rpx[b]), float(rpy[b])), fill=(112, 163, 212, 210), width=2)

    for idx in np.flatnonzero(mask).tolist():
        if not bool(inside[int(idx)]):
            continue
        start = particle_q[int(idx)]
        mag = float(magnitudes[int(idx)])
        ratio = float(np.clip(mag / max(force_cap, 1.0e-8), 0.0, 1.0))
        color_rgb = _spectrum_color(ratio)
        color = (color_rgb[0], color_rgb[1], color_rgb[2], 228)
        draw.ellipse((px[idx] - 2.5, py[idx] - 2.5, px[idx] + 2.5, py[idx] + 2.5), fill=color)
        if mag <= 1.0e-12:
            continue
        direction = vectors[int(idx)] / mag
        end = start + direction * float(max_arrow_world_len) * min(1.0, mag / max(force_cap, 1.0e-8))
        epx, epy, evalid = _project_points_to_screen(
            end.reshape(1, 3),
            cam_pos=case.camera_pos,
            pitch_deg=case.camera_pitch,
            yaw_deg=case.camera_yaw,
            fov_deg=case.camera_fov,
            width=panel_width,
            height=panel_height,
        )
        if not bool(evalid[0]):
            continue
        _draw_arrow(draw, (float(px[idx]), float(py[idx])), (float(epx[0]), float(epy[0])), color, width=2 if ratio < 0.55 else 3)

    title_font = _font(28, bold=True)
    body_font = _font(18)
    draw.rounded_rectangle((16, 16, 478, 140), radius=16, fill=(0, 0, 0, 126))
    case_label = "BOX + CLOTH" if case.case_name == "box_control" else "BUNNY + CLOTH"
    force_label = "Penalty Force" if force_mode == "penalty" else "Total Force"
    draw.text((28, 24), f"{case_label} | {force_label}", fill=(255, 255, 255, 255), font=title_font)
    draw.text((28, 58), "all force-active collision nodes", fill=(220, 231, 239, 255), font=body_font)
    draw.text(
        (28, 84),
        f"sim_frame={sim_frame_index}  colliding_nodes={int(np.count_nonzero(mask))}",
        fill=(245, 241, 234, 255),
        font=body_font,
    )
    draw.text(
        (28, 108),
        f"first_collision={case.first_force_contact_frame_index}",
        fill=(245, 241, 234, 255),
        font=body_font,
    )
    if hold:
        draw.rounded_rectangle((panel_width - 116, 18, panel_width - 18, 56), radius=12, fill=(0, 0, 0, 156))
        draw.text((panel_width - 94, 28), "HOLD", fill=(255, 224, 133, 255), font=_font(20, bold=True))

    bar_x0 = panel_width - 194
    bar_y0 = 86
    bar_w = 150
    bar_h = 16
    for col in range(bar_w):
        rgb = _spectrum_color(col / max(1, bar_w - 1))
        draw.line(((bar_x0 + col, bar_y0), (bar_x0 + col, bar_y0 + bar_h)), fill=(rgb[0], rgb[1], rgb[2], 255), width=1)
    draw.rectangle((bar_x0, bar_y0, bar_x0 + bar_w, bar_y0 + bar_h), outline=(255, 255, 255, 220), width=1)
    draw.text((bar_x0, bar_y0 + 22), "low", fill=(235, 235, 235, 255), font=body_font)
    draw.text((bar_x0 + 108, bar_y0 + 22), "high", fill=(235, 235, 235, 255), font=body_font)
    draw.text((bar_x0 - 4, bar_y0 + 44), f"cap={force_cap:.3e} N", fill=(235, 235, 235, 255), font=body_font)
    return np.asarray(canvas, dtype=np.uint8)


def _compose_board_frame(top_left: np.ndarray, top_right: np.ndarray, bottom_left: np.ndarray, bottom_right: np.ndarray) -> np.ndarray:
    tl = np.asarray(top_left, dtype=np.uint8)
    tr = np.asarray(top_right, dtype=np.uint8)
    bl = np.asarray(bottom_left, dtype=np.uint8)
    br = np.asarray(bottom_right, dtype=np.uint8)
    h, w, _ = tl.shape
    canvas = np.zeros((h * 2, w * 2, 3), dtype=np.uint8)
    canvas[0:h, 0:w] = tl
    canvas[0:h, w : 2 * w] = tr
    canvas[h : 2 * h, 0:w] = bl
    canvas[h : 2 * h, w : 2 * w] = br
    canvas[h - 2 : h + 2, :, :] = 220
    canvas[:, w - 2 : w + 2, :] = 220
    return canvas


def _write_video(frames: list[np.ndarray], out_path: Path, fps: float) -> Path:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg not found in PATH")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    height, width, _ = np.asarray(frames[0], dtype=np.uint8).shape
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{width}x{height}",
        "-r",
        f"{fps:.6f}",
        "-i",
        "-",
        "-an",
        "-vcodec",
        "libx264",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        str(out_path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for frame in frames:
            proc.stdin.write(np.asarray(frame, dtype=np.uint8).tobytes())
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed while encoding the collision board")
    finally:
        if proc.stdin and not proc.stdin.closed:
            proc.stdin.close()
    return out_path


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    box_case = _load_case(args.box_detector_summary.expanduser().resolve(), "box_control", float(args.post_contact_seconds))
    bunny_case = _load_case(args.bunny_detector_summary.expanduser().resolve(), "bunny_baseline", float(args.post_contact_seconds))
    penalty_cap = _case_force_cap(box_case, bunny_case, "penalty", float(args.force_percentile))
    total_cap = _case_force_cap(box_case, bunny_case, "total", float(args.force_percentile))
    board_duration_s = max(box_case.board_clip_duration_s, bunny_case.board_clip_duration_s)
    board_frame_count = max(1, int(round(board_duration_s * float(args.board_fps))) + 1)
    board_frames: list[np.ndarray] = []

    for board_idx in range(board_frame_count):
        t = float(board_idx) / max(float(args.board_fps), 1.0e-8)
        box_frame = min(int(round(t / box_case.sim_frame_dt_s)), int(box_case.clip_end_frame_index))
        bunny_frame = min(int(round(t / bunny_case.sim_frame_dt_s)), int(bunny_case.clip_end_frame_index))
        box_hold = t > box_case.board_clip_duration_s
        bunny_hold = t > bunny_case.board_clip_duration_s
        board = _compose_board_frame(
            _render_case_panel(
                case=box_case,
                sim_frame_index=box_frame,
                force_mode="penalty",
                force_cap=penalty_cap,
                panel_width=int(args.panel_width),
                panel_height=int(args.panel_height),
                max_arrow_world_len=float(args.max_arrow_world_len),
                hold=box_hold,
            ),
            _render_case_panel(
                case=box_case,
                sim_frame_index=box_frame,
                force_mode="total",
                force_cap=total_cap,
                panel_width=int(args.panel_width),
                panel_height=int(args.panel_height),
                max_arrow_world_len=float(args.max_arrow_world_len),
                hold=box_hold,
            ),
            _render_case_panel(
                case=bunny_case,
                sim_frame_index=bunny_frame,
                force_mode="penalty",
                force_cap=penalty_cap,
                panel_width=int(args.panel_width),
                panel_height=int(args.panel_height),
                max_arrow_world_len=float(args.max_arrow_world_len),
                hold=bunny_hold,
            ),
            _render_case_panel(
                case=bunny_case,
                sim_frame_index=bunny_frame,
                force_mode="total",
                force_cap=total_cap,
                panel_width=int(args.panel_width),
                panel_height=int(args.panel_height),
                max_arrow_world_len=float(args.max_arrow_world_len),
                hold=bunny_hold,
            ),
        )
        board_frames.append(board)
        if (board_idx + 1) % 10 == 0 or board_idx + 1 == board_frame_count:
            print(f"[render_bunny_penetration_collision_board] board frame {board_idx + 1}/{board_frame_count}", flush=True)

    board_video = out_dir / "collision_force_board_2x2.mp4"
    _write_video(board_frames, board_video, float(args.board_fps))
    first_frame_path = (
        args.first_frame_png.expanduser().resolve()
        if args.first_frame_png is not None
        else out_dir / "collision_force_board_2x2_first_frame.png"
    )
    Image.fromarray(board_frames[0], mode="RGB").save(first_frame_path)
    summary = {
        "board_video": str(board_video),
        "board_first_frame_png": str(first_frame_path),
        "board_frame_count": int(board_frame_count),
        "board_fps": float(args.board_fps),
        "board_duration_s": float(board_duration_s),
        "panel_semantics": {
            "top_left": "box penalty",
            "top_right": "box total",
            "bottom_left": "bunny penalty",
            "bottom_right": "bunny total",
        },
        "node_selection_mode": "all_force_contact_nodes",
        "legend_present": True,
        "hold_annotation_enabled": True,
        "panel_labels_present": True,
        "force_definitions": {
            "penalty_force": "f_external_total",
            "total_force": "f_internal_total + f_external_total + mass * gravity_vec",
        },
        "force_scales": {
            "penalty_cap_n": float(penalty_cap),
            "total_cap_n": float(total_cap),
            "percentile": float(args.force_percentile),
            "color_map": "blue-cyan-green-yellow-orange-red",
        },
        "cases": {
            "box_control": {
                "detector_summary": str(box_case.summary_path),
                "first_force_contact_frame_index": box_case.first_force_contact_frame_index,
                "clip_end_frame_index": int(box_case.clip_end_frame_index),
                "clip_duration_s": float(box_case.board_clip_duration_s),
            },
            "bunny_baseline": {
                "detector_summary": str(bunny_case.summary_path),
                "first_force_contact_frame_index": bunny_case.first_force_contact_frame_index,
                "clip_end_frame_index": int(bunny_case.clip_end_frame_index),
                "clip_duration_s": float(bunny_case.board_clip_duration_s),
            },
        },
    }
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[render_bunny_penetration_collision_board] video={board_video}", flush=True)
    print(f"[render_bunny_penetration_collision_board] summary={summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
