#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import pickle
import sys
from pathlib import Path
from typing import Any

import numpy as np
import warp as wp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a per-frame collision-force rollout bundle for the cloth box/bunny OFF cases, "
            "saving geometry-contact masks, force-contact masks, penalty force, and total force."
        )
    )
    parser.add_argument("--bundle", type=Path, required=True, help="force_render_bundle.pkl from a phenomenon run")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument(
        "--post-contact-seconds",
        type=float,
        default=1.0,
        help="Clip end rule used for the promoted board: one second after first force-active collision.",
    )
    return parser.parse_args()


def _first_true_frame(mask_2d: np.ndarray) -> int | None:
    active = np.any(np.asarray(mask_2d, dtype=bool), axis=1)
    indices = np.flatnonzero(active)
    return int(indices[0]) if indices.size else None


def _pack_mask_indices(mask_2d: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mask = np.asarray(mask_2d, dtype=bool)
    counts = np.sum(mask, axis=1, dtype=np.int32)
    ptr = np.zeros((mask.shape[0] + 1,), dtype=np.int32)
    ptr[1:] = np.cumsum(counts, dtype=np.int32)
    flat = np.flatnonzero(mask.reshape(-1)).astype(np.int64, copy=False)
    if flat.size:
        flat = (flat % mask.shape[1]).astype(np.int32, copy=False)
    else:
        flat = np.zeros((0,), dtype=np.int32)
    return ptr.astype(np.int32, copy=False), flat


def _selected_video_frame_indices(
    *,
    render_indices: np.ndarray,
    first_force_contact_frame: int | None,
    sim_frame_dt: float,
    post_contact_seconds: float,
) -> tuple[np.ndarray, np.ndarray, int]:
    render_indices = np.asarray(render_indices, dtype=np.int32).reshape(-1)
    if render_indices.size == 0:
        return np.zeros((0,), dtype=np.int32), np.zeros((0,), dtype=np.int32), 0
    if first_force_contact_frame is None or float(post_contact_seconds) <= 0.0:
        video_idx = np.arange(render_indices.shape[0], dtype=np.int32)
        return video_idx, render_indices.copy(), int(render_indices[-1])

    extra_frames = int(round(float(post_contact_seconds) / max(float(sim_frame_dt), 1.0e-12)))
    clip_end_frame = int(first_force_contact_frame) + max(0, extra_frames)
    chosen_video: list[int] = []
    chosen_sim: list[int] = []
    for video_idx, sim_idx in enumerate(render_indices.tolist()):
        if int(sim_idx) > int(clip_end_frame):
            break
        chosen_video.append(int(video_idx))
        chosen_sim.append(int(sim_idx))
    if not chosen_video:
        chosen_video = [0]
        chosen_sim = [int(render_indices[0])]
    return (
        np.asarray(chosen_video, dtype=np.int32),
        np.asarray(chosen_sim, dtype=np.int32),
        int(min(int(clip_end_frame), int(chosen_sim[-1]))),
    )


def main() -> int:
    args = parse_args()
    bundle_path = args.bundle.expanduser().resolve()
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parents[1]
    demos_dir = repo_root / "Newton" / "phystwin_bridge" / "demos"
    sys.path.insert(0, str(demos_dir))
    import demo_cloth_bunny_drop_without_self_contact as demo  # noqa: PLC0415

    with bundle_path.open("rb") as handle:
        bundle = pickle.load(handle)

    run_args = bundle["args"]
    ir_obj = bundle["ir_obj"]
    sim_data = bundle["render_sim_data"]
    device = demo.newton_import_ir.resolve_device(str(bundle["device"]))
    render_frames_dir_raw = str(bundle.get("render_frames_dir", "") or "").strip()
    render_frames_dir = Path(render_frames_dir_raw).expanduser().resolve() if render_frames_dir_raw else None

    wp.init()
    model, meta, n_obj = demo.build_model(ir_obj, run_args, device)
    explicit_context = demo._make_explicit_force_snapshot_context(
        model=model,
        ir_obj=ir_obj,
        args=run_args,
        device=device,
        n_obj=n_obj,
    )
    target_only_args = copy.deepcopy(run_args)
    target_only_args.add_ground_plane = False
    target_model, target_meta, target_n_obj = demo.build_model(ir_obj, target_only_args, device)
    if int(target_n_obj) != int(n_obj):
        raise RuntimeError(
            f"target-only model particle count mismatch: target={target_n_obj} full={n_obj}"
        )
    target_only_context = demo._make_explicit_force_snapshot_context(
        model=target_model,
        ir_obj=ir_obj,
        args=target_only_args,
        device=device,
        n_obj=n_obj,
    )

    particle_q_all = np.asarray(sim_data["particle_q_all"], dtype=np.float32)
    particle_qd_all = np.asarray(sim_data["particle_qd_all"], dtype=np.float32)
    body_q_all = np.asarray(sim_data["body_q"], dtype=np.float32)
    body_qd_all = np.asarray(sim_data["body_qd"], dtype=np.float32)
    sim_frame_dt = float(sim_data["sim_dt"]) * float(sim_data["substeps"])
    n_frames = int(particle_q_all.shape[0])
    render_indices = np.asarray(sim_data.get("render_output_frame_indices"), dtype=np.int32).reshape(-1)
    if render_indices.size == 0:
        raise RuntimeError(f"{bundle_path} is missing render_output_frame_indices")

    snapshots: list[dict[str, Any]] = []
    for frame_idx in range(n_frames):
        snapshot = demo._capture_force_snapshot_from_explicit_state(
            model=model,
            meta=meta,
            ir_obj=ir_obj,
            args=run_args,
            device=device,
            n_obj=n_obj,
            frame_index=int(frame_idx),
            substep_index_in_frame=0,
            global_substep_index=int(frame_idx) * int(sim_data["substeps"]),
            sim_time=float(frame_idx) * sim_frame_dt,
            particle_q=particle_q_all[frame_idx],
            particle_qd=particle_qd_all[frame_idx],
            body_q=body_q_all[frame_idx],
            body_qd=body_qd_all[frame_idx],
            explicit_context=explicit_context,
        )
        target_only_snapshot = demo._capture_force_snapshot_from_explicit_state(
            model=target_model,
            meta=target_meta,
            ir_obj=ir_obj,
            args=target_only_args,
            device=device,
            n_obj=n_obj,
            frame_index=int(frame_idx),
            substep_index_in_frame=0,
            global_substep_index=int(frame_idx) * int(sim_data["substeps"]),
            sim_time=float(frame_idx) * sim_frame_dt,
            particle_q=particle_q_all[frame_idx],
            particle_qd=particle_qd_all[frame_idx],
            body_q=body_q_all[frame_idx],
            body_qd=body_qd_all[frame_idx],
            explicit_context=target_only_context,
        )
        snapshot["rigid_target_only_f_external_total"] = np.asarray(
            target_only_snapshot["f_external_total"], dtype=np.float32
        )
        snapshots.append(snapshot)
        if (frame_idx + 1) % 10 == 0 or frame_idx + 1 == n_frames:
            print(f"[build_bunny_collision_force_bundle] frame {frame_idx + 1}/{n_frames}", flush=True)

    geom_contact_mask = np.stack(
        [np.asarray(snapshot["geom_contact_mask"], dtype=bool) for snapshot in snapshots],
        axis=0,
    )
    force_contact_mask = np.stack(
        [np.asarray(snapshot["force_contact_mask"], dtype=bool) for snapshot in snapshots],
        axis=0,
    )
    target_penalty_force = np.stack(
        [np.asarray(snapshot["rigid_target_only_f_external_total"], dtype=np.float32) for snapshot in snapshots],
        axis=0,
    )
    target_force_contact_mask = (
        np.linalg.norm(target_penalty_force, axis=2).astype(np.float32, copy=False) > 1.0e-8
    )
    rigid_force_contact_mask = np.logical_and(geom_contact_mask, target_force_contact_mask)
    particle_q = np.stack([np.asarray(snapshot["particle_q"], dtype=np.float32) for snapshot in snapshots], axis=0)
    penalty_force = target_penalty_force
    total_force = np.stack(
        [
            (
                np.asarray(snapshot["f_internal_total"], dtype=np.float32)
                + np.asarray(snapshot["f_external_total"], dtype=np.float32)
                + np.asarray(snapshot["particle_mass"], dtype=np.float32)[:, None]
                * np.asarray(snapshot["gravity_vec"], dtype=np.float32)[None, :]
            ).astype(np.float32, copy=False)
            for snapshot in snapshots
        ],
        axis=0,
    )
    penalty_force_norm = np.linalg.norm(penalty_force, axis=2).astype(np.float32, copy=False)
    total_force_norm = np.linalg.norm(total_force, axis=2).astype(np.float32, copy=False)
    sim_frame_indices = np.arange(n_frames, dtype=np.int32)
    sim_time_s = (sim_frame_indices.astype(np.float32) * float(sim_frame_dt)).astype(np.float32, copy=False)
    first_geom_contact_frame = _first_true_frame(geom_contact_mask)
    first_force_contact_frame = _first_true_frame(rigid_force_contact_mask)
    clip_video_frame_indices, clip_render_sim_frame_indices, clip_end_frame = _selected_video_frame_indices(
        render_indices=render_indices,
        first_force_contact_frame=first_force_contact_frame,
        sim_frame_dt=sim_frame_dt,
        post_contact_seconds=float(args.post_contact_seconds),
    )
    first_geom_contact_video_frame = (
        int(np.flatnonzero(render_indices >= int(first_geom_contact_frame))[0])
        if first_geom_contact_frame is not None and np.any(render_indices >= int(first_geom_contact_frame))
        else None
    )
    first_force_contact_video_frame = (
        int(np.flatnonzero(render_indices >= int(first_force_contact_frame))[0])
        if first_force_contact_frame is not None and np.any(render_indices >= int(first_force_contact_frame))
        else None
    )

    geom_ptr, geom_flat = _pack_mask_indices(geom_contact_mask)
    force_ptr, force_flat = _pack_mask_indices(force_contact_mask)
    target_force_ptr, target_force_flat = _pack_mask_indices(target_force_contact_mask)
    rigid_ptr, rigid_flat = _pack_mask_indices(rigid_force_contact_mask)

    npz_path = out_dir / "collision_force_rollout_bundle.npz"
    np.savez_compressed(
        npz_path,
        sim_frame_indices=sim_frame_indices,
        sim_time_s=sim_time_s,
        particle_q=particle_q,
        geom_contact_mask=geom_contact_mask.astype(np.bool_, copy=False),
        force_contact_mask=force_contact_mask.astype(np.bool_, copy=False),
        rigid_force_contact_mask=rigid_force_contact_mask.astype(np.bool_, copy=False),
        geom_contact_index_ptr=geom_ptr,
        geom_contact_index_flat=geom_flat,
        force_contact_index_ptr=force_ptr,
        force_contact_index_flat=force_flat,
        target_force_contact_mask=target_force_contact_mask.astype(np.bool_, copy=False),
        target_force_contact_index_ptr=target_force_ptr,
        target_force_contact_index_flat=target_force_flat,
        rigid_force_contact_index_ptr=rigid_ptr,
        rigid_force_contact_index_flat=rigid_flat,
        penalty_force=penalty_force,
        total_force=total_force,
        penalty_force_norm=penalty_force_norm,
        total_force_norm=total_force_norm,
        render_output_frame_indices=render_indices.astype(np.int32, copy=False),
        clip_video_frame_indices=clip_video_frame_indices.astype(np.int32, copy=False),
        clip_render_sim_frame_indices=clip_render_sim_frame_indices.astype(np.int32, copy=False),
        first_geom_contact_flag=(sim_frame_indices == int(first_geom_contact_frame)).astype(np.bool_, copy=False)
        if first_geom_contact_frame is not None
        else np.zeros((n_frames,), dtype=np.bool_),
        first_force_contact_flag=(sim_frame_indices == int(first_force_contact_frame)).astype(np.bool_, copy=False)
        if first_force_contact_frame is not None
        else np.zeros((n_frames,), dtype=np.bool_),
    )

    summary = {
        "bundle_path": str(bundle_path),
        "detector_npz": str(npz_path),
        "npz_path": str(npz_path),
        "run_out_dir": str(Path(run_args.out_dir).expanduser().resolve()),
        "source_scene_path": str(Path(str(bundle.get("scene_npz_path", ""))).expanduser().resolve()) if str(bundle.get("scene_npz_path", "")).strip() else None,
        "source_summary_path": str(Path(str(bundle.get("summary_json_path", ""))).expanduser().resolve()) if str(bundle.get("summary_json_path", "")).strip() else None,
        "render_frames_dir": None if render_frames_dir is None else str(render_frames_dir),
        "rigid_shape": str(meta.get("rigid_shape", "")),
        "camera": {
            "render_camera_pos": [float(v) for v in np.asarray(sim_data.get("render_camera_pos", np.asarray(run_args.camera_pos, dtype=np.float32)), dtype=np.float32).ravel()],
            "render_camera_pitch_deg": float(sim_data.get("render_camera_pitch_deg", float(run_args.camera_pitch))),
            "render_camera_yaw_deg": float(sim_data.get("render_camera_yaw_deg", float(run_args.camera_yaw))),
            "render_camera_fov_deg": float(sim_data.get("render_camera_fov_deg", float(run_args.camera_fov))),
            "screen_width": int(run_args.screen_width),
            "screen_height": int(run_args.screen_height),
            "render_fps": float(run_args.render_fps),
        },
        "all_colliding_nodes_main_board": True,
        "node_selection_mode": "rigid_force_contact_mask",
        "contact_mask_semantics": {
            "geom_contact_mask": "rigid-target geometry-contact mask from signed penetration against the chosen rigid target",
            "force_contact_mask": "nonzero full-scene external-force mask on the current cloth node",
            "target_force_contact_mask": "nonzero rigid-target-only penalty mask from explicit re-evaluation with add_ground_plane=False",
            "rigid_force_contact_mask": "geom_contact_mask AND target_force_contact_mask; this is the main board node set",
        },
        "force_definitions": {
            "penalty_force": "target-only f_external_total from explicit re-evaluation with add_ground_plane=False; used only on nodes in rigid_force_contact_mask",
            "total_force": "f_internal_total + f_external_total + mass * gravity_vec",
            "drag_note": "Drag is omitted from total force when drag is applied as a post-step velocity correction instead of an accumulated force.",
        },
        "sim_frame_dt_s": float(sim_frame_dt),
        "sim_frame_count": int(n_frames),
        "particle_count": int(particle_q.shape[1]),
        "first_geom_contact_frame_index": first_geom_contact_frame,
        "first_force_contact_frame_index": first_force_contact_frame,
        "first_geom_contact_video_frame_index": first_geom_contact_video_frame,
        "first_force_contact_video_frame_index": first_force_contact_video_frame,
        "clip_end_frame_index": int(clip_end_frame),
        "clip_video_frame_count": int(clip_video_frame_indices.shape[0]),
        "clip_render_sim_frame_indices": [int(v) for v in clip_render_sim_frame_indices.tolist()],
        "clip_video_frame_indices": [int(v) for v in clip_video_frame_indices.tolist()],
        "geom_contact_node_count_per_frame": [int(v) for v in np.sum(geom_contact_mask, axis=1, dtype=np.int32).tolist()],
        "force_contact_node_count_per_frame": [int(v) for v in np.sum(force_contact_mask, axis=1, dtype=np.int32).tolist()],
        "target_force_contact_node_count_per_frame": [int(v) for v in np.sum(target_force_contact_mask, axis=1, dtype=np.int32).tolist()],
        "rigid_force_contact_node_count_per_frame": [int(v) for v in np.sum(rigid_force_contact_mask, axis=1, dtype=np.int32).tolist()],
        "max_penalty_force_n": float(np.max(penalty_force_norm)) if penalty_force_norm.size else 0.0,
        "max_total_force_n": float(np.max(total_force_norm)) if total_force_norm.size else 0.0,
    }
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[build_bunny_collision_force_bundle] npz={npz_path}", flush=True)
    print(f"[build_bunny_collision_force_bundle] summary={summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
