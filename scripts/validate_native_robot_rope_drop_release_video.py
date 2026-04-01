#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


@dataclass
class VideoReport:
    video_path: str
    ffprobe_path: str
    resolution_width: int
    resolution_height: int
    encoded_fps: float
    duration_s: float
    nb_frames: int
    decoded_frame_count: int
    mean_luma: list[float]
    dark_pixel_ratio: list[float]
    black_frame_fraction: float
    near_exact_repeat_fraction: float
    max_static_run: int
    mean_pair_diff: float
    median_pair_diff: float
    min_pair_diff: float
    max_pair_diff: float
    total_edge_ratio: float
    robot_visibility_score: float
    ground_visibility_score: float
    release_motion_score: float | None
    impact_motion_score: float | None
    free_fall_motion_score: float | None
    pre_release_com_speed_m_s: float | None
    post_release_com_speed_m_s: float | None
    post_release_horizontal_speed_m_s: float | None
    post_release_vertical_speed_m_s: float | None
    post_release_horizontal_to_vertical_ratio: float | None
    post_release_horizontal_jump_ratio: float | None
    release_region_visible_score: float | None
    release_dynamics_gate_pass: bool
    hidden_release_region_detected: bool
    release_before_settle_detected: bool
    spring_snap_first_detected: bool
    encoding_gate_pass: bool
    decode_gate_pass: bool
    black_screen_gate_pass: bool
    smoothness_gate_pass: bool
    readability_gate_pass: bool
    overall_gate_pass: bool


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validate the native Franka rope drop/release sanity baseline videos."
    )
    p.add_argument("run_dir", type=Path, help="Canonical run directory to validate.")
    p.add_argument("--presentation-video", type=Path, default=None)
    p.add_argument("--debug-video", type=Path, default=None)
    p.add_argument("--summary-json", type=Path, default=None)
    p.add_argument("--physics-validation-json", type=Path, default=None)
    p.add_argument("--output-dir", type=Path, default=None)
    p.add_argument("--sample-count", type=int, default=12)
    p.add_argument("--black-mean-threshold", type=float, default=18.0)
    p.add_argument("--black-dark-ratio-threshold", type=float, default=0.97)
    p.add_argument("--frame-dark-threshold", type=int, default=12)
    p.add_argument("--near-exact-repeat-threshold", type=float, default=0.05)
    p.add_argument("--near-exact-repeat-fraction-threshold", type=float, default=0.90)
    p.add_argument("--near-exact-max-run-threshold", type=int, default=20)
    p.add_argument("--min-total-edge-ratio", type=float, default=0.010)
    p.add_argument("--min-robot-band-fraction", type=float, default=0.32)
    p.add_argument("--min-ground-band-fraction", type=float, default=0.12)
    p.add_argument("--motion-window-frames", type=int, default=2)
    p.add_argument("--min-release-motion", type=float, default=0.05)
    p.add_argument("--min-impact-motion", type=float, default=0.04)
    p.add_argument("--min-freefall-motion", type=float, default=0.10)
    p.add_argument("--min-freefall-frames", type=int, default=4)
    p.add_argument("--max-pre-release-com-speed", type=float, default=0.18)
    p.add_argument("--max-pre-release-horizontal-speed", type=float, default=0.12)
    p.add_argument("--max-post-release-com-speed", type=float, default=1.80)
    p.add_argument("--max-post-release-horizontal-speed", type=float, default=0.75)
    p.add_argument("--max-post-release-horizontal-to-vertical-ratio", type=float, default=0.75)
    p.add_argument("--max-post-release-horizontal-jump-ratio", type=float, default=2.50)
    p.add_argument("--max-release-to-settle-gap-frames", type=int, default=0)
    p.add_argument("--ground-penetration-tol-mm", type=float, default=1.5)
    return p.parse_args()


def _resolve_path(root: Path, path: Path | None) -> Path | None:
    if path is None:
        return None
    raw = path.expanduser()
    if raw.is_absolute():
        return raw.resolve()
    return (root / raw).resolve()


