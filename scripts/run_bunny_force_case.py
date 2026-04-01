#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import pickle
import sys
from pathlib import Path

import numpy as np
import warp as wp


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Run the cloth-bunny OFF case through simulation + process render, then defer force-artifact rendering."
    )
    parser.add_argument(
        "--bundle-out",
        type=Path,
        default=None,
        help="Optional explicit path for the serialized force-render bundle. Defaults to <force-dump-dir>/force_render_bundle.pkl.",
    )
    return parser.parse_known_args()


def main() -> int:
    script_args, demo_argv = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    demos_dir = repo_root / "Newton" / "phystwin_bridge" / "demos"
    sys.path.insert(0, str(demos_dir))

    import demo_cloth_bunny_drop_without_self_contact as demo  # noqa: PLC0415

    argv_backup = sys.argv
    try:
        sys.argv = ["run_bunny_force_case.py", *demo_argv]
        args = demo.parse_args()
    finally:
        sys.argv = argv_backup

    demo._validate_scaling_args(args)
    args.out_dir = args.out_dir.resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if bool(args.force_diagnostic) and not bool(args.skip_render):
        args.keep_render_frames = True

    wp.init()
    device = demo.newton_import_ir.resolve_device(args.device)
    raw_ir = demo.load_ir(args.ir)
    if args.auto_set_weight is not None:
        demo._maybe_autoset_mass_spring_scale(args, raw_ir, target_total_mass=float(args.auto_set_weight))

    ir_obj = demo._copy_object_only_ir(raw_ir, args)
    if "contact_collision_dist" in ir_obj:
        scaled_dist = float(np.asarray(ir_obj["contact_collision_dist"]).ravel()[0]) * float(args.contact_dist_scale)
        ir_obj["contact_collision_dist"] = np.asarray(scaled_dist, dtype=np.float32)
    if not str(args.prefix).endswith("_off"):
        args.prefix = f"{args.prefix}_off"

    model, meta, n_obj = demo.build_model(ir_obj, args, device)
    sim_data = demo.simulate(model, ir_obj, meta, args, n_obj, device)

    render_sim_data = sim_data
    model_for_io = model
    meta_for_io = meta
    n_obj_for_io = n_obj
    if bool(args.force_diagnostic) and not bool(args.skip_render):
        render_args = copy.deepcopy(args)
        render_args.force_diagnostic = False
        render_args.stop_after_diagnostic = False
        render_args.parity_check = False
        model_render, meta_render, n_obj_render = demo.build_model(ir_obj, render_args, device)
        render_sim_data = demo.simulate(model_render, ir_obj, meta_render, render_args, n_obj_render, device)
        render_sim_data["force_diagnostic"] = sim_data.get("force_diagnostic")
        model_for_io = model_render
        meta_for_io = meta_render
        n_obj_for_io = n_obj_render

    scene_npz = demo.save_scene_npz(args, render_sim_data, meta_for_io, n_obj_for_io)
    out_mp4: Path | None = None
    if not bool(args.skip_render):
        out_mp4 = args.out_dir / f"{args.prefix}_{demo._mass_tag(args.rigid_mass)}.mp4"
        out_mp4.parent.mkdir(parents=True, exist_ok=True)
        demo.render_video(model_for_io, render_sim_data, meta_for_io, args, device, out_mp4)

    summary = demo.build_summary(
        model_for_io,
        args,
        ir_obj,
        render_sim_data,
        meta_for_io,
        n_obj_for_io,
        out_mp4,
        particle_contacts_enabled=False,
        disable_particle_contact_kernel=True,
    )
    summary_path = demo.save_summary_json(args, summary)

    force_diagnostic = sim_data.get("force_diagnostic")
    if isinstance(force_diagnostic, dict) and bool(force_diagnostic.get("enabled", False)):
        bundle_path = (
            script_args.bundle_out.expanduser().resolve()
            if script_args.bundle_out is not None
            else demo._resolve_force_dump_dir(args) / "force_render_bundle.pkl"
        )
        bundle_path.parent.mkdir(parents=True, exist_ok=True)
        diag_snapshot = force_diagnostic.get("render_snapshot")
        if not isinstance(diag_snapshot, dict):
            raise RuntimeError("Force diagnostic bundle requires a render_snapshot dictionary.")
        bundle = {
            "args": args,
            "device": device,
            "ir_obj": ir_obj,
            "diag_snapshot": diag_snapshot,
            "sequence_snapshots": [],
            "render_sim_data": render_sim_data,
            "trigger_substep_global": int(force_diagnostic.get("trigger_substep_global", -1)),
            "scene_npz_path": str(scene_npz),
            "summary_json_path": str(summary_path),
            "video_mp4_path": "" if out_mp4 is None else str(out_mp4),
            "render_frames_dir": (
                ""
                if out_mp4 is None or not bool(args.keep_render_frames)
                else str(out_mp4.parent / f"{out_mp4.stem}_frames")
            ),
        }
        with bundle_path.open("wb") as handle:
            pickle.dump(bundle, handle)
        print(f"Force render bundle: {bundle_path}", flush=True)

    print(f"Scene NPZ: {scene_npz}", flush=True)
    if out_mp4 is not None:
        print(f"Process video: {out_mp4}", flush=True)
    print(f"Summary: {summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
