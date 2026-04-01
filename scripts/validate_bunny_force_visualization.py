#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


@dataclass
class FrameSample:
    index: int
    timestamp_s: float
    mean_luma: float
    dark_pixel_ratio: float
    black_screen_flag: bool
    path: str
    pair_diff_to_previous: float | None = None


@dataclass
class VideoVerdict:
    path: str
    frame_count: int
    fps: float
    duration_s: float
    sampled_indices: list[int]
    black_screen_pass: bool
    motion_pass: bool
    temporal_density_pass: bool
    duration_pass: bool
    motion_scores: list[float]
    max_pair_diff: float
    mean_pair_diff: float
    median_pair_diff: float
    black_frame_fraction: float
    repeat_transition_fraction: float
    motion_density: float
    max_static_run: int
    max_static_run_fraction: float
    slideshow_like_flag: bool
    subject_visibility_pass: bool
    cloth_visibility_fraction: float
    rigid_visibility_fraction: float
    contact_readability_pass: bool
    force_sync_pass: bool
    exact_mapping_ratio_active_interval: float | None
    reused_mapping_ratio_active_interval: float | None
    mapping_path: str | None
    verdict: str
    samples: list[FrameSample]
    contact_sheet: str


@dataclass
class GeometryVisibilityContext:
    particle_q_object: np.ndarray
    render_indices: np.ndarray
    cam_pos: np.ndarray
    pitch_deg: float
    yaw_deg: float
    fov_deg: float
    frame_width: int
    frame_height: int
    point_stride: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate bunny force visualization clips with frame sampling and lightweight visual QA checks."
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        type=Path,
        help="Run directory to inspect. The script searches recursively for .mp4 files and writes qa/ outputs here.",
    )
    parser.add_argument(
        "--video",
        action="append",
        default=[],
        type=Path,
        help="Optional explicit video path. Repeatable. If omitted, .mp4 files are auto-discovered under --run-dir.",
    )
    parser.add_argument("--sample-count", type=int, default=12, help="Number of frames to sample per video.")
    parser.add_argument(
        "--black-mean-threshold",
        type=float,
        default=18.0,
        help="Mean grayscale luminance below which a sampled frame is considered black-screen-like.",
    )
    parser.add_argument(
        "--black-dark-ratio-threshold",
        type=float,
        default=0.97,
        help="Fraction of near-black pixels above which a sampled frame is considered black-screen-like.",
    )
    parser.add_argument(
        "--motion-threshold",
        type=float,
        default=0.75,
        help="Mean absolute grayscale frame-difference threshold used to reject static clips.",
    )
    parser.add_argument(
        "--repeat-frame-threshold",
        type=float,
        default=0.20,
        help="Mean absolute grayscale frame-difference threshold used to classify a transition as repeated/static.",
    )
    parser.add_argument(
        "--temporal-density-threshold",
        type=float,
        default=0.35,
        help="Minimum fraction of sampled transitions that must be meaningfully changing.",
    )
    parser.add_argument(
        "--max-static-run-fraction",
        type=float,
        default=0.50,
        help="Maximum fraction of sampled transitions that may belong to one static/repeated run.",
    )
    parser.add_argument(
        "--frame-dark-threshold",
        type=int,
        default=12,
        help="Pixel threshold used when computing dark-pixel ratio for a sampled frame.",
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=8,
        help="Maximum number of discovered videos to validate when no explicit --video list is provided.",
    )
    parser.add_argument(
        "--output-subdir",
        default="qa",
        help="Relative subdirectory inside --run-dir where outputs are written.",
    )
    parser.add_argument(
        "--min-phenomenon-duration",
        type=float,
        default=3.0,
        help="Minimum acceptable duration [s] for the global phenomenon video.",
    )
    parser.add_argument(
        "--min-force-duration",
        type=float,
        default=4.0,
        help="Minimum acceptable duration [s] for the force mechanism video.",
    )
    return parser.parse_args()


