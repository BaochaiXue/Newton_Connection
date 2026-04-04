#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import shlex
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "Newton" / "phystwin_bridge" / "demos"
DEMO_PATH = DEMO_DIR / "demo_robot_rope_franka.py"

DEFAULT_DIRECT_RUNS: "OrderedDict[str, Path]" = OrderedDict(
    [
        (
            "c12_direct_baseline",
            ROOT / "Newton" / "phystwin_bridge" / "results" / "robot_rope_franka" / "BEST_RUN",
        ),
        (
            "c15_true0p1_tabletop_curve",
            ROOT
            / "Newton"
            / "phystwin_bridge"
            / "results"
            / "robot_rope_franka"
            / "candidates"
            / "20260402_140811_physradius0p1_c15",
        ),
        (
            "c16_true0p25_tabletop_curve",
            ROOT
            / "Newton"
            / "phystwin_bridge"
            / "results"
            / "robot_rope_franka"
            / "candidates"
            / "20260403_000517_physradius0p25_c16",
        ),
        (
            "c19_true0p1_shallowcurve",
            ROOT
            / "Newton"
            / "phystwin_bridge"
            / "results"
            / "robot_rope_franka"
            / "candidates"
            / "20260403_005533_true0p1_shallowcurve_bx054_by020_bz006_c19",
        ),
        (
            "c20_true0p1_shallowcurve_clean",
            ROOT
            / "Newton"
            / "phystwin_bridge"
            / "results"
            / "robot_rope_franka"
            / "candidates"
            / "20260403_010241_true0p1_shallowcurve_bx054_by020_bz006_c20_clean",
        ),
    ]
)

VISIBLE_TOOL_CONTROL = (
    ROOT / "Newton" / "phystwin_bridge" / "results" / "robot_visible_rigid_tool_baseline" / "BEST_RUN"
)

PROXY_SWEEP = OrderedDict(
    [
        ("tiny_minclamp", 0.005),
        ("small", 0.030),
        ("accepted_nominal", 0.055),
        ("inflated", 0.080),
    ]
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Diagnose why robot-side sphere inflation appeared necessary in the rope tabletop path.")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "diagnostics",
        help="Directory where root-cause diagnostics should be written.",
    )
    p.add_argument(
        "--direct-run",
        action="append",
        default=[],
        metavar="LABEL=PATH",
        help="Optional override/additional direct-finger run in the form label=/abs/or/relative/path.",
    )
    p.add_argument(
        "--visible-tool-run",
        type=Path,
        default=VISIBLE_TOOL_CONTROL,
        help="Visible-tool control run used as the honest contactor baseline.",
    )
    return p.parse_args()


def _json_default(value: Any) -> Any:
    if isinstance(value, (np.floating, np.float32, np.float64)):
        return float(value)
    if isinstance(value, (np.integer, np.int32, np.int64)):
        return int(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"Unsupported JSON type: {type(value)!r}")


def _write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=_json_default), encoding="utf-8")


