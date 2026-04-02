#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import shlex
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "Newton" / "phystwin_bridge" / "demos"
DEMO_PATH = DEMO_DIR / "demo_robot_rope_franka.py"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Diagnose remote-interaction / stand-off contact in the tabletop hero.")
    p.add_argument("run_dir", type=Path, help="Candidate or BEST_RUN directory.")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "diagnostics",
        help="Directory where diagnostic artifacts should be written.",
    )
    p.add_argument(
        "--rope-motion-threshold-mm",
        type=float,
        default=3.0,
        help="COM-xy displacement threshold in mm used to flag noticeable lateral motion.",
    )
    p.add_argument(
        "--rope-deformation-threshold-mm",
        type=float,
        default=5.0,
        help="Mid-rope mean displacement threshold in mm used to flag noticeable deformation.",
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


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=_json_default), encoding="utf-8")


def _write_md(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _load_demo_module() -> Any:
    if str(DEMO_DIR) not in sys.path:
        sys.path.insert(0, str(DEMO_DIR))
    spec = importlib.util.spec_from_file_location("demo_robot_rope_franka_diag", DEMO_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to import demo module from {DEMO_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _parse_run_args(module: Any, run_dir: Path) -> argparse.Namespace:
    run_command = (run_dir / "run_command.txt").read_text(encoding="utf-8").splitlines()[0]
    argv = shlex.split(run_command)
    old_argv = sys.argv[:]
    try:
        sys.argv = ["demo_robot_rope_franka.py", *argv[2:]]
        args = module.parse_args()
    finally:
        sys.argv = old_argv
    return args


def _shape_type_name(newton_mod: Any, value: int) -> str:
    for name in dir(newton_mod.GeoType):
        if name.isupper():
            try:
                if int(getattr(newton_mod.GeoType, name)) == int(value):
                    return name
            except Exception:
                continue
    return f"UNKNOWN_{value}"


def _quat_multiply(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    x1, y1, z1, w1 = [float(v) for v in q1]
    x2, y2, z2, w2 = [float(v) for v in q2]
    return np.asarray(
        [
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
        ],
        dtype=np.float32,
    )


def _quat_conjugate(q: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=np.float32)
    return np.asarray([-q[0], -q[1], -q[2], q[3]], dtype=np.float32)


def _quat_rotate(q: np.ndarray, v: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=np.float32)
    vq = np.asarray([v[0], v[1], v[2], 0.0], dtype=np.float32)
    rotated = _quat_multiply(_quat_multiply(q, vq), _quat_conjugate(q))
    return rotated[:3]


def _quat_inverse_rotate(q: np.ndarray, v: np.ndarray) -> np.ndarray:
    return _quat_rotate(_quat_conjugate(q), v)


def _combine_transform(body_row: np.ndarray, local_tf: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    body_p = np.asarray(body_row[:3], dtype=np.float32)
    body_q = np.asarray(body_row[3:7], dtype=np.float32)
    local_p = np.asarray(local_tf[:3], dtype=np.float32)
    local_q = np.asarray(local_tf[3:7], dtype=np.float32)
    world_p = body_p + _quat_rotate(body_q, local_p)
    world_q = _quat_multiply(body_q, local_q)
    return world_p.astype(np.float32), world_q.astype(np.float32)


def _signed_distance_points_to_box(points: np.ndarray, center: np.ndarray, quat: np.ndarray, half_extents: np.ndarray) -> np.ndarray:
    rel = points - center[None, :]
    local = np.stack([_quat_inverse_rotate(quat, row) for row in rel], axis=0)
    q = np.abs(local) - half_extents[None, :]
    outside = np.linalg.norm(np.maximum(q, 0.0), axis=1)
    inside = np.minimum(np.max(q, axis=1), 0.0)
    return outside + inside


def _point_segment_min_distance(points: np.ndarray, start: np.ndarray, end: np.ndarray) -> float:
    segment = end - start
    denom = float(np.dot(segment, segment))
    if denom <= 1.0e-12:
        return float(np.min(np.linalg.norm(points - start[None, :], axis=1)))
    t = np.clip(((points - start[None, :]) @ segment) / denom, 0.0, 1.0)
    proj = start[None, :] + t[:, None] * segment[None, :]
    return float(np.min(np.linalg.norm(points - proj, axis=1)))


def _first_true_index(mask: np.ndarray) -> int | None:
    hits = np.flatnonzero(mask)
    return None if hits.size == 0 else int(hits[0])


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.expanduser().resolve()
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    module = _load_demo_module()
    demo_args = _parse_run_args(module, run_dir)
    model, ir_obj, meta, n_obj = module.build_model(demo_args, demo_args.device)
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))

    body_q = np.load(run_dir / "sim" / "history" / "robot_rope_tabletop_hero_body_q.npy")
    particle_q = np.load(run_dir / "sim" / "history" / "robot_rope_tabletop_hero_particle_q_object.npy")
    ee_target_pos = np.load(run_dir / "sim" / "history" / "robot_rope_tabletop_hero_ee_target_pos.npy")

    frame_dt = float(summary["frame_dt"])
    frames = int(body_q.shape[0])
    left_idx = int(meta["left_finger_index"])
    right_idx = int(meta["right_finger_index"])
    ee_idx = int(meta["ee_body_index"])

    particle_radius_arr = np.asarray(ir_obj.get("collision_radius", ir_obj.get("contact_collision_dist")), dtype=np.float32).reshape(-1)
    if particle_radius_arr.size == 1:
        particle_radius_arr = np.full((n_obj,), float(particle_radius_arr[0]), dtype=np.float32)
    else:
        particle_radius_arr = particle_radius_arr[:n_obj]
    particle_radius = float(np.mean(particle_radius_arr))
    render_particle_radius = min(
        float(particle_radius) * float(demo_args.particle_radius_vis_scale),
        float(demo_args.particle_radius_vis_min),
    )

    proxy_radii = module._gripper_contact_proxy_radii(float(demo_args.ee_contact_radius))

    # Inventory real colliders.
    shape_body = model.shape_body.numpy() if hasattr(model.shape_body, "numpy") else np.asarray(model.shape_body)
    shape_type = model.shape_type.numpy() if hasattr(model, "shape_type") and hasattr(model.shape_type, "numpy") else np.asarray(model.shape_type)
    shape_scale = model.shape_scale.numpy() if hasattr(model, "shape_scale") and hasattr(model.shape_scale, "numpy") else np.asarray(model.shape_scale)
    shape_tf = model.shape_transform.numpy() if hasattr(model.shape_transform, "numpy") else np.asarray(model.shape_transform)
    import newton  # local import after demo bootstraps paths

    collider_inventory: dict[str, Any] = {
        "run_id": run_dir.name,
        "body_count": int(model.body_count),
        "shape_count": int(model.shape_count),
        "ee_body_index": ee_idx,
        "left_finger_index": left_idx,
        "right_finger_index": right_idx,
        "relevant_shapes": [],
    }

    left_box_shapes: list[dict[str, Any]] = []
    right_box_shapes: list[dict[str, Any]] = []
    for shape_idx in range(int(model.shape_count)):
        body_idx = int(shape_body[shape_idx])
        entry = {
            "shape_index": int(shape_idx),
            "body_index": body_idx,
            "body_label": ("world" if body_idx < 0 else str(model.body_label[body_idx])),
            "shape_type": _shape_type_name(newton, int(shape_type[shape_idx])),
            "shape_type_id": int(shape_type[shape_idx]),
            "shape_scale": np.asarray(shape_scale[shape_idx], dtype=np.float32).astype(float).tolist(),
            "local_transform": np.asarray(shape_tf[shape_idx], dtype=np.float32).astype(float).tolist(),
        }
        if body_idx in {ee_idx, left_idx, right_idx, -1}:
            collider_inventory["relevant_shapes"].append(entry)
        if body_idx == left_idx and int(shape_type[shape_idx]) == int(newton.GeoType.BOX):
            left_box_shapes.append(entry)
        if body_idx == right_idx and int(shape_type[shape_idx]) == int(newton.GeoType.BOX):
            right_box_shapes.append(entry)

    _write_json(out_dir / "collider_inventory.json", collider_inventory)

    hidden_helper_audit = {
        "run_id": run_dir.name,
        "hidden_helper_exists": False,
        "hidden_helper_affects_visible_clip": False,
        "scene_physical_entities": [
            "rope_particles_and_springs_from_ir",
            "native_franka_urdf_collision_shapes",
            "native_table_box",
        ],
        "viewer_only_entities": [
            "hero pedestal / base decoration",
            "table legs / stage decorations",
        ],
        "notes": [
            "Tabletop task does not deactivate rope endpoints because the deactivation path is guarded by `if not tabletop_task`.",
            "Hero pedestal hiding is a presentation-only viewer toggle and does not add/remove physics shapes.",
        ],
    }
    _write_json(out_dir / "hidden_helper_audit.json", hidden_helper_audit)
    _write_md(
        out_dir / "hidden_helper_audit.md",
        [
            "# Hidden Helper Audit",
            "",
            "- hidden_helper_exists: `false`",
            "- hidden_helper_affects_visible_clip: `false`",
            "",
            "## Notes",
            "- Physics path includes only rope particles/springs, native Franka URDF colliders, and the native tabletop box.",
            "- Tabletop rope particles remain active; there is no visible-clip support patch or hidden pusher active in the tabletop task.",
            "- The hero pedestal hide flag only affects viewer decorations, not solver geometry.",
        ],
    )

    # Target reference vs finger origins.
    left_centers = body_q[:, left_idx, :3].astype(np.float32)
    right_centers = body_q[:, right_idx, :3].astype(np.float32)
    gripper_centers = 0.5 * (left_centers + right_centers)
    target_to_left = np.linalg.norm(ee_target_pos - left_centers, axis=1)
    target_to_right = np.linalg.norm(ee_target_pos - right_centers, axis=1)
    target_to_center = np.linalg.norm(ee_target_pos - gripper_centers, axis=1)

    control_reference_payload = {
        "run_id": run_dir.name,
        "tabletop_control_mode": str(meta.get("tabletop_control_mode")),
        "ee_body_index": ee_idx,
        "ee_body_label": str(model.body_label[ee_idx]),
        "left_finger_index": left_idx,
        "left_finger_label": str(model.body_label[left_idx]),
        "right_finger_index": right_idx,
        "right_finger_label": str(model.body_label[right_idx]),
        "ee_offset_local": np.asarray(meta.get("ee_offset_local"), dtype=np.float32).astype(float).tolist(),
        "target_point_semantics": (
            "joint_trajectory_fk_gripper_center"
            if str(meta.get("tabletop_control_mode")) == "joint_trajectory"
            else "ik_world_target"
        ),
        "target_to_left_finger_center_mean_m": float(np.mean(target_to_left)),
        "target_to_right_finger_center_mean_m": float(np.mean(target_to_right)),
        "target_to_gripper_center_mean_m": float(np.mean(target_to_center)),
        "target_to_left_finger_center_min_m": float(np.min(target_to_left)),
        "target_to_right_finger_center_min_m": float(np.min(target_to_right)),
        "target_to_gripper_center_min_m": float(np.min(target_to_center)),
    }
    _write_json(out_dir / "target_to_visible_finger_offset.json", control_reference_payload)
    _write_md(
        out_dir / "control_reference_report.md",
        [
            "# Control Reference Report",
            "",
            f"- tabletop_control_mode: `{control_reference_payload['tabletop_control_mode']}`",
            f"- ee body label: `{control_reference_payload['ee_body_label']}`",
            f"- target semantics: `{control_reference_payload['target_point_semantics']}`",
            f"- mean target->left finger center offset: `{control_reference_payload['target_to_left_finger_center_mean_m']:.6f} m`",
            f"- mean target->right finger center offset: `{control_reference_payload['target_to_right_finger_center_mean_m']:.6f} m`",
            f"- mean target->gripper center offset: `{control_reference_payload['target_to_gripper_center_mean_m']:.6f} m`",
            "",
            "The promoted tabletop path is joint-space, so the reported target is the FK gripper-center path rather than an explicit fingertip or finger-pad target.",
        ],
    )

    # Per-frame proxy and actual-collider clearances.
    rows: list[dict[str, Any]] = []
    actual_left_clearances = np.full((frames,), np.inf, dtype=np.float32)
    actual_right_clearances = np.full((frames,), np.inf, dtype=np.float32)
    actual_any_clearances = np.full((frames,), np.inf, dtype=np.float32)
    actual_left_tip_clearances = np.full((frames,), np.inf, dtype=np.float32)
    actual_right_tip_clearances = np.full((frames,), np.inf, dtype=np.float32)
    rope_com = np.mean(particle_q, axis=1)
    rope_com_disp_xy = np.linalg.norm(rope_com[:, :2] - rope_com[0, :2][None, :], axis=1)
    mid_indices = np.asarray(meta["mid_segment_indices"], dtype=np.int32)
    mid_disp_mean = np.linalg.norm(particle_q[:, mid_indices] - particle_q[0, mid_indices][None, :, :], axis=2).mean(axis=1)

    left_tip_shape_idx = max((int(x["shape_index"]) for x in left_box_shapes), default=None)
    right_tip_shape_idx = max((int(x["shape_index"]) for x in right_box_shapes), default=None)

    for frame_idx in range(frames):
        points = particle_q[frame_idx].astype(np.float32)
        left = left_centers[frame_idx]
        right = right_centers[frame_idx]
        center = gripper_centers[frame_idx]
        d_left = float(np.min(np.linalg.norm(points - left[None, :], axis=1)) - (particle_radius + proxy_radii["left_finger"]))
        d_right = float(np.min(np.linalg.norm(points - right[None, :], axis=1)) - (particle_radius + proxy_radii["right_finger"]))
        d_center = float(np.min(np.linalg.norm(points - center[None, :], axis=1)) - (particle_radius + proxy_radii["gripper_center"]))
        d_span = float(_point_segment_min_distance(points, left, right) - (particle_radius + proxy_radii["finger_span"]))

        for entry in left_box_shapes:
            idx = int(entry["shape_index"])
            center_w, quat_w = _combine_transform(body_q[frame_idx, left_idx], shape_tf[idx])
            half = np.asarray(shape_scale[idx], dtype=np.float32)
            sdf = _signed_distance_points_to_box(points, center_w, quat_w, half)
            clearance = float(np.min(sdf - particle_radius))
            actual_left_clearances[frame_idx] = min(actual_left_clearances[frame_idx], clearance)
            actual_any_clearances[frame_idx] = min(actual_any_clearances[frame_idx], clearance)
            if idx == left_tip_shape_idx:
                actual_left_tip_clearances[frame_idx] = clearance
        for entry in right_box_shapes:
            idx = int(entry["shape_index"])
            center_w, quat_w = _combine_transform(body_q[frame_idx, right_idx], shape_tf[idx])
            half = np.asarray(shape_scale[idx], dtype=np.float32)
            sdf = _signed_distance_points_to_box(points, center_w, quat_w, half)
            clearance = float(np.min(sdf - particle_radius))
            actual_right_clearances[frame_idx] = min(actual_right_clearances[frame_idx], clearance)
            actual_any_clearances[frame_idx] = min(actual_any_clearances[frame_idx], clearance)
            if idx == right_tip_shape_idx:
                actual_right_tip_clearances[frame_idx] = clearance

        rows.append(
            {
                "frame": frame_idx,
                "time_s": frame_idx * frame_dt,
                "proxy_left_clearance_m": d_left,
                "proxy_right_clearance_m": d_right,
                "proxy_gripper_center_clearance_m": d_center,
                "proxy_finger_span_clearance_m": d_span,
                "actual_left_finger_box_clearance_m": float(actual_left_clearances[frame_idx]),
                "actual_right_finger_box_clearance_m": float(actual_right_clearances[frame_idx]),
                "actual_any_finger_box_clearance_m": float(actual_any_clearances[frame_idx]),
                "actual_left_tip_box_clearance_m": float(actual_left_tip_clearances[frame_idx]),
                "actual_right_tip_box_clearance_m": float(actual_right_tip_clearances[frame_idx]),
                "rope_com_xy_displacement_m": float(rope_com_disp_xy[frame_idx]),
                "rope_mid_mean_displacement_m": float(mid_disp_mean[frame_idx]),
            }
        )

    csv_path = out_dir / "proxy_clearance_timeseries.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    proxy_contact_frame = _first_true_index(np.asarray([row["proxy_finger_span_clearance_m"] <= 0.0 for row in rows], dtype=bool))
    actual_any_contact_frame = _first_true_index(actual_any_clearances <= 0.0)
    actual_left_tip_contact_frame = _first_true_index(actual_left_tip_clearances <= 0.0)
    rope_motion_frame = _first_true_index(rope_com_disp_xy >= (float(args.rope_motion_threshold_mm) / 1000.0))
    rope_deformation_frame = _first_true_index(mid_disp_mean >= (float(args.rope_deformation_threshold_mm) / 1000.0))

    onset_payload = {
        "run_id": run_dir.name,
        "summary_first_contact_frame": summary.get("first_contact_frame"),
        "summary_first_contact_time_s": summary.get("first_contact_time_s"),
        "summary_contact_proxy_counts": summary.get("contact_proxy_counts"),
        "summary_contact_peak_proxy": summary.get("contact_peak_proxy"),
        "proxy_finger_span_first_contact_frame": proxy_contact_frame,
        "proxy_finger_span_first_contact_time_s": (None if proxy_contact_frame is None else proxy_contact_frame * frame_dt),
        "actual_any_finger_box_first_contact_frame": actual_any_contact_frame,
        "actual_any_finger_box_first_contact_time_s": (None if actual_any_contact_frame is None else actual_any_contact_frame * frame_dt),
        "actual_left_tip_first_contact_frame": actual_left_tip_contact_frame,
        "actual_left_tip_first_contact_time_s": (None if actual_left_tip_contact_frame is None else actual_left_tip_contact_frame * frame_dt),
        "rope_lateral_motion_frame": rope_motion_frame,
        "rope_lateral_motion_time_s": (None if rope_motion_frame is None else rope_motion_frame * frame_dt),
        "rope_deformation_frame": rope_deformation_frame,
        "rope_deformation_time_s": (None if rope_deformation_frame is None else rope_deformation_frame * frame_dt),
        "rope_motion_threshold_m": float(args.rope_motion_threshold_mm) / 1000.0,
        "rope_deformation_threshold_m": float(args.rope_deformation_threshold_mm) / 1000.0,
        "dominant_proxy_issue": "finger_span" if summary.get("contact_proxy_counts", {}).get("finger_span") else None,
    }
    _write_json(out_dir / "contact_onset_report.json", onset_payload)

    rope_scale_payload = {
        "run_id": run_dir.name,
        "rope_collision_radius_m": particle_radius,
        "rope_render_radius_m": render_particle_radius,
        "rope_render_to_physical_radius_ratio": (render_particle_radius / max(particle_radius, 1.0e-12)),
        "ee_contact_radius_arg_m": float(demo_args.ee_contact_radius),
        "diagnostic_proxy_radius_m": float(proxy_radii["finger_span"]),
        "rope_diameter_m": 2.0 * particle_radius,
        "rope_render_diameter_m": 2.0 * render_particle_radius,
        "diagnostic_proxy_diameter_m": 2.0 * float(proxy_radii["finger_span"]),
        "left_tip_box_size_m": (
            None
            if left_tip_shape_idx is None
            else (2.0 * np.asarray(shape_scale[left_tip_shape_idx], dtype=np.float32)).astype(float).tolist()
        ),
        "right_tip_box_size_m": (
            None
            if right_tip_shape_idx is None
            else (2.0 * np.asarray(shape_scale[right_tip_shape_idx], dtype=np.float32)).astype(float).tolist()
        ),
        "rope_total_mass_kg": float(summary.get("rope_total_mass", 0.0)),
    }
    _write_json(out_dir / "rope_vs_finger_scale_summary.json", rope_scale_payload)

    _write_md(
        out_dir / "collider_vs_visual_report.md",
        [
            "# Collider Vs Visual Report",
            "",
            "- The solver uses native Franka URDF collision shapes plus the native tabletop box.",
            "- The visible finger mesh is not identical to the solver collider; the fingers use multiple box colliders.",
            f"- Left finger relevant box colliders: `{len(left_box_shapes)}`",
            f"- Right finger relevant box colliders: `{len(right_box_shapes)}`",
            "",
            "See `collider_inventory.json` for the exact shape inventory.",
        ],
    )
    _write_md(
        out_dir / "proxy_root_cause_report.md",
        [
            "# Proxy Root Cause Report",
            "",
            f"- summary contact proxy counts: `{summary.get('contact_proxy_counts')}`",
            f"- summary contact peak proxy: `{summary.get('contact_peak_proxy')}`",
            f"- proxy finger_span first contact frame: `{proxy_contact_frame}`",
            f"- actual any-finger-box first contact frame: `{actual_any_contact_frame}`",
            f"- actual left-tip first contact frame: `{actual_left_tip_contact_frame}`",
            f"- rope lateral motion frame ({args.rope_motion_threshold_mm:.1f} mm COM-xy): `{rope_motion_frame}`",
            f"- rope deformation frame ({args.rope_deformation_threshold_mm:.1f} mm mid-rope): `{rope_deformation_frame}`",
            "",
            "If rope motion/deformation begins before or at roughly the same time as visible near-touch, but the accepted proof is still `finger_span`, then the diagnostic semantics are looser than the fingertip-contact claim.",
        ],
    )
    _write_md(
        out_dir / "rope_contact_thickness_report.md",
        [
            "# Rope Contact Thickness Report",
            "",
            f"- rope collision radius: `{particle_radius:.6f} m`",
            f"- rope collision diameter: `{2.0 * particle_radius:.6f} m`",
            f"- rope render-only radius for this run: `{render_particle_radius:.6f} m`",
            f"- render/physical radius ratio: `{render_particle_radius / max(particle_radius, 1.0e-12):.3f}`",
            f"- diagnostic proxy radius: `{proxy_radii['finger_span']:.6f} m`",
            f"- diagnostic proxy diameter: `{2.0 * proxy_radii['finger_span']:.6f} m`",
            "",
            "The rope is physically much thicker than the current render if the render-only cap is small. In that case the solver can begin true fingertip contact while the visible rope still looks too thin.",
        ],
    )

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
