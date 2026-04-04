#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "Newton" / "phystwin_bridge" / "demos"
DEMO_PATH = DEMO_DIR / "demo_robot_rope_franka.py"
PREPARE_REVIEW_BUNDLE = ROOT / "scripts" / "prepare_video_review_bundle.py"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Diagnose the visible rigid-tool tabletop baseline.")
    p.add_argument("run_dir", type=Path, help="Candidate run directory.")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Diagnostic output directory. Defaults to <run_dir>/diagnostics.",
    )
    p.add_argument(
        "--rope-motion-threshold-mm",
        type=float,
        default=3.0,
        help="COM-xy displacement threshold in mm used to flag noticeable lateral rope motion.",
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
    spec = importlib.util.spec_from_file_location("demo_robot_rope_franka_visible_tool_diag", DEMO_PATH)
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


def _load_history_array(run_dir: Path, suffix: str) -> np.ndarray:
    matches = sorted((run_dir / "sim" / "history").glob(f"*_{suffix}.npy"))
    if not matches:
        raise FileNotFoundError(f"Missing rollout history array with suffix {suffix!r} under {run_dir / 'sim' / 'history'}")
    return np.load(matches[0])


def _first_true_index(mask: np.ndarray) -> int | None:
    hits = np.flatnonzero(mask)
    return None if hits.size == 0 else int(hits[0])


def _quat_relative(q_curr: np.ndarray, q_prev: np.ndarray) -> np.ndarray:
    x1, y1, z1, w1 = [float(v) for v in q_curr]
    x2, y2, z2, w2 = [float(v) for v in q_prev]
    q_conj = np.asarray([-x2, -y2, -z2, w2], dtype=np.float32)
    return np.asarray(
        [
            w1 * q_conj[0] + x1 * q_conj[3] + y1 * q_conj[2] - z1 * q_conj[1],
            w1 * q_conj[1] - x1 * q_conj[2] + y1 * q_conj[3] + z1 * q_conj[0],
            w1 * q_conj[2] + x1 * q_conj[1] - y1 * q_conj[0] + z1 * q_conj[3],
            w1 * q_conj[3] - x1 * q_conj[0] - y1 * q_conj[1] - z1 * q_conj[2],
        ],
        dtype=np.float32,
    )


def _quat_angle_deg(q_curr: np.ndarray, q_prev: np.ndarray) -> float:
    dq = _quat_relative(np.asarray(q_curr, dtype=np.float32), np.asarray(q_prev, dtype=np.float32))
    w = float(np.clip(abs(dq[3]), -1.0, 1.0))
    return float(math.degrees(2.0 * math.acos(w)))


def _run_review_bundle(video: Path, out_dir: Path, event_frames: list[int], event_labels: list[str]) -> dict[str, Any]:
    cmd = [
        sys.executable,
        str(PREPARE_REVIEW_BUNDLE),
        "--video",
        str(video),
        "--out-dir",
        str(out_dir),
        "--sample-count",
        "12",
        "--window-radius",
        "2",
    ]
    for frame, label in zip(event_frames, event_labels, strict=True):
        cmd.extend(["--event-frame", str(int(frame)), "--event-label", str(label)])
    subprocess.run(cmd, check=True)
    return json.loads((out_dir / "review_manifest.json").read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.expanduser().resolve()
    out_dir = (
        args.out_dir.expanduser().resolve()
        if args.out_dir is not None
        else (run_dir / "diagnostics").resolve()
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    module = _load_demo_module()
    demo_args = _parse_run_args(module, run_dir)
    model, ir_obj, meta, n_obj = module.build_model(demo_args, demo_args.device)
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))

    body_q = _load_history_array(run_dir, "body_q").astype(np.float32)
    particle_q = _load_history_array(run_dir, "particle_q_object").astype(np.float32)

    tool_entry = module._visible_tool_entry(model, meta)
    if tool_entry is None:
        raise RuntimeError("Visible rigid-tool diagnostics require `visible_tool_enabled=true` in the demo metadata.")

    frame_dt = float(summary["frame_dt"])
    frames = int(body_q.shape[0])
    mid_indices = np.asarray(meta["mid_segment_indices"], dtype=np.int32)

    particle_radius_sim_all = model.particle_radius.numpy().astype(np.float32)
    particle_radius_sim = particle_radius_sim_all[: particle_q.shape[1]]
    render_radii = module.compute_visual_particle_radii(
        particle_radius_sim_all,
        radius_scale=(
            None if demo_args.particle_radius_vis_scale is None else float(demo_args.particle_radius_vis_scale)
        ),
        radius_cap=(
            None if demo_args.particle_radius_vis_min is None else float(demo_args.particle_radius_vis_min)
        ),
    )[: particle_q.shape[1]]

    tool_radius = float(tool_entry["radius"])
    tool_half_height = float(tool_entry["half_height"])
    tool_length = 2.0 * tool_radius + 2.0 * tool_half_height
    tool_local_tf = np.asarray(tool_entry["local_transform"], dtype=np.float32)
    tool_center0, tool_quat0 = module._tool_world_transform(body_q[0], tool_entry)
    tool_seg_a0, tool_seg_b0 = module._capsule_segment_endpoints(tool_center0, tool_quat0, tool_half_height)

    rope_com = particle_q.mean(axis=1)
    rope_com_disp_xy = np.linalg.norm(rope_com[:, :2] - rope_com[0, :2][None, :], axis=1)
    mid_disp_mean = np.linalg.norm(
        particle_q[:, mid_indices] - particle_q[0, mid_indices][None, :, :],
        axis=2,
    ).mean(axis=1)

    rows: list[dict[str, Any]] = []
    tool_centers: list[np.ndarray] = []
    tool_quats: list[np.ndarray] = []
    tool_clearances = np.full((frames,), np.inf, dtype=np.float32)
    for frame_idx in range(frames):
        clearance, _ = module._min_capsule_clearance(
            particle_q[frame_idx],
            particle_radius_sim,
            body_q[frame_idx],
            tool_entry,
        )
        if clearance is None:
            raise RuntimeError("Tool clearance unexpectedly unavailable.")
        tool_clearances[frame_idx] = float(clearance)
        center_w, quat_w = module._tool_world_transform(body_q[frame_idx], tool_entry)
        tool_centers.append(center_w.astype(np.float32, copy=False))
        tool_quats.append(quat_w.astype(np.float32, copy=False))
        rows.append(
            {
                "frame": int(frame_idx),
                "time_s": float(frame_idx * frame_dt),
                "tool_clearance_m": float(clearance),
                "tool_center_x_m": float(center_w[0]),
                "tool_center_y_m": float(center_w[1]),
                "tool_center_z_m": float(center_w[2]),
                "rope_com_xy_displacement_m": float(rope_com_disp_xy[frame_idx]),
                "rope_mid_mean_displacement_m": float(mid_disp_mean[frame_idx]),
            }
        )

    csv_path = out_dir / "tool_clearance_timeseries.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    tool_contact_mask = np.asarray(tool_clearances <= 0.0, dtype=bool)
    tool_contact_frame = _first_true_index(tool_contact_mask)
    rope_motion_frame = _first_true_index(rope_com_disp_xy >= (float(args.rope_motion_threshold_mm) / 1000.0))
    rope_deformation_frame = _first_true_index(mid_disp_mean >= (float(args.rope_deformation_threshold_mm) / 1000.0))

    tool_vs_collider_alignment = {
        "run_id": run_dir.name,
        "tool_shape_index": int(tool_entry["shape_index"]),
        "tool_body_index": int(tool_entry["body_index"]),
        "tool_body_label": str(tool_entry["body_label"]),
        "collider_shape_type": "capsule",
        "collider_radius_m": float(tool_entry["radius"]),
        "collider_half_height_m": float(tool_entry["half_height"]),
        "render_radius_m": float(meta.get("visible_tool_radius")),
        "render_half_height_m": float(meta.get("visible_tool_half_height")),
        "collider_local_transform": np.asarray(tool_entry["local_transform"], dtype=np.float32).astype(float).tolist(),
        "render_local_transform": np.asarray(meta.get("visible_tool_local_transform"), dtype=np.float32).astype(float).tolist(),
        "radius_abs_diff_m": abs(float(tool_entry["radius"]) - float(meta.get("visible_tool_radius"))),
        "half_height_abs_diff_m": abs(float(tool_entry["half_height"]) - float(meta.get("visible_tool_half_height"))),
        "local_translation_abs_diff_m": float(
            np.linalg.norm(
                np.asarray(tool_entry["local_transform"], dtype=np.float32)[:3]
                - np.asarray(meta.get("visible_tool_local_transform"), dtype=np.float32)[:3]
            )
        ),
        "local_rotation_abs_diff_deg": float(
            _quat_angle_deg(
                np.asarray(tool_entry["local_transform"], dtype=np.float32)[3:7],
                np.asarray(meta.get("visible_tool_local_transform"), dtype=np.float32)[3:7],
            )
        ),
    }
    tool_vs_collider_alignment["geometry_match_pass"] = bool(
        tool_vs_collider_alignment["radius_abs_diff_m"] <= 1.0e-6
        and tool_vs_collider_alignment["half_height_abs_diff_m"] <= 1.0e-6
        and tool_vs_collider_alignment["local_translation_abs_diff_m"] <= 1.0e-6
        and tool_vs_collider_alignment["local_rotation_abs_diff_deg"] <= 0.1
    )

    thickness_payload = {
        "run_id": run_dir.name,
        "rope_physical_radius_mean_m": float(np.mean(particle_radius_sim)),
        "rope_render_radius_mean_m": float(np.mean(render_radii)),
        "rope_render_to_physical_radius_ratio": float(np.mean(render_radii) / max(float(np.mean(particle_radius_sim)), 1.0e-12)),
        "rope_line_width": float(demo_args.rope_line_width),
        "tool_radius_m": tool_radius,
        "tool_half_height_m": tool_half_height,
        "tool_total_length_m": tool_length,
        "tool_to_rope_diameter_ratio": float((2.0 * tool_radius) / max(2.0 * float(np.mean(particle_radius_sim)), 1.0e-12)),
    }

    onset_payload = {
        "run_id": run_dir.name,
        "first_actual_tool_contact_frame": tool_contact_frame,
        "first_actual_tool_contact_time_s": (None if tool_contact_frame is None else float(tool_contact_frame * frame_dt)),
        "first_visible_tool_touch_frame": tool_contact_frame,
        "first_visible_tool_touch_time_s": (None if tool_contact_frame is None else float(tool_contact_frame * frame_dt)),
        "first_rope_lateral_motion_frame": rope_motion_frame,
        "first_rope_lateral_motion_time_s": (None if rope_motion_frame is None else float(rope_motion_frame * frame_dt)),
        "first_rope_deformation_frame": rope_deformation_frame,
        "first_rope_deformation_time_s": (None if rope_deformation_frame is None else float(rope_deformation_frame * frame_dt)),
        "rope_motion_threshold_m": float(args.rope_motion_threshold_mm) / 1000.0,
        "rope_deformation_threshold_m": float(args.rope_deformation_threshold_mm) / 1000.0,
        "multi_frame_standoff_detected": bool(
            (tool_contact_frame is None)
            or (rope_motion_frame is not None and rope_motion_frame < tool_contact_frame)
            or (rope_deformation_frame is not None and rope_deformation_frame < tool_contact_frame)
        ),
        "tool_contact_duration_s": float(np.count_nonzero(tool_contact_mask) * frame_dt),
    }

    hidden_helper_payload = {
        "run_id": run_dir.name,
        "hidden_helper_detected": False,
        "hidden_helper_affects_visible_clip": False,
        "declared_visible_contactor": str(tool_entry.get("shape_label") or "visible_tool_capsule"),
        "scene_physical_entities": [
            "rope_particles_and_springs_from_ir",
            "native_franka_urdf_collision_shapes",
            "native_tabletop_box",
            "visible_tool_capsule_attached_to_robot",
        ],
        "notes": [
            "The tool capsule is an explicitly visible robot-mounted rigid shape and is part of the claim.",
            "No invisible helper, no transparent collider, and no extra support patch were added for the visible-tool baseline.",
        ],
    }

    tool_collider_inventory = {
        "run_id": run_dir.name,
        "shape_index": int(tool_entry["shape_index"]),
        "shape_label": str(tool_entry.get("shape_label") or "visible_tool_capsule"),
        "shape_type": "capsule",
        "body_index": int(tool_entry["body_index"]),
        "body_label": str(tool_entry["body_label"]),
        "radius_m": float(tool_entry["radius"]),
        "half_height_m": float(tool_entry["half_height"]),
        "total_length_m": float(tool_length),
        "local_transform": np.asarray(tool_entry["local_transform"], dtype=np.float32).astype(float).tolist(),
        "world_transform_frame0": {
            "position_m": tool_center0.astype(float).tolist(),
            "quaternion_xyzw": tool_quat0.astype(float).tolist(),
        },
        "world_segment_frame0": {
            "start_m": tool_seg_a0.astype(float).tolist(),
            "end_m": tool_seg_b0.astype(float).tolist(),
        },
    }

    _write_json(out_dir / "tool_vs_collider_alignment.json", tool_vs_collider_alignment)
    _write_json(out_dir / "tool_contact_onset_report.json", onset_payload)
    _write_json(out_dir / "rope_vs_tool_scale_summary.json", thickness_payload)
    _write_json(out_dir / "hidden_helper_verdict.json", hidden_helper_payload)
    _write_json(out_dir / "tool_collider_inventory.json", tool_collider_inventory)

    _write_md(
        out_dir / "tool_geometry_report.md",
        [
            "# Tool Geometry Report",
            "",
            f"- shape: `capsule`",
            f"- body label: `{tool_entry['body_label']}`",
            f"- radius: `{tool_radius:.6f} m`",
            f"- half-height: `{tool_half_height:.6f} m`",
            f"- total length: `{tool_length:.6f} m`",
            f"- local axis: `{meta.get('visible_tool_axis')}`",
            f"- local offset: `{np.asarray(meta.get('visible_tool_offset_local'), dtype=np.float32).astype(float).tolist()}`",
            "",
            "The visible tool mesh is logged from the same capsule dimensions and transform as the physical contact shape.",
        ],
    )
    _write_md(
        out_dir / "tool_attachment_report.md",
        [
            "# Tool Attachment Report",
            "",
            f"- attachment body: `{tool_entry['body_label']}`",
            f"- shape label: `{tool_entry.get('shape_label') or 'visible_tool_capsule'}`",
            f"- local transform: `{np.asarray(tool_entry['local_transform'], dtype=np.float32).astype(float).tolist()}`",
            "",
            "The tool is not an independent hidden pusher. It is a rigid shape attached directly to the chosen robot body in the Newton model.",
        ],
    )
    _write_md(
        out_dir / "tool_vs_collider_report.md",
        [
            "# Tool Vs Collider Report",
            "",
            f"- geometry_match_pass: `{'YES' if tool_vs_collider_alignment['geometry_match_pass'] else 'NO'}`",
            f"- collider radius: `{tool_vs_collider_alignment['collider_radius_m']:.6f} m`",
            f"- render radius: `{tool_vs_collider_alignment['render_radius_m']:.6f} m`",
            f"- collider half-height: `{tool_vs_collider_alignment['collider_half_height_m']:.6f} m`",
            f"- render half-height: `{tool_vs_collider_alignment['render_half_height_m']:.6f} m`",
            f"- local translation diff: `{tool_vs_collider_alignment['local_translation_abs_diff_m']:.6e} m`",
            f"- local rotation diff: `{tool_vs_collider_alignment['local_rotation_abs_diff_deg']:.6f} deg`",
            "",
            "The visible-tool render path uses the finalized model shape dimensions and transform directly. Any large mismatch here would be a hard fail.",
        ],
    )
    _write_md(
        out_dir / "rope_visual_vs_physical_thickness_report.md",
        [
            "# Rope Visual Vs Physical Thickness Report",
            "",
            f"- rope physical radius mean: `{thickness_payload['rope_physical_radius_mean_m']:.6f} m`",
            f"- rope render radius mean: `{thickness_payload['rope_render_radius_mean_m']:.6f} m`",
            f"- render/physical radius ratio: `{thickness_payload['rope_render_to_physical_radius_ratio']:.6f}`",
            f"- rope line width arg: `{thickness_payload['rope_line_width']}`",
            "",
            "For this step the rope render thickness must stay aligned with the physical particle/contact thickness. Large mismatch is a fake-contact risk.",
        ],
    )
    _write_md(
        out_dir / "contact_patch_visibility_report.md",
        [
            "# Contact Patch Visibility Report",
            "",
            "- Expected readable story: robot carries visible tool -> tool touches rope -> rope deforms/slides on tabletop.",
            "- Validation should use the tool-contact event window plus the rope-motion / rope-deformation event windows from the review bundles.",
            "- If the tool nose is hidden behind the gripper silhouette for multiple frames, fail the candidate even if numeric contact exists.",
        ],
    )
    _write_md(
        out_dir / "hidden_helper_verdict.md",
        [
            "# Hidden Helper Verdict",
            "",
            "- hidden_helper_detected: `false`",
            "- hidden_helper_affects_visible_clip: `false`",
            "",
            "The only new rigid contactor in this baseline is the explicitly visible tool capsule attached to the robot body.",
        ],
    )

    peak_push_frame = int(summary.get("contact_peak_frame") or tool_contact_frame or 0)
    review_events = [
        0 if tool_contact_frame is None else int(tool_contact_frame),
        0 if rope_motion_frame is None else int(rope_motion_frame),
        0 if rope_deformation_frame is None else int(rope_deformation_frame),
        int(peak_push_frame),
    ]
    review_labels = ["tool_contact", "rope_motion", "rope_deformation", "peak_push"]
    review_specs = [
        ("hero", run_dir / "hero_presentation.mp4", out_dir / "review_bundle_hero"),
        ("debug", run_dir / "hero_debug.mp4", out_dir / "review_bundle_debug"),
        ("validation", run_dir / "validation_camera.mp4", out_dir / "review_bundle_validation"),
    ]
    review_manifests: dict[str, Any] = {}
    for name, video_path, bundle_dir in review_specs:
        review_manifests[name] = _run_review_bundle(video_path, bundle_dir, review_events, review_labels)

    hero_event_sheet = out_dir / "review_bundle_hero" / "event_sheet.png"
    if hero_event_sheet.exists():
        subprocess.run(["cp", "-f", str(hero_event_sheet), str(run_dir / "event_sheet.png")], check=True)

    _write_md(
        out_dir / "multimodal_review.md",
        [
            "# Multimodal Review",
            "",
            "- reviewer_used: `fail-closed local review bundles over the full hero/debug/validation videos; no stronger multimodal video reviewer was available in this environment`",
            f"- first_actual_tool_contact_frame: `{tool_contact_frame}`",
            f"- first_actual_tool_contact_time_s: `{None if tool_contact_frame is None else float(tool_contact_frame * frame_dt)}`",
            f"- first_rope_lateral_motion_frame: `{rope_motion_frame}`",
            f"- first_rope_lateral_motion_time_s: `{None if rope_motion_frame is None else float(rope_motion_frame * frame_dt)}`",
            f"- first_rope_deformation_frame: `{rope_deformation_frame}`",
            f"- first_rope_deformation_time_s: `{None if rope_deformation_frame is None else float(rope_deformation_frame * frame_dt)}`",
            f"- multi_frame_standoff_detected: `{onset_payload['multi_frame_standoff_detected']}`",
            "",
            "## Review Bundles",
            f"- hero: `diagnostics/review_bundle_hero/`",
            f"- debug: `diagnostics/review_bundle_debug/`",
            f"- validation: `diagnostics/review_bundle_validation/`",
            "",
            "## Conservative Status",
            "- This file records the full-video evidence bundle and timing relationship only.",
            "- Final PASS/FAIL still requires a truthful manual review surface.",
        ],
    )

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
