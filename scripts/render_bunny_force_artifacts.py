#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path

import numpy as np
import warp as wp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render bunny force-diagnostic artifacts from a serialized bundle.")
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument(
        "--force-dump-dir",
        type=Path,
        default=None,
        help="Optional override for where force-diagnostic artifacts should be written.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle_path = args.bundle.expanduser().resolve()
    repo_root = Path(__file__).resolve().parents[1]
    demos_dir = repo_root / "Newton" / "phystwin_bridge" / "demos"
    sys.path.insert(0, str(demos_dir))

    import demo_cloth_bunny_drop_without_self_contact as demo  # noqa: PLC0415

    with bundle_path.open("rb") as handle:
        bundle = pickle.load(handle)

    render_args = bundle["args"]
    if args.force_dump_dir is not None:
        render_args.force_dump_dir = args.force_dump_dir.expanduser().resolve()
    device = str(bundle["device"])
    ir_obj = bundle["ir_obj"]
    diag_snapshot = bundle["diag_snapshot"]
    sequence_snapshots = bundle.get("sequence_snapshots", [])
    render_sim_data = bundle.get("render_sim_data")
    trigger_substep_global = int(bundle.get("trigger_substep_global", -1))
    render_frames_dir_raw = str(bundle.get("render_frames_dir", "") or "").strip()
    render_frames_dir = Path(render_frames_dir_raw).expanduser().resolve() if render_frames_dir_raw else None
    base_video_path_raw = str(bundle.get("video_mp4_path", "") or "").strip()
    base_video_path = Path(base_video_path_raw).expanduser().resolve() if base_video_path_raw else None
    if base_video_path is None:
        scene_npz_raw = str(bundle.get("scene_npz_path", "") or "").strip()
        if scene_npz_raw:
            scene_npz = Path(scene_npz_raw).expanduser().resolve()
            inferred = scene_npz.with_name(scene_npz.name.replace("_scene.npz", ".mp4"))
            if inferred.exists():
                base_video_path = inferred

    wp.init()
    resolved_device = demo.newton_import_ir.resolve_device(device)
    model, meta, _ = demo.build_model(ir_obj, render_args, resolved_device)
    try:
        if render_sim_data is not None and trigger_substep_global >= 0:
            n_obj = int(np.asarray(render_sim_data["particle_q_object"]).shape[1])
            print(
                "[render_bunny_force_artifacts] building full-process force sequence from rollout states...",
                flush=True,
            )
            sequence_snapshots = demo._build_full_process_force_sequence_from_rollout(
                model=model,
                meta=meta,
                ir_obj=ir_obj,
                args=render_args,
                device=resolved_device,
                sim_data=render_sim_data,
                n_obj=n_obj,
                trigger_substep_global=trigger_substep_global,
                trigger_snapshot=diag_snapshot,
            )
            print(
                f"[render_bunny_force_artifacts] full-process sequence snapshots={len(sequence_snapshots)} trigger={trigger_substep_global}",
                flush=True,
            )
        else:
            print(
                f"[render_bunny_force_artifacts] fallback sequence snapshots={len(sequence_snapshots)} trigger={trigger_substep_global}",
                flush=True,
            )
        demo._finalize_force_diagnostic_artifacts(
            model,
            meta,
            render_args,
            resolved_device,
            diag_snapshot,
            sequence_snapshots,
            ir_obj=ir_obj,
            sim_data=render_sim_data,
            base_video_path=base_video_path,
            base_frames_dir=render_frames_dir,
        )
        print(
            f"[render_bunny_force_artifacts] finalized force artifacts under {render_args.force_dump_dir}",
            flush=True,
        )
    finally:
        del model
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
