#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Validate physics for the native robot rope drop/release baseline and "
            "optionally compare apply_drag=False vs apply_drag=True runs."
        )
    )
    p.add_argument("run_dir", type=Path, help="Primary run directory to validate")
    p.add_argument(
        "--compare-run-dir",
        type=Path,
        default=None,
        help="Optional second run directory for A/B comparison.",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output physics_validation.json path. Defaults to <run_dir>/physics_validation.json.",
    )
    p.add_argument("--gravity-mag", type=float, default=9.8)
    p.add_argument(
        "--gravity-tolerance-ratio",
        type=float,
        default=0.30,
        help="Acceptable fractional error from g for the early-fall acceleration fit.",
    )
    p.add_argument(
        "--contact-margin-m",
        type=float,
        default=1.0e-3,
        help="Tolerance added to the radius-based ground-contact threshold.",
    )
    p.add_argument(
        "--penetration-margin-m",
        type=float,
        default=1.0e-4,
        help="Tolerance used when deciding whether a rope point penetrated below the ground plane.",
    )
    p.add_argument(
        "--fit-min-frames",
        type=int,
        default=8,
        help="Minimum number of pre-contact samples needed for the early-fall acceleration fit.",
    )
    p.add_argument(
        "--fit-trim-frac",
        type=float,
        default=0.10,
        help="Trim this fraction off the start and end of the pre-contact interval before fitting.",
    )
    p.add_argument(
        "--impact-window-frames",
        type=int,
        default=20,
        help="Number of frames used for the local impact-speed fit before first contact.",
    )
    p.add_argument(
        "--settle-window-seconds",
        type=float,
        default=0.08,
        help="Pre-release settle window length [s].",
    )
    p.add_argument(
        "--pre-release-particle-speed-mean-max",
        type=float,
        default=0.05,
        help="Maximum allowed rope particle mean speed over the settle window [m/s].",
    )
    p.add_argument(
        "--pre-release-com-horizontal-speed-max",
        type=float,
        default=0.03,
        help="Maximum allowed rope COM horizontal speed over the settle window [m/s].",
    )
    p.add_argument(
        "--pre-release-support-speed-mean-max",
        type=float,
        default=0.02,
        help="Maximum allowed support-patch mean speed over the settle window [m/s].",
    )
    p.add_argument(
        "--post-release-kick-window-seconds",
        type=float,
        default=0.08,
        help="Window [s] used to average post-release horizontal kick.",
    )
    p.add_argument(
        "--post-release-horizontal-kick-max",
        type=float,
        default=0.10,
        help="Maximum allowed average COM horizontal speed immediately after release [m/s].",
    )
    return p.parse_args()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_one(root: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        found = sorted(root.glob(pattern))
        if found:
            return found[0]
    return None


def _infer_bool_from_command(cmd_path: Path, flag: str) -> bool | None:
    if not cmd_path.exists():
        return None
    try:
        tokens = shlex.split(cmd_path.read_text(encoding="utf-8").strip())
    except Exception:
        return None
    if flag in tokens:
        return True
    no_flag = f"--no-{flag[2:]}" if flag.startswith("--") else None
    if no_flag and no_flag in tokens:
        return False
    return None


def _infer_bool_from_run_dir(run_dir: Path) -> bool | None:
    name = str(run_dir).lower()
    if any(token in name for token in ("drag_off", "drag-off", "nodrag", "no_drag")):
        return False
    if any(token in name for token in ("drag_on", "drag-on", "apply_drag", "withdrag")):
        return True
    return None


def _infer_ground_z(summary: dict[str, Any]) -> float:
    for key in ("physical_ground_z", "ground_z", "floor_z", "floor_height", "contact_ground_z"):
        val = summary.get(key)
        if isinstance(val, (int, float)) and math.isfinite(float(val)):
            return float(val)
    return 0.0


def _infer_frame_dt(summary: dict[str, Any]) -> float:
    frame_dt = summary.get("frame_dt")
    if isinstance(frame_dt, (int, float)) and float(frame_dt) > 0.0:
        return float(frame_dt)
    sim_dt = summary.get("sim_dt")
    substeps = summary.get("substeps")
    if isinstance(sim_dt, (int, float)) and isinstance(substeps, (int, float)) and float(sim_dt) > 0.0 and int(substeps) > 0:
        return float(sim_dt) * int(substeps)
    raise ValueError("Could not infer frame_dt from summary")


def _load_series(path: Path) -> np.ndarray:
    arr = np.load(path, mmap_mode="r")
    if arr.ndim != 3 or arr.shape[-1] != 3:
        raise ValueError(f"Unexpected rope history shape: {arr.shape} from {path}")
    return arr


def _load_ir_collision_radius(summary: dict[str, Any]) -> np.ndarray:
    ir_path = summary.get("ir_path")
    if not ir_path:
        raise FileNotFoundError("summary is missing ir_path")
    with np.load(Path(str(ir_path)).expanduser().resolve(), allow_pickle=False) as ir:
        if "collision_radius" in ir.files:
            radii = np.asarray(ir["collision_radius"], dtype=np.float32)
        elif "contact_collision_dist" in ir.files:
            radii = np.asarray(ir["contact_collision_dist"], dtype=np.float32).reshape(1)
        else:
            raise KeyError(f"IR at {ir_path} is missing collision radius information")
    radii = radii.reshape(-1)
    if radii.size == 0:
        raise ValueError(f"IR at {ir_path} has an empty collision-radius array")
    return radii.astype(np.float32, copy=False)


def _load_ir_spring_data(summary: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    ir_path = summary.get("ir_path")
    if not ir_path:
        raise FileNotFoundError("summary is missing ir_path")
    with np.load(Path(str(ir_path)).expanduser().resolve(), allow_pickle=False) as ir:
        n_obj = int(np.asarray(ir["num_object_points"]).ravel()[0])
        edges = np.asarray(ir["spring_edges"], dtype=np.int32)
        rest = np.asarray(
            ir["spring_rest_length"] if "spring_rest_length" in ir.files else ir.get("spring_rest_lengths", np.zeros((edges.shape[0],), dtype=np.float32)),
            dtype=np.float32,
        ).reshape(-1)
    obj_mask = np.logical_and(edges[:, 0] < n_obj, edges[:, 1] < n_obj)
    edges = edges[obj_mask]
    if rest.shape[0] == obj_mask.shape[0]:
        rest = rest[obj_mask]
    if rest.shape[0] != edges.shape[0]:
        rest = np.zeros((edges.shape[0],), dtype=np.float32)
    return edges.astype(np.int32, copy=False), rest.astype(np.float32, copy=False)


def _series_com_and_min_z(particle_q: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
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
    frame_finite = finite.all(axis=(1, 2))
    return com.astype(np.float32, copy=False), min_z, frame_finite


def _settle_window_metrics(
    particle_speed_mean: np.ndarray,
    com_horizontal_speed: np.ndarray,
    support_patch_speed_mean: np.ndarray,
    *,
    release_idx: int,
    window_frames: int,
    frame_dt: float,
    particle_speed_threshold_m_s: float,
    com_horizontal_speed_threshold_m_s: float,
    support_patch_speed_threshold_m_s: float,
) -> tuple[dict[str, Any], bool]:
    start = max(0, int(release_idx) - int(window_frames))
    end = max(start, int(release_idx) - 1)
    if end < start:
        values = {
            "window_start_frame": int(start),
            "window_end_frame": int(end),
            "window_duration_s": 0.0,
            "particle_speed_mean_max_m_s": None,
            "particle_speed_mean_mean_m_s": None,
            "com_horizontal_speed_max_m_s": None,
            "com_horizontal_speed_mean_m_s": None,
            "support_patch_speed_mean_max_m_s": None,
            "support_patch_speed_mean_mean_m_s": None,
            "particle_speed_mean_threshold_m_s": float(particle_speed_threshold_m_s),
            "com_horizontal_speed_threshold_m_s": float(com_horizontal_speed_threshold_m_s),
            "support_patch_speed_threshold_m_s": float(support_patch_speed_threshold_m_s),
        }
        return values, False
    p = particle_speed_mean[start : end + 1]
    c = com_horizontal_speed[start : end + 1]
    s = support_patch_speed_mean[start : end + 1]
    values = {
        "window_start_frame": int(start),
        "window_end_frame": int(end),
        "window_duration_s": float((end - start + 1) * frame_dt),
        "particle_speed_mean_max_m_s": float(np.max(p)) if p.size else None,
        "particle_speed_mean_mean_m_s": float(np.mean(p)) if p.size else None,
        "com_horizontal_speed_max_m_s": float(np.max(c)) if c.size else None,
        "com_horizontal_speed_mean_m_s": float(np.mean(c)) if c.size else None,
        "support_patch_speed_mean_max_m_s": float(np.max(s)) if s.size else None,
        "support_patch_speed_mean_mean_m_s": float(np.mean(s)) if s.size else None,
        "particle_speed_mean_threshold_m_s": float(particle_speed_threshold_m_s),
        "com_horizontal_speed_threshold_m_s": float(com_horizontal_speed_threshold_m_s),
        "support_patch_speed_threshold_m_s": float(support_patch_speed_threshold_m_s),
    }
    settle_ok = (
        (end - start + 1) >= int(window_frames)
        and values["particle_speed_mean_max_m_s"] is not None
        and values["particle_speed_mean_max_m_s"] <= float(particle_speed_threshold_m_s)
        and values["com_horizontal_speed_max_m_s"] <= float(com_horizontal_speed_threshold_m_s)
        and values["support_patch_speed_mean_max_m_s"] <= float(support_patch_speed_threshold_m_s)
    )
    return values, bool(settle_ok)


def _fit_quadratic_time_series(times: np.ndarray, values: np.ndarray) -> dict[str, float]:
    times = np.asarray(times, dtype=np.float64)
    values = np.asarray(values, dtype=np.float64)
    tau = times - float(times[0])
    a = np.column_stack([np.ones_like(tau), tau, tau * tau])
    coeffs, *_ = np.linalg.lstsq(a, values, rcond=None)
    pred = a @ coeffs
    resid = values - pred
    ss_res = float(np.sum(resid * resid))
    centered = values - float(np.mean(values))
    ss_tot = float(np.sum(centered * centered))
    r2 = 1.0 if ss_tot <= 1.0e-18 else max(0.0, 1.0 - ss_res / ss_tot)
    return {
        "z0_m": float(coeffs[0]),
        "vz0_m_s": float(coeffs[1]),
        "az_m_s2": float(2.0 * coeffs[2]),
        "r2": float(r2),
        "rmse_m": float(math.sqrt(ss_res / max(int(values.size), 1))),
    }


def _fit_linear_velocity(times: np.ndarray, values: np.ndarray) -> dict[str, float]:
    times = np.asarray(times, dtype=np.float64)
    values = np.asarray(values, dtype=np.float64)
    tau = times - float(times[0])
    a = np.column_stack([np.ones_like(tau), tau])
    coeffs, *_ = np.linalg.lstsq(a, values, rcond=None)
    pred = a @ coeffs
    resid = values - pred
    ss_res = float(np.sum(resid * resid))
    return {
        "z0_m": float(coeffs[0]),
        "vz_m_s": float(coeffs[1]),
        "rmse_m": float(math.sqrt(ss_res / max(int(values.size), 1))),
    }


def _trimmed_window_indices(
    release_idx: int,
    contact_idx: int,
    *,
    min_frames: int,
    trim_frac: float,
) -> tuple[int, int] | None:
    if contact_idx <= release_idx + 1:
        return None
    span = contact_idx - release_idx
    trim = max(1, int(round(span * float(trim_frac))))
    start = release_idx + trim
    end = contact_idx - trim
    if end - start + 1 < min_frames:
        start = release_idx + 1
        end = contact_idx - 1
    if end - start + 1 < min_frames:
        return None
    return start, end


def _estimate_run_metrics(
    run_dir: Path,
    *,
    gravity_mag: float,
    gravity_tolerance_ratio: float,
    contact_margin_m: float,
    penetration_margin_m: float,
    fit_min_frames: int,
    fit_trim_frac: float,
    impact_window_frames: int,
    settle_window_seconds: float,
    pre_release_particle_speed_mean_max: float,
    pre_release_com_horizontal_speed_max: float,
    pre_release_support_speed_mean_max: float,
    post_release_kick_window_seconds: float,
    post_release_horizontal_kick_max: float,
) -> dict[str, Any]:
    run_dir = run_dir.expanduser().resolve()
    summary_path = _find_one(run_dir, ["summary.json", "*_summary.json", "work/*_summary.json"])
    if summary_path is None:
        raise FileNotFoundError(f"No summary.json found under {run_dir}")
    summary = _read_json(summary_path)

    hist_path = None
    hist_info = summary.get("history_storage_files")
    if isinstance(hist_info, dict):
        candidate = hist_info.get("particle_q_object")
        if candidate:
            hist_path = Path(str(candidate)).expanduser().resolve()
    if hist_path is None or not hist_path.exists():
        hist_path = _find_one(run_dir, ["particle_q_object.npy", "work/*_particle_q_object.npy", "sim/history/*particle_q_object.npy", "**/*particle_q_object.npy"])
    if hist_path is None:
        raise FileNotFoundError(f"No particle_q_object history found under {run_dir}")

    command_path = _find_one(run_dir, ["command.txt", "work/command.txt"])
    apply_drag = None
    if isinstance(summary.get("apply_drag"), bool):
        apply_drag = bool(summary["apply_drag"])
    elif command_path is not None:
        apply_drag = _infer_bool_from_command(command_path, "--apply-drag")
    if apply_drag is None:
        apply_drag = _infer_bool_from_run_dir(run_dir)

    particle_q = _load_series(hist_path)
    rope_com_xyz, min_rope_z, finite_frames = _series_com_and_min_z(particle_q)
    frame_dt = _infer_frame_dt(summary)
    times = np.arange(rope_com_xyz.shape[0], dtype=np.float64) * float(frame_dt)
    ground_z = _infer_ground_z(summary)
    collision_radii = _load_ir_collision_radius(summary)
    spring_edges, spring_rest = _load_ir_spring_data(summary)
    support_patch_indices = np.asarray(summary.get("support_patch_indices") or [], dtype=np.int32).reshape(-1)
    contact_threshold_z = float(ground_z + float(np.min(collision_radii)) + float(contact_margin_m))
    penetration_threshold_z = float(ground_z - float(penetration_margin_m))

    rope_com_vel = np.zeros_like(rope_com_xyz, dtype=np.float32)
    if rope_com_xyz.shape[0] > 1:
        rope_com_vel[1:] = (rope_com_xyz[1:] - rope_com_xyz[:-1]) / max(float(frame_dt), 1.0e-12)
        rope_com_vel[0] = rope_com_vel[1]
    rope_com_horizontal_speed = np.linalg.norm(rope_com_vel[:, :2], axis=1).astype(np.float32, copy=False)
    rope_com_vertical_speed = rope_com_vel[:, 2].astype(np.float32, copy=False)

    particle_speed_mean = np.zeros((particle_q.shape[0],), dtype=np.float32)
    support_patch_speed_mean = np.zeros((particle_q.shape[0],), dtype=np.float32)
    spring_energy_proxy = np.zeros((particle_q.shape[0],), dtype=np.float32)
    for frame_idx in range(1, particle_q.shape[0]):
        q_prev = np.asarray(particle_q[frame_idx - 1], dtype=np.float32)
        q_curr = np.asarray(particle_q[frame_idx], dtype=np.float32)
        qd = (q_curr - q_prev) / max(float(frame_dt), 1.0e-12)
        particle_speed_mean[frame_idx] = float(np.mean(np.linalg.norm(qd, axis=1)))
        if support_patch_indices.size:
            support_patch_speed_mean[frame_idx] = float(np.mean(np.linalg.norm(qd[support_patch_indices], axis=1)))
        if spring_edges.size:
            edge_vec = q_curr[spring_edges[:, 0]] - q_curr[spring_edges[:, 1]]
            edge_len = np.linalg.norm(edge_vec, axis=1)
            stretch = edge_len - spring_rest
            spring_energy_proxy[frame_idx] = float(np.mean(stretch * stretch))
    if particle_q.shape[0] > 1:
        particle_speed_mean[0] = particle_speed_mean[1]
        support_patch_speed_mean[0] = support_patch_speed_mean[1]
        spring_energy_proxy[0] = spring_energy_proxy[1]

    contact_mask = min_rope_z <= contact_threshold_z
    contact_frames = np.flatnonzero(contact_mask)
    first_contact_idx = int(contact_frames[0]) if contact_frames.size else None
    first_contact_time_s = None if first_contact_idx is None else float(times[first_contact_idx])

    penetration_mask = min_rope_z < penetration_threshold_z
    penetration_frames = np.flatnonzero(penetration_mask)
    penetrates_below_ground = bool(penetration_frames.size)
    min_rope_z_min_m = float(np.nanmin(min_rope_z))
    min_rope_z_minus_ground_m = float(min_rope_z_min_m - ground_z)

    release_idx = summary.get("release_frame")
    if isinstance(release_idx, (int, np.integer)) and 0 <= int(release_idx) < rope_com_xyz.shape[0]:
        release_idx = int(release_idx)
    else:
        release_idx = None
    release_time_s = None if release_idx is None else float(times[release_idx])

    release_before_contact = bool(
        release_idx is not None and first_contact_idx is not None and release_idx < first_contact_idx
    )
    settle_window_frames = max(1, int(np.ceil(float(settle_window_seconds) / max(float(frame_dt), 1.0e-12))))
    settle = None
    settle_ok = False
    if release_idx is not None:
        settle, settle_ok = _settle_window_metrics(
            particle_speed_mean,
            rope_com_horizontal_speed,
            support_patch_speed_mean,
            release_idx=release_idx,
            window_frames=settle_window_frames,
            frame_dt=float(frame_dt),
            particle_speed_threshold_m_s=float(pre_release_particle_speed_mean_max),
            com_horizontal_speed_threshold_m_s=float(pre_release_com_horizontal_speed_max),
            support_patch_speed_threshold_m_s=float(pre_release_support_speed_mean_max),
        )

    impact_speed_m_s = None
    impact_vz_m_s = None
    impact_fit = None
    if first_contact_idx is not None:
        window_end = first_contact_idx
        window_start = max(0, first_contact_idx - max(2, int(impact_window_frames)))
        if release_idx is not None:
            window_start = max(window_start, release_idx)
        if window_end - window_start >= 2:
            impact_fit = _fit_linear_velocity(times[window_start:window_end], rope_com_xyz[window_start:window_end, 2])
            impact_vz_m_s = float(impact_fit["vz_m_s"])
            impact_speed_m_s = float(abs(impact_vz_m_s))

    early_fall_fit = None
    gravity_like = None
    gravity_error_ratio = None
    fit_window = None
    if release_idx is not None and first_contact_idx is not None:
        trimmed = _trimmed_window_indices(
            release_idx,
            first_contact_idx,
            min_frames=fit_min_frames,
            trim_frac=fit_trim_frac,
        )
        if trimmed is not None:
            fit_start, fit_end = trimmed
            fit_window = {
                "start_frame": int(fit_start),
                "end_frame": int(fit_end),
                "start_time_s": float(times[fit_start]),
                "end_time_s": float(times[fit_end]),
                "sample_count": int(fit_end - fit_start + 1),
            }
            early_fall_fit = _fit_quadratic_time_series(
                times[fit_start : fit_end + 1],
                rope_com_xyz[fit_start : fit_end + 1, 2],
            )
            gravity_error_ratio = float(abs(early_fall_fit["az_m_s2"] + float(gravity_mag)) / max(float(gravity_mag), 1.0e-12))
            gravity_like = bool(gravity_error_ratio <= float(gravity_tolerance_ratio))
        else:
            gravity_like = None
    if gravity_like is None and early_fall_fit is not None:
        gravity_error_ratio = float(abs(early_fall_fit["az_m_s2"] + float(gravity_mag)) / max(float(gravity_mag), 1.0e-12))
        gravity_like = bool(gravity_error_ratio <= float(gravity_tolerance_ratio))

    post_release_horizontal_kick_m_s = None
    early_fall_com_horizontal_velocity_m_s = None
    post_release_window = None
    kick_window_frames = max(1, int(np.ceil(float(post_release_kick_window_seconds) / max(float(frame_dt), 1.0e-12))))
    post_release_horizontal_kick_ok = None
    if release_idx is not None:
        kick_end = min(int(rope_com_horizontal_speed.shape[0]), int(release_idx) + int(kick_window_frames))
        kick_slice = rope_com_horizontal_speed[int(release_idx):kick_end]
        if kick_slice.size:
            post_release_horizontal_kick_m_s = float(np.mean(kick_slice))
            early_fall_com_horizontal_velocity_m_s = float(kick_slice[0])
            post_release_horizontal_kick_ok = bool(post_release_horizontal_kick_m_s <= float(post_release_horizontal_kick_max))
            post_release_window = {
                "start_frame": int(release_idx),
                "end_frame": int(kick_end - 1),
                "duration_s": float(kick_slice.size * frame_dt),
                "kick_threshold_m_s": float(post_release_horizontal_kick_max),
            }

    pre_release_spring_energy_proxy = None
    post_release_spring_energy_proxy = None
    if release_idx is not None:
        pre_slice = spring_energy_proxy[max(0, int(release_idx) - int(kick_window_frames)) : int(release_idx)]
        post_slice = spring_energy_proxy[int(release_idx) : min(int(spring_energy_proxy.shape[0]), int(release_idx) + int(kick_window_frames))]
        if pre_slice.size:
            pre_release_spring_energy_proxy = float(np.mean(pre_slice))
        if post_slice.size:
            post_release_spring_energy_proxy = float(np.mean(post_slice))

    post_contact_mask = np.zeros_like(min_rope_z, dtype=bool)
    if first_contact_idx is not None:
        post_contact_mask[first_contact_idx:] = True
    elif release_idx is not None:
        post_contact_mask[release_idx:] = True
    else:
        post_contact_mask[int(0.90 * len(post_contact_mask)) :] = True

    settling_min_z = float(np.mean(min_rope_z[post_contact_mask])) if np.any(post_contact_mask) else None
    settling_min_z_std = float(np.std(min_rope_z[post_contact_mask])) if np.any(post_contact_mask) else None

    contact_phase = summary.get("first_contact_phase")
    task = summary.get("task")
    render_mode = summary.get("render_mode")

    validation = {
        "run_dir": str(run_dir),
        "summary_path": str(summary_path),
        "history_path": str(hist_path),
        "command_path": None if command_path is None else str(command_path),
        "apply_drag": apply_drag,
        "task": task,
        "render_mode": render_mode,
        "frames": int(rope_com_xyz.shape[0]),
        "frame_dt_s": float(frame_dt),
        "gravity_mag_m_s2": float(gravity_mag),
        "ground_z_m": float(ground_z),
        "contact_threshold_z_m": float(contact_threshold_z),
        "penetration_threshold_z_m": float(penetration_threshold_z),
        "series": {
            "time_s": times.tolist(),
            "rope_com_xyz_m": rope_com_xyz.astype(np.float32, copy=False).tolist(),
            "rope_com_z_m": rope_com_xyz[:, 2].astype(np.float32, copy=False).tolist(),
            "rope_com_horizontal_speed_m_s": rope_com_horizontal_speed.astype(np.float32, copy=False).tolist(),
            "rope_com_vertical_speed_m_s": rope_com_vertical_speed.astype(np.float32, copy=False).tolist(),
            "rope_particle_mean_speed_m_s": particle_speed_mean.astype(np.float32, copy=False).tolist(),
            "support_patch_mean_speed_m_s": support_patch_speed_mean.astype(np.float32, copy=False).tolist(),
            "rope_min_z_m": min_rope_z.astype(np.float32, copy=False).tolist(),
            "spring_energy_proxy": spring_energy_proxy.astype(np.float32, copy=False).tolist(),
            "finite_frame_mask": finite_frames.astype(bool).tolist(),
        },
        "release": {
            "frame": release_idx,
            "time_s": release_time_s,
            "before_first_contact": release_before_contact,
            "post_release_horizontal_kick_m_s": post_release_horizontal_kick_m_s,
            "early_fall_com_horizontal_velocity_m_s": early_fall_com_horizontal_velocity_m_s,
            "post_release_horizontal_kick_ok": post_release_horizontal_kick_ok,
            "post_release_window": post_release_window,
        },
        "support_patch": {
            "indices": support_patch_indices.astype(int).tolist(),
            "count": int(support_patch_indices.size),
            "center_m": summary.get("support_patch_center_m"),
            "visible_support_center_m": summary.get("visible_support_center_m"),
        },
        "settle": settle,
        "ground_contact": {
            "first_contact_frame": first_contact_idx,
            "first_contact_time_s": first_contact_time_s,
            "contact_found": bool(first_contact_idx is not None),
            "contact_threshold_z_m": float(contact_threshold_z),
            "penetrates_below_ground": penetrates_below_ground,
            "penetration_frame": None if not penetration_frames.size else int(penetration_frames[0]),
            "min_rope_z_min_m": min_rope_z_min_m,
            "min_rope_z_minus_ground_m": min_rope_z_minus_ground_m,
        },
        "impact": {
            "impact_speed_m_s": impact_speed_m_s,
            "impact_vz_m_s": impact_vz_m_s,
            "fit_window_frames": None
            if impact_fit is None
            else {
                "start_frame": int(max(0, first_contact_idx - max(2, int(impact_window_frames)))) if first_contact_idx is not None else None,
                "end_frame": first_contact_idx,
            },
            "local_velocity_fit": impact_fit,
        },
        "early_fall_fit": {
            "window": fit_window,
            "quadratic_fit": early_fall_fit,
            "gravity_error_ratio": gravity_error_ratio,
            "gravity_like": gravity_like,
            "gravity_tolerance_ratio": float(gravity_tolerance_ratio),
        },
        "settling": {
            "post_contact_min_z_mean_m": settling_min_z,
            "post_contact_min_z_std_m": settling_min_z_std,
        },
        "checks": {
            "finite_trajectory": bool(np.all(finite_frames)),
            "release_before_first_contact": release_before_contact,
            "contact_found": bool(first_contact_idx is not None),
            "gravity_like": gravity_like,
            "penetrates_below_ground": penetrates_below_ground,
            "settle_before_release": bool(settle_ok),
            "post_release_horizontal_kick_ok": post_release_horizontal_kick_ok,
        },
        "source_summary": {
            "first_contact_phase": contact_phase,
            "release_frame": release_idx,
            "release_time_s": release_time_s,
            "first_contact_frame": first_contact_idx,
            "first_contact_time_s": first_contact_time_s,
            "min_clearance_min_m": summary.get("min_clearance_min_m"),
            "rope_com_displacement_m": summary.get("rope_com_displacement_m"),
            "contact_duration_s": summary.get("contact_duration_s"),
            "contact_active_frames": summary.get("contact_active_frames"),
            "summary_settle_gate_pass": summary.get("settle_gate_pass"),
            "summary_settle_gate_metrics": summary.get("settle_gate_metrics"),
            "summary_preroll_settle_pass": summary.get("preroll_settle_pass"),
            "summary_preroll_settle_metrics": summary.get("preroll_settle_metrics"),
            "summary_post_release_horizontal_kick_m_s": summary.get("post_release_horizontal_kick_m_s"),
            "pre_release_spring_energy_proxy": pre_release_spring_energy_proxy,
            "post_release_spring_energy_proxy": post_release_spring_energy_proxy,
        },
    }
    return validation


def _compare_runs(
    primary: dict[str, Any],
    secondary: dict[str, Any],
    gravity_mag: float,
    *,
    gravity_tolerance_ratio: float,
) -> dict[str, Any]:
    t_a = np.asarray(primary["series"]["time_s"], dtype=np.float64)
    t_b = np.asarray(secondary["series"]["time_s"], dtype=np.float64)
    z_a = np.asarray(primary["series"]["rope_com_z_m"], dtype=np.float64)
    z_b = np.asarray(secondary["series"]["rope_com_z_m"], dtype=np.float64)
    min_z_a = np.asarray(primary["series"]["rope_min_z_m"], dtype=np.float64)
    min_z_b = np.asarray(secondary["series"]["rope_min_z_m"], dtype=np.float64)

    rel_a = primary["release"]["time_s"]
    rel_b = secondary["release"]["time_s"]
    contact_a = primary["ground_contact"]["first_contact_time_s"]
    contact_b = secondary["ground_contact"]["first_contact_time_s"]

    overlap_t0 = None
    overlap_t1 = None
    if rel_a is not None and rel_b is not None and contact_a is not None and contact_b is not None:
        overlap_t0 = max(float(rel_a), float(rel_b))
        overlap_t1 = min(float(contact_a), float(contact_b))
    if overlap_t0 is None or overlap_t1 is None or overlap_t1 <= overlap_t0:
        overlap_t0 = 0.0
        overlap_t1 = min(float(t_a[-1]), float(t_b[-1]))
    if overlap_t1 <= overlap_t0:
        return {
            "shared_window": None,
            "gravity_mag_m_s2": float(gravity_mag),
            "early_fall_com_z_rmse_m": None,
            "early_fall_com_z_max_abs_diff_m": None,
            "early_fall_min_z_rmse_m": None,
            "first_contact_time_delta_s": None,
            "impact_speed_delta_m_s": None,
            "impact_speed_ratio": None,
            "gravity_error_ratio_delta": None,
            "settling_min_z_mean_delta_m": None,
            "drag_effect_conclusion": "insufficient_overlap",
        }

    dt = min(
        float(primary["frame_dt_s"]),
        float(secondary["frame_dt_s"]),
        max((overlap_t1 - overlap_t0) / 200.0, 1.0e-6),
    )
    grid = np.arange(overlap_t0, overlap_t1 + 0.5 * dt, dt, dtype=np.float64)
    z_a_i = np.interp(grid, t_a, z_a)
    z_b_i = np.interp(grid, t_b, z_b)
    min_z_a_i = np.interp(grid, t_a, min_z_a)
    min_z_b_i = np.interp(grid, t_b, min_z_b)
    diff_z = z_b_i - z_a_i
    diff_min_z = min_z_b_i - min_z_a_i

    impact_a = primary["impact"]["impact_speed_m_s"]
    impact_b = secondary["impact"]["impact_speed_m_s"]
    gravity_err_a = primary["early_fall_fit"]["gravity_error_ratio"]
    gravity_err_b = secondary["early_fall_fit"]["gravity_error_ratio"]
    settling_a = primary["settling"]["post_contact_min_z_mean_m"]
    settling_b = secondary["settling"]["post_contact_min_z_mean_m"]

    impact_speed_ratio = None
    if impact_a not in (None, 0.0) and impact_b is not None:
        impact_speed_ratio = float(impact_b / max(float(impact_a), 1.0e-12))

    gravity_error_ratio_delta = None
    if gravity_err_a is not None and gravity_err_b is not None:
        gravity_error_ratio_delta = float(gravity_err_b - gravity_err_a)

    settling_delta = None
    if settling_a is not None and settling_b is not None:
        settling_delta = float(settling_b - settling_a)

    drag_effect_conclusion = "minor"
    if gravity_err_a is None or gravity_err_b is None:
        drag_effect_conclusion = "unclear"
    elif gravity_err_a > gravity_tolerance_ratio or gravity_err_b > gravity_tolerance_ratio:
        drag_effect_conclusion = "one_or_both_runs_not_gravity_like"
    elif abs(float(np.mean(diff_z))) > 0.01 or abs(float(np.mean(diff_min_z))) > 0.01:
        drag_effect_conclusion = "material"

    return {
        "shared_window": {
            "start_time_s": float(overlap_t0),
            "end_time_s": float(overlap_t1),
            "sample_count": int(grid.size),
            "sample_dt_s": float(dt),
        },
        "gravity_mag_m_s2": float(gravity_mag),
        "early_fall_com_z_rmse_m": float(math.sqrt(float(np.mean(diff_z * diff_z)))),
        "early_fall_com_z_max_abs_diff_m": float(np.max(np.abs(diff_z))),
        "early_fall_min_z_rmse_m": float(math.sqrt(float(np.mean(diff_min_z * diff_min_z)))),
        "early_fall_min_z_max_abs_diff_m": float(np.max(np.abs(diff_min_z))),
        "first_contact_time_delta_s": None
        if contact_a is None or contact_b is None
        else float(contact_b - contact_a),
        "impact_speed_delta_m_s": None
        if impact_a is None or impact_b is None
        else float(impact_b - impact_a),
        "impact_speed_ratio": impact_speed_ratio,
        "gravity_error_ratio_delta": gravity_error_ratio_delta,
        "settling_min_z_mean_delta_m": settling_delta,
        "drag_effect_conclusion": drag_effect_conclusion,
    }


def _compact_run_snapshot(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_dir": run.get("run_dir"),
        "apply_drag": run.get("apply_drag"),
        "release": run.get("release"),
        "settle": run.get("settle"),
        "support_patch": run.get("support_patch"),
        "ground_contact": run.get("ground_contact"),
        "impact": run.get("impact"),
        "early_fall_fit": run.get("early_fall_fit"),
        "settling": run.get("settling"),
        "checks": run.get("checks"),
    }


def main() -> int:
    args = parse_args()
    primary = _estimate_run_metrics(
        args.run_dir,
        gravity_mag=float(args.gravity_mag),
        gravity_tolerance_ratio=float(args.gravity_tolerance_ratio),
        contact_margin_m=float(args.contact_margin_m),
        penetration_margin_m=float(args.penetration_margin_m),
        fit_min_frames=int(args.fit_min_frames),
        fit_trim_frac=float(args.fit_trim_frac),
        impact_window_frames=int(args.impact_window_frames),
        settle_window_seconds=float(args.settle_window_seconds),
        pre_release_particle_speed_mean_max=float(args.pre_release_particle_speed_mean_max),
        pre_release_com_horizontal_speed_max=float(args.pre_release_com_horizontal_speed_max),
        pre_release_support_speed_mean_max=float(args.pre_release_support_speed_mean_max),
        post_release_kick_window_seconds=float(args.post_release_kick_window_seconds),
        post_release_horizontal_kick_max=float(args.post_release_horizontal_kick_max),
    )

    payload: dict[str, Any] = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gravity_mag_m_s2": float(args.gravity_mag),
        "primary": primary,
    }

    if args.compare_run_dir is not None:
        secondary = _estimate_run_metrics(
            args.compare_run_dir,
            gravity_mag=float(args.gravity_mag),
            gravity_tolerance_ratio=float(args.gravity_tolerance_ratio),
            contact_margin_m=float(args.contact_margin_m),
            penetration_margin_m=float(args.penetration_margin_m),
            fit_min_frames=int(args.fit_min_frames),
            fit_trim_frac=float(args.fit_trim_frac),
            impact_window_frames=int(args.impact_window_frames),
            settle_window_seconds=float(args.settle_window_seconds),
            pre_release_particle_speed_mean_max=float(args.pre_release_particle_speed_mean_max),
            pre_release_com_horizontal_speed_max=float(args.pre_release_com_horizontal_speed_max),
            pre_release_support_speed_mean_max=float(args.pre_release_support_speed_mean_max),
            post_release_kick_window_seconds=float(args.post_release_kick_window_seconds),
            post_release_horizontal_kick_max=float(args.post_release_horizontal_kick_max),
        )
        payload["comparison"] = {
            "primary_run_dir": str(Path(args.run_dir).expanduser().resolve()),
            "compare_run_dir": str(Path(args.compare_run_dir).expanduser().resolve()),
            "primary_apply_drag": primary.get("apply_drag"),
            "compare_apply_drag": secondary.get("apply_drag"),
            "metrics": _compare_runs(
                primary,
                secondary,
                float(args.gravity_mag),
                gravity_tolerance_ratio=float(args.gravity_tolerance_ratio),
            ),
            "primary_snapshot": _compact_run_snapshot(primary),
            "compare_snapshot": _compact_run_snapshot(secondary),
        }
        payload["gravity_like_both_runs"] = bool(
            primary["checks"]["gravity_like"] is True and secondary["checks"]["gravity_like"] is True
        )
    else:
        payload["gravity_like_primary"] = primary["checks"]["gravity_like"]

    output_path = args.output
    if output_path is None:
        output_path = Path(args.run_dir).expanduser().resolve() / "physics_validation.json"
    else:
        output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
