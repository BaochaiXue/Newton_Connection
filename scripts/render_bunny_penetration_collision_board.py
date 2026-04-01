#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render the self-collision-OFF bunny/box all-colliding-node 2x2 board: "
            "box penalty, box total, bunny penalty, bunny total."
        )
    )
    parser.add_argument("--box-summary", "--box-detector-summary", dest="box_summary", type=Path, required=True)
    parser.add_argument("--bunny-summary", "--bunny-detector-summary", dest="bunny_summary", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument(
        "--force-percentile",
        type=float,
        default=98.0,
        help="Shared percentile cap used to define the display scale for each force family.",
    )
    parser.add_argument(
        "--max-arrow-world-len",
        type=float,
        default=0.04,
        help="Maximum displayed arrow length in world units after percentile capping.",
    )
    parser.add_argument("--board-width", type=int, default=1920)
    parser.add_argument("--board-height", type=int, default=1080)
    return parser.parse_args()


def _camera_basis_from_pitch_yaw(pitch_deg: float, yaw_deg: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pitch = np.deg2rad(float(pitch_deg))
    yaw = np.deg2rad(float(yaw_deg))
    forward = np.asarray(
        [
            np.cos(pitch) * np.cos(yaw),
            np.cos(pitch) * np.sin(yaw),
            np.sin(pitch),
        ],
        dtype=np.float32,
    )
    forward /= max(np.linalg.norm(forward), 1.0e-8)
    world_up = np.asarray([0.0, 0.0, 1.0], dtype=np.float32)
    right = np.cross(forward, world_up).astype(np.float32, copy=False)
    if np.linalg.norm(right) <= 1.0e-8:
        right = np.asarray([1.0, 0.0, 0.0], dtype=np.float32)
    right /= max(np.linalg.norm(right), 1.0e-8)
    up = np.cross(right, forward).astype(np.float32, copy=False)
    up /= max(np.linalg.norm(up), 1.0e-8)
    return forward, right, up


def _project_world_to_screen(
    point_world: np.ndarray,
    *,
    cam_pos: np.ndarray,
    pitch_deg: float,
    yaw_deg: float,
    fov_deg: float,
    width: int,
    height: int,
) -> tuple[float, float] | None:
    forward, right, up = _camera_basis_from_pitch_yaw(pitch_deg, yaw_deg)
    v = np.asarray(point_world, dtype=np.float32) - np.asarray(cam_pos, dtype=np.float32)
    z = float(np.dot(v, forward))
    if z <= 1.0e-6:
        return None
    x = float(np.dot(v, right))
    y = float(np.dot(v, up))
    aspect = float(width) / max(float(height), 1.0)
    tan_half = np.tan(np.deg2rad(float(fov_deg)) * 0.5)
    if tan_half <= 1.0e-8:
        return None
    ndc_x = x / (z * tan_half * aspect)
    ndc_y = y / (z * tan_half)
    px = (ndc_x * 0.5 + 0.5) * float(width)
    py = (0.5 - ndc_y * 0.5) * float(height)
    return float(px), float(py)


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _force_color_bgr(magnitude: float, cap: float) -> tuple[int, int, int]:
    if cap <= 1.0e-12:
        value = 0
    else:
        value = int(np.clip(round(255.0 * float(magnitude) / float(cap)), 0, 255))
    color = cv2.applyColorMap(np.asarray([[value]], dtype=np.uint8), cv2.COLORMAP_JET)[0, 0]
    return int(color[0]), int(color[1]), int(color[2])


def _draw_header_block(
    panel: np.ndarray,
    *,
    title: str,
    subtitle: str,
    footer: str,
) -> None:
    cv2.rectangle(panel, (0, 0), (panel.shape[1], 74), (0, 0, 0), thickness=-1)
    cv2.putText(panel, title, (14, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.82, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(panel, subtitle, (14, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.54, (220, 220, 220), 1, cv2.LINE_AA)
    cv2.rectangle(panel, (0, panel.shape[0] - 34), (panel.shape[1], panel.shape[0]), (0, 0, 0), thickness=-1)
    cv2.putText(
        panel,
        footer,
        (14, panel.shape[0] - 11),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.53,
        (230, 230, 230),
        1,
        cv2.LINE_AA,
    )


def _draw_colorbar(panel: np.ndarray, *, label: str, cap: float, top: int = 64) -> None:
    bar_w = 170
    bar_h = 18
    x1 = panel.shape[1] - 18
    x0 = x1 - bar_w
    y0 = top
    y1 = y0 + bar_h
    gradient = np.linspace(0, 255, bar_w, dtype=np.uint8)[None, :]
    bar = cv2.applyColorMap(gradient, cv2.COLORMAP_JET)
    bar = cv2.resize(bar, (bar_w, bar_h), interpolation=cv2.INTER_LINEAR)
    panel[y0:y1, x0:x1] = bar
    cv2.rectangle(panel, (x0, y0), (x1, y1), (255, 255, 255), thickness=1)
    cv2.putText(panel, label, (x0, y0 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (245, 245, 245), 1, cv2.LINE_AA)
    cv2.putText(panel, "0", (x0, y1 + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (235, 235, 235), 1, cv2.LINE_AA)
    cv2.putText(
        panel,
        f"{cap:.3f} N",
        (x1 - 78, y1 + 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (235, 235, 235),
        1,
        cv2.LINE_AA,
    )


def _load_frame(frame_dir: Path, video_frame_index: int, panel_size: tuple[int, int]) -> np.ndarray:
    frame_path = frame_dir / f"frame_{int(video_frame_index):05d}.png"
    frame_bgr = cv2.imread(str(frame_path), cv2.IMREAD_COLOR)
    if frame_bgr is None:
        raise FileNotFoundError(f"missing render frame: {frame_path}")
    panel_w, panel_h = panel_size
    if frame_bgr.shape[1] != panel_w or frame_bgr.shape[0] != panel_h:
        frame_bgr = cv2.resize(frame_bgr, (panel_w, panel_h), interpolation=cv2.INTER_AREA)
    return frame_bgr


def _gather_case_data(summary_path: Path) -> dict[str, object]:
    summary = _load_json(summary_path)
    npz = np.load(Path(str(summary["detector_npz"])))
    return {
        "summary_path": str(summary_path.resolve()),
        "summary": summary,
        "npz": npz,
        "frame_dir": Path(str(summary["render_frames_dir"])).expanduser().resolve(),
        "clip_video_frame_indices": np.asarray(summary["clip_video_frame_indices"], dtype=np.int32),
        "clip_render_sim_frame_indices": np.asarray(summary["clip_render_sim_frame_indices"], dtype=np.int32),
    }


def _family_cap(case_payloads: list[dict[str, object]], family_key: str, percentile: float) -> float:
    values: list[np.ndarray] = []
    for payload in case_payloads:
        npz = payload["npz"]
        sim_indices = np.asarray(payload["clip_render_sim_frame_indices"], dtype=np.int32)
        mask = np.asarray(npz["rigid_force_contact_mask"][sim_indices], dtype=bool)
        norms = np.asarray(npz[f"{family_key}_norm"][sim_indices], dtype=np.float32)
        if np.any(mask):
            values.append(norms[mask])
    if not values:
        return 1.0
    merged = np.concatenate(values, axis=0)
    if merged.size == 0:
        return 1.0
    cap = float(np.percentile(merged, float(percentile)))
    if cap <= 1.0e-8:
        cap = float(np.max(merged))
    return max(cap, 1.0e-6)


def _draw_force_field(
    panel: np.ndarray,
    *,
    particle_q: np.ndarray,
    force_vec: np.ndarray,
    rigid_force_contact_mask: np.ndarray,
    cam_pos: np.ndarray,
    pitch_deg: float,
    yaw_deg: float,
    fov_deg: float,
    force_cap: float,
    max_arrow_world_len: float,
) -> None:
    if not np.any(rigid_force_contact_mask):
        return
    panel_h, panel_w = panel.shape[:2]
    indices = np.flatnonzero(rigid_force_contact_mask)
    points = np.asarray(particle_q[indices], dtype=np.float32)
    forces = np.asarray(force_vec[indices], dtype=np.float32)
    mags = np.linalg.norm(forces, axis=1)
    original = panel.copy()
    overlay = panel.copy()
    base_scale = float(max_arrow_world_len) / max(float(force_cap), 1.0e-12)

    for point_world, force_world, magnitude in zip(points, forces, mags):
        start = _project_world_to_screen(
            point_world,
            cam_pos=cam_pos,
            pitch_deg=pitch_deg,
            yaw_deg=yaw_deg,
            fov_deg=fov_deg,
            width=panel_w,
            height=panel_h,
        )
        if start is None:
            continue
        sx, sy = int(round(start[0])), int(round(start[1]))
        if sx < -8 or sy < -8 or sx >= panel_w + 8 or sy >= panel_h + 8:
            continue
        color = _force_color_bgr(float(magnitude), float(force_cap))
        cv2.circle(overlay, (sx, sy), 2, color, thickness=-1, lineType=cv2.LINE_AA)
        if magnitude <= 1.0e-12:
            continue
        scale = base_scale * min(1.0, float(force_cap) / max(float(magnitude), 1.0e-12))
        arrow_end_world = point_world + force_world * float(scale)
        end = _project_world_to_screen(
            arrow_end_world,
            cam_pos=cam_pos,
            pitch_deg=pitch_deg,
            yaw_deg=yaw_deg,
            fov_deg=fov_deg,
            width=panel_w,
            height=panel_h,
        )
        if end is None:
            continue
        ex, ey = int(round(end[0])), int(round(end[1]))
        if abs(ex - sx) + abs(ey - sy) < 2:
            continue
        cv2.arrowedLine(
            overlay,
            (sx, sy),
            (ex, ey),
            color,
            thickness=1,
            line_type=cv2.LINE_AA,
            tipLength=0.25,
        )
    panel[:] = cv2.addWeighted(overlay, 0.82, original, 0.18, 0.0)


def _render_panel(
    *,
    case_label: str,
    family_label: str,
    frame_dir: Path,
    video_frame_index: int,
    sim_frame_index: int,
    panel_size: tuple[int, int],
    detector_npz,
    force_key: str,
    force_cap: float,
    max_arrow_world_len: float,
    camera: dict[str, object],
    colliding_count: int,
    first_contact_frame: int | None,
    hold: bool,
) -> np.ndarray:
    panel = _load_frame(frame_dir, int(video_frame_index), panel_size)
    particle_q = np.asarray(detector_npz["particle_q"][int(sim_frame_index)], dtype=np.float32)
    rigid_mask = np.asarray(detector_npz["rigid_force_contact_mask"][int(sim_frame_index)], dtype=bool)
    force_vec = np.asarray(detector_npz[force_key][int(sim_frame_index)], dtype=np.float32)
    _draw_force_field(
        panel,
        particle_q=particle_q,
        force_vec=force_vec,
        rigid_force_contact_mask=rigid_mask,
        cam_pos=np.asarray(camera["render_camera_pos"], dtype=np.float32),
        pitch_deg=float(camera["render_camera_pitch_deg"]),
        yaw_deg=float(camera["render_camera_yaw_deg"]),
        fov_deg=float(camera["render_camera_fov_deg"]),
        force_cap=float(force_cap),
        max_arrow_world_len=float(max_arrow_world_len),
    )
    _draw_header_block(
        panel,
        title=f"{case_label} | {family_label}",
        subtitle="all rigid force-active cloth nodes",
        footer=(
            f"sim frame {int(sim_frame_index)} | colliding nodes {int(colliding_count)}"
            + (f" | first collision {int(first_contact_frame)}" if first_contact_frame is not None else "")
        ),
    )
    _draw_colorbar(panel, label=f"{family_label} magnitude", cap=float(force_cap))
    if hold:
        cv2.rectangle(panel, (panel.shape[1] - 112, panel.shape[0] - 66), (panel.shape[1] - 12, panel.shape[0] - 38), (0, 0, 0), thickness=-1)
        cv2.putText(panel, "HOLD", (panel.shape[1] - 98, panel.shape[0] - 46), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 225, 120), 2, cv2.LINE_AA)
    if first_contact_frame is not None and int(sim_frame_index) == int(first_contact_frame):
        cv2.rectangle(panel, (14, 86), (220, 112), (0, 0, 0), thickness=-1)
        cv2.putText(panel, "FIRST COLLISION", (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.56, (255, 225, 120), 2, cv2.LINE_AA)
    return panel


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    box_case = _gather_case_data(args.box_summary.expanduser().resolve())
    bunny_case = _gather_case_data(args.bunny_summary.expanduser().resolve())
    cases = {"box_control": box_case, "bunny_baseline": bunny_case}

    render_fps = float(box_case["summary"]["camera"]["render_fps"])
    if abs(render_fps - float(bunny_case["summary"]["camera"]["render_fps"])) > 1.0e-6:
        raise RuntimeError("box and bunny detector summaries disagree on render_fps")

    panel_w = int(args.board_width) // 2
    panel_h = int(args.board_height) // 2
    board_w = panel_w * 2
    board_h = panel_h * 2
    panel_size = (panel_w, panel_h)

    penalty_cap = _family_cap([box_case, bunny_case], "penalty_force", float(args.force_percentile))
    total_cap = _family_cap([box_case, bunny_case], "total_force", float(args.force_percentile))
    board_frame_count = max(
        int(box_case["clip_video_frame_indices"].shape[0]),
        int(bunny_case["clip_video_frame_indices"].shape[0]),
    )

    board_video_path = out_dir / "collision_force_board_2x2.mp4"
    writer = cv2.VideoWriter(
        str(board_video_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        render_fps,
        (board_w, board_h),
    )
    if not writer.isOpened():
        raise RuntimeError(f"failed to open video writer: {board_video_path}")

    first_frame_path = out_dir / "collision_force_board_2x2_first_frame.png"
    board_frames_written = 0
    try:
        for board_idx in range(board_frame_count):
            board = np.zeros((board_h, board_w, 3), dtype=np.uint8)
            panel_specs = [
                ("box_control", "BOX", "Penalty force", "penalty_force", penalty_cap, (0, 0)),
                ("box_control", "BOX", "Total force", "total_force", total_cap, (0, panel_w)),
                ("bunny_baseline", "BUNNY", "Penalty force", "penalty_force", penalty_cap, (panel_h, 0)),
                ("bunny_baseline", "BUNNY", "Total force", "total_force", total_cap, (panel_h, panel_w)),
            ]
            for case_key, case_label, family_label, force_key, force_cap, (y0, x0) in panel_specs:
                case_payload = cases[case_key]
                clip_len = int(case_payload["clip_video_frame_indices"].shape[0])
                source_idx = min(int(board_idx), max(0, clip_len - 1))
                hold = int(board_idx) >= clip_len
                sim_frame_index = int(case_payload["clip_render_sim_frame_indices"][source_idx])
                panel = _render_panel(
                    case_label=case_label,
                    family_label=family_label,
                    frame_dir=case_payload["frame_dir"],
                    video_frame_index=int(case_payload["clip_video_frame_indices"][source_idx]),
                    sim_frame_index=sim_frame_index,
                    panel_size=panel_size,
                    detector_npz=case_payload["npz"],
                    force_key=force_key,
                    force_cap=force_cap,
                    max_arrow_world_len=float(args.max_arrow_world_len),
                    camera=case_payload["summary"]["camera"],
                    colliding_count=int(np.sum(np.asarray(case_payload["npz"]["rigid_force_contact_mask"][sim_frame_index], dtype=np.int32))),
                    first_contact_frame=case_payload["summary"].get("first_force_contact_frame_index"),
                    hold=hold,
                )
                board[y0 : y0 + panel_h, x0 : x0 + panel_w] = panel
            writer.write(board)
            if board_idx == 0:
                cv2.imwrite(str(first_frame_path), board)
            board_frames_written += 1
            if (board_idx + 1) % 15 == 0 or board_idx + 1 == board_frame_count:
                print(f"[render_bunny_penetration_collision_board] frame {board_idx + 1}/{board_frame_count}", flush=True)
    finally:
        writer.release()

    exact_ratios: list[float] = []
    reused_ratios: list[float] = []
    per_case: dict[str, object] = {}
    for case_key, case_payload in cases.items():
        clip_len = int(case_payload["clip_video_frame_indices"].shape[0])
        hold_count = max(0, board_frame_count - clip_len)
        exact_ratio = float(clip_len) / max(float(board_frame_count), 1.0)
        reused_ratio = float(hold_count) / max(float(board_frame_count), 1.0)
        exact_ratios.append(exact_ratio)
        reused_ratios.append(reused_ratio)
        summary = case_payload["summary"]
        per_case[case_key] = {
            "detector_summary_path": case_payload["summary_path"],
            "detector_npz_path": str(Path(str(summary["detector_npz"])).expanduser().resolve()),
            "render_frames_dir": str(case_payload["frame_dir"]),
            "selected_video_frame_indices": [int(v) for v in case_payload["clip_video_frame_indices"].tolist()],
            "selected_render_sim_frame_indices": [int(v) for v in case_payload["clip_render_sim_frame_indices"].tolist()],
            "first_force_contact_frame_index": summary.get("first_force_contact_frame_index"),
            "clip_end_frame_index": summary.get("clip_end_frame_index"),
            "clip_video_frame_count": clip_len,
            "hold_frame_count": hold_count,
            "exact_mapping_ratio_full_display_interval": exact_ratio,
            "reused_mapping_ratio_full_display_interval": reused_ratio,
        }

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "board_video": str(board_video_path),
        "board_first_frame": str(first_frame_path),
        "render_fps": render_fps,
        "board_width": board_w,
        "board_height": board_h,
        "panel_width": panel_w,
        "panel_height": panel_h,
        "board_frame_count": board_frames_written,
        "panel_order": ["top_left", "top_right", "bottom_left", "bottom_right"],
        "panel_semantics": {
            "top_left": "box_penalty",
            "top_right": "box_total",
            "bottom_left": "bunny_penalty",
            "bottom_right": "bunny_total",
        },
        "panel_labels_present": True,
        "all_colliding_nodes_main_board": True,
        "node_mask_semantics": "rigid_force_contact_mask",
        "node_selection_mode": "rigid_force_contact_mask",
        "force_definitions": {
            "penalty_force": "f_external_total on the current frame; used only on nodes in rigid_force_contact_mask",
            "total_force": "f_internal_total + f_external_total + mass * gravity_vec",
            "drag_note": "Drag is omitted from total force when drag is applied as a post-step velocity correction instead of an accumulated force.",
        },
        "colorbar_present": True,
        "legend_present": True,
        "hold_annotation_present": True,
        "color_scale": {
            "percentile_cap_rule": f"{float(args.force_percentile):.1f}th percentile over all rigid_force_contact_mask nodes across both cases for the displayed clip",
            "penalty_force_cap_n": penalty_cap,
            "total_force_cap_n": total_cap,
            "max_arrow_world_len": float(args.max_arrow_world_len),
            "colormap": "cv2.COLORMAP_JET, with red as high force",
        },
        "exact_mapping_ratio_full_display_interval": float(min(exact_ratios)) if exact_ratios else 1.0,
        "reused_mapping_ratio_full_display_interval": float(max(reused_ratios)) if reused_ratios else 0.0,
        "cases": per_case,
    }
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[render_bunny_penetration_collision_board] video={board_video_path}", flush=True)
    print(f"[render_bunny_penetration_collision_board] summary={summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