def _discover_first(root: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        matches = sorted(root.glob(pattern))
        if matches:
            return matches[0].resolve()
    return None


def _load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _ffprobe(video_path: Path) -> dict[str, Any]:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_streams",
        "-show_format",
        str(video_path),
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(proc.stdout)


def _decode_check(video_path: Path, out_path: Path) -> bool:
    cmd = ["ffmpeg", "-v", "error", "-i", str(video_path), "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(proc.stderr, encoding="utf-8")
    return proc.returncode == 0 and not proc.stderr.strip()


def _video_stream(ffprobe_payload: dict[str, Any]) -> dict[str, Any]:
    for stream in ffprobe_payload.get("streams", []):
        if str(stream.get("codec_type")) == "video":
            return stream
    return {}


def _fps_from_stream(stream: dict[str, Any]) -> float:
    value = str(stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/1")
    if "/" in value:
        num, den = value.split("/", 1)
        try:
            num_f = float(num)
            den_f = float(den)
            return num_f / den_f if den_f != 0.0 else 0.0
        except Exception:
            return 0.0
    try:
        return float(value)
    except Exception:
        return 0.0


def _duration_from_payload(ffprobe_payload: dict[str, Any]) -> float:
    try:
        return float(ffprobe_payload.get("format", {}).get("duration", 0.0) or 0.0)
    except Exception:
        return 0.0


def _open_video(video_path: Path) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"failed to open video: {video_path}")
    return cap


def _sample_indices(frame_count: int, sample_count: int) -> list[int]:
    if frame_count <= 1:
        return [0]
    raw = np.linspace(0, frame_count - 1, num=min(sample_count, frame_count))
    out: list[int] = []
    seen: set[int] = set()
    for value in raw:
        idx = max(0, min(frame_count - 1, int(round(float(value)))))
        if idx not in seen:
            seen.add(idx)
            out.append(idx)
    return out


def _read_frame(cap: cv2.VideoCapture, idx: int) -> np.ndarray:
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, frame = cap.read()
    if not ok or frame is None:
        raise RuntimeError(f"failed to read frame {idx}")
    return frame


def _gray(frame_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)


def _edge_profile(gray: np.ndarray) -> dict[str, float]:
    edges = cv2.Canny(gray, 60, 160)
    total = float((edges > 0).mean())
    h = edges.shape[0]
    upper_end = max(1, int(round(0.72 * h)))
    lower_start = min(h - 1, int(round(0.72 * h)))
    upper_mid = float((edges[:upper_end] > 0).mean()) if upper_end > 0 else 0.0
    lower = float((edges[lower_start:] > 0).mean()) if lower_start < h else 0.0
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    return {
        "total_edge_ratio": total,
        "upper_mid_edge_ratio": upper_mid,
        "lower_edge_ratio": lower,
        "laplacian_var": lap_var,
    }


def _motion_score(gray_a: np.ndarray, gray_b: np.ndarray) -> float:
    diff = np.abs(gray_a.astype(np.float32) - gray_b.astype(np.float32))
    return float(diff.mean())


def _local_motion_score(grays: list[np.ndarray], idx: int, radius: int) -> float | None:
    if not grays:
        return None
    start = max(0, int(idx) - int(radius))
    end = min(len(grays) - 1, int(idx) + int(radius))
    if end <= start:
        return None
    diffs = [_motion_score(grays[i], grays[i + 1]) for i in range(start, end)]
    return float(np.mean(diffs)) if diffs else None


def _make_sheet(
    frames_rgb: list[np.ndarray],
    labels: list[str],
    out_path: Path,
    *,
    cols: int = 4,
) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pil_frames = [Image.fromarray(f) for f in frames_rgb]
    w = max(img.width for img in pil_frames)
    h = max(img.height for img in pil_frames)
    rows = math.ceil(len(pil_frames) / cols)
    title_h = 28
    canvas = Image.new("RGB", (cols * w, rows * (h + title_h)), color=(242, 244, 247))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    for i, (img, label) in enumerate(zip(pil_frames, labels)):
        r = i // cols
        c = i % cols
        x = c * w
        y = r * (h + title_h)
        draw.rectangle((x, y, x + w, y + title_h), fill=(228, 232, 238))
        draw.text((x + 8, y + 4), label, fill=(25, 29, 38), font=font)
        canvas.paste(img, (x, y + title_h))
    canvas.save(out_path)
    return out_path


def _map_summary_frame_to_video_frame(
    summary_frame: int | None,
    *,
    summary_frames: int,
    video_frames: int,
) -> int | None:
    if summary_frame is None:
        return None
    if summary_frames <= 1 or video_frames <= 1:
        return max(0, min(video_frames - 1, int(summary_frame)))
    ratio = float(summary_frame) / float(max(summary_frames - 1, 1))
    mapped = int(round(ratio * float(video_frames - 1)))
    return max(0, min(video_frames - 1, mapped))


def _first_int(*payloads: dict[str, Any], keys: list[str]) -> int | None:
    for payload in payloads:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, (int, np.integer)) and not isinstance(value, bool):
                return int(value)
            if isinstance(value, float) and math.isfinite(value):
                return int(round(value))
    return None


def _first_float(*payloads: dict[str, Any], keys: list[str]) -> float | None:
    for payload in payloads:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool):
                value_f = float(value)
                if math.isfinite(value_f):
                    return value_f
    return None


def _first_series(*payloads: dict[str, Any], keys: list[str]) -> list[float] | None:
    for payload in payloads:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, list) and value:
                try:
                    arr = [float(v) for v in value]
                except Exception:
                    continue
                return arr
            if isinstance(value, tuple) and value:
                try:
                    arr = [float(v) for v in value]
                except Exception:
                    continue
                return arr
    return None


def _primary_payload(payload: dict[str, Any]) -> dict[str, Any]:
    primary = payload.get("primary")
    return primary if isinstance(primary, dict) else payload


def _resolve_series_path(run_dir: Path, summary: dict[str, Any], *, key: str) -> Path | None:
    hist_info = summary.get("history_storage_files")
    if isinstance(hist_info, dict):
        candidate = hist_info.get(key)
        if candidate:
            path = Path(str(candidate)).expanduser()
            if not path.is_absolute():
                path = (run_dir / path).resolve()
            if path.exists():
                return path
    return _discover_first(
        run_dir,
        [
            f"{key}.npy",
            f"work/*{key}.npy",
            f"sim/history/*{key}.npy",
            f"**/*{key}.npy",
        ],
    )


def _load_series(path: Path) -> np.ndarray:
    arr = np.load(path, mmap_mode="r")
    return np.asarray(arr)


