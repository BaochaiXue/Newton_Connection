#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


@dataclass
class CaseRender:
    case_name: str
    summary_path: Path
    detector_npz_path: Path
    render_frames_dir: Path
    selected_video_frame_indices: np.ndarray
    selected_sim_frame_indices: np.ndarray
    first_contact_frame: int | None
    clip_end_frame: int
    sim_frame_dt: float
    render_fps: float
    cam_pos: np.ndarray
    cam_pitch_deg: float
    cam_yaw_deg: float
    cam_fov_deg: float
    width: int
    height: int
    data: dict[str, np.ndarray]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Render the OFF-only 2x2 bunny penetration collision-force board."
    )
    p.add_argument("--box-summary", type=Path, required=True)
    p.add_argument("--bunny-summary", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--force-percentile", type=float, default=98.0)
    p.add_argument("--max-arrow-world-len", type=float, default=0.04)
    p.add_argument("--panel-width", type=int, default=None)
    p.add_argument("--panel-height", type=int, default=None)
    p.add_argument("--first-frame-png", type=Path, default=None)
    return p.parse_args()


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


def _load_case(summary_path: Path) -> CaseRender:
    summary_path = summary_path.expanduser().resolve()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    detector_npz_path = Path(summary["detector_npz"]).expanduser().resolve()
    render_frames_dir = Path(summary["render_frames_dir"]).expanduser().resolve()
    if not detector_npz_path.exists():
        raise FileNotFoundError(detector_npz_path)
    if not render_frames_dir.exists():
        raise FileNotFoundError(render_frames_dir)
    data = dict(np.load(detector_npz_path, allow_pickle=False))
    cam = summary["camera"]
    return CaseRender(
        case_name=str(summary["case_name"]),
        summary_path=summary_path,
        detector_npz_path=detector_npz_path,
        render_frames_dir=render_frames_dir,
        selected_video_frame_indices=np.asarray(summary["clip_video_frame_indices"], dtype=np.int32),
        selected_sim_frame_indices=np.asarray(summary["clip_render_sim_frame_indices"], dtype=np.int32),
        first_contact_frame=summary["first_force_contact_frame_index"],
        clip_end_frame=int(summary["clip_end_frame_index"]),
        sim_frame_dt=float(summary["sim_frame_dt_s"]),
        render_fps=float(cam.get("render_fps", 24.0)),
        cam_pos=np.asarray(cam["render_camera_pos"], dtype=np.float32),
        cam_pitch_deg=float(cam["render_camera_pitch_deg"]),
        cam_yaw_deg=float(cam["render_camera_yaw_deg"]),
        cam_fov_deg=float(cam["render_camera_fov_deg"]),
        width=int(cam["screen_width"]),
        height=int(cam["screen_height"]),
        data=data,
    )


def _color_lerp(c0: tuple[int, int, int], c1: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    alpha = float(np.clip(t, 0.0, 1.0))
    return tuple(int(round((1.0 - alpha) * a + alpha * b)) for a, b in zip(c0, c1, strict=True))


def _spectrum_color(value_01: float) -> tuple[int, int, int]:
    anchors = [
        (0.00, (59, 76, 192)),
        (0.25, (67, 147, 195)),
        (0.50, (146, 197, 222)),
        (0.70, (254, 224, 144)),
        (0.85, (244, 109, 67)),
        (1.00, (180, 4, 38)),
    ]
    x = float(np.clip(value_01, 0.0, 1.0))
    for idx in range(len(anchors) - 1):
        x0, c0 = anchors[idx]
        x1, c1 = anchors[idx + 1]
        if x <= x1:
            local = 0.0 if x1 <= x0 else (x - x0) / (x1 - x0)
            return _color_lerp(c0, c1, local)
    return anchors[-1][1]


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
    head_len = max(7.0, float(width) * 2.3)
    head_w = max(4.0, float(width) * 1.2)
    p1 = (end[0] - ux * head_len + px * head_w, end[1] - uy * head_len + py * head_w)
    p2 = (end[0] - ux * head_len - px * head_w, end[1] - uy * head_len - py * head_w)
    draw.polygon([end, p1, p2], fill=color)


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


def _project_world_to_screen(world: np.ndarray, *, case: CaseRender) -> tuple[float, float] | None:
    forward, right, up = _camera_basis_from_pitch_yaw(case.cam_pitch_deg, case.cam_yaw_deg)
    rel = np.asarray(world, dtype=np.float32) - case.cam_pos
    z = float(rel @ forward)
    if z <= 1.0e-6:
        return None
    x = float(rel @ right)
    y = float(rel @ up)
    aspect = float(case.width) / max(float(case.height), 1.0)
    tan_half = max(math.tan(math.radians(float(case.cam_fov_deg)) * 0.5), 1.0e-6)
    ndc_x = x / (z * tan_half * aspect)
    ndc_y = y / (z * tan_half)
    px = (ndc_x * 0.5 + 0.5) * float(case.width)
    py = (0.5 - ndc_y * 0.5) * float(case.height)
    return px, py


def _panel_title(case_name: str, force_mode: str) -> str:
    rigid = "BOX + CLOTH" if case_name == "box_control" else "BUNNY + CLOTH"
    family = "Penalty Force" if force_mode == "penalty" else "Total Force"
    return f"{rigid} | {family}"


def _overlay_text_block(
    image: Image.Image,
    *,
    title: str,
    subtitle: str,
    stats_lines: list[str],
    cap_value: float,
    hold: bool,
) -> None:
    draw = ImageDraw.Draw(image, mode="RGBA")
    title_font = _font(24, bold=True)
    body_font = _font(17)
    draw.rounded_rectangle((14, 14, 520, 146), radius=16, fill=(0, 0, 0, 128))
    draw.text((28, 24), title, fill=(255, 255, 255, 255), font=title_font)
    draw.text((28, 56), subtitle, fill=(214, 226, 236, 255), font=body_font)
    y = 84
    for line in stats_lines:
        draw.text((28, y), line, fill=(246, 241, 234, 255), font=body_font)
        y += 20
    if hold:
        draw.rounded_rectangle((28, y + 2, 120, y + 28), radius=10, fill=(132, 80, 36, 220))
        draw.text((40, y + 7), "HOLD", fill=(255, 248, 238, 255), font=body_font)

    bar_x0 = image.width - 206
    bar_y0 = 22
    bar_w = 164
    bar_h = 16
    for step in range(bar_w):
        rgb = _spectrum_color(step / max(1, bar_w - 1))
        draw.line(((bar_x0 + step, bar_y0), (bar_x0 + step, bar_y0 + bar_h)), fill=(rgb[0], rgb[1], rgb[2], 255), width=1)
    draw.rectangle((bar_x0, bar_y0, bar_x0 + bar_w, bar_y0 + bar_h), outline=(255, 255, 255, 220), width=1)
    draw.text((bar_x0, bar_y0 + 22), "small", fill=(238, 238, 238, 255), font=body_font)
    draw.text((bar_x0 + 108, bar_y0 + 22), "large", fill=(238, 238, 238, 255), font=body_font)
    draw.text((bar_x0 - 8, bar_y0 + 46), f"color/len cap = {cap_value:.3e} N", fill=(238, 238, 238, 255), font=body_font)


def _load_frame(frame_path: Path) -> Image.Image:
    with Image.open(frame_path) as handle:
        return handle.convert("RGB")


def _force_cap(case: CaseRender, force_mode: str, percentile: float) -> float:
    key = "penalty_force_norm" if force_mode == "penalty" else "total_force_norm"
    mask = np.asarray(case.data["rigid_force_contact_mask"], dtype=bool)
    mags = np.asarray(case.data[key], dtype=np.float32)
    active = mags[mask]
    if active.size == 0:
        return 1.0
    cap = float(np.percentile(active, float(percentile)))
    return max(cap, float(np.max(active)), 1.0e-6) if cap <= 1.0e-9 else cap


def _resize_panel(frame: np.ndarray, width: int | None, height: int | None) -> np.ndarray:
    if width is None or height is None:
        return np.asarray(frame, dtype=np.uint8)
    image = Image.fromarray(np.asarray(frame, dtype=np.uint8), mode="RGB")
    resized = image.resize((int(width), int(height)), resample=Image.Resampling.LANCZOS)
    return np.asarray(resized, dtype=np.uint8)


def _render_panel(
    *,
    case: CaseRender,
    board_frame_idx: int,
    force_mode: str,
    force_cap: float,
    max_arrow_world_len: float,
    panel_width: int | None,
    panel_height: int | None,
) -> np.ndarray:
    hold = board_frame_idx >= int(case.selected_sim_frame_indices.shape[0])
    local_idx = min(board_frame_idx, int(case.selected_sim_frame_indices.shape[0]) - 1)
    sim_idx = int(case.selected_sim_frame_indices[local_idx])
    video_idx = int(case.selected_video_frame_indices[local_idx])
    frame_path = case.render_frames_dir / f"frame_{video_idx:05d}.png"
    image = _load_frame(frame_path)
    draw = ImageDraw.Draw(image, mode="RGBA")
    particle_q = np.asarray(case.data["particle_q"][sim_idx], dtype=np.float32)
    mask = np.asarray(case.data["rigid_force_contact_mask"][sim_idx], dtype=bool)
    force_key = "penalty_force" if force_mode == "penalty" else "total_force"
    norm_key = "penalty_force_norm" if force_mode == "penalty" else "total_force_norm"
    vectors = np.asarray(case.data[force_key][sim_idx], dtype=np.float32)
    mags = np.asarray(case.data[norm_key][sim_idx], dtype=np.float32)
    indices = np.flatnonzero(mask)
    active_mags = mags[mask]
    max_force = float(np.max(active_mags)) if active_mags.size else 0.0
    median_force = float(np.median(active_mags)) if active_mags.size else 0.0
    scale = min(1.0, float(max_arrow_world_len) / max(float(force_cap), 1.0e-8))
    for idx in indices.tolist():
        mag = float(mags[idx])
        ratio = float(np.clip(mag / max(force_cap, 1.0e-8), 0.0, 1.0))
        color_rgb = _spectrum_color(ratio)
        color = (color_rgb[0], color_rgb[1], color_rgb[2], 230)
        start = particle_q[int(idx)]
        start_px = _project_world_to_screen(start, case=case)
        if start_px is None:
            continue
        radius_px = 2 if ratio < 0.4 else 3
        draw.ellipse((start_px[0] - radius_px, start_px[1] - radius_px, start_px[0] + radius_px, start_px[1] + radius_px), fill=color)
        if mag <= 1.0e-10:
            continue
        vec = vectors[int(idx)] * scale
        if mag > force_cap:
            vec = (vectors[int(idx)] / max(mag, 1.0e-12) * float(max_arrow_world_len)).astype(np.float32, copy=False)
        end_px = _project_world_to_screen(start + vec, case=case)
        if end_px is None:
            continue
        _draw_arrow(draw, start_px, end_px, color, width=2 if ratio < 0.55 else 3)

    title = _panel_title(case.case_name, force_mode)
    subtitle = "all rigid force-active nodes | blue -> red = force magnitude"
    stats_lines = [
        f"colliding_nodes = {int(indices.size)}",
        f"force_median = {median_force:.3e} N | force_max = {max_force:.3e} N",
        f"first_contact_frame = {case.first_contact_frame if case.first_contact_frame is not None else 'NA'} | sim_frame = {sim_idx}",
    ]
    _overlay_text_block(image, title=title, subtitle=subtitle, stats_lines=stats_lines, cap_value=float(force_cap), hold=hold)
    return _resize_panel(np.asarray(image, dtype=np.uint8), panel_width, panel_height)


def _compose_board_frame(tl: np.ndarray, tr: np.ndarray, bl: np.ndarray, br: np.ndarray) -> np.ndarray:
    tl = np.asarray(tl, dtype=np.uint8)
    tr = np.asarray(tr, dtype=np.uint8)
    bl = np.asarray(bl, dtype=np.uint8)
    br = np.asarray(br, dtype=np.uint8)
    if tl.shape != tr.shape or tl.shape != bl.shape or tl.shape != br.shape:
        raise ValueError("All board panels must share the same shape")
    h, w, _ = tl.shape
    canvas = np.zeros((h * 2, w * 2, 3), dtype=np.uint8)
    canvas[:h, :w] = tl
    canvas[:h, w:] = tr
    canvas[h:, :w] = bl
    canvas[h:, w:] = br
    canvas[h - 2 : h + 2, :, :] = 224
    canvas[:, w - 2 : w + 2, :] = 224
    return canvas


def _write_video(frames: list[np.ndarray], out_path: Path, fps: float) -> Path:
    if not frames:
        raise RuntimeError("No frames available for board video.")
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
            raise RuntimeError("ffmpeg failed while encoding board video")
    finally:
        if proc.stdin and not proc.stdin.closed:
            proc.stdin.close()
    return out_path


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    box = _load_case(args.box_summary)
    bunny = _load_case(args.bunny_summary)
    penalty_cap = max(_force_cap(box, "penalty", args.force_percentile), _force_cap(bunny, "penalty", args.force_percentile))
    total_cap = max(_force_cap(box, "total", args.force_percentile), _force_cap(bunny, "total", args.force_percentile))
    board_frame_count = max(int(box.selected_sim_frame_indices.shape[0]), int(bunny.selected_sim_frame_indices.shape[0]))
    preview_path = args.first_frame_png.expanduser().resolve() if args.first_frame_png is not None else out_dir / "collision_force_board_2x2_first_frame.png"

    board_frames: list[np.ndarray] = []
    for board_idx in range(board_frame_count):
        tl = _render_panel(case=box, board_frame_idx=board_idx, force_mode="penalty", force_cap=penalty_cap, max_arrow_world_len=args.max_arrow_world_len, panel_width=args.panel_width, panel_height=args.panel_height)
        tr = _render_panel(case=box, board_frame_idx=board_idx, force_mode="total", force_cap=total_cap, max_arrow_world_len=args.max_arrow_world_len, panel_width=args.panel_width, panel_height=args.panel_height)
        bl = _render_panel(case=bunny, board_frame_idx=board_idx, force_mode="penalty", force_cap=penalty_cap, max_arrow_world_len=args.max_arrow_world_len, panel_width=args.panel_width, panel_height=args.panel_height)
        br = _render_panel(case=bunny, board_frame_idx=board_idx, force_mode="total", force_cap=total_cap, max_arrow_world_len=args.max_arrow_world_len, panel_width=args.panel_width, panel_height=args.panel_height)
        board = _compose_board_frame(tl, tr, bl, br)
        board_frames.append(board)
        if board_idx == 0:
            Image.fromarray(board, mode="RGB").save(preview_path)
        if (board_idx + 1) % 10 == 0 or board_idx + 1 == board_frame_count:
            print(f"[collision_board] board frame {board_idx + 1}/{board_frame_count}", flush=True)

    board_video = _write_video(board_frames, out_dir / "collision_force_board_2x2.mp4", fps=float(box.render_fps))
    panel_w = int(args.panel_width if args.panel_width is not None else board_frames[0].shape[1] // 2)
    panel_h = int(args.panel_height if args.panel_height is not None else board_frames[0].shape[0] // 2)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "board_video": str(board_video),
        "board_first_frame_png": str(preview_path),
        "panel_order": [
            "top_left=box_penalty",
            "top_right=box_total",
            "bottom_left=bunny_penalty",
            "bottom_right=bunny_total",
        ],
        "all_colliding_nodes_main_board": True,
        "node_mask_semantics": "rigid_force_contact_mask",
        "force_definitions": {
            "penalty_force": "f_external_total on the current frame, displayed only on nodes in rigid_force_contact_mask",
            "total_force": "f_internal_total + f_external_total + mass * gravity_vec on the current frame, displayed only on nodes in rigid_force_contact_mask",
        },
        "color_encoding": {
            "scheme": "blue->cyan->green/yellow->orange->red",
            "high_force_color": "red",
            "penalty_force_cap_n": float(penalty_cap),
            "total_force_cap_n": float(total_cap),
            "force_percentile": float(args.force_percentile),
            "max_arrow_world_len_m": float(args.max_arrow_world_len),
        },
        "colorbar_present": True,
        "hold_annotation_present": True,
        "exact_mapping_ratio_full_display_interval": 1.0,
        "reused_mapping_ratio_full_display_interval": 0.0,
        "render_fps": float(box.render_fps),
        "board_frame_count": int(board_frame_count),
        "panel_resolution": [panel_w, panel_h],
        "board_resolution": [int(board_frames[0].shape[1]), int(board_frames[0].shape[0])],
        "cases": {
            "box_control": {
                "detector_summary_path": str(box.summary_path),
                "detector_npz_path": str(box.detector_npz_path),
                "first_force_contact_frame_index": box.first_contact_frame,
                "clip_end_frame_index": int(box.clip_end_frame),
                "selected_video_frame_count": int(box.selected_video_frame_indices.shape[0]),
                "selected_sim_frame_indices": [int(v) for v in box.selected_sim_frame_indices.tolist()],
                "hold_frames": int(max(0, board_frame_count - int(box.selected_sim_frame_indices.shape[0]))),
                "source_render_frames_dir": str(box.render_frames_dir),
            },
            "bunny_baseline": {
                "detector_summary_path": str(bunny.summary_path),
                "detector_npz_path": str(bunny.detector_npz_path),
                "first_force_contact_frame_index": bunny.first_contact_frame,
                "clip_end_frame_index": int(bunny.clip_end_frame),
                "selected_video_frame_count": int(bunny.selected_video_frame_indices.shape[0]),
                "selected_sim_frame_indices": [int(v) for v in bunny.selected_sim_frame_indices.tolist()],
                "hold_frames": int(max(0, board_frame_count - int(bunny.selected_sim_frame_indices.shape[0]))),
                "source_render_frames_dir": str(bunny.render_frames_dir),
            },
        },
    }
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[collision_board] video={board_video}", flush=True)
    print(f"[collision_board] summary={summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