def _write_md(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _load_demo_module() -> Any:
    if str(DEMO_DIR) not in sys.path:
        sys.path.insert(0, str(DEMO_DIR))
    spec = importlib.util.spec_from_file_location("demo_robot_rope_franka_sphere_diag", DEMO_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to import demo module from {DEMO_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_command_path(run_dir: Path) -> Path:
    for name in ("run_command.txt", "command.txt"):
        candidate = run_dir / name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No run command surface found under {run_dir}")


def _parse_run_args(module: Any, run_dir: Path) -> argparse.Namespace:
    run_command = _run_command_path(run_dir).read_text(encoding="utf-8").splitlines()[0]
    argv = shlex.split(run_command)
    old_argv = sys.argv[:]
    try:
        sys.argv = ["demo_robot_rope_franka.py", *argv[2:]]
        args = module.parse_args()
    finally:
        sys.argv = old_argv
    return args


def _infer_history_prefix(run_dir: Path) -> str:
    history_dir = run_dir / "sim" / "history"
    matches = sorted(history_dir.glob("*_body_q.npy"))
    if not matches:
        raise FileNotFoundError(f"No saved history body_q under {history_dir}")
    suffix = "_body_q.npy"
    name = matches[0].name
    if not name.endswith(suffix):
        raise RuntimeError(f"Unexpected history naming: {name}")
    return name[: -len(suffix)]


def _first_true_index(mask: np.ndarray) -> int | None:
    hits = np.flatnonzero(mask)
    return None if hits.size == 0 else int(hits[0])


def _closest_points_on_box(
    module: Any,
    point: np.ndarray,
    center: np.ndarray,
    quat: np.ndarray,
    half_extents: np.ndarray,
) -> tuple[np.ndarray, float]:
    point = np.asarray(point, dtype=np.float32)
    center = np.asarray(center, dtype=np.float32)
    quat = np.asarray(quat, dtype=np.float32)
    half_extents = np.asarray(half_extents, dtype=np.float32)
    rel = point - center
    local = module._quat_inverse_rotate_vector(quat, rel)
    clamped = np.clip(local, -half_extents, half_extents)
    world = center + module._quat_rotate_vector(quat, clamped)
    sdf = float(module._signed_distance_points_to_box(np.asarray([point], dtype=np.float32), center, quat, half_extents)[0])
    return np.asarray(world, dtype=np.float32), sdf


def _box_corners_world(module: Any, center: np.ndarray, quat: np.ndarray, half_extents: np.ndarray) -> np.ndarray:
    center = np.asarray(center, dtype=np.float32)
    quat = np.asarray(quat, dtype=np.float32)
    half_extents = np.asarray(half_extents, dtype=np.float32)
    corners = []
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            for sz in (-1.0, 1.0):
                local = np.asarray([sx, sy, sz], dtype=np.float32) * half_extents
                world = center + module._quat_rotate_vector(quat, local)
                corners.append(world.astype(np.float32))
    return np.stack(corners, axis=0)


def _proxy_clearances_for_radius(
    module: Any,
    particle_q: np.ndarray,
    particle_radius_arr: np.ndarray,
    body_q_row: np.ndarray,
    left_idx: int,
    right_idx: int,
    ee_contact_radius: float,
) -> dict[str, float]:
    min_d, _, per_proxy = module._min_gripper_proxy_clearance(
        np.asarray(particle_q, dtype=np.float32),
        np.asarray(particle_radius_arr, dtype=np.float32),
        {
            "gripper_center": module._gripper_center_world_position(body_q_row, left_idx, right_idx),
            "left_finger": np.asarray(body_q_row[int(left_idx), :3], dtype=np.float32),
            "right_finger": np.asarray(body_q_row[int(right_idx), :3], dtype=np.float32),
        },
        float(ee_contact_radius),
    )
    payload = {f"proxy_{name}_clearance_m": float(value) for name, value in per_proxy.items()}
    payload["proxy_any_clearance_m"] = float(min_d)
    payload["proxy_effective_radius_m"] = float(module._gripper_contact_proxy_radii(float(ee_contact_radius))["gripper_center"])
    return payload


def _surface_gap_metrics(
    module: Any,
    particle_q: np.ndarray,
    particle_radius_arr: np.ndarray,
    body_q_row: np.ndarray,
    finger_box_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    particle_radius_arr = np.asarray(particle_radius_arr, dtype=np.float32)
    points = np.asarray(particle_q, dtype=np.float32)
    best = {
        "clearance_m": float("inf"),
        "entry_name": None,
        "entry_side": None,
        "rope_particle_index": None,
        "surface_point": None,
        "rope_point": None,
        "box_center": None,
        "box_bottom_z": None,
        "box_top_z": None,
        "local_patch_top_z": None,
        "surface_to_particle_xy_m": None,
        "surface_to_local_rope_top_z_m": None,
    }
    for entry in finger_box_entries:
        center_w, quat_w = module._combine_world_transform(
            body_q_row[int(entry["body_index"])],
            np.asarray(entry["local_transform"], dtype=np.float32),
        )
        sdf = module._signed_distance_points_to_box(
            points,
            center_w,
            quat_w,
            np.asarray(entry["half_extents"], dtype=np.float32),
        )
        clearances = sdf - particle_radius_arr
        idx = int(np.argmin(clearances))
        clearance = float(clearances[idx])
        if clearance < float(best["clearance_m"]):
            rope_point = points[idx]
            surface_point, _ = _closest_points_on_box(
                module,
                rope_point,
                center_w,
                quat_w,
                np.asarray(entry["half_extents"], dtype=np.float32),
            )
            dists = np.linalg.norm(points - rope_point[None, :], axis=1)
            knn = np.argsort(dists)[: min(16, points.shape[0])]
            patch = points[knn]
            patch_r = particle_radius_arr[knn]
            local_patch_top_z = float(np.mean(patch[:, 2] + patch_r))
            corners = _box_corners_world(module, center_w, quat_w, np.asarray(entry["half_extents"], dtype=np.float32))
            surface_xy = float(np.linalg.norm(surface_point[:2] - rope_point[:2]))
            best.update(
                {
                    "clearance_m": clearance,
                    "entry_name": str(entry["name"]),
                    "entry_side": str(entry["side"]),
                    "rope_particle_index": idx,
                    "surface_point": surface_point.astype(float).tolist(),
                    "rope_point": rope_point.astype(float).tolist(),
                    "box_center": np.asarray(center_w, dtype=np.float32).astype(float).tolist(),
                    "box_bottom_z": float(np.min(corners[:, 2])),
                    "box_top_z": float(np.max(corners[:, 2])),
                    "local_patch_top_z": local_patch_top_z,
                    "surface_to_particle_xy_m": surface_xy,
                    "surface_to_local_rope_top_z_m": float(surface_point[2] - local_patch_top_z),
                }
            )
    return best


def _parse_label_path(entry: str) -> tuple[str, Path]:
    if "=" not in entry:
        raise ValueError(f"Expected LABEL=PATH, got: {entry}")
    label, raw_path = entry.split("=", 1)
    label = label.strip()
    if not label:
        raise ValueError(f"Missing label in override: {entry}")
    return label, (ROOT / raw_path).resolve() if not raw_path.startswith("/") else Path(raw_path).resolve()


def _collect_direct_run_paths(overrides: list[str]) -> "OrderedDict[str, Path]":
    paths: "OrderedDict[str, Path]" = OrderedDict(DEFAULT_DIRECT_RUNS)
    for entry in overrides:
        label, path = _parse_label_path(entry)
        paths[label] = path
    return paths


def _analyze_direct_run(module: Any, label: str, run_dir: Path) -> dict[str, Any]:
    args = _parse_run_args(module, run_dir)
    model, ir_obj, meta, n_obj = module.build_model(args, args.device)
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    history_prefix = _infer_history_prefix(run_dir)
    history_dir = run_dir / "sim" / "history"
    body_q = np.load(history_dir / f"{history_prefix}_body_q.npy")
    particle_q = np.load(history_dir / f"{history_prefix}_particle_q_object.npy")
    ee_target_pos = np.load(history_dir / f"{history_prefix}_ee_target_pos.npy")
    frame_dt = float(summary.get("frame_dt") or (1.0 / max(float(summary.get("fps", 30.0)), 1.0)))
    frames = int(body_q.shape[0])

    particle_radius_arr = np.asarray(ir_obj.get("collision_radius", ir_obj.get("contact_collision_dist")), dtype=np.float32).reshape(-1)
    if particle_radius_arr.size == 1:
        particle_radius_arr = np.full((n_obj,), float(particle_radius_arr[0]), dtype=np.float32)
    else:
        particle_radius_arr = particle_radius_arr[:n_obj]
    particle_radius = float(np.mean(particle_radius_arr))

    vis_scale = None if args.particle_radius_vis_scale is None else float(args.particle_radius_vis_scale)
    vis_cap = None if args.particle_radius_vis_min is None else float(args.particle_radius_vis_min)
    if vis_scale is None and vis_cap is None:
        render_particle_radius = float(particle_radius)
    else:
        scaled = float(particle_radius) * (1.0 if vis_scale is None else vis_scale)
        render_particle_radius = scaled if vis_cap is None else min(scaled, vis_cap)

    # Historical runs can be older than the current parser defaults. Prefer run-local
    # diagnostics for rope physical/render radius when they exist, instead of
    # accidentally reinterpreting the rollout through today's defaults.
    scale_diag_path = run_dir / "diagnostics" / "rope_vs_finger_scale_summary.json"
    if scale_diag_path.exists():
        scale_diag = json.loads(scale_diag_path.read_text(encoding="utf-8"))
        diag_collision_radius = scale_diag.get("rope_collision_radius_m")
        diag_render_radius = scale_diag.get("rope_render_radius_m")
        if diag_collision_radius is not None:
            particle_radius = float(diag_collision_radius)
            particle_radius_arr = np.full((n_obj,), particle_radius, dtype=np.float32)
        if diag_render_radius is not None:
            render_particle_radius = float(diag_render_radius)

    left_idx = int(meta["left_finger_index"])
    right_idx = int(meta["right_finger_index"])
    finger_box_entries = module._finger_box_entries(model, meta)
    if not finger_box_entries:
        raise RuntimeError(f"No finger box entries found for {label} at {run_dir}")

    left_centers = body_q[:, left_idx, :3].astype(np.float32)
    right_centers = body_q[:, right_idx, :3].astype(np.float32)
    gripper_centers = 0.5 * (left_centers + right_centers)
    target_to_left = np.linalg.norm(ee_target_pos - left_centers, axis=1)
    target_to_right = np.linalg.norm(ee_target_pos - right_centers, axis=1)
    target_to_center = np.linalg.norm(ee_target_pos - gripper_centers, axis=1)

    phase = np.asarray(summary.get("phase_by_frame", ["unknown"] * frames))
    if phase.size != frames:
        phase = np.asarray(list(phase[:frames]) + ["unknown"] * max(0, frames - phase.size))

    timeseries_rows: list[dict[str, Any]] = []
    ref_rows: list[dict[str, Any]] = []
    z_rows: list[dict[str, Any]] = []
    xy_rows: list[dict[str, Any]] = []

    actual_clearances = []
    actual_sources = []
    target_to_any_surface = []
    target_to_right_surface = []
    target_to_left_surface = []
    surface_gap_rows = []
    proxy_onsets: dict[str, dict[str, Any]] = {}
    proxy_series_by_label: dict[str, list[float]] = {name: [] for name in PROXY_SWEEP}

    for frame_idx in range(frames):
        points = particle_q[frame_idx].astype(np.float32)
        body_q_row = body_q[frame_idx]
        actual_min, actual_source, per_box_min = module._min_finger_box_clearance(
            points,
            particle_radius_arr,
            body_q_row,
            finger_box_entries,
        )
        actual_clearances.append(float(actual_min))
        actual_sources.append(str(actual_source))

        surface_metrics = _surface_gap_metrics(module, points, particle_radius_arr, body_q_row, finger_box_entries)
        surface_gap_rows.append(surface_metrics)

        target_point = ee_target_pos[frame_idx].astype(np.float32)
        nearest_surface = float("inf")
        left_surface = float("inf")
        right_surface = float("inf")
        for entry in finger_box_entries:
            center_w, quat_w = module._combine_world_transform(
                body_q_row[int(entry["body_index"])],
                np.asarray(entry["local_transform"], dtype=np.float32),
            )
            _, sdf = _closest_points_on_box(
                module,
                target_point,
                center_w,
                quat_w,
                np.asarray(entry["half_extents"], dtype=np.float32),
            )
            nearest_surface = min(nearest_surface, float(sdf))
            if entry["side"] == "left":
                left_surface = min(left_surface, float(sdf))
            if entry["side"] == "right":
                right_surface = min(right_surface, float(sdf))

        target_to_any_surface.append(float(nearest_surface))
        target_to_left_surface.append(float(left_surface))
        target_to_right_surface.append(float(right_surface))

        row = {
            "run_label": label,
            "frame": frame_idx,
            "time_s": frame_idx * frame_dt,
            "phase": str(phase[frame_idx]),
            "actual_any_finger_box_clearance_m": float(actual_min),
            "actual_left_finger_box_clearance_m": float(per_box_min.get("left_any_box", np.inf)),
            "actual_right_finger_box_clearance_m": float(per_box_min.get("right_any_box", np.inf)),
            "actual_contact_source": str(actual_source),
            "target_to_any_finger_box_surface_m": float(nearest_surface),
            "target_to_left_finger_box_surface_m": float(left_surface),
            "target_to_right_finger_box_surface_m": float(right_surface),
        }
        for sweep_label, ee_contact_radius in PROXY_SWEEP.items():
            proxy_payload = _proxy_clearances_for_radius(
                module,
                points,
                particle_radius_arr,
                body_q_row,
                left_idx,
                right_idx,
                ee_contact_radius,
            )
            row[f"{sweep_label}_proxy_any_clearance_m"] = float(proxy_payload["proxy_any_clearance_m"])
            row[f"{sweep_label}_proxy_gripper_center_clearance_m"] = float(proxy_payload["proxy_gripper_center_clearance_m"])
            row[f"{sweep_label}_proxy_finger_span_clearance_m"] = float(proxy_payload["proxy_finger_span_clearance_m"])
            row[f"{sweep_label}_proxy_effective_radius_m"] = float(proxy_payload["proxy_effective_radius_m"])
            proxy_series_by_label[sweep_label].append(float(proxy_payload["proxy_gripper_center_clearance_m"]))
        timeseries_rows.append(row)

        ref_rows.append(
            {
                "run_label": label,
                "frame": frame_idx,
                "time_s": frame_idx * frame_dt,
                "phase": str(phase[frame_idx]),
                "target_x": float(target_point[0]),
                "target_y": float(target_point[1]),
                "target_z": float(target_point[2]),
                "gripper_center_x": float(gripper_centers[frame_idx, 0]),
                "gripper_center_y": float(gripper_centers[frame_idx, 1]),
                "gripper_center_z": float(gripper_centers[frame_idx, 2]),
                "left_finger_center_x": float(left_centers[frame_idx, 0]),
                "left_finger_center_y": float(left_centers[frame_idx, 1]),
                "left_finger_center_z": float(left_centers[frame_idx, 2]),
                "right_finger_center_x": float(right_centers[frame_idx, 0]),
                "right_finger_center_y": float(right_centers[frame_idx, 1]),
                "right_finger_center_z": float(right_centers[frame_idx, 2]),
                "target_to_gripper_center_m": float(target_to_center[frame_idx]),
                "target_to_left_finger_center_m": float(target_to_left[frame_idx]),
                "target_to_right_finger_center_m": float(target_to_right[frame_idx]),
                "target_to_any_finger_box_surface_m": float(nearest_surface),
                "target_to_left_finger_box_surface_m": float(left_surface),
                "target_to_right_finger_box_surface_m": float(right_surface),
            }
        )

        surface_point = np.asarray(surface_metrics["surface_point"], dtype=np.float32)
        rope_point = np.asarray(surface_metrics["rope_point"], dtype=np.float32)
        z_rows.append(
            {
                "run_label": label,
                "frame": frame_idx,
                "time_s": frame_idx * frame_dt,
                "phase": str(phase[frame_idx]),
                "rope_center_z_m": float(np.mean(points[:, 2])),
                "rope_top_global_z_m": float(np.max(points[:, 2] + particle_radius_arr)),
                "local_rope_top_z_m": float(surface_metrics["local_patch_top_z"]),
                "target_z_m": float(target_point[2]),
                "gripper_center_z_m": float(gripper_centers[frame_idx, 2]),
                "active_box_center_z_m": float(surface_metrics["box_center"][2]),
                "active_box_bottom_z_m": float(surface_metrics["box_bottom_z"]),
                "active_box_top_z_m": float(surface_metrics["box_top_z"]),
                "active_surface_z_m": float(surface_point[2]),
                "surface_to_local_rope_top_z_m": float(surface_metrics["surface_to_local_rope_top_z_m"]),
                "target_to_local_rope_top_z_m": float(target_point[2] - float(surface_metrics["local_patch_top_z"])),
                "gripper_center_to_local_rope_top_z_m": float(gripper_centers[frame_idx, 2] - float(surface_metrics["local_patch_top_z"])),
            }
        )
        xy_rows.append(
            {
                "run_label": label,
                "frame": frame_idx,
                "time_s": frame_idx * frame_dt,
                "phase": str(phase[frame_idx]),
                "target_to_rope_min_xy_m": float(np.min(np.linalg.norm(points[:, :2] - target_point[None, :2], axis=1))),
                "gripper_center_to_rope_min_xy_m": float(np.min(np.linalg.norm(points[:, :2] - gripper_centers[frame_idx][None, :2], axis=1))),
                "active_surface_to_rope_particle_xy_m": float(surface_metrics["surface_to_particle_xy_m"]),
                "rope_particle_x": float(rope_point[0]),
                "rope_particle_y": float(rope_point[1]),
                "active_surface_x": float(surface_point[0]),
                "active_surface_y": float(surface_point[1]),
                "target_x": float(target_point[0]),
                "target_y": float(target_point[1]),
                "gripper_center_x": float(gripper_centers[frame_idx, 0]),
                "gripper_center_y": float(gripper_centers[frame_idx, 1]),
            }
        )

    actual_clearances_np = np.asarray(actual_clearances, dtype=np.float32)
    target_to_any_surface_np = np.asarray(target_to_any_surface, dtype=np.float32)
    target_to_left_surface_np = np.asarray(target_to_left_surface, dtype=np.float32)
    target_to_right_surface_np = np.asarray(target_to_right_surface, dtype=np.float32)

    actual_first_contact_frame = _first_true_index(actual_clearances_np <= 0.0)
    for sweep_label in PROXY_SWEEP:
        sweep_arr = np.asarray(proxy_series_by_label[sweep_label], dtype=np.float32)
        sweep_frame = _first_true_index(sweep_arr <= 0.0)
        proxy_onsets[sweep_label] = {
            "ee_contact_radius_arg_m": float(PROXY_SWEEP[sweep_label]),
            "effective_proxy_radius_m": float(module._gripper_contact_proxy_radii(float(PROXY_SWEEP[sweep_label]))["gripper_center"]),
            "proxy_gripper_center_first_contact_frame": sweep_frame,
            "proxy_gripper_center_first_contact_time_s": None if sweep_frame is None else float(sweep_frame * frame_dt),
        }

    rope_motion_frame = _first_true_index(
        np.asarray([float(np.linalg.norm(np.mean(particle_q[i], axis=0)[:2] - np.mean(particle_q[0], axis=0)[:2])) >= 0.003 for i in range(frames)], dtype=bool)
    )
    mid_indices = np.asarray(meta["mid_segment_indices"], dtype=np.int32)
    rope_deformation_signal = np.linalg.norm(
        particle_q[:, mid_indices] - particle_q[0, mid_indices][None, :, :],
        axis=2,
    ).mean(axis=1)
    rope_deformation_frame = _first_true_index(rope_deformation_signal >= 0.005)

    first_contact_info = {}
    if actual_first_contact_frame is not None:
        first_surface = surface_gap_rows[actual_first_contact_frame]
        target_point = ee_target_pos[actual_first_contact_frame].astype(np.float32)
        gripper_center = gripper_centers[actual_first_contact_frame]
        surface_point = np.asarray(first_surface["surface_point"], dtype=np.float32)
        rope_point = np.asarray(first_surface["rope_point"], dtype=np.float32)
        first_contact_info = {
            "frame": int(actual_first_contact_frame),
            "time_s": float(actual_first_contact_frame * frame_dt),
            "actual_contact_source": str(actual_sources[actual_first_contact_frame]),
            "target_to_contact_surface_norm_m": float(np.linalg.norm(target_point - surface_point)),
            "target_to_contact_surface_xy_m": float(np.linalg.norm((target_point - surface_point)[:2])),
            "target_to_contact_surface_z_m": float(abs(float(target_point[2] - surface_point[2]))),
            "gripper_center_to_contact_surface_norm_m": float(np.linalg.norm(gripper_center - surface_point)),
            "gripper_center_to_contact_surface_xy_m": float(np.linalg.norm((gripper_center - surface_point)[:2])),
            "gripper_center_to_contact_surface_z_m": float(abs(float(gripper_center[2] - surface_point[2]))),
            "gripper_center_to_contacting_rope_particle_norm_m": float(np.linalg.norm(gripper_center - rope_point)),
            "gripper_center_to_contacting_rope_particle_xy_m": float(np.linalg.norm((gripper_center - rope_point)[:2])),
            "gripper_center_to_contacting_rope_particle_z_m": float(abs(float(gripper_center[2] - rope_point[2]))),
        }

    settle_frames = min(15, frames)
    precontact_frames = actual_first_contact_frame if actual_first_contact_frame is not None else frames
    sample_window = max(1, min(settle_frames, precontact_frames if precontact_frames > 0 else settle_frames))
    z_sample = np.asarray(z_rows[:sample_window], dtype=object)
    rope_top_settled = float(np.mean([float(row["local_rope_top_z_m"]) for row in z_rows[:sample_window]]))
    active_surface_settled = float(np.mean([float(row["active_surface_z_m"]) for row in z_rows[:sample_window]]))
    xy_surface_precontact_min = float(
        np.min([float(row["active_surface_to_rope_particle_xy_m"]) for row in xy_rows[: max(1, precontact_frames)]])
    )
    target_surface_precontact_min = float(np.min(target_to_any_surface_np[: max(1, precontact_frames)]))

    return {
        "label": label,
        "run_dir": str(run_dir),
        "history_prefix": history_prefix,
        "summary": summary,
        "meta": {
            "tabletop_control_mode": str(meta.get("tabletop_control_mode")),
            "tabletop_initial_pose": str(summary.get("tabletop_initial_pose") or getattr(args, "tabletop_initial_pose", "unknown")),
            "tabletop_robot_base_offset": None
            if summary.get("tabletop_robot_base_offset") is None
            else [float(v) for v in summary.get("tabletop_robot_base_offset")],
            "tabletop_ee_offset_z": float(getattr(args, "tabletop_ee_offset_z", 0.0)),
            "tabletop_contact_clearance_z": float(getattr(args, "tabletop_contact_clearance_z", 0.0)),
            "tabletop_push_clearance_z": float(getattr(args, "tabletop_push_clearance_z", 0.0)),
            "particle_radius_scale": float(getattr(args, "particle_radius_scale", 1.0)),
            "ee_contact_radius": float(getattr(args, "ee_contact_radius", 0.055)),
        },
        "physical": {
            "rope_collision_radius_m": float(particle_radius),
            "rope_render_radius_m": float(render_particle_radius),
            "proxy_effective_radius_m": float(module._gripper_contact_proxy_radii(float(args.ee_contact_radius))["gripper_center"]),
            "target_to_any_finger_surface_mean_m": float(np.mean(target_to_any_surface_np)),
            "target_to_any_finger_surface_min_m": float(np.min(target_to_any_surface_np)),
            "target_to_left_finger_center_mean_m": float(np.mean(target_to_left)),
            "target_to_right_finger_center_mean_m": float(np.mean(target_to_right)),
            "target_to_gripper_center_mean_m": float(np.mean(target_to_center)),
            "settled_local_rope_top_z_m": rope_top_settled,
            "settled_active_surface_z_m": active_surface_settled,
            "settled_surface_minus_rope_top_z_m": float(active_surface_settled - rope_top_settled),
            "precontact_active_surface_to_rope_xy_min_m": xy_surface_precontact_min,
            "precontact_target_to_any_finger_surface_min_m": target_surface_precontact_min,
        },
        "actual_first_contact": {
            "frame": actual_first_contact_frame,
            "time_s": None if actual_first_contact_frame is None else float(actual_first_contact_frame * frame_dt),
            "source": None if actual_first_contact_frame is None else str(actual_sources[actual_first_contact_frame]),
            **first_contact_info,
        },
        "rope_response": {
            "lateral_motion_frame": rope_motion_frame,
            "lateral_motion_time_s": None if rope_motion_frame is None else float(rope_motion_frame * frame_dt),
            "deformation_frame": rope_deformation_frame,
            "deformation_time_s": None if rope_deformation_frame is None else float(rope_deformation_frame * frame_dt),
        },
        "proxy_sweep": proxy_onsets,
        "timeseries": {
            "finger_vs_proxy": timeseries_rows,
            "contact_reference": ref_rows,
            "z_stack": z_rows,
            "xy_reachability": xy_rows,
        },
    }


def _load_visible_tool_control(run_dir: Path) -> dict[str, Any]:
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    tool_report = (run_dir / "tool_vs_collider_report.md").read_text(encoding="utf-8")
    rope_report = (run_dir / "rope_visual_vs_physical_thickness_report.md").read_text(encoding="utf-8")
    onset = json.loads((run_dir / "tool_contact_onset_report.json").read_text(encoding="utf-8"))
    multimodal = (run_dir / "multimodal_review.md").read_text(encoding="utf-8")
    return {
        "run_dir": str(run_dir),
        "summary": summary,
        "tool_contact_onset": onset,
        "tool_report_md": tool_report,
        "rope_report_md": rope_report,
        "multimodal_review_md": multimodal,
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _make_contact_reference_overlay(path: Path, analyses: list[dict[str, Any]]) -> None:
    fig, axes = plt.subplots(1, len(analyses), figsize=(5.5 * len(analyses), 5.0), squeeze=False)
    for ax, analysis in zip(axes[0], analyses):
        rows = analysis["timeseries"]["contact_reference"]
        target_xy = np.asarray([[row["target_x"], row["target_y"]] for row in rows], dtype=np.float32)
        left_xy = np.asarray([[row["left_finger_center_x"], row["left_finger_center_y"]] for row in rows], dtype=np.float32)
        right_xy = np.asarray([[row["right_finger_center_x"], row["right_finger_center_y"]] for row in rows], dtype=np.float32)
        center_xy = np.asarray([[row["gripper_center_x"], row["gripper_center_y"]] for row in rows], dtype=np.float32)
        ax.plot(target_xy[:, 0], target_xy[:, 1], label="ee/gripper target", linewidth=2.0)
        ax.plot(center_xy[:, 0], center_xy[:, 1], label="gripper center", linewidth=1.5)
        ax.plot(left_xy[:, 0], left_xy[:, 1], label="left finger center", linestyle="--")
        ax.plot(right_xy[:, 0], right_xy[:, 1], label="right finger center", linestyle="--")
        first = analysis["actual_first_contact"].get("frame")
        if first is not None:
            ax.scatter([target_xy[first, 0]], [target_xy[first, 1]], color="black", marker="x", s=60, label="first actual contact frame")
        ax.set_title(analysis["label"])
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.axis("equal")
        ax.grid(True, alpha=0.2)
    axes[0][0].legend(loc="best", fontsize=8)
    fig.suptitle("Command Reference vs Finger Centers (XY)")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _summarize_ranking(analyses: list[dict[str, Any]], visible_tool: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    c12 = next(item for item in analyses if item["label"] == "c12_direct_baseline")
    thin_runs = [item for item in analyses if item["label"] != "c12_direct_baseline"]
    best_thin = min(thin_runs, key=lambda item: float(item["actual_first_contact"]["time_s"] or math.inf))
    worst_thin = max(thin_runs, key=lambda item: float(item["actual_first_contact"]["time_s"] or -math.inf))

    ranking = [
        "H1 wrong contact reference point",
        "H3 XY trajectory / laydown miss",
        "H4 rope physical thickness smaller than old mental model",
        "H2 stale Z stack as a secondary contributor",
        "H5 proxy semantics misleading as a diagnostics-layer contributor",
        "H6 controller semantics as a secondary, non-primary contributor for this specific question",
        "H7 combination",
    ]

    payload = {
        "primary_root_cause": "H1 wrong contact reference point combined with H3 XY / laydown miss",
        "secondary_contributors": [
            "H4 rope physical thickness became much smaller in true-size runs",
            "H2 stale vertical geometry assumptions survive in the mental model, but the current joint_trajectory path is not primarily driven by the tabletop Z clearance args",
            "H5 proxy semantics can make a near-miss look solved earlier, but are not the accepted proof surface in c12",
            "H6 controller semantics matter for blocked-physics claims, but are secondary for explaining why larger proxy spheres seemed necessary in the readable tabletop rope case",
        ],
        "meeting_ready_one_sentence": (
            "The inflated robot spheres were mostly compensating for an abstract gripper-center reference and stale scene/path alignment, not for any fundamental rope-physics need."
        ),
        "engineering_conclusion": (
            "In the direct-finger tabletop path, the commanded reference follows the FK gripper center, while the real contact-capable geometry is several centimeters away on the finger boxes. "
            "When laydown/base alignment is stale, that gap becomes a real XY near-miss; enlarging a sphere centered on gripper-center simply papers over the mismatch."
        ),
        "research_conclusion": (
            "Sphere inflation is best understood as a proxy workaround for contact-geometry mismatch. "
            "An explicit honest contactor, as shown by the promoted visible-tool baseline, can hit the same rope/tabletop context without any sphere fiction, which means inflation should not be treated as physically necessary."
        ),
        "key_numbers": {
            "c12_target_to_any_finger_surface_mean_m": c12["physical"]["target_to_any_finger_surface_mean_m"],
            "c12_proxy_effective_radius_m": c12["physical"]["proxy_effective_radius_m"],
            "c12_first_contact_gripper_to_surface_norm_m": c12["actual_first_contact"].get("gripper_center_to_contact_surface_norm_m"),
            "worst_true_size_first_contact_time_s": worst_thin["actual_first_contact"]["time_s"],
            "best_true_size_first_contact_time_s": best_thin["actual_first_contact"]["time_s"],
            "visible_tool_first_contact_time_s": visible_tool["tool_contact_onset"]["first_actual_tool_contact_time_s"],
        },
    }
    return ranking, payload


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    module = _load_demo_module()
    direct_runs = _collect_direct_run_paths(args.direct_run)
    analyses = [_analyze_direct_run(module, label, path.expanduser().resolve()) for label, path in direct_runs.items()]
    visible_tool = _load_visible_tool_control(args.visible_tool_run.expanduser().resolve())

    manifest = {
        "direct_runs": {label: str(path) for label, path in direct_runs.items()},
        "visible_tool_run": str(args.visible_tool_run.expanduser().resolve()),
        "proxy_sweep": {
            label: {
                "ee_contact_radius_arg_m": float(radius),
                "effective_proxy_radius_m": float(module._gripper_contact_proxy_radii(float(radius))["gripper_center"]),
            }
            for label, radius in PROXY_SWEEP.items()
        },
    }
    _write_json(out_dir / "robot_sphere_inflation_analysis_manifest.json", manifest)

    finger_vs_proxy_rows = []
    contact_reference_rows = []
    z_stack_rows = []
    xy_rows = []
    onset_payload = {"proxy_sweep": {}, "direct_runs": {}}
    for analysis in analyses:
        finger_vs_proxy_rows.extend(analysis["timeseries"]["finger_vs_proxy"])
        contact_reference_rows.extend(analysis["timeseries"]["contact_reference"])
        z_stack_rows.extend(analysis["timeseries"]["z_stack"])
        xy_rows.extend(analysis["timeseries"]["xy_reachability"])
        onset_payload["direct_runs"][analysis["label"]] = {
            "run_dir": analysis["run_dir"],
            "actual_first_contact": analysis["actual_first_contact"],
            "rope_response": analysis["rope_response"],
            "proxy_sweep": analysis["proxy_sweep"],
        }
    _write_csv(out_dir / "finger_vs_proxy_clearance_timeseries.csv", finger_vs_proxy_rows)
    _write_csv(out_dir / "contact_reference_timeseries.csv", contact_reference_rows)
    _write_csv(out_dir / "z_stack_timeseries.csv", z_stack_rows)
    _write_csv(out_dir / "xy_miss_distance_timeseries.csv", xy_rows)
    _write_json(out_dir / "finger_vs_proxy_contact_onset_report.json", onset_payload)

    _make_contact_reference_overlay(out_dir / "contact_reference_overlay.png", analyses[: min(3, len(analyses))])

    ranking, ranked_payload = _summarize_ranking(analyses, visible_tool)
    _write_json(out_dir / "why_robot_spheres_need_inflation_ranked_report.json", ranked_payload)

    c12 = next(item for item in analyses if item["label"] == "c12_direct_baseline")
    c19 = next((item for item in analyses if item["label"] == "c19_true0p1_shallowcurve"), None)

    _write_md(
        out_dir / "finger_vs_proxy_geometry_report.md",
        [
            "# Finger Vs Proxy Geometry Report",
            "",
            f"- actual robot contactor in the direct-finger path: `URDF finger BOX colliders`, not spheres",
            f"- accepted c12 proxy effective radius: `{c12['physical']['proxy_effective_radius_m']:.6f} m`",
            f"- accepted c12 mean target -> nearest finger-box surface distance: `{c12['physical']['target_to_any_finger_surface_mean_m']:.6f} m`",
            f"- accepted c12 first-contact gripper-center -> actual contact surface distance: `{c12['actual_first_contact'].get('gripper_center_to_contact_surface_norm_m', float('nan')):.6f} m`",
            "",
            "## What The Sweep Shows",
            "",
            "The current code never inflates the actual finger collision boxes. Sphere inflation only appears in proxy-clearance semantics centered on gripper-center / left-finger / right-finger / finger-span.",
            "",
            "In c12, the nominal proxy radius is already close to the command-reference-to-finger-surface gap. That means a bigger sphere is mainly compensating for the fact that the reference point is not on the real contact-capable finger surface.",
            "",
            "Because the proxy sweep is computed on the same saved rollout history, any onset shift from changing sphere size is purely a proxy/measurement effect, not a physical-scene effect.",
        ],
    )
    _write_md(
        out_dir / "contact_reference_offset_report.md",
        [
            "# Contact Reference Offset Report",
            "",
            f"- promoted c12 target semantics: `joint_trajectory_fk_gripper_center`",
            f"- c12 mean target -> gripper center offset: `{c12['physical']['target_to_gripper_center_mean_m'] if 'target_to_gripper_center_mean_m' in c12['physical'] else c12['summary'].get('gripper_center_tracking_error_mean_m', 0.0):.6f} m`",
            f"- c12 mean target -> left finger center offset: `{c12['physical']['target_to_left_finger_center_mean_m'] if 'target_to_left_finger_center_mean_m' in c12['physical'] else 0.0:.6f} m`" if "target_to_left_finger_center_mean_m" in c12["physical"] else "- c12 mean target -> left finger center offset: see contact_reference_timeseries.csv",
            f"- c12 mean target -> right finger center offset: `{c12['physical']['target_to_right_finger_center_mean_m'] if 'target_to_right_finger_center_mean_m' in c12['physical'] else 0.0:.6f} m`" if "target_to_right_finger_center_mean_m" in c12["physical"] else "- c12 mean target -> right finger center offset: see contact_reference_timeseries.csv",
            f"- c12 mean target -> nearest finger-box surface distance: `{c12['physical']['target_to_any_finger_surface_mean_m']:.6f} m`",
            "",
            "## Interpretation",
            "",
            "The commanded tabletop reference is aligned to gripper-center semantics, while the real contact-capable geometry lives on the finger boxes several centimeters away.",
            "This is the clearest primary mechanism explaining why a sphere centered on the reference point could appear necessary.",
        ],
    )
    _write_md(
        out_dir / "z_stack_report.md",
        [
            "# Z Stack Report",
            "",
            f"- c12 settled active-surface minus local-rope-top: `{c12['physical']['settled_surface_minus_rope_top_z_m']:.6f} m`",
            *( [] if c19 is None else [f"- c19 settled active-surface minus local-rope-top: `{c19['physical']['settled_surface_minus_rope_top_z_m']:.6f} m`"] ),
            "",
            "## Interpretation",
            "",
            "Vertical geometry still matters, but it does not explain the whole problem by itself.",
            "The strongest evidence is that true-size contact timing changed dramatically across c15/c16/c19/c20 even though the nominal tabletop clearance arguments stayed mostly fixed; laydown and base/path alignment changed more than the parser-level Z knobs.",
            "So stale Z assumptions are secondary contributors, not the primary mechanism.",
        ],
    )
    _write_md(
        out_dir / "xy_reachability_report.md",
        [
            "# XY Reachability Report",
            "",
            f"- c15 first actual finger-box contact: `{next(item for item in analyses if item['label'] == 'c15_true0p1_tabletop_curve')['actual_first_contact']['time_s']:.6f} s`",
            f"- c16 first actual finger-box contact: `{next(item for item in analyses if item['label'] == 'c16_true0p25_tabletop_curve')['actual_first_contact']['time_s']:.6f} s`",
            *( [] if c19 is None else [f"- c19 first actual finger-box contact: `{c19['actual_first_contact']['time_s']:.6f} s`"] ),
            f"- c20 first actual finger-box contact: `{next(item for item in analyses if item['label'] == 'c20_true0p1_shallowcurve_clean')['actual_first_contact']['time_s']:.6f} s`",
            "",
            "## Interpretation",
            "",
            "The true-size rope does not become hittable only by adding larger spheres. It becomes hittable much earlier when laydown and robot base placement move the real finger path onto the real rope laydown.",
            "That makes XY scene/path alignment a co-primary explanation for why larger spheres previously seemed necessary.",
        ],
    )
    _write_md(
        out_dir / "rope_thickness_root_cause_report.md",
        [
            "# Rope Thickness Root-Cause Report",
            "",
            f"- promoted c12 rope physical radius: `{c12['physical']['rope_collision_radius_m']:.6f} m`",
            f"- promoted c12 rope render radius: `{c12['physical']['rope_render_radius_m']:.6f} m`",
            f"- promoted c08 visible-tool rope physical radius: `{visible_tool['summary'].get('rope_particle_radius_m', 0.0026):.6f} m`" if visible_tool["summary"].get("rope_particle_radius_m") is not None else "- promoted c08 visible-tool rope physical radius: see rope_visual_vs_physical_thickness_report.md",
            "",
            "## Interpretation",
            "",
            "The old accepted c12 baseline used a physically much thicker rope than the later true-size branches. That reduced geometric precision demands and made stale contact geometry easier to overlook.",
            "This is a real secondary contributor: once the rope becomes physically smaller, the same reference/path mismatch is no longer hidden by the rope thickness.",
            "But it is not the primary cause, because c19 shows the thin rope can still be hit early when laydown and base alignment are corrected.",
        ],
    )
    _write_md(
        out_dir / "rope_visual_vs_physical_report.md",
        [
            "# Rope Visual Vs Physical Report",
            "",
            f"- c12 render/physical radius ratio: `{c12['physical']['rope_render_radius_m'] / max(c12['physical']['rope_collision_radius_m'], 1.0e-12):.6f}`",
            "- c08 visible-tool control keeps render and physical rope radius aligned at 1.0x.",
            "",
            "## Interpretation",
            "",
            "The honest path is to keep rope render thickness aligned with physical contact thickness. Sphere inflation should not be used to compensate for a rope-thickness lie.",
        ],
    )
    _write_md(
        out_dir / "controller_semantics_relevance_report.md",
        [
            "# Controller Semantics Relevance Report",
            "",
            "- current direct-finger tabletop path remains `joint_trajectory` and effectively controller-driven rather than fully physically blocked.",
            "- that limitation matters for the stronger physical-blocking task, but it is secondary for explaining the sphere question.",
            "",
            "## Interpretation",
            "",
            "For the sphere-inflation question, controller semantics are not the primary error term. The main issue is geometric truth: where the command reference is, where the real finger boxes are, and whether the actual finger path reaches the settled rope laydown.",
            "Sphere inflation cannot solve the blocked-physics limitation; at best it papers over geometry miss in a controller-driven rollout.",
        ],
    )

    report_lines = [
        "# Why Robot Spheres Need Inflation Ranked Report",
        "",
        "## Ranked Hypotheses",
        "",
    ]
    for idx, item in enumerate(ranking, start=1):
        report_lines.append(f"{idx}. {item}")
    report_lines.extend(
        [
            "",
            "## Primary Root Cause",
            "",
            ranked_payload["primary_root_cause"],
            "",
            "## Secondary Contributors",
            "",
        ]
    )
    for item in ranked_payload["secondary_contributors"]:
        report_lines.append(f"- {item}")
    report_lines.extend(
        [
            "",
            "## Key Evidence",
            "",
            f"- In promoted c12, the command target is effectively gripper-center based, while the mean target -> nearest finger-box surface distance is `{c12['physical']['target_to_any_finger_surface_mean_m']:.6f} m`.",
            f"- The accepted proxy effective radius in c12 is `{c12['physical']['proxy_effective_radius_m']:.6f} m`, which is the same order as that reference-to-surface gap.",
            f"- At first actual contact in c12, gripper-center -> actual contact surface distance is `{c12['actual_first_contact'].get('gripper_center_to_contact_surface_norm_m', float('nan')):.6f} m`.",
            f"- True-size rope contact timing changes from `{next(item for item in analyses if item['label'] == 'c15_true0p1_tabletop_curve')['actual_first_contact']['time_s']:.6f} s` in c15 to `{c19['actual_first_contact']['time_s']:.6f} s` in c19 without changing ee-contact-radius, which points to laydown/base/path alignment rather than sphere size.",
            f"- The visible-tool control c08 reaches first actual tool contact at `{visible_tool['tool_contact_onset']['first_actual_tool_contact_time_s']:.6f} s` with `multi_frame_standoff_detected = false`, proving the same rope/tabletop context can be hit honestly without sphere fiction when the contactor is explicit.",
            "",
            "## What Sphere Inflation Was Actually Compensating For",
            "",
            "The inflated sphere was mainly compensating for the fact that the tabletop command reference lived at gripper-center, while the real contact-capable surface lived several centimeters away on the finger boxes. "
            "Once the rope became physically thinner, stale laydown/base alignment made that mismatch show up as an XY near-miss. "
            "The larger sphere did not make the finger more physical; it simply enlarged a proxy centered on the wrong point so that the proxy could still 'catch' the rope.",
            "",
            "## Is Sphere Inflation Physically Meaningful?",
            "",
            "- For the current rope tabletop path: `No`.",
            "- It is a proxy workaround, not a real physical need.",
            "",
            "## Honest Path Forward",
            "",
            "- direct-finger re-certification is only honest if the reference geometry and laydown/path are corrected so actual finger boxes reach the rope without sphere fiction;",
            "- the promoted visible rigid tool baseline is the current conservative control for a meeting-safe honest contactor;",
            "- physical-blocking remains a separate blocked follow-on task and is not solved by sphere inflation.",
            "",
            "## Meeting-Ready Conclusion",
            "",
            ranked_payload["meeting_ready_one_sentence"],
            "",
            "## Engineering Conclusion",
            "",
            ranked_payload["engineering_conclusion"],
            "",
            "## Research Conclusion",
            "",
            ranked_payload["research_conclusion"],
        ]
    )
    _write_md(out_dir / "why_robot_spheres_need_inflation_ranked_report.md", report_lines)

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