def _series_com_and_min_z(particle_q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    q = np.asarray(particle_q, dtype=np.float32)
    finite = np.isfinite(q)
    counts = finite.sum(axis=1).astype(np.float32)
    sums = np.where(finite, q, 0.0).sum(axis=1)
    com = np.divide(
        sums,
        counts,
        out=np.full((q.shape[0], 3), np.nan, dtype=np.float32),
        where=counts > 0.0,
    )
    z = q[..., 2]
    z_finite = np.isfinite(z)
    min_z = np.where(z_finite, z, np.inf).min(axis=1).astype(np.float32, copy=False)
    return com.astype(np.float32, copy=False), min_z


def _frame_dt_from_payload(summary: dict[str, Any], physics: dict[str, Any]) -> float | None:
    for payload in (physics, summary):
        value = _first_float(payload, keys=["frame_dt_s", "frame_dt"])
        if value is not None and value > 0.0:
            return float(value)
        sim_dt = _first_float(payload, keys=["sim_dt"])
        substeps = payload.get("substeps")
        if sim_dt is not None and isinstance(substeps, (int, float, np.integer, np.floating)) and int(substeps) > 0:
            return float(sim_dt) * int(substeps)
    return None


def _window_mean_speed(series_xyz: np.ndarray, start: int, end: int, frame_dt: float) -> tuple[float | None, float | None]:
    if end <= start or end - start < 1 or frame_dt <= 0.0:
        return None, None
    window = np.asarray(series_xyz[start : end + 1], dtype=np.float32)
    if window.shape[0] < 2:
        return None, None
    vel = np.diff(window, axis=0) / float(frame_dt)
    speed = np.linalg.norm(vel, axis=1)
    horiz = np.linalg.norm(vel[:, :2], axis=1)
    vert = np.abs(vel[:, 2])
    return float(np.mean(speed)), float(np.mean(horiz)), float(np.mean(vert))


def _assess_release_dynamics(
    run_dir: Path,
    summary: dict[str, Any],
    physics: dict[str, Any],
    *,
    presentation_report: VideoReport,
    max_pre_release_com_speed: float,
    max_pre_release_horizontal_speed: float,
    max_post_release_com_speed: float,
    max_post_release_horizontal_speed: float,
    max_post_release_horizontal_to_vertical_ratio: float,
    max_post_release_horizontal_jump_ratio: float,
    max_release_to_settle_gap_frames: int,
) -> dict[str, Any]:
    primary = _primary_payload(physics)
    frame_dt = _frame_dt_from_payload(summary, primary)
    release_frame = _first_int(summary, primary, keys=["release_frame", "release_frame_idx", "release_frame_index"])
    settle_frame = _first_int(summary, primary, keys=["settle_frame", "settled_frame", "support_settled_frame", "settle_release_frame"])

    release_video_motion = presentation_report.release_motion_score
    release_region_visible_score = None if release_video_motion is None else float(release_video_motion)

    com_xyz = None
    min_rope_z_series = None
    series_source = None
    series_payload = primary.get("series") if isinstance(primary.get("series"), dict) else {}
    if isinstance(series_payload, dict):
        rope_com_xyz = series_payload.get("rope_com_xyz_m")
        rope_min_z = series_payload.get("rope_min_z_m")
        if isinstance(rope_com_xyz, list) and rope_com_xyz and isinstance(rope_com_xyz[0], list) and len(rope_com_xyz[0]) == 3:
            com_xyz = np.asarray(rope_com_xyz, dtype=np.float32)
            series_source = "physics.series.rope_com_xyz_m"
        if isinstance(rope_min_z, list) and rope_min_z:
            min_rope_z_series = np.asarray(rope_min_z, dtype=np.float32)
            series_source = series_source or "physics.series.rope_min_z_m"

    if com_xyz is None or min_rope_z_series is None:
        hist_path = _resolve_series_path(run_dir, summary, key="particle_q_object")
        if hist_path is None:
            hist_path = _resolve_series_path(run_dir, summary, key="particle_q_all")
        if hist_path is not None and hist_path.exists():
            particle_q = _load_series(hist_path)
            if particle_q.ndim == 3 and particle_q.shape[-1] == 3:
                com_xyz, min_rope_z_series = _series_com_and_min_z(particle_q)
                series_source = str(hist_path)

    pre_release_com_speed = None
    pre_release_horizontal_speed = None
    post_release_com_speed = None
    post_release_horizontal_speed = None
    post_release_vertical_speed = None
    post_release_horizontal_to_vertical_ratio = None
    post_release_horizontal_jump_ratio = None
    hidden_release_region_detected = False
    release_before_settle_detected = False
    spring_snap_first_detected = False
    release_dynamics_gate_pass = True
    summary_release_time = _first_float(summary, primary, keys=["release_time_s", "release_time"])
    if release_frame is None and summary_release_time is not None and frame_dt is not None and frame_dt > 0.0:
        release_frame = int(round(summary_release_time / frame_dt))

    if com_xyz is not None and frame_dt is not None and release_frame is not None and 0 <= release_frame < com_xyz.shape[0]:
        pre_start = max(0, release_frame - 4)
        pre_end = max(pre_start + 1, release_frame - 1)
        post_start = min(com_xyz.shape[0] - 2, release_frame + 1)
        post_end = min(com_xyz.shape[0] - 1, release_frame + 4)

        pre_stats = _window_mean_speed(com_xyz, pre_start, pre_end, frame_dt)
        post_stats = _window_mean_speed(com_xyz, post_start, post_end, frame_dt)
        if pre_stats[0] is not None:
            pre_release_com_speed = float(pre_stats[0])
            pre_release_horizontal_speed = float(pre_stats[1]) if pre_stats[1] is not None else None
        if post_stats[0] is not None:
            post_release_com_speed = float(post_stats[0])
            post_release_horizontal_speed = float(post_stats[1]) if post_stats[1] is not None else None
            post_release_vertical_speed = float(post_stats[2]) if post_stats[2] is not None else None

        if post_release_horizontal_speed is not None and post_release_vertical_speed is not None:
            post_release_horizontal_to_vertical_ratio = float(
                post_release_horizontal_speed / max(post_release_vertical_speed, 1.0e-6)
            )
        if pre_release_horizontal_speed is not None and post_release_horizontal_speed is not None:
            post_release_horizontal_jump_ratio = float(
                post_release_horizontal_speed / max(pre_release_horizontal_speed, 1.0e-6)
            )

        if settle_frame is not None and release_frame < settle_frame - max(0, int(max_release_to_settle_gap_frames)):
            release_before_settle_detected = True
        if pre_release_com_speed is not None and pre_release_com_speed > float(max_pre_release_com_speed):
            release_before_settle_detected = True
        if pre_release_horizontal_speed is not None and pre_release_horizontal_speed > float(max_pre_release_horizontal_speed):
            release_before_settle_detected = True

        if release_video_motion is None:
            hidden_release_region_detected = True
        elif release_video_motion < 0.08 and (post_release_com_speed is None or post_release_com_speed >= 0.15):
            hidden_release_region_detected = True
        elif release_video_motion < 0.04:
            hidden_release_region_detected = True

        if post_release_com_speed is not None and post_release_com_speed > float(max_post_release_com_speed):
            spring_snap_first_detected = True
        if post_release_horizontal_speed is not None and post_release_horizontal_speed > float(max_post_release_horizontal_speed):
            spring_snap_first_detected = True
        if post_release_horizontal_to_vertical_ratio is not None and post_release_horizontal_to_vertical_ratio > float(
            max_post_release_horizontal_to_vertical_ratio
        ):
            spring_snap_first_detected = True
        if post_release_horizontal_jump_ratio is not None and post_release_horizontal_jump_ratio > float(
            max_post_release_horizontal_jump_ratio
        ):
            spring_snap_first_detected = True

        release_dynamics_gate_pass = not (
            hidden_release_region_detected or release_before_settle_detected or spring_snap_first_detected
        )
    else:
        release_dynamics_gate_pass = True

    return {
        "series_source": series_source,
        "frame_dt_s": frame_dt,
        "release_frame": release_frame,
        "settle_frame": settle_frame,
        "release_region_visible_score": release_region_visible_score,
        "pre_release_com_speed_m_s": pre_release_com_speed,
        "pre_release_horizontal_speed_m_s": pre_release_horizontal_speed,
        "post_release_com_speed_m_s": post_release_com_speed,
        "post_release_horizontal_speed_m_s": post_release_horizontal_speed,
        "post_release_vertical_speed_m_s": post_release_vertical_speed,
        "post_release_horizontal_to_vertical_ratio": post_release_horizontal_to_vertical_ratio,
        "post_release_horizontal_jump_ratio": post_release_horizontal_jump_ratio,
        "hidden_release_region_detected": hidden_release_region_detected,
        "release_before_settle_detected": release_before_settle_detected,
        "spring_snap_first_detected": spring_snap_first_detected,
        "release_dynamics_gate_pass": release_dynamics_gate_pass,
    }


def _extract_ground_z(summary: dict[str, Any], physics: dict[str, Any]) -> float:
    value = _first_float(summary, physics, keys=["ground_z_m", "ground_z", "floor_z"])
    return 0.0 if value is None else float(value)


def _extract_min_rope_z(summary: dict[str, Any], physics: dict[str, Any]) -> float | None:
    series = _first_series(
        physics,
        summary,
        keys=[
            "min_rope_z_over_time",
            "rope_min_z_over_time",
            "particle_min_z_over_time",
            "min_particle_z_over_time",
        ],
    )
    if series is not None:
        return float(np.min(np.asarray(series, dtype=np.float32)))
    value = _first_float(
        physics,
        summary,
        keys=[
            "min_rope_z_m",
            "rope_min_z_m",
            "min_particle_z_m",
            "particle_min_z_m",
        ],
    )
    return None if value is None else float(value)


def _extract_event_frames(summary: dict[str, Any], physics: dict[str, Any], video_frames: int) -> dict[str, int | None]:
    summary_frames = int(summary.get("frames") or physics.get("frames") or video_frames or 0)
    release_frame = _first_int(summary, physics, keys=["release_frame", "release_frame_idx", "release_frame_index"])
    impact_frame = _first_int(
        summary,
        physics,
        keys=[
            "first_ground_contact_frame",
            "ground_contact_frame",
            "impact_frame",
            "first_contact_frame",
        ],
    )
    settle_frame = _first_int(summary, physics, keys=["settle_frame", "settled_frame", "last_contact_frame"])
    release_video = _map_summary_frame_to_video_frame(
        release_frame, summary_frames=summary_frames, video_frames=video_frames
    )
    impact_video = _map_summary_frame_to_video_frame(
        impact_frame, summary_frames=summary_frames, video_frames=video_frames
    )
    settle_video = _map_summary_frame_to_video_frame(
        settle_frame, summary_frames=summary_frames, video_frames=video_frames
    )
    pre_release_video = None if release_video is None else max(0, release_video - 2)
    mid_fall_video = None
    if release_video is not None and impact_video is not None and impact_video > release_video + 1:
        mid_fall_video = release_video + max(1, (impact_video - release_video) // 2)
    elif release_video is not None:
        mid_fall_video = min(video_frames - 1, release_video + max(2, video_frames // 6))
    return {
        "setup": 0,
        "pre_release": pre_release_video,
        "release": release_video,
        "mid_fall": mid_fall_video,
        "impact": impact_video,
        "settle": settle_video if settle_video is not None else max(0, video_frames - 1),
    }


def _assess_physics_gate(summary: dict[str, Any], physics: dict[str, Any], *, ground_tol_mm: float) -> dict[str, Any]:
    ground_z = _extract_ground_z(summary, physics)
    min_rope_z = _extract_min_rope_z(summary, physics)
    penetration_mm = None
    rope_through_ground_detected = False
    if min_rope_z is not None:
        penetration_mm = float((ground_z - min_rope_z) * 1000.0)
        rope_through_ground_detected = penetration_mm > float(ground_tol_mm)

    ground_contact_frame = _first_int(
        summary,
        physics,
        keys=[
            "first_ground_contact_frame",
            "ground_contact_frame",
            "impact_frame",
            "first_contact_frame",
        ],
    )
    ground_contact_time_s = _first_float(
        summary,
        physics,
        keys=[
            "first_ground_contact_time_s",
            "ground_contact_time_s",
            "impact_time_s",
            "first_contact_time_s",
        ],
    )
    release_frame = _first_int(summary, physics, keys=["release_frame", "release_frame_idx", "release_frame_index"])
    release_time_s = _first_float(summary, physics, keys=["release_time_s", "release_time", "release_t_s"])
    early_fall_accel = _first_float(
        summary,
        physics,
        keys=[
            "early_fall_vertical_acceleration_m_s2",
            "early_fall_accel_m_s2",
            "fit_early_fall_accel_m_s2",
            "early_fall_acceleration_estimate_m_s2",
        ],
    )
    if early_fall_accel is None:
        nested_fit = physics.get("early_fall_fit")
        if isinstance(nested_fit, dict):
            quad_fit = nested_fit.get("quadratic_fit")
            if isinstance(quad_fit, dict):
                value = quad_fit.get("az_m_s2")
                if isinstance(value, (int, float)):
                    early_fall_accel = float(value)
    gravity_reference = _first_float(
        summary,
        physics,
        keys=["gravity_mag", "gravity_magnitude", "g_m_s2", "gravity_mag_m_s2", "gravity_reference_m_s2"],
    )
    if gravity_reference is None:
        nested_fit = physics.get("early_fall_fit")
        if isinstance(nested_fit, dict):
            value = nested_fit.get("gravity_tolerance_ratio")
            _ = value
        source = physics.get("gravity_mag_m_s2")
        if isinstance(source, (int, float)):
            gravity_reference = float(source)
    gravity_like = None
    if gravity_like is None and isinstance(physics.get("early_fall_fit"), dict):
        nested_flag = physics["early_fall_fit"].get("gravity_like")
        if isinstance(nested_flag, bool):
            gravity_like = bool(nested_flag)
    if early_fall_accel is not None and gravity_reference is not None and gravity_reference > 1.0e-6:
        gravity_like = abs(abs(early_fall_accel) - gravity_reference) / gravity_reference <= 0.30
    return {
        "ground_z_m": float(ground_z),
        "min_rope_z_m": None if min_rope_z is None else float(min_rope_z),
        "ground_penetration_mm": penetration_mm,
        "rope_through_ground_detected": bool(rope_through_ground_detected),
        "ground_contact_frame": ground_contact_frame,
        "ground_contact_time_s": ground_contact_time_s,
        "release_frame": release_frame,
        "release_time_s": release_time_s,
        "early_fall_vertical_acceleration_m_s2": early_fall_accel,
        "gravity_reference_m_s2": gravity_reference,
        "gravity_like": gravity_like,
        "physics_gate_pass": bool(not rope_through_ground_detected),
    }


def _analyze_video(
    video_path: Path,
    *,
    run_dir: Path,
    summary_payload: dict[str, Any],
    physics_payload: dict[str, Any],
    sample_count: int,
    black_mean_threshold: float,
    black_dark_ratio_threshold: float,
    frame_dark_threshold: int,
    near_exact_repeat_threshold: float,
    near_exact_repeat_fraction_threshold: float,
    near_exact_max_run_threshold: int,
    min_total_edge_ratio: float,
    min_robot_band_fraction: float,
    min_ground_band_fraction: float,
    motion_window_frames: int,
    min_release_motion: float,
    min_impact_motion: float,
    min_freefall_motion: float,
    min_freefall_frames: int,
    max_pre_release_com_speed: float,
    max_pre_release_horizontal_speed: float,
    max_post_release_com_speed: float,
    max_post_release_horizontal_speed: float,
    max_post_release_horizontal_to_vertical_ratio: float,
    max_post_release_horizontal_jump_ratio: float,
    max_release_to_settle_gap_frames: int,
    output_ffprobe: Path,
    decode_log_path: Path,
) -> tuple[VideoReport, dict[str, Any], list[np.ndarray], list[str]]:
    ffprobe_payload = _ffprobe(video_path)
    _write_json(output_ffprobe, ffprobe_payload)
    decode_pass = _decode_check(video_path, decode_log_path)
    stream = _video_stream(ffprobe_payload)
    width = int(stream.get("width") or 0)
    height = int(stream.get("height") or 0)
    fps = _fps_from_stream(stream)
    duration = _duration_from_payload(ffprobe_payload)
    nb_frames = int(stream.get("nb_frames") or 0)

    cap = _open_video(video_path)
    try:
        decoded_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        sampled_indices = _sample_indices(decoded_frame_count, sample_count)
        sampled_frames_bgr = [_read_frame(cap, idx) for idx in sampled_indices]
        all_grays: list[np.ndarray] = []
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                break
            all_grays.append(_gray(frame))
    finally:
        cap.release()

    sampled_grays = [_gray(frame) for frame in sampled_frames_bgr]
    sampled_frames_rgb = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in sampled_frames_bgr]

    mean_lumas: list[float] = []
    dark_ratios: list[float] = []
    black_flags: list[bool] = []
    total_edge_ratios: list[float] = []
    robot_band_fractions: list[float] = []
    ground_band_fractions: list[float] = []
    laplacians: list[float] = []
    for gray in sampled_grays:
        mean_luma = float(gray.mean())
        dark_ratio = float((gray < frame_dark_threshold).mean())
        mean_lumas.append(mean_luma)
        dark_ratios.append(dark_ratio)
        black_flags.append(mean_luma < black_mean_threshold and dark_ratio > black_dark_ratio_threshold)
        profile = _edge_profile(gray)
        total_edge_ratios.append(profile["total_edge_ratio"])
        robot_band_fractions.append(
            profile["upper_mid_edge_ratio"] / max(profile["total_edge_ratio"], 1.0e-6)
        )
        ground_band_fractions.append(profile["lower_edge_ratio"] / max(profile["total_edge_ratio"], 1.0e-6))
        laplacians.append(profile["laplacian_var"])

    pair_diffs: list[float] = []
    for i in range(1, len(all_grays)):
        pair_diffs.append(_motion_score(all_grays[i - 1], all_grays[i]))
    if pair_diffs:
        repeated = [v <= near_exact_repeat_threshold for v in pair_diffs]
        near_exact_repeat_fraction = float(np.mean(repeated))
        max_static_run = 0
        cur = 0
        for flag in repeated:
            cur = cur + 1 if flag else 0
            max_static_run = max(max_static_run, cur)
        mean_pair_diff = float(np.mean(pair_diffs))
        median_pair_diff = float(np.median(pair_diffs))
        min_pair_diff = float(np.min(pair_diffs))
        max_pair_diff = float(np.max(pair_diffs))
    else:
        near_exact_repeat_fraction = 1.0
        max_static_run = 0
        mean_pair_diff = 0.0
        median_pair_diff = 0.0
        min_pair_diff = 0.0
        max_pair_diff = 0.0

    black_screen_pass = not any(black_flags)
    smoothness_pass = (
        not (
            near_exact_repeat_fraction > near_exact_repeat_fraction_threshold
            and max_static_run > near_exact_max_run_threshold
            and max_pair_diff < 1.0
            and mean_pair_diff < 0.5
        )
    )
    encoding_pass = width >= 1280 and height >= 720 and fps >= 24.0 and duration >= 1.0 and (
        nb_frames == 0 or nb_frames >= 30
    )

    total_edge_ratio = float(max(total_edge_ratios) if total_edge_ratios else 0.0)
    robot_visibility_score = float(max(robot_band_fractions) if robot_band_fractions else 0.0)
    ground_visibility_score = float(max(ground_band_fractions) if ground_band_fractions else 0.0)

    event_frames = _extract_event_frames(summary_payload, physics_payload, decoded_frame_count)
    release_frame = event_frames.get("release")
    impact_frame = event_frames.get("impact")

    release_motion_score = None
    impact_motion_score = None
    free_fall_motion_score = None
    if all_grays:
        release_motion_score = _local_motion_score(all_grays, int(release_frame), motion_window_frames) if release_frame is not None else None
        impact_motion_score = _local_motion_score(all_grays, int(impact_frame), motion_window_frames) if impact_frame is not None else None
        if release_frame is not None and impact_frame is not None and int(impact_frame) > int(release_frame) + min_freefall_frames:
            window_scores: list[float] = []
            for idx in range(int(release_frame) + 1, int(impact_frame)):
                score = _local_motion_score(all_grays, idx, motion_window_frames)
                if score is not None:
                    window_scores.append(score)
            if window_scores:
                free_fall_motion_score = float(np.mean(window_scores))

    readable_flags: list[bool] = []
    if release_frame is not None and impact_frame is not None:
        readable_flags.append(int(impact_frame) > int(release_frame) + min_freefall_frames)
    if release_motion_score is not None:
        readable_flags.append(release_motion_score >= min_release_motion)
    if impact_motion_score is not None:
        readable_flags.append(impact_motion_score >= min_impact_motion)
    if free_fall_motion_score is not None:
        readable_flags.append(free_fall_motion_score >= min_freefall_motion)
    readability_pass = bool(readable_flags) and all(readable_flags)

    scene_readable_gate = bool(
        total_edge_ratio >= min_total_edge_ratio
        and robot_visibility_score >= min_robot_band_fraction
        and ground_visibility_score >= min_ground_band_fraction
    )

    report = VideoReport(
        video_path=str(video_path),
        ffprobe_path=str(output_ffprobe),
        resolution_width=width,
        resolution_height=height,
        encoded_fps=float(fps),
        duration_s=float(duration),
        nb_frames=nb_frames,
        decoded_frame_count=decoded_frame_count,
        mean_luma=mean_lumas,
        dark_pixel_ratio=dark_ratios,
        black_frame_fraction=float(np.mean(black_flags)) if black_flags else 1.0,
        near_exact_repeat_fraction=float(near_exact_repeat_fraction),
        max_static_run=max_static_run,
        mean_pair_diff=mean_pair_diff,
        median_pair_diff=median_pair_diff,
        min_pair_diff=min_pair_diff,
        max_pair_diff=max_pair_diff,
        total_edge_ratio=total_edge_ratio,
        robot_visibility_score=robot_visibility_score,
        ground_visibility_score=ground_visibility_score,
        release_motion_score=release_motion_score,
        impact_motion_score=impact_motion_score,
        free_fall_motion_score=free_fall_motion_score,
        pre_release_com_speed_m_s=None,
        post_release_com_speed_m_s=None,
        post_release_horizontal_speed_m_s=None,
        post_release_vertical_speed_m_s=None,
        post_release_horizontal_to_vertical_ratio=None,
        post_release_horizontal_jump_ratio=None,
        release_region_visible_score=None if release_motion_score is None else float(release_motion_score),
        release_dynamics_gate_pass=True,
        hidden_release_region_detected=False,
        release_before_settle_detected=False,
        spring_snap_first_detected=False,
        encoding_gate_pass=bool(encoding_pass),
        decode_gate_pass=bool(decode_pass),
        black_screen_gate_pass=bool(black_screen_pass),
        smoothness_gate_pass=bool(smoothness_pass),
        readability_gate_pass=bool(scene_readable_gate and readability_pass),
        overall_gate_pass=bool(
            encoding_pass and decode_pass and black_screen_pass and smoothness_pass and scene_readable_gate and readability_pass
        ),
    )

    release_dynamics = _assess_release_dynamics(
        run_dir,
        summary_payload,
        physics_payload,
        presentation_report=report,
        max_pre_release_com_speed=max_pre_release_com_speed,
        max_pre_release_horizontal_speed=max_pre_release_horizontal_speed,
        max_post_release_com_speed=max_post_release_com_speed,
        max_post_release_horizontal_speed=max_post_release_horizontal_speed,
        max_post_release_horizontal_to_vertical_ratio=max_post_release_horizontal_to_vertical_ratio,
        max_post_release_horizontal_jump_ratio=max_post_release_horizontal_jump_ratio,
        max_release_to_settle_gap_frames=max_release_to_settle_gap_frames,
    )
    report.pre_release_com_speed_m_s = release_dynamics["pre_release_com_speed_m_s"]
    report.post_release_com_speed_m_s = release_dynamics["post_release_com_speed_m_s"]
    report.post_release_horizontal_speed_m_s = release_dynamics["post_release_horizontal_speed_m_s"]
    report.post_release_vertical_speed_m_s = release_dynamics["post_release_vertical_speed_m_s"]
    report.post_release_horizontal_to_vertical_ratio = release_dynamics["post_release_horizontal_to_vertical_ratio"]
    report.post_release_horizontal_jump_ratio = release_dynamics["post_release_horizontal_jump_ratio"]
    report.release_region_visible_score = release_dynamics["release_region_visible_score"]
    report.release_dynamics_gate_pass = bool(release_dynamics["release_dynamics_gate_pass"])
    report.hidden_release_region_detected = bool(release_dynamics["hidden_release_region_detected"])
    report.release_before_settle_detected = bool(release_dynamics["release_before_settle_detected"])
    report.spring_snap_first_detected = bool(release_dynamics["spring_snap_first_detected"])
    report.overall_gate_pass = bool(report.overall_gate_pass and report.release_dynamics_gate_pass)

    meta = {
        "sampled_indices": sampled_indices,
        "sampled_frames_rgb": sampled_frames_rgb,
        "sampled_frames_gray": sampled_grays,
        "event_frames": event_frames,
        "scene_readable_gate_pass": bool(scene_readable_gate),
        "release_motion_pass": None if release_motion_score is None else bool(release_motion_score >= min_release_motion),
        "impact_motion_pass": None if impact_motion_score is None else bool(impact_motion_score >= min_impact_motion),
        "free_fall_motion_pass": None if free_fall_motion_score is None else bool(free_fall_motion_score >= min_freefall_motion),
        "release_dynamics": release_dynamics,
    }
    return report, meta, sampled_frames_rgb, [str(i) for i in sampled_indices]


def _event_sheet_frames(
    video_path: Path,
    event_frames: dict[str, int | None],
    *,
    output_dir: Path,
) -> tuple[list[np.ndarray], list[str], list[Path]]:
    cap = _open_video(video_path)
    try:
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        chosen: list[int] = []
        labels: list[str] = []
        for name in ["setup", "pre_release", "release", "mid_fall", "impact", "settle"]:
            idx = event_frames.get(name)
            if idx is None:
                continue
            idx = max(0, min(frame_count - 1, int(idx)))
            if idx in chosen:
                continue
            chosen.append(idx)
            labels.append(f"{name} | frame {idx}")
        frames_bgr = [_read_frame(cap, idx) for idx in chosen]
    finally:
        cap.release()
    frames_rgb = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in frames_bgr]
    keyframe_paths: list[Path] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for i, (idx, rgb) in enumerate(zip(chosen, frames_rgb), start=1):
        path = output_dir / f"event_{i:02d}_frame_{idx:06d}.png"
        Image.fromarray(rgb).save(path)
        keyframe_paths.append(path)
    return frames_rgb, labels, keyframe_paths


def _readability_summary(report: VideoReport, physics_gate_pass: bool, scene_readable: bool) -> bool:
    return bool(report.overall_gate_pass and physics_gate_pass and scene_readable)


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.expanduser().resolve()
    if not run_dir.exists():
        raise FileNotFoundError(f"run_dir does not exist: {run_dir}")

    qa_dir = (args.output_dir or (run_dir / "qa")).expanduser().resolve()
    keyframes_dir = run_dir / "keyframes"
    qa_dir.mkdir(parents=True, exist_ok=True)
    keyframes_dir.mkdir(parents=True, exist_ok=True)

    summary_path = _resolve_path(run_dir, args.summary_json) or _discover_first(
        run_dir,
        ["summary.json", "*_summary.json", "work/*_summary.json", "sim/*summary.json"],
    )
    physics_path = _resolve_path(run_dir, args.physics_validation_json) or _discover_first(
        run_dir,
        ["physics_validation.json", "*_physics_validation.json", "work/*physics_validation.json"],
    )
    summary_payload = _load_json(summary_path)
    physics_payload = _load_json(physics_path)

    presentation_video = _resolve_path(run_dir, args.presentation_video) or _discover_first(
        run_dir,
        [
            "final_presentation.mp4",
            "media/final_presentation.mp4",
            "final.mp4",
            "media/final.mp4",
            "*.mp4",
            "media/*.mp4",
        ],
    )
    debug_video = _resolve_path(run_dir, args.debug_video) or _discover_first(
        run_dir,
        [
            "final_debug.mp4",
            "media/final_debug.mp4",
            "debug.mp4",
            "media/debug.mp4",
        ],
    )
    if presentation_video is None:
        raise FileNotFoundError(f"no presentation video found under {run_dir}")
    if debug_video is None:
        raise FileNotFoundError(f"no debug video found under {run_dir}")

    presentation_ffprobe = qa_dir / "ffprobe.json"
    presentation_decode_log = qa_dir / "decode.log"
    presentation_report, presentation_meta, sampled_rgb, _ = _analyze_video(
        presentation_video,
        run_dir=run_dir,
        summary_payload=summary_payload,
        physics_payload=physics_payload,
        sample_count=args.sample_count,
        black_mean_threshold=args.black_mean_threshold,
        black_dark_ratio_threshold=args.black_dark_ratio_threshold,
        frame_dark_threshold=args.frame_dark_threshold,
        near_exact_repeat_threshold=args.near_exact_repeat_threshold,
        near_exact_repeat_fraction_threshold=args.near_exact_repeat_fraction_threshold,
        near_exact_max_run_threshold=args.near_exact_max_run_threshold,
        min_total_edge_ratio=args.min_total_edge_ratio,
        min_robot_band_fraction=args.min_robot_band_fraction,
        min_ground_band_fraction=args.min_ground_band_fraction,
        motion_window_frames=args.motion_window_frames,
        min_release_motion=args.min_release_motion,
        min_impact_motion=args.min_impact_motion,
        min_freefall_motion=args.min_freefall_motion,
        min_freefall_frames=args.min_freefall_frames,
        max_pre_release_com_speed=args.max_pre_release_com_speed,
        max_pre_release_horizontal_speed=args.max_pre_release_horizontal_speed,
        max_post_release_com_speed=args.max_post_release_com_speed,
        max_post_release_horizontal_speed=args.max_post_release_horizontal_speed,
        max_post_release_horizontal_to_vertical_ratio=args.max_post_release_horizontal_to_vertical_ratio,
        max_post_release_horizontal_jump_ratio=args.max_post_release_horizontal_jump_ratio,
        max_release_to_settle_gap_frames=args.max_release_to_settle_gap_frames,
        output_ffprobe=presentation_ffprobe,
        decode_log_path=presentation_decode_log,
    )
    debug_ffprobe = qa_dir / "debug_ffprobe.json"
    debug_decode_log = qa_dir / "debug_decode.log"
    debug_report, debug_meta, _, _ = _analyze_video(
        debug_video,
        run_dir=run_dir,
        summary_payload=summary_payload,
        physics_payload=physics_payload,
        sample_count=args.sample_count,
        black_mean_threshold=args.black_mean_threshold,
        black_dark_ratio_threshold=args.black_dark_ratio_threshold,
        frame_dark_threshold=args.frame_dark_threshold,
        near_exact_repeat_threshold=args.near_exact_repeat_threshold,
        near_exact_repeat_fraction_threshold=args.near_exact_repeat_fraction_threshold,
        near_exact_max_run_threshold=args.near_exact_max_run_threshold,
        min_total_edge_ratio=args.min_total_edge_ratio,
        min_robot_band_fraction=args.min_robot_band_fraction,
        min_ground_band_fraction=args.min_ground_band_fraction,
        motion_window_frames=args.motion_window_frames,
        min_release_motion=args.min_release_motion,
        min_impact_motion=args.min_impact_motion,
        min_freefall_motion=args.min_freefall_motion,
        min_freefall_frames=args.min_freefall_frames,
        max_pre_release_com_speed=args.max_pre_release_com_speed,
        max_pre_release_horizontal_speed=args.max_pre_release_horizontal_speed,
        max_post_release_com_speed=args.max_post_release_com_speed,
        max_post_release_horizontal_speed=args.max_post_release_horizontal_speed,
        max_post_release_horizontal_to_vertical_ratio=args.max_post_release_horizontal_to_vertical_ratio,
        max_post_release_horizontal_jump_ratio=args.max_post_release_horizontal_jump_ratio,
        max_release_to_settle_gap_frames=args.max_release_to_settle_gap_frames,
        output_ffprobe=debug_ffprobe,
        decode_log_path=debug_decode_log,
    )

    physics_gate = _assess_physics_gate(summary_payload, physics_payload, ground_tol_mm=args.ground_penetration_tol_mm)
    event_frames = dict(presentation_meta["event_frames"])
    event_frames_with_impact = dict(event_frames)
    impact_override = physics_gate.get("ground_contact_frame")
    release_override = physics_gate.get("release_frame")
    if impact_override is not None:
        event_frames_with_impact["impact"] = int(impact_override)
    if release_override is not None:
        event_frames_with_impact["release"] = int(release_override)
    event_frames_with_impact["settle"] = event_frames.get("settle")

    event_frames_rgb, event_labels, event_keyframes = _event_sheet_frames(
        presentation_video,
        event_frames_with_impact,
        output_dir=keyframes_dir,
    )
    contact_sheet_path = _make_sheet(
        sampled_rgb,
        [f"sample_{i + 1:02d} | frame {idx}" for i, idx in enumerate(presentation_meta["sampled_indices"])],
        qa_dir / "contact_sheet.png",
        cols=4,
    )
    event_sheet_path = _make_sheet(
        event_frames_rgb,
        event_labels,
        qa_dir / "event_sheet.png",
        cols=max(1, min(4, len(event_frames_rgb))),
    )

    summary_frames = int(summary_payload.get("frames") or physics_payload.get("frames") or presentation_report.decoded_frame_count or 0)
    release_frame = physics_gate.get("release_frame")
    impact_frame = physics_gate.get("ground_contact_frame")
    release_time_s = physics_gate.get("release_time_s")
    impact_time_s = physics_gate.get("ground_contact_time_s")
    presentation_validation = asdict(presentation_report)
    debug_validation = asdict(debug_report)
    validation: dict[str, Any] = {
        "run_dir": str(run_dir),
        "summary_path": None if summary_path is None else str(summary_path),
        "physics_validation_path": None if physics_path is None else str(physics_path),
        "presentation_video": presentation_validation,
        "debug_video": debug_validation,
        "physics_gate": physics_gate,
        "sample_count": int(args.sample_count),
        "black_mean_threshold": float(args.black_mean_threshold),
        "black_dark_ratio_threshold": float(args.black_dark_ratio_threshold),
        "frame_dark_threshold": int(args.frame_dark_threshold),
        "near_exact_repeat_threshold": float(args.near_exact_repeat_threshold),
        "near_exact_repeat_fraction_threshold": float(args.near_exact_repeat_fraction_threshold),
        "near_exact_max_run_threshold": int(args.near_exact_max_run_threshold),
        "min_total_edge_ratio": float(args.min_total_edge_ratio),
        "min_robot_band_fraction": float(args.min_robot_band_fraction),
        "min_ground_band_fraction": float(args.min_ground_band_fraction),
        "motion_window_frames": int(args.motion_window_frames),
        "min_release_motion": float(args.min_release_motion),
        "min_impact_motion": float(args.min_impact_motion),
        "min_freefall_motion": float(args.min_freefall_motion),
        "min_freefall_frames": int(args.min_freefall_frames),
        "max_pre_release_com_speed": float(args.max_pre_release_com_speed),
        "max_pre_release_horizontal_speed": float(args.max_pre_release_horizontal_speed),
        "max_post_release_com_speed": float(args.max_post_release_com_speed),
        "max_post_release_horizontal_speed": float(args.max_post_release_horizontal_speed),
        "max_post_release_horizontal_to_vertical_ratio": float(args.max_post_release_horizontal_to_vertical_ratio),
        "max_post_release_horizontal_jump_ratio": float(args.max_post_release_horizontal_jump_ratio),
        "max_release_to_settle_gap_frames": int(args.max_release_to_settle_gap_frames),
        "ground_penetration_tolerance_mm": float(args.ground_penetration_tol_mm),
        "presentation_event_frames": event_frames,
        "release_dynamics": presentation_meta["release_dynamics"],
        "summary_frame_count": summary_frames,
        "contact_sheet_path": str(contact_sheet_path),
        "event_sheet_path": str(event_sheet_path),
        "keyframes_dir": str(keyframes_dir),
        "overall_gate_pass": bool(
            presentation_report.overall_gate_pass
            and debug_report.overall_gate_pass
            and physics_gate["physics_gate_pass"]
        ),
    }
    _write_json(qa_dir / "validation.json", validation)

    verdict_lines = [
        "# Native Robot Rope Drop/Release Video Verdict",
        "",
        "## Files",
        f"- Presentation video: `{presentation_video}`",
        f"- Debug video: `{debug_video}`",
        f"- Summary: `{summary_path}`",
        f"- Physics validation: `{physics_path}`",
        f"- ffprobe: `{presentation_ffprobe}`",
        f"- Contact sheet: `{contact_sheet_path}`",
        f"- Event sheet: `{event_sheet_path}`",
        "",
        "## Presentation Gates",
        f"- Encoding: {'PASS' if presentation_report.encoding_gate_pass else 'FAIL'}",
        f"- Decode: {'PASS' if presentation_report.decode_gate_pass else 'FAIL'}",
        f"- Black screen: {'PASS' if presentation_report.black_screen_gate_pass else 'FAIL'}",
        f"- Smoothness: {'PASS' if presentation_report.smoothness_gate_pass else 'FAIL'}",
        f"- Scene readability: {'PASS' if presentation_meta['scene_readable_gate_pass'] else 'FAIL'}",
        f"- Event readability: {'PASS' if presentation_report.readability_gate_pass else 'FAIL'}",
        "",
        "## Debug Gates",
        f"- Encoding: {'PASS' if debug_report.encoding_gate_pass else 'FAIL'}",
        f"- Decode: {'PASS' if debug_report.decode_gate_pass else 'FAIL'}",
        f"- Black screen: {'PASS' if debug_report.black_screen_gate_pass else 'FAIL'}",
        f"- Smoothness: {'PASS' if debug_report.smoothness_gate_pass else 'FAIL'}",
        f"- Scene readability: {'PASS' if debug_meta['scene_readable_gate_pass'] else 'FAIL'}",
        f"- Event readability: {'PASS' if debug_report.readability_gate_pass else 'FAIL'}",
        f"- Release dynamics gate: {'PASS' if presentation_report.release_dynamics_gate_pass else 'FAIL'}",
        "",
        "## Physics Gate",
        f"- Ground contact frame: {impact_frame}",
        f"- Ground contact time: {impact_time_s}",
        f"- Release frame: {release_frame}",
        f"- Release time: {release_time_s}",
        f"- Ground penetration detected: {'YES' if physics_gate['rope_through_ground_detected'] else 'NO'}",
        f"- Ground penetration mm: {physics_gate['ground_penetration_mm']}",
        f"- Early fall acceleration: {physics_gate['early_fall_vertical_acceleration_m_s2']}",
        f"- Gravity-like fit: {physics_gate['gravity_like']}",
        "",
        "## Release Dynamics",
        f"- Release region visible score: {presentation_report.release_region_visible_score}",
        f"- Pre-release COM speed: {presentation_report.pre_release_com_speed_m_s}",
        f"- Post-release COM speed: {presentation_report.post_release_com_speed_m_s}",
        f"- Post-release horizontal speed: {presentation_report.post_release_horizontal_speed_m_s}",
        f"- Post-release horizontal to vertical ratio: {presentation_report.post_release_horizontal_to_vertical_ratio}",
        f"- Post-release horizontal jump ratio: {presentation_report.post_release_horizontal_jump_ratio}",
        f"- Hidden release region detected: {'YES' if presentation_report.hidden_release_region_detected else 'NO'}",
        f"- Release-before-settle detected: {'YES' if presentation_report.release_before_settle_detected else 'NO'}",
        f"- Spring-snap-first detected: {'YES' if presentation_report.spring_snap_first_detected else 'NO'}",
        "",
        "## Final Status",
        f"- Presentation overall: {'PASS' if presentation_report.overall_gate_pass else 'FAIL'}",
        f"- Debug overall: {'PASS' if debug_report.overall_gate_pass else 'FAIL'}",
        f"- Physics overall: {'PASS' if physics_gate['physics_gate_pass'] else 'FAIL'}",
        f"- Combined overall: {'PASS' if validation['overall_gate_pass'] else 'FAIL'}",
    ]
    _write_markdown(qa_dir / "verdict.md", verdict_lines)

    print(f"[validate_native_robot_rope_drop_release_video] run_dir={run_dir}")
    print(f"[validate_native_robot_rope_drop_release_video] presentation={presentation_video}")
    print(f"[validate_native_robot_rope_drop_release_video] debug={debug_video}")
    print(f"[validate_native_robot_rope_drop_release_video] verdict={qa_dir / 'verdict.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