def _resolve_path(path: Path, base: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    if path.exists():
        return path.resolve()
    candidate = base / path
    return candidate.resolve()


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


def _fit_camera_to_points(
    points_world: np.ndarray,
    *,
    yaw_deg: float,
    pitch_deg: float,
    fov_deg: float,
    aspect: float,
    min_distance: float = 0.28,
    pad: float = 1.18,
) -> np.ndarray:
    points = np.asarray(points_world, dtype=np.float32).reshape(-1, 3)
    if points.size == 0:
        return np.asarray([-0.95, 0.85, 0.78], dtype=np.float32)
    bbox_min = np.min(points, axis=0)
    bbox_max = np.max(points, axis=0)
    center = (0.5 * (bbox_min + bbox_max)).astype(np.float32, copy=False)
    forward, right, up = _camera_basis_from_pitch_yaw(pitch_deg, yaw_deg)
    rel = points - center[None, :]
    x = np.abs(rel @ right)
    y = np.abs(rel @ up)
    z_off = rel @ forward
    tan_half_y = max(math.tan(math.radians(float(fov_deg)) * 0.5), 1.0e-6)
    tan_half_x = tan_half_y * max(float(aspect), 1.0e-6)
    req_x = float(np.max(x / tan_half_x - z_off)) if x.size else 0.0
    req_y = float(np.max(y / tan_half_y - z_off)) if y.size else 0.0
    distance = max(float(min_distance), float(pad) * max(req_x, req_y, 0.0))
    return (center - forward * distance).astype(np.float32, copy=False)


def _project_points_to_screen(
    points_world: np.ndarray,
    *,
    cam_pos: np.ndarray,
    pitch_deg: float,
    yaw_deg: float,
    fov_deg: float,
    width: int,
    height: int,
) -> tuple[np.ndarray, np.ndarray]:
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
    return px, py


def _load_geometry_visibility_context(
    video_path: Path,
    *,
    frame_width: int,
    frame_height: int,
    frame_count: int,
) -> GeometryVisibilityContext | None:
    stem = video_path.with_suffix("")
    scene_path = stem.with_name(f"{stem.name}_scene.npz")
    if not scene_path.exists():
        return None
    summary_path = stem.with_name(f"{stem.name}_summary.json")
    summary = {}
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception:
            summary = {}
    scene = np.load(scene_path, allow_pickle=True)
    if "particle_q_object" not in scene:
        return None
    particle_q_object = np.asarray(scene["particle_q_object"], dtype=np.float32)
    n_frames = int(particle_q_object.shape[0])
    render_end_frame = int(summary.get("render_end_frame", max(0, n_frames - 1)))
    render_end_frame = max(0, min(render_end_frame, n_frames - 1))
    render_indices = np.clip(
        np.round(np.linspace(0.0, float(render_end_frame), max(1, int(frame_count)))).astype(np.int32),
        0,
        render_end_frame,
    )
    sample_frames = np.unique(
        np.linspace(0, max(0, render_end_frame), num=min(max(6, render_end_frame + 1), 14)).astype(np.int32)
    )
    cloth_stride = max(1, int(particle_q_object.shape[1] // 320))
    scene_points = particle_q_object[sample_frames, ::cloth_stride].reshape(-1, 3).astype(np.float32, copy=False)
    cam_pos = _fit_camera_to_points(
        scene_points,
        yaw_deg=float(summary.get("camera_yaw_deg") or -40.0),
        pitch_deg=float(summary.get("camera_pitch_deg") or -10.0),
        fov_deg=float(summary.get("camera_fov_deg") or 55.0),
        aspect=float(frame_width) / max(float(frame_height), 1.0),
    )
    point_stride = max(1, int(particle_q_object.shape[1] // 800))
    return GeometryVisibilityContext(
        particle_q_object=particle_q_object,
        render_indices=render_indices,
        cam_pos=cam_pos,
        pitch_deg=float(summary.get("camera_pitch_deg") or -10.0),
        yaw_deg=float(summary.get("camera_yaw_deg") or -40.0),
        fov_deg=float(summary.get("camera_fov_deg") or 55.0),
        frame_width=int(frame_width),
        frame_height=int(frame_height),
        point_stride=int(point_stride),
    )


def _cloth_visible_from_geometry(ctx: GeometryVisibilityContext | None, sample_frame_index: int) -> bool | None:
    if ctx is None:
        return None
    if sample_frame_index < 0 or sample_frame_index >= int(ctx.render_indices.shape[0]):
        return None
    sim_idx = int(ctx.render_indices[sample_frame_index])
    pts = ctx.particle_q_object[sim_idx, :: ctx.point_stride].astype(np.float32, copy=False)
    px, py = _project_points_to_screen(
        pts,
        cam_pos=ctx.cam_pos,
        pitch_deg=ctx.pitch_deg,
        yaw_deg=ctx.yaw_deg,
        fov_deg=ctx.fov_deg,
        width=ctx.frame_width,
        height=ctx.frame_height,
    )
    valid = np.isfinite(px) & np.isfinite(py)
    if not np.any(valid):
        return False
    x = px[valid]
    y = py[valid]
    inside = (x >= 0.0) & (x < float(ctx.frame_width)) & (y >= 0.0) & (y < float(ctx.frame_height))
    if int(np.count_nonzero(inside)) < 16:
        return False
    x = x[inside]
    y = y[inside]
    w_frac = float((np.max(x) - np.min(x) + 1.0) / max(1.0, float(ctx.frame_width)))
    h_frac = float((np.max(y) - np.min(y) + 1.0) / max(1.0, float(ctx.frame_height)))
    area_frac = float(np.count_nonzero(inside) / max(1, pts.shape[0]))
    return bool(area_frac >= 0.10 and w_frac >= 0.08 and h_frac >= 0.03)


def _discover_videos(run_dir: Path, max_videos: int) -> list[Path]:
    candidates: list[Path] = []
    for path in sorted(run_dir.rglob("*.mp4")):
        if "qa" in path.parts:
            continue
        name = path.name.lower()
        if any(token in name for token in ("snapshot", "sheet", "contact_sheet", "thumb", "still")):
            continue
        candidates.append(path)
    return candidates[:max_videos]


def _video_slug(video_path: Path, run_dir: Path) -> str:
    try:
        rel = video_path.resolve().relative_to(run_dir.resolve())
        parts = list(rel.with_suffix("").parts)
    except Exception:
        parts = list(video_path.with_suffix("").parts)
    slug = "__".join(part for part in parts if part and part not in (".", ".."))
    return slug or video_path.stem


def _open_video(video_path: Path) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"failed to open video: {video_path}")
    return cap


def _frame_count_from_cap(cap: cv2.VideoCapture) -> int:
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    return count if count > 0 else 0


def _fps_from_cap(cap: cv2.VideoCapture) -> float:
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    return fps if fps > 0.0 else 30.0


def _read_all_frames(cap: cv2.VideoCapture) -> list[np.ndarray]:
    frames: list[np.ndarray] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    return frames


def _sample_indices(frame_count: int, sample_count: int) -> list[int]:
    if frame_count <= 1:
        return [0]
    count = min(sample_count, frame_count)
    raw = np.linspace(0, frame_count - 1, num=count)
    indices: list[int] = []
    seen: set[int] = set()
    for value in raw:
        idx = int(round(float(value)))
        idx = max(0, min(frame_count - 1, idx))
        if idx not in seen:
            seen.add(idx)
            indices.append(idx)
    if len(indices) < count:
        for idx in range(frame_count):
            if idx not in seen:
                seen.add(idx)
                indices.append(idx)
            if len(indices) >= count:
                break
    return indices


def _seek_and_read(cap: cv2.VideoCapture, frame_index: int) -> np.ndarray:
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ok, frame = cap.read()
    if not ok or frame is None:
        raise RuntimeError(f"failed to read frame {frame_index}")
    return frame


def _grayscale(frame_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)


def _downscale_gray(gray: np.ndarray, size: tuple[int, int] = (160, 90)) -> np.ndarray:
    return cv2.resize(gray, size, interpolation=cv2.INTER_AREA)


def _make_frame_sample(
    frame_bgr: np.ndarray,
    index: int,
    fps: float,
    frame_dark_threshold: int,
    black_mean_threshold: float,
    black_dark_ratio_threshold: float,
    out_path: Path,
) -> FrameSample:
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    Image.fromarray(rgb).save(out_path)
    gray = _grayscale(frame_bgr)
    mean_luma = float(gray.mean())
    dark_pixel_ratio = float((gray < frame_dark_threshold).mean())
    black_screen_flag = mean_luma < black_mean_threshold and dark_pixel_ratio > black_dark_ratio_threshold
    return FrameSample(
        index=index,
        timestamp_s=index / fps if fps > 0.0 else float(index),
        mean_luma=mean_luma,
        dark_pixel_ratio=dark_pixel_ratio,
        black_screen_flag=black_screen_flag,
        path=str(out_path),
    )


def _pairwise_motion_scores(samples: list[FrameSample], gray_frames: list[np.ndarray]) -> list[float]:
    scores: list[float] = []
    for i in range(1, len(gray_frames)):
        diff = np.abs(gray_frames[i].astype(np.float32) - gray_frames[i - 1].astype(np.float32))
        score = float(diff.mean())
        scores.append(score)
        samples[i].pair_diff_to_previous = score
    return scores


def _longest_run(mask: np.ndarray) -> int:
    best = 0
    current = 0
    for value in mask.tolist():
        if bool(value):
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def _transition_metrics(
    motion_scores: list[float],
    motion_threshold: float,
    repeat_frame_threshold: float,
    temporal_density_threshold: float,
    max_static_run_fraction: float,
) -> dict[str, object]:
    if not motion_scores:
        return {
            "motion_density": 0.0,
            "repeat_transition_fraction": 1.0,
            "max_static_run": 0,
            "max_static_run_fraction": 1.0,
            "temporal_density_pass": False,
            "slideshow_like_flag": True,
        }
    scores = np.asarray(motion_scores, dtype=np.float32)
    moving = scores >= motion_threshold
    repeated = scores <= repeat_frame_threshold
    static = ~moving
    max_static_run = _longest_run(static)
    motion_density = float(moving.mean())
    repeat_transition_fraction = float(repeated.mean())
    max_static_run_frac = float(max_static_run / max(1, len(scores)))
    temporal_density_pass = motion_density >= temporal_density_threshold and max_static_run_frac <= max_static_run_fraction
    slideshow_like_flag = not temporal_density_pass
    return {
        "motion_density": motion_density,
        "repeat_transition_fraction": repeat_transition_fraction,
        "max_static_run": max_static_run,
        "max_static_run_fraction": max_static_run_frac,
        "temporal_density_pass": temporal_density_pass,
        "slideshow_like_flag": slideshow_like_flag,
    }


def _largest_component_fraction(mask: np.ndarray) -> tuple[float, float, float]:
    mask_u8 = np.asarray(mask, dtype=np.uint8)
    if mask_u8.ndim != 2 or not np.any(mask_u8):
        return 0.0, 0.0, 0.0
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask_u8, connectivity=8)
    if count <= 1:
        return 0.0, 0.0, 0.0
    areas = stats[1:, cv2.CC_STAT_AREA]
    comp_idx = int(np.argmax(areas)) + 1
    x, y, w, h, area = stats[comp_idx]
    height, width = mask_u8.shape
    return float(area / max(1, height * width)), float(w / max(1, width)), float(h / max(1, height))


def _subject_visibility_metrics(frame_bgr: np.ndarray, *, is_force_video: bool) -> dict[str, float | bool]:
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    h, w = rgb.shape[:2]
    if is_force_video:
        global_rgb = rgb[:, : max(1, int(round(w * 0.68))), :]
        zoom_rgb = rgb[:, max(0, int(round(w * 0.62))) :, :]
    else:
        global_rgb = rgb
        zoom_rgb = None

    r = global_rgb[:, :, 0]
    g = global_rgb[:, :, 1]
    b = global_rgb[:, :, 2]
    cloth_mask = (r > 165) & (g > 145) & (b < 145)
    rigid_mask = ((b > 150) & (g > 145) & (r < 175)) | ((r > 150) & (g > 65) & (g < 180) & (b < 170))

    cloth_area_frac, cloth_w_frac, cloth_h_frac = _largest_component_fraction(cloth_mask)
    rigid_area_frac, rigid_w_frac, rigid_h_frac = _largest_component_fraction(rigid_mask)
    if is_force_video:
        cloth_visible = cloth_area_frac >= 0.004 and cloth_w_frac >= 0.16 and cloth_h_frac >= 0.08
    else:
        cloth_visible = cloth_area_frac >= 0.0015 and cloth_w_frac >= 0.08 and cloth_h_frac >= 0.03
    rigid_visible = rigid_area_frac >= 0.01 and rigid_w_frac >= 0.12 and rigid_h_frac >= 0.08

    contact_readability_pass = True
    if zoom_rgb is not None and zoom_rgb.size:
        zr = zoom_rgb[:, :, 0]
        zg = zoom_rgb[:, :, 1]
        zb = zoom_rgb[:, :, 2]
        white = int(np.count_nonzero((zr > 210) & (zg > 210) & (zb > 210)))
        gray = int(np.count_nonzero((zr > 120) & (zr < 210) & (np.abs(zr.astype(np.int16) - zg.astype(np.int16)) < 18) & (np.abs(zr.astype(np.int16) - zb.astype(np.int16)) < 18)))
        red = int(np.count_nonzero((zr > 170) & (zg < 120) & (zb < 120)))
        purple = int(np.count_nonzero((zr > 110) & (zb > 140) & (zg < 150)))
        green = int(np.count_nonzero((zg > 150) & (zr < 140) & (zb < 140)))
        contact_readability_pass = (
            white >= 24
            and red >= 24
            and purple >= 24
            and green >= 24
            and gray >= 8
        )

    return {
        "cloth_visible": bool(cloth_visible),
        "rigid_visible": bool(rigid_visible),
        "cloth_area_fraction": float(cloth_area_frac),
        "rigid_area_fraction": float(rigid_area_frac),
        "contact_readability_pass": bool(contact_readability_pass),
    }


def _build_contact_sheet(
    video_path: Path,
    samples: list[FrameSample],
    qa_dir: Path,
    video_verdict: VideoVerdict,
    sheet_slug: str,
    columns: int = 3,
) -> Path:
    sheet_dir = qa_dir / "contact_sheets"
    sheet_dir.mkdir(parents=True, exist_ok=True)
    sheet_path = sheet_dir / f"{sheet_slug}_contact_sheet.png"

    tile_w = 320
    frame_h = 180
    caption_h = 72
    pad = 16
    header_h = 140
    rows = max(1, math.ceil(len(samples) / columns))
    width = columns * tile_w + (columns + 1) * pad
    height = header_h + rows * (frame_h + caption_h + pad) + pad

    canvas = Image.new("RGB", (width, height), (20, 20, 20))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    title_lines = [
        f"Bunny force visualization QA: {video_path.name}",
        "verdict={verdict}  black={black}  motion={motion}  temporal={temporal}".format(
            verdict=video_verdict.verdict,
            black=video_verdict.black_screen_pass,
            motion=video_verdict.motion_pass,
            temporal=video_verdict.temporal_density_pass,
        ),
        f"frames={video_verdict.frame_count}  fps={video_verdict.fps:.2f}  duration={video_verdict.duration_s:.2f}s",
        "black_frame_fraction={black:.2f}  motion_density={density:.2f}  repeat_fraction={repeat:.2f}  max_static_run={run}".format(
            black=video_verdict.black_frame_fraction,
            density=video_verdict.motion_density,
            repeat=video_verdict.repeat_transition_fraction,
            run=video_verdict.max_static_run,
        ),
        f"max_pair_diff={video_verdict.max_pair_diff:.2f}  mean_pair_diff={video_verdict.mean_pair_diff:.2f}  median_pair_diff={video_verdict.median_pair_diff:.2f}",
    ]
    y = pad
    for line in title_lines:
        draw.text((pad, y), line, fill=(245, 245, 245), font=font)
        y += 22

    for idx, sample in enumerate(samples):
        row = idx // columns
        col = idx % columns
        x = pad + col * (tile_w + pad)
        y0 = header_h + row * (frame_h + caption_h + pad)
        with Image.open(sample.path) as frame:
            tile = Image.new("RGB", (tile_w, frame_h + caption_h), (34, 34, 34))
            fitted = ImageOps.contain(frame.convert("RGB"), (tile_w, frame_h))
            fx = (tile_w - fitted.width) // 2
            fy = (frame_h - fitted.height) // 2
            tile.paste(fitted, (fx, fy))
            tdraw = ImageDraw.Draw(tile)
            border_color = (205, 75, 75) if sample.black_screen_flag else (110, 190, 120)
            tdraw.rectangle([0, 0, tile_w - 1, frame_h - 1], outline=border_color, width=3)
            caption_lines = [
                f"#{idx + 1} idx={sample.index} t={sample.timestamp_s:.2f}s",
                f"mean={sample.mean_luma:.1f} dark={sample.dark_pixel_ratio:.2f} diff_prev="
                + ("n/a" if sample.pair_diff_to_previous is None else f"{sample.pair_diff_to_previous:.2f}"),
            ]
            cap_y = frame_h + 6
            for line in caption_lines:
                tdraw.text((8, cap_y), line, fill=(240, 240, 240), font=font)
                cap_y += 16
            canvas.paste(tile, (x, y0))

    canvas.save(sheet_path)
    return sheet_path


def _render_verdict_markdown(run_dir: Path, report: dict[str, object]) -> str:
    lines = [
        "# Bunny Force Visualization QA Verdict",
        "",
        f"- Run directory: `{run_dir}`",
        f"- Generated at: `{report['generated_at']}`",
        f"- Overall verdict: **{report['overall_verdict']}**",
        f"- Sample count: `{report['sample_count']}`",
        f"- Black mean threshold: `{report['black_mean_threshold']}`",
        f"- Dark pixel threshold: `{report['black_dark_ratio_threshold']}`",
        f"- Motion threshold: `{report['motion_threshold']}`",
        "",
        "## Checks",
    ]
    for video in report["videos"]:
        lines.extend(
            [
                f"### `{video['path']}`",
                f"- Verdict: **{video['verdict']}**",
                f"- Black-screen pass: `{video['black_screen_pass']}`",
                f"- Motion pass: `{video['motion_pass']}`",
                f"- Duration pass: `{video['duration_pass']}`",
                f"- Duration: `{video['duration_s']:.2f}s`",
                f"- Temporal-density pass: `{video['temporal_density_pass']}`",
                f"- Black frame fraction: `{video['black_frame_fraction']:.2f}`",
                f"- Motion density: `{video['motion_density']:.2f}`",
                f"- Repeat transition fraction: `{video['repeat_transition_fraction']:.2f}`",
                f"- Max static run: `{video['max_static_run']}`",
                f"- Max static run fraction: `{video['max_static_run_fraction']:.2f}`",
                f"- Max pair diff: `{video['max_pair_diff']:.2f}`",
                f"- Mean pair diff: `{video['mean_pair_diff']:.2f}`",
                f"- Median pair diff: `{video['median_pair_diff']:.2f}`",
                f"- Slideshow-like flag: `{video['slideshow_like_flag']}`",
                f"- Subject visibility pass: `{video['subject_visibility_pass']}`",
                f"- Cloth visibility fraction: `{video['cloth_visibility_fraction']:.3f}`",
                f"- Rigid visibility fraction: `{video['rigid_visibility_fraction']:.3f}`",
                f"- Contact readability pass: `{video['contact_readability_pass']}`",
                f"- Force synchronization pass: `{video['force_sync_pass']}`",
                f"- exact_mapping_ratio_active_interval: `{video['exact_mapping_ratio_active_interval']}`",
                f"- reused_mapping_ratio_active_interval: `{video['reused_mapping_ratio_active_interval']}`",
                f"- Mapping report: `{video['mapping_path']}`",
                f"- Contact sheet: `{video['contact_sheet']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Manual Review Template",
            "",
            "- Frame sampling looks representative:",
            "- Black-screen check is acceptable:",
            "- Motion / non-static check is acceptable:",
            "- Temporal-density / repeated-frame check is acceptable:",
            "- Global cloth and rigid visibility are acceptable:",
            "- Contact patch readability is acceptable:",
            "- Contact sheet is readable:",
            "- Final reviewer verdict:",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.expanduser().resolve()
    qa_dir = run_dir / args.output_subdir
    qa_dir.mkdir(parents=True, exist_ok=True)
    for relative in ("contact_sheets", "sampled_frames"):
        target = qa_dir / relative
        if target.exists():
            shutil.rmtree(target)
    for filename in ("report.json", "verdict.md"):
        target = qa_dir / filename
        if target.exists():
            target.unlink()

    explicit_videos = [_resolve_path(video, run_dir) for video in args.video]
    videos = explicit_videos or _discover_videos(run_dir, args.max_videos)
    if not videos:
        print(f"[validate_bunny_force_visualization] no .mp4 videos found under {run_dir}")
        return 2

    report_videos: list[dict[str, object]] = []
    for video_path in videos:
        if not video_path.exists():
            print(f"[validate_bunny_force_visualization] missing video: {video_path}")
            return 2

        cap = _open_video(video_path)
        try:
            frame_count = _frame_count_from_cap(cap)
            fps = _fps_from_cap(cap)
            if frame_count > 0:
                indices = _sample_indices(frame_count, args.sample_count)
                sampled_frames = [_seek_and_read(cap, idx) for idx in indices]
            else:
                sampled_frames = _read_all_frames(cap)
                frame_count = len(sampled_frames)
                indices = _sample_indices(frame_count, args.sample_count)
                sampled_frames = [sampled_frames[idx] for idx in indices]
        finally:
            cap.release()

        gray_frames = [_downscale_gray(_grayscale(frame)) for frame in sampled_frames]
        video_slug = _video_slug(video_path, run_dir)
        sample_dir = qa_dir / "sampled_frames" / video_slug
        sample_dir.mkdir(parents=True, exist_ok=True)

        samples: list[FrameSample] = []
        for order, (index, frame) in enumerate(zip(indices, sampled_frames, strict=False)):
            sample_path = sample_dir / f"frame_{order:02d}_idx{index:06d}.png"
            samples.append(
                _make_frame_sample(
                    frame,
                    index=index,
                    fps=fps,
                    frame_dark_threshold=args.frame_dark_threshold,
                    black_mean_threshold=args.black_mean_threshold,
                    black_dark_ratio_threshold=args.black_dark_ratio_threshold,
                    out_path=sample_path,
                )
            )

        is_force_video = "force_diag" in video_path.name.lower() or "force" in video_path.name.lower()
        geometry_visibility_ctx = None if is_force_video else _load_geometry_visibility_context(
            video_path,
            frame_width=int(sampled_frames[0].shape[1]),
            frame_height=int(sampled_frames[0].shape[0]),
            frame_count=frame_count,
        )
        motion_threshold = float(args.motion_threshold if not is_force_video else 0.30)
        temporal_density_threshold = float(args.temporal_density_threshold if not is_force_video else 0.54)
        if not is_force_video:
            temporal_density_threshold = min(temporal_density_threshold, 0.15)
        max_static_run_fraction = float(args.max_static_run_fraction if is_force_video else max(args.max_static_run_fraction, 0.85))
        motion_scores = _pairwise_motion_scores(samples, gray_frames)
        temporal_metrics = _transition_metrics(
            motion_scores,
            motion_threshold=motion_threshold,
            repeat_frame_threshold=args.repeat_frame_threshold,
            temporal_density_threshold=temporal_density_threshold,
            max_static_run_fraction=max_static_run_fraction,
        )
        visibility_records: list[dict[str, float | bool]] = []
        for sample, frame in zip(samples, sampled_frames, strict=False):
            metrics = _subject_visibility_metrics(frame, is_force_video=is_force_video)
            if not is_force_video:
                cloth_visible_geom = _cloth_visible_from_geometry(geometry_visibility_ctx, sample.index)
                if cloth_visible_geom is not None:
                    metrics["cloth_visible"] = bool(cloth_visible_geom)
            visibility_records.append(metrics)
        cloth_visibility_fraction = float(np.mean([1.0 if item["cloth_visible"] else 0.0 for item in visibility_records]))
        rigid_visibility_fraction = float(np.mean([1.0 if item["rigid_visible"] else 0.0 for item in visibility_records]))
        contact_readability_pass = True if not is_force_video else bool(
            np.mean([1.0 if item["contact_readability_pass"] else 0.0 for item in visibility_records]) >= 0.50
        )
        force_sync_pass = True
        exact_mapping_ratio_active_interval = None
        reused_mapping_ratio_active_interval = None
        mapping_path = None
        if is_force_video:
            candidate = video_path.with_name(f"{video_path.stem}_mapping.json")
            mapping_path = str(candidate) if candidate.exists() else None
            if candidate.exists():
                try:
                    mapping_payload = json.loads(candidate.read_text(encoding="utf-8"))
                    exact_mapping_ratio_active_interval = float(
                        mapping_payload.get("exact_mapping_ratio_active_interval", 0.0)
                    )
                    reused_mapping_ratio_active_interval = float(
                        mapping_payload.get("reused_mapping_ratio_active_interval", 1.0)
                    )
                    force_sync_pass = exact_mapping_ratio_active_interval >= 0.95
                except Exception:
                    force_sync_pass = False
            else:
                force_sync_pass = False
        if is_force_video:
            subject_visibility_pass = cloth_visibility_fraction >= 0.90 and rigid_visibility_fraction >= 0.90
        else:
            subject_visibility_pass = cloth_visibility_fraction >= 0.15 and rigid_visibility_fraction >= 0.90
        black_frame_fraction = sum(1 for sample in samples if sample.black_screen_flag) / max(1, len(samples))
        black_screen_pass = black_frame_fraction < 0.5
        motion_pass = bool(motion_scores) and max(motion_scores) >= motion_threshold
        temporal_density_pass = bool(temporal_metrics["temporal_density_pass"])
        duration_s = (frame_count / fps) if fps > 0.0 else 0.0
        min_duration = float(args.min_force_duration if is_force_video else args.min_phenomenon_duration)
        duration_pass = duration_s >= min_duration
        verdict = "PASS" if (
            black_screen_pass
            and motion_pass
            and duration_pass
            and temporal_density_pass
            and subject_visibility_pass
            and contact_readability_pass
            and force_sync_pass
        ) else "FAIL"
        video_verdict = VideoVerdict(
            path=str(video_path),
            frame_count=frame_count,
            fps=fps,
            duration_s=duration_s,
            sampled_indices=indices,
            black_screen_pass=black_screen_pass,
            motion_pass=motion_pass,
            temporal_density_pass=temporal_density_pass,
            duration_pass=duration_pass,
            motion_scores=motion_scores,
            max_pair_diff=max(motion_scores) if motion_scores else 0.0,
            mean_pair_diff=float(np.mean(motion_scores)) if motion_scores else 0.0,
            median_pair_diff=float(np.median(motion_scores)) if motion_scores else 0.0,
            black_frame_fraction=black_frame_fraction,
            repeat_transition_fraction=float(temporal_metrics["repeat_transition_fraction"]),
            motion_density=float(temporal_metrics["motion_density"]),
            max_static_run=int(temporal_metrics["max_static_run"]),
            max_static_run_fraction=float(temporal_metrics["max_static_run_fraction"]),
            slideshow_like_flag=bool(temporal_metrics["slideshow_like_flag"]),
            subject_visibility_pass=bool(subject_visibility_pass),
            cloth_visibility_fraction=cloth_visibility_fraction,
            rigid_visibility_fraction=rigid_visibility_fraction,
            contact_readability_pass=bool(contact_readability_pass),
            force_sync_pass=bool(force_sync_pass),
            exact_mapping_ratio_active_interval=exact_mapping_ratio_active_interval,
            reused_mapping_ratio_active_interval=reused_mapping_ratio_active_interval,
            mapping_path=mapping_path,
            verdict=verdict,
            samples=samples,
            contact_sheet="",
        )
        contact_sheet = _build_contact_sheet(video_path, samples, qa_dir, video_verdict, video_slug)
        video_verdict.contact_sheet = str(contact_sheet)
        report_videos.append(asdict(video_verdict))

    overall_verdict = "PASS" if all(video["verdict"] == "PASS" for video in report_videos) else "FAIL"
    report: dict[str, object] = {
        "run_dir": str(run_dir),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_count": args.sample_count,
        "black_mean_threshold": args.black_mean_threshold,
        "black_dark_ratio_threshold": args.black_dark_ratio_threshold,
        "motion_threshold": args.motion_threshold,
        "repeat_frame_threshold": args.repeat_frame_threshold,
        "temporal_density_threshold": args.temporal_density_threshold,
        "max_static_run_fraction": args.max_static_run_fraction,
        "overall_verdict": overall_verdict,
        "videos": report_videos,
    }

    serialized = json.dumps(report, indent=2)
    (qa_dir / "report.json").write_text(serialized, encoding="utf-8")
    (qa_dir / "metrics.json").write_text(serialized, encoding="utf-8")
    (qa_dir / "verdict.md").write_text(_render_verdict_markdown(run_dir, report), encoding="utf-8")

    print(f"[validate_bunny_force_visualization] run_dir={run_dir}")
    print(f"[validate_bunny_force_visualization] qa_dir={qa_dir}")
    print(f"[validate_bunny_force_visualization] overall_verdict={overall_verdict}")
    for video in report_videos:
        print(
            "  - {path}: {verdict} (black={black}, motion={motion}, duration={duration}, temporal={temporal}, force_sync={force_sync}, contact_sheet={sheet})".format(
                path=video["path"],
                verdict=video["verdict"],
                black=video["black_screen_pass"],
                motion=video["motion_pass"],
                duration=video["duration_pass"],
                temporal=video["temporal_density_pass"],
                force_sync=video["force_sync_pass"],
                sheet=video["contact_sheet"],
            )
        )

    return 0 if overall_verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
