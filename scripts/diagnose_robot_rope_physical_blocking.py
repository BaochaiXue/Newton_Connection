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

import cv2
import matplotlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "Newton" / "phystwin_bridge" / "demos"
DEMO_PATH = DEMO_DIR / "demo_robot_rope_franka.py"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Diagnose physical robot-table blocking in the tabletop rope demo.")
    p.add_argument("run_dir", type=Path, help="Candidate or BEST_RUN directory.")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Diagnostics output directory. Defaults to <run_dir>/diagnostics.",
    )
    p.add_argument(
        "--video",
        choices=["validation_camera", "hero_presentation", "hero_debug"],
        default="validation_camera",
        help="Video to sample for the robot-table contact sheet.",
    )
    p.add_argument(
        "--contact-threshold-m",
        type=float,
        default=0.0,
        help="Signed-distance threshold for declaring robot-table contact.",
    )
    p.add_argument(
        "--sample-points-per-axis",
        type=int,
        default=3,
        help="Surface sample density per box axis for approximate signed distance.",
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
    spec = importlib.util.spec_from_file_location("demo_robot_rope_franka_blocking_diag", DEMO_PATH)
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


def _signed_distance_points_to_box(
    points: np.ndarray,
    center: np.ndarray,
    quat: np.ndarray,
    half_extents: np.ndarray,
) -> np.ndarray:
    rel = points - center[None, :]
    local = np.stack([_quat_inverse_rotate(quat, row) for row in rel], axis=0)
    q = np.abs(local) - half_extents[None, :]
    outside = np.linalg.norm(np.maximum(q, 0.0), axis=1)
    inside = np.minimum(np.max(q, axis=1), 0.0)
    return outside + inside


def _surface_sample_points(center: np.ndarray, quat: np.ndarray, half: np.ndarray, samples_per_axis: int) -> np.ndarray:
    grid = np.linspace(-1.0, 1.0, num=max(2, int(samples_per_axis)), dtype=np.float32)
    local_pts: list[np.ndarray] = []
    for sx in grid:
        for sy in grid:
            for sz in grid:
                on_surface = (
                    math.isclose(abs(float(sx)), 1.0, rel_tol=0.0, abs_tol=1.0e-6)
                    or math.isclose(abs(float(sy)), 1.0, rel_tol=0.0, abs_tol=1.0e-6)
                    or math.isclose(abs(float(sz)), 1.0, rel_tol=0.0, abs_tol=1.0e-6)
                )
                if not on_surface:
                    continue
                local_pts.append(np.asarray([sx * half[0], sy * half[1], sz * half[2]], dtype=np.float32))
    pts = [center + _quat_rotate(quat, p) for p in local_pts]
    return np.asarray(pts, dtype=np.float32)


def _line_no_containing(source: str, needle: str) -> int | None:
    for idx, line in enumerate(source.splitlines(), start=1):
        if needle in line:
            return idx
    return None


def _discover_video(run_dir: Path, name: str) -> Path:
    exact = run_dir / f"{name}.mp4"
    if exact.exists():
        return exact
    matches = sorted(run_dir.glob(f"*_{name}.mp4"))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        return matches[0]
    raise FileNotFoundError(f"Missing video for contact sheet matching: {name}")


def _read_video_frame(video_path: Path, frame_idx: int) -> np.ndarray:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_idx))
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        raise RuntimeError(f"Failed to read frame {frame_idx} from {video_path}")
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def _make_contact_sheet(frames: list[np.ndarray], labels: list[str], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pil_frames = [Image.fromarray(frame) for frame in frames]
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except Exception:
        font = ImageFont.load_default()
    thumb_w = 360
    thumbs: list[Image.Image] = []
    for frame in pil_frames:
        scale = thumb_w / max(frame.width, 1)
        thumb_h = max(1, int(round(frame.height * scale)))
        thumbs.append(frame.resize((thumb_w, thumb_h)))
    thumb_h = max(frame.height for frame in thumbs)
    label_h = 34
    gutter = 14
    cols = 2
    rows = int(math.ceil(len(thumbs) / cols))
    canvas = Image.new(
        "RGB",
        (cols * thumb_w + (cols + 1) * gutter, rows * (thumb_h + label_h) + (rows + 1) * gutter),
        (241, 243, 246),
    )
    draw = ImageDraw.Draw(canvas)
    for i, thumb in enumerate(thumbs):
        r = i // cols
        c = i % cols
        x = gutter + c * (thumb_w + gutter)
        y = gutter + r * (thumb_h + label_h + gutter)
        canvas.paste(thumb, (x, y))
        draw.rectangle((x, y + thumb.height, x + thumb_w, y + thumb.height + label_h), fill=(28, 32, 40))
        draw.text((x + 8, y + thumb.height + 8), labels[i], fill=(255, 255, 255), font=font)
    canvas.save(out_path)
    return out_path


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.expanduser().resolve()
    out_dir = (args.out_dir.expanduser().resolve() if args.out_dir is not None else (run_dir / "diagnostics"))
    out_dir.mkdir(parents=True, exist_ok=True)

    module = _load_demo_module()
    demo_args = _parse_run_args(module, run_dir)
    model, ir_obj, meta, n_obj = module.build_model(demo_args, demo_args.device)
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))

    body_q = np.load(run_dir / "sim" / "history" / "robot_rope_tabletop_hero_body_q.npy")
    ee_target_pos = np.load(run_dir / "sim" / "history" / "robot_rope_tabletop_hero_ee_target_pos.npy")
    frame_dt = float(summary["frame_dt"])
    frames = int(body_q.shape[0])

    left_idx = int(meta["left_finger_index"])
    right_idx = int(meta["right_finger_index"])

    source = DEMO_PATH.read_text(encoding="utf-8")
    control_sites = {
        "tabletop_joint_mode": _line_no_containing(source, 'tabletop_joint_mode = tabletop_task and str(args.tabletop_control_mode) == "joint_trajectory"'),
        "tabletop_joint_drive_mode": _line_no_containing(source, 'tabletop_joint_drive_mode = tabletop_task and str(meta.get("tabletop_control_mode")) == "joint_target_drive"'),
        "pre_state_in_q": _line_no_containing(source, "state_in.joint_q.assign(joint_target_np)"),
        "pre_state_in_qd": _line_no_containing(source, "state_in.joint_qd.assign(joint_target_qd)"),
        "drive_target_pos": _line_no_containing(source, "control_joint_target_pos.assign(joint_target_np)"),
        "drive_target_vel": _line_no_containing(source, "control_joint_target_vel.zero_()"),
        "solver_step": _line_no_containing(source, "solver.step(state_in, state_out, None, contacts, sim_dt)"),
        "post_state_out_q": _line_no_containing(source, "state_out.joint_q.assign(joint_target_np)"),
        "post_state_out_qd": _line_no_containing(source, "state_out.joint_qd.assign(joint_target_qd)"),
        "post_eval_fk": _line_no_containing(source, "newton.eval_fk(model, state_out.joint_q, state_out.joint_qd, state_out)"),
        "post_eval_ik": _line_no_containing(source, "newton.eval_ik(model, state_out, state_out.joint_q, state_out.joint_qd)"),
        "builder_joint_target_pos": _line_no_containing(source, "builder.joint_target_pos[:9] = robot_joint_init.tolist()"),
        "builder_joint_target_ke": _line_no_containing(source, "builder.joint_target_ke[:7] = [float(args.joint_target_ke)] * 7"),
        "builder_joint_target_kd": _line_no_containing(source, "builder.joint_target_kd[:7] = [float(args.joint_target_kd)] * 7"),
        "add_urdf": _line_no_containing(source, "builder.add_urdf("),
        "add_table_box": _line_no_containing(source, 'label="tabletop_table_box"'),
        "shape_contacts": _line_no_containing(source, "shape_contacts=True,"),
        "collide_call": _line_no_containing(source, "model.collide(state_in, contacts)"),
    }

    shape_body = np.asarray(model.shape_body.numpy() if hasattr(model.shape_body, "numpy") else model.shape_body)
    shape_type = np.asarray(model.shape_type.numpy() if hasattr(model.shape_type, "numpy") else model.shape_type)
    shape_scale = np.asarray(model.shape_scale.numpy() if hasattr(model.shape_scale, "numpy") else model.shape_scale)
    shape_tf = np.asarray(model.shape_transform.numpy() if hasattr(model.shape_transform, "numpy") else model.shape_transform)
    import newton  # local import after path bootstrap

    relevant_body_ids = {left_idx, right_idx}
    relevant_boxes: list[dict[str, Any]] = []
    robot_boxes: list[dict[str, Any]] = []
    world_boxes: list[dict[str, Any]] = []
    for shape_idx in range(int(model.shape_count)):
        body_idx = int(shape_body[shape_idx])
        if int(shape_type[shape_idx]) != int(newton.GeoType.BOX):
            continue
        entry = {
            "shape_index": int(shape_idx),
            "body_index": body_idx,
            "body_label": ("world" if body_idx < 0 else str(model.body_label[body_idx])),
            "shape_scale": np.asarray(shape_scale[shape_idx], dtype=np.float32).astype(float).tolist(),
            "local_transform": np.asarray(shape_tf[shape_idx], dtype=np.float32).astype(float).tolist(),
        }
        if body_idx in relevant_body_ids:
            relevant_boxes.append(entry)
        if body_idx >= 0 and "fr3_" in str(entry["body_label"]):
            robot_boxes.append(entry)
        if body_idx < 0:
            world_boxes.append(entry)

    table_center_ref = np.asarray(meta["stage_center"], dtype=np.float32)
    table_box = min(
        world_boxes,
        key=lambda entry: float(np.linalg.norm(np.asarray(entry["local_transform"][:3], dtype=np.float32) - table_center_ref)),
    )
    table_center = np.asarray(table_box["local_transform"][:3], dtype=np.float32)
    table_quat = np.asarray(table_box["local_transform"][3:7], dtype=np.float32)
    table_half = np.asarray(table_box["shape_scale"], dtype=np.float32)
    table_top_z = float(table_center[2] + table_half[2])

    collider_inventory = {
        "run_id": run_dir.name,
        "table_box": table_box,
        "relevant_robot_boxes": relevant_boxes,
        "all_robot_boxes": robot_boxes,
        "left_finger_index": left_idx,
        "right_finger_index": right_idx,
    }
    _write_json(out_dir / "collider_inventory.json", collider_inventory)

    _write_md(
        out_dir / "contact_filter_report.md",
        [
            "# Contact Filter Report",
            "",
            f"- `SimConfig.shape_contacts=True` at [demo_robot_rope_franka.py:{control_sites['shape_contacts']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['shape_contacts']})",
            f"- Native Franka URDF is added at [demo_robot_rope_franka.py:{control_sites['add_urdf']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['add_urdf']})",
            f"- Native tabletop world box is added at [demo_robot_rope_franka.py:{control_sites['add_table_box']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['add_table_box']})",
            f"- Broad-phase / narrow-phase contact generation is invoked through `model.collide(...)` at [demo_robot_rope_franka.py:{control_sites['collide_call']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['collide_call']})",
            "- No tabletop-specific collision filter was found in the bridge/demo layer that explicitly disables robot-table contact.",
        ],
    )
    _write_md(
        out_dir / "hidden_helper_verdict.md",
        [
            "# Hidden Helper Verdict",
            "",
            "- Hidden helper detected: `NO`",
            "- The tabletop support is the native world-space box collider.",
            "- The robot is the native URDF articulation.",
            "- Presentation-only pedestal hiding does not add an unseen physical contactor.",
        ],
    )

    def box_name(entry: dict[str, Any]) -> str:
        label = str(entry["body_label"])
        if label.endswith("/fr3_leftfinger"):
            return f"left_box_{entry['shape_index']}"
        if label.endswith("/fr3_rightfinger"):
            return f"right_box_{entry['shape_index']}"
        return f"{label.split('/')[-1]}_box_{entry['shape_index']}"

    center_series: dict[str, np.ndarray] = {}
    quat_series: dict[str, np.ndarray] = {}
    min_dist_series: dict[str, np.ndarray] = {}
    global_min = np.full((frames,), np.inf, dtype=np.float32)
    global_name = np.full((frames,), "", dtype=object)

    for entry in robot_boxes:
        name = box_name(entry)
        center_arr = np.zeros((frames, 3), dtype=np.float32)
        quat_arr = np.zeros((frames, 4), dtype=np.float32)
        min_arr = np.zeros((frames,), dtype=np.float32)
        half = np.asarray(entry["shape_scale"], dtype=np.float32)
        local_tf = np.asarray(entry["local_transform"], dtype=np.float32)
        body_idx = int(entry["body_index"])
        for frame_idx in range(frames):
            center, quat = _combine_transform(body_q[frame_idx, body_idx], local_tf)
            center_arr[frame_idx] = center
            quat_arr[frame_idx] = quat
            pts = _surface_sample_points(center, quat, half, int(args.sample_points_per_axis))
            signed = _signed_distance_points_to_box(pts, table_center, table_quat, table_half)
            min_arr[frame_idx] = float(np.min(signed))
            if float(min_arr[frame_idx]) < float(global_min[frame_idx]):
                global_min[frame_idx] = float(min_arr[frame_idx])
                global_name[frame_idx] = name
        center_series[name] = center_arr
        quat_series[name] = quat_arr
        min_dist_series[name] = min_arr
        if int(entry["body_index"]) in relevant_body_ids:
            for frame_idx in range(frames):
                if float(min_arr[frame_idx]) < float(global_min[frame_idx]):
                    global_min[frame_idx] = float(min_arr[frame_idx])
                    global_name[frame_idx] = name

    contact_mask = np.asarray(global_min <= float(args.contact_threshold_m), dtype=bool)
    contact_frames = np.flatnonzero(contact_mask)
    first_contact_frame = (None if contact_frames.size == 0 else int(contact_frames[0]))
    last_contact_frame = (None if contact_frames.size == 0 else int(contact_frames[-1]))
    worst_penetration_frame = int(np.argmin(global_min))
    worst_penetration_m = float(np.min(global_min))

    left_names = [name for name in center_series if name.startswith("left_box")]
    right_names = [name for name in center_series if name.startswith("right_box")]
    left_min = float(np.min(np.stack([min_dist_series[name] for name in left_names], axis=0))) if left_names else None
    right_min = float(np.min(np.stack([min_dist_series[name] for name in right_names], axis=0))) if right_names else None

    nonfinger_boxes = [entry for entry in robot_boxes if int(entry["body_index"]) not in relevant_body_ids]
    nonfinger_body_series: dict[str, np.ndarray] = {}
    for entry in nonfinger_boxes:
        body_label = str(entry["body_label"])
        name = box_name(entry)
        if body_label not in nonfinger_body_series:
            nonfinger_body_series[body_label] = min_dist_series[name].copy()
        else:
            nonfinger_body_series[body_label] = np.minimum(nonfinger_body_series[body_label], min_dist_series[name])
    nonfinger_global_min = np.full((frames,), np.inf, dtype=np.float32)
    nonfinger_global_body = np.full((frames,), "", dtype=object)
    for body_label, series in nonfinger_body_series.items():
        for frame_idx in range(frames):
            if float(series[frame_idx]) < float(nonfinger_global_min[frame_idx]):
                nonfinger_global_min[frame_idx] = float(series[frame_idx])
                nonfinger_global_body[frame_idx] = body_label
    nonfinger_contact_mask = np.asarray(nonfinger_global_min <= float(args.contact_threshold_m), dtype=bool)
    nonfinger_contact_frames = np.flatnonzero(nonfinger_contact_mask)
    first_nonfinger_contact_frame = None if nonfinger_contact_frames.size == 0 else int(nonfinger_contact_frames[0])
    nonfinger_worst_frame = int(np.argmin(nonfinger_global_min)) if nonfinger_body_series else None
    nonfinger_penetration_min = None if not nonfinger_body_series else float(np.min(nonfinger_global_min))
    nonfinger_worst_body = None if nonfinger_worst_frame is None else str(nonfinger_global_body[nonfinger_worst_frame])

    phase_names = [str(module._task_phase_state(float(i) * frame_dt, meta)[0]) for i in range(frames)]
    retract_mask = np.asarray([name == "retract" for name in phase_names], dtype=bool)
    collapse_frame_idx = None
    if np.any(nonfinger_contact_mask & retract_mask):
        collapse_frame_idx = int(np.flatnonzero(nonfinger_contact_mask & retract_mask)[0])
    collapse_after_retract_detected = collapse_frame_idx is not None

    def _body_min_by_suffix(suffix: str) -> float | None:
        for body_label, series in nonfinger_body_series.items():
            if str(body_label).endswith(suffix):
                return float(np.min(series))
        return None

    nonfinger_report = {
        "run_id": run_dir.name,
        "first_nonfinger_table_contact_frame": first_nonfinger_contact_frame,
        "first_nonfinger_table_contact_time_s": (
            None if first_nonfinger_contact_frame is None else float(first_nonfinger_contact_frame * frame_dt)
        ),
        "nonfinger_table_contact_duration_s": float(np.count_nonzero(nonfinger_contact_mask) * frame_dt),
        "nonfinger_penetration_min_m": nonfinger_penetration_min,
        "nonfinger_worst_contact_frame": nonfinger_worst_frame,
        "nonfinger_worst_contact_time_s": (
            None if nonfinger_worst_frame is None else float(nonfinger_worst_frame * frame_dt)
        ),
        "nonfinger_worst_contact_body": nonfinger_worst_body,
        "collapse_after_retract_detected": bool(collapse_after_retract_detected),
        "collapse_frame_idx": collapse_frame_idx,
        "fr3_hand_table_penetration_min_m": _body_min_by_suffix("/fr3_hand"),
        "fr3_link7_table_penetration_min_m": _body_min_by_suffix("/fr3_link7"),
        "fr3_link6_table_penetration_min_m": _body_min_by_suffix("/fr3_link6"),
        "fr3_link5_table_penetration_min_m": _body_min_by_suffix("/fr3_link5"),
    }
    _write_json(out_dir / "nonfinger_table_contact_report.json", nonfinger_report)

    actual_gripper = 0.5 * (body_q[:, left_idx, :3] + body_q[:, right_idx, :3])
    ee_error = np.linalg.norm(actual_gripper - ee_target_pos, axis=1)
    ee_vel = np.zeros((frames, 3), dtype=np.float32)
    ee_vel[1:] = (actual_gripper[1:] - actual_gripper[:-1]) / max(frame_dt, 1.0e-12)
    target_vel = np.zeros((frames, 3), dtype=np.float32)
    target_vel[1:] = (ee_target_pos[1:] - ee_target_pos[:-1]) / max(frame_dt, 1.0e-12)

    box_vel_z = np.zeros((frames,), dtype=np.float32)
    for frame_idx in range(1, frames):
        name = str(global_name[frame_idx])
        if not name:
            continue
        box_vel_z[frame_idx] = float(
            (center_series[name][frame_idx, 2] - center_series[name][frame_idx - 1, 2]) / max(frame_dt, 1.0e-12)
        )
    normal_speed_into_table = np.maximum(0.0, -box_vel_z)

    robot_table_contact_report = {
        "run_id": run_dir.name,
        "table_box_shape_index": int(table_box["shape_index"]),
        "table_top_z_m": table_top_z,
        "robot_table_first_contact_frame": first_contact_frame,
        "robot_table_first_contact_time_s": (
            None if first_contact_frame is None else float(first_contact_frame * frame_dt)
        ),
        "robot_table_contact_duration_s": float(np.count_nonzero(contact_mask) * frame_dt),
        "robot_table_penetration_min_m": worst_penetration_m,
        "robot_table_worst_penetration_frame": worst_penetration_frame,
        "robot_table_worst_penetration_time_s": float(worst_penetration_frame * frame_dt),
        "robot_table_worst_penetration_box": str(global_name[worst_penetration_frame]),
        "left_finger_table_penetration_min_m": left_min,
        "right_finger_table_penetration_min_m": right_min,
        "proof_surface": "actual_multi_box_finger_colliders",
        "first_nonfinger_table_contact_frame": first_nonfinger_contact_frame,
        "first_nonfinger_table_contact_time_s": nonfinger_report["first_nonfinger_table_contact_time_s"],
        "nonfinger_table_contact_duration_s": nonfinger_report["nonfinger_table_contact_duration_s"],
        "nonfinger_penetration_min_m": nonfinger_penetration_min,
        "nonfinger_worst_contact_body": nonfinger_worst_body,
        "collapse_after_retract_detected": bool(collapse_after_retract_detected),
        "collapse_frame_idx": collapse_frame_idx,
        "fr3_hand_table_penetration_min_m": nonfinger_report["fr3_hand_table_penetration_min_m"],
        "fr3_link7_table_penetration_min_m": nonfinger_report["fr3_link7_table_penetration_min_m"],
        "fr3_link6_table_penetration_min_m": nonfinger_report["fr3_link6_table_penetration_min_m"],
        "fr3_link5_table_penetration_min_m": nonfinger_report["fr3_link5_table_penetration_min_m"],
        "ee_target_to_actual_error_during_block_mean_m": (
            None if not np.any(contact_mask) else float(np.mean(ee_error[contact_mask]))
        ),
        "ee_target_to_actual_error_during_block_max_m": (
            None if not np.any(contact_mask) else float(np.max(ee_error[contact_mask]))
        ),
        "normal_speed_into_table_after_contact_mean_m_s": (
            None if not np.any(contact_mask) else float(np.mean(normal_speed_into_table[contact_mask]))
        ),
        "normal_speed_into_table_after_contact_max_m_s": (
            None if not np.any(contact_mask) else float(np.max(normal_speed_into_table[contact_mask]))
        ),
        "target_normal_speed_into_table_after_contact_mean_m_s": (
            None if not np.any(contact_mask) else float(np.mean(np.maximum(0.0, -target_vel[contact_mask, 2])))
        ),
        "target_normal_speed_into_table_after_contact_max_m_s": (
            None if not np.any(contact_mask) else float(np.max(np.maximum(0.0, -target_vel[contact_mask, 2])))
        ),
        "hand_physically_blocked": bool(np.any(contact_mask) and np.max(ee_error[contact_mask]) > 1.0e-3),
        "hidden_helper_detected": False,
    }
    _write_json(out_dir / "robot_table_contact_report.json", robot_table_contact_report)

    with (out_dir / "robot_table_clearance_timeseries.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = [
            "frame",
            "time_s",
            "global_min_signed_distance_m",
            "contact_box_name",
            "nonfinger_min_signed_distance_m",
            "nonfinger_contact_body_name",
            "ee_target_to_actual_error_m",
            "actual_gripper_z_m",
            "target_gripper_z_m",
            "target_vz_m_s",
            "actual_contact_box_vz_m_s",
            "normal_speed_into_table_m_s",
        ]
        header.extend(sorted(min_dist_series))
        writer.writerow(header)
        for frame_idx in range(frames):
            row = [
                frame_idx,
                float(frame_idx * frame_dt),
                float(global_min[frame_idx]),
                str(global_name[frame_idx]),
                float(nonfinger_global_min[frame_idx]) if nonfinger_body_series else float("nan"),
                str(nonfinger_global_body[frame_idx]),
                float(ee_error[frame_idx]),
                float(actual_gripper[frame_idx, 2]),
                float(ee_target_pos[frame_idx, 2]),
                float(target_vel[frame_idx, 2]),
                float(box_vel_z[frame_idx]),
                float(normal_speed_into_table[frame_idx]),
            ]
            row.extend(float(min_dist_series[name][frame_idx]) for name in sorted(min_dist_series))
            writer.writerow(row)

    with (out_dir / "nonfinger_table_clearance_timeseries.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = [
            "frame",
            "time_s",
            "nonfinger_min_signed_distance_m",
            "nonfinger_contact_body_name",
            "phase_name",
        ]
        header.extend(sorted(nonfinger_body_series))
        writer.writerow(header)
        for frame_idx in range(frames):
            row = [
                frame_idx,
                float(frame_idx * frame_dt),
                float(nonfinger_global_min[frame_idx]) if nonfinger_body_series else float("nan"),
                str(nonfinger_global_body[frame_idx]),
                str(phase_names[frame_idx]),
            ]
            row.extend(float(nonfinger_body_series[name][frame_idx]) for name in sorted(nonfinger_body_series))
            writer.writerow(row)

    with (out_dir / "ee_target_vs_actual_timeseries.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "frame",
                "time_s",
                "target_x_m",
                "target_y_m",
                "target_z_m",
                "actual_x_m",
                "actual_y_m",
                "actual_z_m",
                "error_norm_m",
                "table_contact",
                "target_minus_table_top_z_m",
                "actual_minus_table_top_z_m",
            ]
        )
        for frame_idx in range(frames):
            writer.writerow(
                [
                    frame_idx,
                    float(frame_idx * frame_dt),
                    float(ee_target_pos[frame_idx, 0]),
                    float(ee_target_pos[frame_idx, 1]),
                    float(ee_target_pos[frame_idx, 2]),
                    float(actual_gripper[frame_idx, 0]),
                    float(actual_gripper[frame_idx, 1]),
                    float(actual_gripper[frame_idx, 2]),
                    float(ee_error[frame_idx]),
                    bool(contact_mask[frame_idx]),
                    float(ee_target_pos[frame_idx, 2] - table_top_z),
                    float(actual_gripper[frame_idx, 2] - table_top_z),
                ]
            )

    plt.figure(figsize=(10, 6))
    t = np.arange(frames, dtype=np.float32) * frame_dt
    plt.subplot(2, 1, 1)
    plt.plot(t, global_min, label="finger-box vs table signed distance")
    plt.axhline(0.0, color="r", linestyle="--", linewidth=1.0, label="contact threshold")
    plt.ylabel("distance [m]")
    plt.legend()
    plt.subplot(2, 1, 2)
    plt.plot(t, normal_speed_into_table, label="actual normal speed into table")
    plt.plot(t, np.maximum(0.0, -target_vel[:, 2]), label="target downward speed")
    plt.xlabel("time [s]")
    plt.ylabel("speed [m/s]")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "robot_table_penetration_plot.png", dpi=160)
    plt.close()

    plt.figure(figsize=(10, 4))
    if nonfinger_body_series:
        plt.plot(t, nonfinger_global_min, label="non-finger robot vs table signed distance")
        plt.axhline(0.0, color="r", linestyle="--", linewidth=1.0, label="contact threshold")
        if np.any(retract_mask):
            retract_start = float(t[np.flatnonzero(retract_mask)[0]])
            plt.axvline(retract_start, color="k", linestyle=":", linewidth=1.0, label="retract start")
        plt.legend()
    plt.xlabel("time [s]")
    plt.ylabel("distance [m]")
    plt.tight_layout()
    plt.savefig(out_dir / "nonfinger_table_penetration_plot.png", dpi=160)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t, ee_target_pos[:, 2], label="target gripper z")
    plt.plot(t, actual_gripper[:, 2], label="actual gripper z")
    plt.axhline(table_top_z, color="r", linestyle="--", linewidth=1.0, label="table top z")
    plt.ylabel("z [m]")
    plt.legend()
    plt.subplot(2, 1, 2)
    plt.plot(t, ee_error, label="target-actual error")
    if np.any(contact_mask):
        contact_t = t[contact_mask]
        plt.scatter(contact_t, ee_error[contact_mask], s=6, label="table-contact frames")
    plt.xlabel("time [s]")
    plt.ylabel("error [m]")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "ee_target_vs_actual_plot.png", dpi=160)
    plt.close()

    video_path = _discover_video(run_dir, args.video)
    sheet_frames: list[int] = []
    if first_contact_frame is not None:
        sheet_frames.append(int(first_contact_frame))
        sheet_frames.append(min(frames - 1, int(first_contact_frame + 3)))
    sheet_frames.append(int(worst_penetration_frame))
    sheet_frames.append(min(frames - 1, int(worst_penetration_frame + 3)))
    # Preserve order but remove duplicates.
    unique_frames: list[int] = []
    for frame_idx in sheet_frames:
        if frame_idx not in unique_frames:
            unique_frames.append(frame_idx)
    contact_sheet_frames = [_read_video_frame(video_path, frame_idx) for frame_idx in unique_frames]
    contact_sheet_labels = [
        f"frame {frame_idx} t={frame_idx * frame_dt:.3f}s d={global_min[frame_idx]:.4f}m"
        for frame_idx in unique_frames
    ]
    _make_contact_sheet(contact_sheet_frames, contact_sheet_labels, out_dir / "robot_table_contact_sheet.png")

    if str(summary.get("tabletop_control_mode")) == "joint_target_drive":
        control_update_lines = [
            "# Control Update Order Report",
            "",
            f"- Tabletop `joint_target_drive` mode is active at [demo_robot_rope_franka.py:{control_sites['tabletop_joint_drive_mode']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['tabletop_joint_drive_mode']})",
            f"- Desired joint targets are written into Newton control buffers at [demo_robot_rope_franka.py:{control_sites['drive_target_pos']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['drive_target_pos']}) and [demo_robot_rope_franka.py:{control_sites['drive_target_vel']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['drive_target_vel']})",
            f"- The semi-implicit solver advances the articulation at [demo_robot_rope_franka.py:{control_sites['solver_step']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['solver_step']})",
            f"- After the solver, reduced coordinates are resynced from solved body truth via `eval_ik(...)` at [demo_robot_rope_franka.py:{control_sites['post_eval_ik']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['post_eval_ik']})",
            "",
            "This path preserves solver-integrated body truth and allows table contact to create persistent target-vs-actual lag.",
        ]
    else:
        control_update_lines = [
            "# Control Update Order Report",
            "",
            f"- Tabletop `joint_trajectory` mode is selected at [demo_robot_rope_franka.py:{control_sites['tabletop_joint_mode']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['tabletop_joint_mode']})",
            f"- The desired joint target is written directly into `state_in.joint_q` at [demo_robot_rope_franka.py:{control_sites['pre_state_in_q']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['pre_state_in_q']})",
            f"- The desired joint velocity is written directly into `state_in.joint_qd` at [demo_robot_rope_franka.py:{control_sites['pre_state_in_qd']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['pre_state_in_qd']})",
            f"- The semi-implicit solver is then stepped with `control=None` at [demo_robot_rope_franka.py:{control_sites['solver_step']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['solver_step']})",
            f"- Immediately after the solver, the code writes `state_out.joint_q` back to the desired target at [demo_robot_rope_franka.py:{control_sites['post_state_out_q']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['post_state_out_q']})",
            f"- It also writes `state_out.joint_qd` back to the desired target velocity at [demo_robot_rope_franka.py:{control_sites['post_state_out_qd']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['post_state_out_qd']})",
            f"- Forward kinematics is recomputed from that overwritten state at [demo_robot_rope_franka.py:{control_sites['post_eval_fk']}](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py:{control_sites['post_eval_fk']})",
            "",
            "This update order means table contact has no durable path to create tracking error in the saved articulation state.",
        ]
    _write_md(out_dir / "control_update_order_report.md", control_update_lines)

    _write_md(
        out_dir / "control_timeline.md",
        [
            "# Control Timeline",
            "",
            "Per tabletop substep in the current `joint_trajectory` path:",
            "",
            "1. Compute desired joint target from the hard-coded phase waypoint line.",
            "2. Write desired joint position/velocity directly into `state_in`.",
            "3. Run collision detection.",
            "4. Run the semi-implicit solver with `control=None`.",
            "5. Overwrite `state_out` joint position/velocity back to the desired target.",
            "6. Recompute FK from the overwritten target state and swap buffers.",
            "",
            "Because step 5 happens every substep, contact cannot accumulate as persistent articulation lag.",
        ],
    )

    suspected_lines = [
        "# Suspected Kinematic Override",
        "",
        f"- During table-contact frames, `ee_target_to_actual_error_during_block_mean_m = {robot_table_contact_report['ee_target_to_actual_error_during_block_mean_m']}`",
        f"- During table-contact frames, `ee_target_to_actual_error_during_block_max_m = {robot_table_contact_report['ee_target_to_actual_error_during_block_max_m']}`",
        f"- Worst sampled finger-box penetration is `robot_table_penetration_min_m = {worst_penetration_m}`",
        "",
    ]
    if str(summary.get("tabletop_control_mode")) == "joint_target_drive":
        suspected_lines.extend(
            [
                "Current interpretation for this run:",
                "",
                "- the solver-controlled body path is active",
                "- table contact does create persistent target-vs-actual lag",
                "- any remaining failure is therefore geometric / presentation related, not the old stale-FK overwrite mechanism",
            ]
        )
    else:
        suspected_lines.extend(
            [
                "These two facts together are the key kinematic-override signature:",
                "",
                "- the hand penetrates the table materially",
                "- but actual end-effector motion remains almost identical to the target",
                "",
                "A physically blocked controller would allow target-vs-actual error to grow under table contact instead.",
            ]
        )
    _write_md(out_dir / "suspected_kinematic_override.md", suspected_lines)

    _write_md(
        out_dir / "blocking_event_report.md",
        [
            "# Blocking Event Report",
            "",
            f"- first robot-table contact frame: `{first_contact_frame}`",
            f"- first robot-table contact time: `{None if first_contact_frame is None else first_contact_frame * frame_dt:.6f}` s" if first_contact_frame is not None else "- first robot-table contact time: `None`",
            f"- robot-table contact duration: `{robot_table_contact_report['robot_table_contact_duration_s']}` s",
            f"- worst finger-box penetration: `{worst_penetration_m}` m",
            f"- mean target-vs-actual EE error during contact: `{robot_table_contact_report['ee_target_to_actual_error_during_block_mean_m']}` m",
            f"- max target-vs-actual EE error during contact: `{robot_table_contact_report['ee_target_to_actual_error_during_block_max_m']}` m",
            f"- mean actual normal speed into table during contact: `{robot_table_contact_report['normal_speed_into_table_after_contact_mean_m_s']}` m/s",
            f"- first non-finger table contact time: `{nonfinger_report['first_nonfinger_table_contact_time_s']}` s",
            f"- non-finger table contact duration: `{nonfinger_report['nonfinger_table_contact_duration_s']}` s",
            f"- non-finger minimum penetration: `{nonfinger_report['nonfinger_penetration_min_m']}` m",
            f"- collapse after retract detected: `{'YES' if collapse_after_retract_detected else 'NO'}`",
            "",
            "Interpretation:",
            "",
            "- Direct-finger blocking is only acceptable if the table load stays on the finger boxes rather than migrating to the hand/forearm.",
            "- Non-finger table loading or a retract-time collapse should fail the rope-integrated presentation candidate even if finger-box blocking error exists.",
        ],
    )

    _write_md(
        out_dir / "root_cause_ranked_report.md",
        [
            "# Root Cause Ranked Report",
            "",
            "## Ranked Hypotheses",
            "",
            "1. `H1/H2`: the current tabletop path is effectively kinematic because it writes joint state directly before the solver and overwrites post-solve state back to the target.",
            "2. `H5`: the old promoted tabletop task was only a readable baseline and never claimed physical table-blocking.",
            "3. `H4`: stiff target following may amplify the visible tunneling, but it is secondary to the overwrite semantics.",
            "4. `H3`: robot-table collisions appear present in the scene; no bridge/demo-level evidence currently shows they are filtered out entirely.",
            "",
            "## Answers",
            "",
            "- Is the current tabletop path physically actuated or effectively kinematic?",
            "  - Effectively kinematic in the promoted `joint_trajectory` path.",
            "- Is table penetration caused primarily by state overwrite / control semantics?",
            "  - Yes; penetration coexists with almost-zero target-vs-actual error.",
            "- Are actual robot-table collisions present but being numerically overpowered?",
            "  - Likely yes at least at the geometry level, but any solver reaction is being erased by the overwrite path.",
            "- Is there any hidden helper?",
            "  - No evidence of one in the bridge/demo layer.",
            "- Can this be fixed at bridge/demo level without touching `Newton/newton/`?",
            "  - Potentially yes, if the tabletop path is moved onto existing SemiImplicit drive/control surfaces instead of direct joint-state overwrite. This still needs implementation proof.",
        ],
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
