#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import pickle
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import warp as wp
from PIL import Image, ImageDraw, ImageFont


@dataclass
class CaseContext:
    case_name: str
    bundle_path: Path
    args: argparse.Namespace
    ir_obj: dict[str, Any]
    sim_data: dict[str, Any]
    frame_paths: list[Path]
    render_indices: np.ndarray
    selected_video_frame_indices: list[int]
    selected_sim_frame_indices: list[int]
    snapshots: list[dict[str, Any]]
    cam_pos: np.ndarray
    cam_pitch: float
    cam_yaw: float
    cam_fov: float
    width: int
    height: int
    first_contact_frame: int | None
    clip_end_frame: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render a 2x2 board for the bunny penetration study: box/bunny x penalty/total force, "
            "using all cloth nodes that are in rigid contact on every displayed frame."
        )
    )
    parser.add_argument("--box-bundle", type=Path, required=True)
    parser.add_argument("--bunny-bundle", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument(
        "--post-contact-seconds",
        type=float,
        default=1.0,
        help="Trim each case to t=0 through this many seconds after first rigid contact.",
    )
    parser.add_argument(
        "--force-percentile",
        type=float,
        default=98.0,
        help="Percentile used to cap arrow/color normalization for each force family.",
    )
    parser.add_argument(
        "--max-arrow-world-len",
        type=float,
        default=0.04,
        help="Maximum world-space arrow length used after force normalization.",
    )
    parser.add_argument(
        "--first-frame-png",
        type=Path,
        default=None,
        help="Optional explicit path for the first composited board frame.",
    )
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


def _color_lerp(c0: tuple[int, int, int], c1: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    alpha = float(np.clip(t, 0.0, 1.0))
    return tuple(
        int(round((1.0 - alpha) * float(a) + alpha * float(b)))
        for a, b in zip(c0, c1, strict=True)
    )


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


def _overlay_text_block(
    image: Image.Image,
    *,
    title: str,
    subtitle: str,
    stats_lines: list[str],
    cap_value: float,
) -> None:
    draw = ImageDraw.Draw(image, mode="RGBA")
    title_font = _font(26, bold=True)
    body_font = _font(18)
    draw.rounded_rectangle((14, 14, 516, 146), radius=16, fill=(0, 0, 0, 128))
    draw.text((28, 24), title, fill=(255, 255, 255, 255), font=title_font)
    draw.text((28, 56), subtitle, fill=(214, 226, 236, 255), font=body_font)
    y = 84
    for line in stats_lines:
        draw.text((28, y), line, fill=(246, 241, 234, 255), font=body_font)
        y += 20

    bar_x0 = image.width - 206
    bar_y0 = 22
    bar_w = 164
    bar_h = 16
    for step in range(bar_w):
        rgb = _spectrum_color(step / max(1, bar_w - 1))
        draw.line(
            ((bar_x0 + step, bar_y0), (bar_x0 + step, bar_y0 + bar_h)),
            fill=(rgb[0], rgb[1], rgb[2], 255),
            width=1,
        )
    draw.rectangle((bar_x0, bar_y0, bar_x0 + bar_w, bar_y0 + bar_h), outline=(255, 255, 255, 220), width=1)
    draw.text((bar_x0, bar_y0 + 22), "small", fill=(238, 238, 238, 255), font=body_font)
    draw.text((bar_x0 + 108, bar_y0 + 22), "large", fill=(238, 238, 238, 255), font=body_font)
    draw.text(
        (bar_x0 - 6, bar_y0 + 46),
        f"color/len cap = {cap_value:.3e} N",
        fill=(238, 238, 238, 255),
        font=body_font,
    )


def _target_force_vectors(snapshot: dict[str, Any], force_mode: str) -> np.ndarray:
    external = np.asarray(snapshot["f_external_total"], dtype=np.float32)
    if force_mode == "penalty":
        return external
    internal = np.asarray(snapshot["f_internal_total"], dtype=np.float32)
    return (internal + external).astype(np.float32, copy=False)


def _target_contact_mask(snapshot: dict[str, Any]) -> np.ndarray:
    return np.asarray(snapshot["geom_contact_mask"], dtype=bool)


def _force_cap(snapshots: list[dict[str, Any]], force_mode: str, percentile: float) -> float:
    mags: list[np.ndarray] = []
    for snapshot in snapshots:
        mask = _target_contact_mask(snapshot)
        if not np.any(mask):
            continue
        vectors = _target_force_vectors(snapshot, force_mode)[mask]
        if vectors.size == 0:
            continue
        mags.append(np.linalg.norm(vectors, axis=1).astype(np.float32, copy=False))
    if not mags:
        return 1.0
    concat = np.concatenate(mags, axis=0)
    cap = float(np.percentile(concat, float(percentile)))
    return max(cap, float(np.max(concat)), 1.0e-6) if cap <= 1.0e-9 else cap


def _load_frame(path: Path) -> Image.Image:
    with Image.open(path) as handle:
        return handle.convert("RGB")


def _bundle_frames_dir(bundle: dict[str, Any]) -> Path:
    raw = str(bundle.get("render_frames_dir", "") or "").strip()
    if not raw:
        raise FileNotFoundError("Bundle does not contain render_frames_dir; rerun the case with force-diagnostic rendering enabled.")
    path = Path(raw).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Saved render frames not found: {path}")
    return path


def _resolve_first_contact_frame(sim_data: dict[str, Any]) -> int | None:
    first_contact = int(sim_data.get("first_rigid_contact_frame", -1))
    return None if first_contact < 0 else int(first_contact)


def _selected_video_frame_indices(
    *,
    render_indices: np.ndarray,
    frame_count: int,
    first_contact_frame: int | None,
    sim_frame_dt: float,
    post_contact_seconds: float,
) -> tuple[list[int], list[int], int]:
    render_indices = np.asarray(render_indices, dtype=np.int32).reshape(-1)
    usable_count = min(int(frame_count), int(render_indices.shape[0]))
    if usable_count <= 0:
        return [], [], 0
    if first_contact_frame is None or float(post_contact_seconds) <= 0.0:
        last_video_idx = usable_count - 1
        selected_video = list(range(usable_count))
        selected_sim = [int(v) for v in render_indices[:usable_count].tolist()]
        return selected_video, selected_sim, int(render_indices[min(last_video_idx, render_indices.shape[0] - 1)])

    extra_frames = int(round(float(post_contact_seconds) / max(float(sim_frame_dt), 1.0e-12)))
    clip_end_frame = int(first_contact_frame) + max(0, extra_frames)
    selected_video: list[int] = []
    selected_sim: list[int] = []
    for video_idx in range(usable_count):
        sim_idx = int(render_indices[video_idx])
        if sim_idx > clip_end_frame:
            break
        selected_video.append(int(video_idx))
        selected_sim.append(sim_idx)
    if not selected_video:
        selected_video = [0]
        selected_sim = [int(render_indices[0])]
    return selected_video, selected_sim, int(min(clip_end_frame, int(render_indices[selected_video[-1]])))


def _load_case_context(bundle_path: Path, case_name: str, demo_module, post_contact_seconds: float) -> CaseContext:
    with bundle_path.open("rb") as handle:
        bundle = pickle.load(handle)

    args = bundle["args"]
    ir_obj = bundle["ir_obj"]
    sim_data = bundle["render_sim_data"]
    frames_dir = _bundle_frames_dir(bundle)
    frame_paths = sorted(frames_dir.glob("frame_*.png"))
    if not frame_paths:
        raise FileNotFoundError(f"No saved frame PNGs under {frames_dir}")

    render_indices = np.asarray(
        sim_data.get("render_output_frame_indices"),
        dtype=np.int32,
    ).reshape(-1)
    if render_indices.size == 0:
        raise RuntimeError(f"Bundle {bundle_path} does not contain render_output_frame_indices")

    sim_frame_dt = float(sim_data["sim_dt"]) * float(sim_data["substeps"])
    first_contact_frame = _resolve_first_contact_frame(sim_data)
    selected_video, selected_sim, clip_end_frame = _selected_video_frame_indices(
        render_indices=render_indices,
        frame_count=len(frame_paths),
        first_contact_frame=first_contact_frame,
        sim_frame_dt=sim_frame_dt,
        post_contact_seconds=post_contact_seconds,
    )

    device = demo_module.newton_import_ir.resolve_device(str(bundle["device"]))
    model, meta, n_obj = demo_module.build_model(ir_obj, args, device)
    explicit_context = demo_module._make_explicit_force_snapshot_context(
        model=model,
        ir_obj=ir_obj,
        args=args,
        device=device,
        n_obj=n_obj,
    )
    snapshots: list[dict[str, Any]] = []
    for idx, sim_idx in enumerate(selected_sim):
        snapshot = demo_module._capture_force_snapshot_from_explicit_state(
            model=model,
            meta=meta,
            ir_obj=ir_obj,
            args=args,
            device=device,
            n_obj=n_obj,
            frame_index=int(sim_idx),
            substep_index_in_frame=0,
            global_substep_index=int(sim_idx) * int(sim_data["substeps"]),
            sim_time=float(sim_idx) * sim_frame_dt,
            particle_q=np.asarray(sim_data["particle_q_all"][sim_idx], dtype=np.float32),
            particle_qd=np.asarray(sim_data["particle_qd_all"][sim_idx], dtype=np.float32),
            body_q=np.asarray(sim_data["body_q"][sim_idx], dtype=np.float32),
            body_qd=np.asarray(sim_data["body_qd"][sim_idx], dtype=np.float32),
            explicit_context=explicit_context,
        )
        snapshots.append(snapshot)
        if (idx + 1) % 10 == 0 or idx + 1 == len(selected_sim):
            print(f"[collision_board] {case_name}: snapshot {idx + 1}/{len(selected_sim)}", flush=True)

    cam_pos = np.asarray(
        sim_data.get("render_camera_pos", np.asarray(args.camera_pos, dtype=np.float32)),
        dtype=np.float32,
    )
    return CaseContext(
        case_name=case_name,
        bundle_path=bundle_path,
        args=args,
        ir_obj=ir_obj,
        sim_data=sim_data,
        frame_paths=frame_paths,
        render_indices=render_indices,
        selected_video_frame_indices=selected_video,
        selected_sim_frame_indices=selected_sim,
        snapshots=snapshots,
        cam_pos=cam_pos,
        cam_pitch=float(sim_data.get("render_camera_pitch_deg", float(args.camera_pitch))),
        cam_yaw=float(sim_data.get("render_camera_yaw_deg", float(args.camera_yaw))),
        cam_fov=float(sim_data.get("render_camera_fov_deg", float(args.camera_fov))),
        width=int(args.screen_width),
        height=int(args.screen_height),
        first_contact_frame=first_contact_frame,
        clip_end_frame=clip_end_frame,
    )


def _project_point(case: CaseContext, demo_module, world: np.ndarray) -> tuple[float, float] | None:
    return demo_module._project_world_to_screen(
        np.asarray(world, dtype=np.float32),
        cam_pos=np.asarray(case.cam_pos, dtype=np.float32),
        pitch_deg=float(case.cam_pitch),
        yaw_deg=float(case.cam_yaw),
        fov_deg=float(case.cam_fov),
        width=int(case.width),
        height=int(case.height),
    )


def _panel_title(case_name: str, force_mode: str) -> str:
    case_label = "BOX + CLOTH" if case_name == "box_control" else "BUNNY + CLOTH"
    force_label = "Penalty Force" if force_mode == "penalty" else "Total Force"
    return f"{case_label} | {force_label}"


def _overlay_case_panel(
    *,
    case: CaseContext,
    snapshot: dict[str, Any],
    frame_path: Path,
    force_mode: str,
    force_cap: float,
    max_arrow_world_len: float,
    demo_module,
) -> np.ndarray:
    image = _load_frame(frame_path)
    draw = ImageDraw.Draw(image, mode="RGBA")
    mask = _target_contact_mask(snapshot)
    particle_q = np.asarray(snapshot["particle_q"], dtype=np.float32)
    vectors = _target_force_vectors(snapshot, force_mode)
    mags = np.linalg.norm(vectors, axis=1).astype(np.float32, copy=False)
    contact_indices = np.flatnonzero(mask)
    active_force_count = int(np.count_nonzero(mask & (mags > 1.0e-8)))
    active_mags = mags[mask]
    max_force = float(np.max(active_mags)) if active_mags.size else 0.0
    median_force = float(np.median(active_mags)) if active_mags.size else 0.0

    for idx in contact_indices.tolist():
        mag = float(mags[idx])
        ratio = float(np.clip(mag / max(force_cap, 1.0e-8), 0.0, 1.0))
        color_rgb = _spectrum_color(ratio)
        color = (color_rgb[0], color_rgb[1], color_rgb[2], 230)
        start = particle_q[int(idx)]
        start_px = _project_point(case, demo_module, start)
        if start_px is None:
            continue
        radius_px = 2 if ratio < 0.4 else 3
        draw.ellipse(
            (start_px[0] - radius_px, start_px[1] - radius_px, start_px[0] + radius_px, start_px[1] + radius_px),
            fill=color,
        )
        if mag <= 1.0e-10:
            continue
        vec = np.asarray(vectors[int(idx)], dtype=np.float32)
        scaled = vec * min(1.0, max_arrow_world_len / max(force_cap, 1.0e-8))
        if mag > force_cap:
            scaled = (vec / mag * max_arrow_world_len).astype(np.float32, copy=False)
        end_px = _project_point(case, demo_module, start + scaled)
        if end_px is None:
            continue
        width_px = 2 if ratio < 0.55 else 3
        _draw_arrow(draw, start_px, end_px, color, width=width_px)

    title = _panel_title(case.case_name, force_mode)
    subtitle = "contact nodes only | blue -> red = force magnitude"
    stats_lines = [
        f"contact_nodes = {int(contact_indices.size)} | nonzero_force_nodes = {active_force_count}",
        f"force_median = {median_force:.3e} N | force_max = {max_force:.3e} N",
        f"first_contact_frame = {case.first_contact_frame if case.first_contact_frame is not None else 'NA'} | sim_frame = {int(snapshot['frame_index'])}",
    ]
    _overlay_text_block(
        image,
        title=title,
        subtitle=subtitle,
        stats_lines=stats_lines,
        cap_value=float(force_cap),
    )
    return np.asarray(image, dtype=np.uint8)


def _compose_board_frame(
    top_left: np.ndarray,
    top_right: np.ndarray,
    bottom_left: np.ndarray,
    bottom_right: np.ndarray,
) -> np.ndarray:
    tl = np.asarray(top_left, dtype=np.uint8)
    tr = np.asarray(top_right, dtype=np.uint8)
    bl = np.asarray(bottom_left, dtype=np.uint8)
    br = np.asarray(bottom_right, dtype=np.uint8)
    if tl.shape != tr.shape or tl.shape != bl.shape or tl.shape != br.shape:
        raise ValueError("All board panels must share the same shape")
    h, w, _ = tl.shape
    canvas = np.zeros((h * 2, w * 2, 3), dtype=np.uint8)
    canvas[0:h, 0:w] = tl
    canvas[0:h, w : 2 * w] = tr
    canvas[h : 2 * h, 0:w] = bl
    canvas[h : 2 * h, w : 2 * w] = br
    canvas[h - 2 : h + 2, :, :] = 224
    canvas[:, w - 2 : w + 2, :] = 224
    return canvas


def _write_video(frames: list[np.ndarray], out_path: Path, fps: float) -> Path:
    if not frames:
        raise RuntimeError("No frames available for collision board rendering.")
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
            raise RuntimeError("ffmpeg failed while encoding collision board video")
    finally:
        if proc.stdin and not proc.stdin.closed:
            proc.stdin.close()
    return out_path


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parents[1]
    demos_dir = repo_root / "Newton" / "phystwin_bridge" / "demos"
    sys.path.insert(0, str(demos_dir))
    import demo_cloth_bunny_drop_without_self_contact as demo  # noqa: PLC0415

    wp.init()

    box_case = _load_case_context(
        args.box_bundle.expanduser().resolve(),
        "box_control",
        demo,
        float(args.post_contact_seconds),
    )
    bunny_case = _load_case_context(
        args.bunny_bundle.expanduser().resolve(),
        "bunny_baseline",
        demo,
        float(args.post_contact_seconds),
    )

    if (box_case.width, box_case.height) != (bunny_case.width, bunny_case.height):
        raise ValueError("Box and bunny cases must use the same render resolution for 2x2 composition.")

    penalty_cap = max(
        _force_cap(box_case.snapshots, "penalty", float(args.force_percentile)),
        _force_cap(bunny_case.snapshots, "penalty", float(args.force_percentile)),
    )
    total_cap = max(
        _force_cap(box_case.snapshots, "total", float(args.force_percentile)),
        _force_cap(bunny_case.snapshots, "total", float(args.force_percentile)),
    )

    board_frames: list[np.ndarray] = []
    box_last_penalty: np.ndarray | None = None
    box_last_total: np.ndarray | None = None
    bunny_last_penalty: np.ndarray | None = None
    bunny_last_total: np.ndarray | None = None

    board_frame_count = max(len(box_case.snapshots), len(bunny_case.snapshots))
    fps = float(box_case.args.render_fps)
    preview_path = (
        args.first_frame_png.expanduser().resolve()
        if args.first_frame_png is not None
        else out_dir / "collision_force_board_2x2_first_frame.png"
    )

    for board_idx in range(board_frame_count):
        if board_idx < len(box_case.snapshots):
            box_snapshot = box_case.snapshots[board_idx]
            box_frame = box_case.frame_paths[box_case.selected_video_frame_indices[board_idx]]
            box_last_penalty = _overlay_case_panel(
                case=box_case,
                snapshot=box_snapshot,
                frame_path=box_frame,
                force_mode="penalty",
                force_cap=float(penalty_cap),
                max_arrow_world_len=float(args.max_arrow_world_len),
                demo_module=demo,
            )
            box_last_total = _overlay_case_panel(
                case=box_case,
                snapshot=box_snapshot,
                frame_path=box_frame,
                force_mode="total",
                force_cap=float(total_cap),
                max_arrow_world_len=float(args.max_arrow_world_len),
                demo_module=demo,
            )
        if board_idx < len(bunny_case.snapshots):
            bunny_snapshot = bunny_case.snapshots[board_idx]
            bunny_frame = bunny_case.frame_paths[bunny_case.selected_video_frame_indices[board_idx]]
            bunny_last_penalty = _overlay_case_panel(
                case=bunny_case,
                snapshot=bunny_snapshot,
                frame_path=bunny_frame,
                force_mode="penalty",
                force_cap=float(penalty_cap),
                max_arrow_world_len=float(args.max_arrow_world_len),
                demo_module=demo,
            )
            bunny_last_total = _overlay_case_panel(
                case=bunny_case,
                snapshot=bunny_snapshot,
                frame_path=bunny_frame,
                force_mode="total",
                force_cap=float(total_cap),
                max_arrow_world_len=float(args.max_arrow_world_len),
                demo_module=demo,
            )

        if box_last_penalty is None or box_last_total is None or bunny_last_penalty is None or bunny_last_total is None:
            raise RuntimeError("Board composition could not initialize all four panels.")
        board = _compose_board_frame(
            box_last_penalty,
            box_last_total,
            bunny_last_penalty,
            bunny_last_total,
        )
        board_frames.append(board)
        if board_idx == 0:
            Image.fromarray(board, mode="RGB").save(preview_path)
        if (board_idx + 1) % 10 == 0 or board_idx + 1 == board_frame_count:
            print(f"[collision_board] board frame {board_idx + 1}/{board_frame_count}", flush=True)

    out_video = out_dir / "collision_force_board_2x2.mp4"
    _write_video(board_frames, out_video, fps=fps)

    summary = {
        "board_video": str(out_video),
        "board_first_frame_png": str(preview_path),
        "render_fps": fps,
        "board_frame_count": int(board_frame_count),
        "panel_resolution": [int(box_case.width), int(box_case.height)],
        "board_resolution": [int(box_case.width * 2), int(box_case.height * 2)],
        "normalization_caps": {
            "penalty_force_cap_n": float(penalty_cap),
            "total_force_cap_n": float(total_cap),
            "percentile": float(args.force_percentile),
            "max_arrow_world_len_m": float(args.max_arrow_world_len),
        },
        "cases": {
            "box_control": {
                "bundle": str(box_case.bundle_path),
                "selected_video_frame_count": int(len(box_case.selected_video_frame_indices)),
                "selected_sim_frame_count": int(len(box_case.selected_sim_frame_indices)),
                "first_contact_frame": box_case.first_contact_frame,
                "clip_end_frame": int(box_case.clip_end_frame),
            },
            "bunny_baseline": {
                "bundle": str(bunny_case.bundle_path),
                "selected_video_frame_count": int(len(bunny_case.selected_video_frame_indices)),
                "selected_sim_frame_count": int(len(bunny_case.selected_sim_frame_indices)),
                "first_contact_frame": bunny_case.first_contact_frame,
                "clip_end_frame": int(bunny_case.clip_end_frame),
            },
        },
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[collision_board] video={out_video}", flush=True)
    print(f"[collision_board] summary={out_dir / 'summary.json'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
