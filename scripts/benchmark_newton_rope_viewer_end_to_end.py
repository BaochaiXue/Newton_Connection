#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import warp as wp


ROOT = Path(__file__).resolve().parents[1]
NEWTON_ROOT = ROOT / "Newton" / "newton"
DEMOS_ROOT = ROOT / "Newton" / "phystwin_bridge" / "demos"

sys.path.insert(0, str(NEWTON_ROOT))
sys.path.insert(0, str(DEMOS_ROOT))

import newton.viewer  # noqa: E402
import demo_rope_control_realtime_viewer as demo  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Benchmark the Newton rope real viewer with rendering ON.")
    p.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Stage output directory.",
    )
    p.add_argument(
        "--prefix",
        type=str,
        default="E1_viewer_end_to_end",
    )
    p.add_argument(
        "--runs",
        type=int,
        default=3,
    )
    p.add_argument(
        "--warmup-runs",
        type=int,
        default=1,
    )
    p.add_argument(
        "--controller-write-mode",
        choices=["baseline", "precomputed"],
        default="precomputed",
    )
    p.add_argument(
        "--ir",
        type=Path,
        default=ROOT / "Newton" / "phystwin_bridge" / "ir" / "rope_double_hand" / "phystwin_ir_v2_bf_strict.npz",
    )
    p.add_argument("--runtime-device", default="cuda:0")
    p.add_argument("--sim-dt", type=float, default=5e-05)
    p.add_argument("--segment-substeps", type=int, default=667)
    p.add_argument("--steps-per-render", type=int, default=667)
    p.add_argument("--trajectory-frame-limit", type=int, default=None)
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--csv-out", type=Path, default=None)
    p.add_argument("--headless", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def _build_demo_args(run_args: argparse.Namespace) -> argparse.Namespace:
    parser = demo.create_parser()
    argv = [
        "--viewer",
        "gl",
        "--runtime-device",
        str(run_args.runtime_device),
        "--ir",
        str(run_args.ir),
        "--sim-dt",
        str(run_args.sim_dt),
        "--segment-substeps",
        str(run_args.segment_substeps),
        "--steps-per-render",
        str(run_args.steps_per_render),
        "--controller-write-mode",
        str(run_args.controller_write_mode),
        "--out-dir",
        str(run_args.out_dir),
        "--prefix",
        str(run_args.prefix),
        "--no-add-ground-plane",
        "--no-shape-contacts",
    ]
    if run_args.trajectory_frame_limit is not None:
        argv.extend(["--trajectory-frame-limit", str(int(run_args.trajectory_frame_limit))])
    if bool(run_args.headless):
        argv.append("--headless")
    else:
        argv.append("--no-headless")
    return parser.parse_args(argv)


def _mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    arr = np.asarray(values, dtype=np.float64)
    return float(np.mean(arr)), float(np.std(arr))


def _run_episode(args: argparse.Namespace) -> dict[str, Any]:
    viewer = newton.viewer.ViewerGL(headless=bool(args.headless))
    example = demo.NewtonRopeControlViewer(viewer, args)
    step_ms: list[float] = []
    render_ms: list[float] = []
    wall_start = time.perf_counter()
    try:
        while viewer.is_running():
            if not example.finished:
                example.step()
                step_ms.append(float(example.last_step_wall_ms))
            example.render()
            render_ms.append(float(example.last_render_wall_ms))
            if example.finished:
                break
    finally:
        try:
            viewer.close()
        except Exception:
            pass
    wall_ms = 1000.0 * (time.perf_counter() - wall_start)
    sim_time_sec = float(example.sim_time)
    viewer_frames = int(example._render_frame_count)
    viewer_fps = float(viewer_frames) / max(wall_ms / 1000.0, 1.0e-12)
    effective_rtf = sim_time_sec / max(wall_ms / 1000.0, 1.0e-12)
    mean_step_ms, std_step_ms = _mean_std(step_ms)
    mean_render_ms, std_render_ms = _mean_std(render_ms)
    return {
        "wall_ms": float(wall_ms),
        "sim_time_sec": sim_time_sec,
        "viewer_frames": viewer_frames,
        "trajectory_frames": int(example.n_traj_frames),
        "total_substeps": int(example.total_substeps),
        "viewer_fps": float(viewer_fps),
        "rtf": float(effective_rtf),
        "ms_per_sim_second": float(wall_ms / max(sim_time_sec, 1.0e-12)),
        "step_wall_ms_mean": mean_step_ms,
        "step_wall_ms_std": std_step_ms,
        "render_wall_ms_mean": mean_render_ms,
        "render_wall_ms_std": std_render_ms,
        "render_on": True,
        "viewer_backend": "gl_headless" if bool(args.headless) else "gl",
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "run_index",
        "wall_ms",
        "sim_time_sec",
        "viewer_frames",
        "trajectory_frames",
        "total_substeps",
        "viewer_fps",
        "rtf",
        "ms_per_sim_second",
        "step_wall_ms_mean",
        "render_wall_ms_mean",
        "viewer_backend",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fieldnames})


def main() -> int:
    args = parse_args()
    args.out_dir = args.out_dir.expanduser().resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.ir = args.ir.expanduser().resolve()
    demo_args = _build_demo_args(args)

    wp.init()

    for _ in range(max(0, int(args.warmup_runs))):
        _run_episode(demo_args)

    runs: list[dict[str, Any]] = []
    for idx in range(max(1, int(args.runs))):
        payload = _run_episode(demo_args)
        payload["run_index"] = idx
        runs.append(payload)

    wall_values = [float(r["wall_ms"]) for r in runs]
    fps_values = [float(r["viewer_fps"]) for r in runs]
    rtf_values = [float(r["rtf"]) for r in runs]
    ms_per_sim_sec_values = [float(r["ms_per_sim_second"]) for r in runs]
    step_values = [float(r["step_wall_ms_mean"]) for r in runs]
    render_values = [float(r["render_wall_ms_mean"]) for r in runs]

    summary = {
        "case_name": "rope_double_hand",
        "mode": "viewer_end_to_end",
        "viewer_backend": "gl_headless" if bool(args.headless) else "gl",
        "render_on": True,
        "runtime_device": str(args.runtime_device),
        "controller_write_mode": str(args.controller_write_mode),
        "sim_dt": float(demo_args.sim_dt),
        "segment_substeps": int(demo_args.segment_substeps),
        "steps_per_render": int(demo_args.steps_per_render),
        "trajectory_frame_limit": args.trajectory_frame_limit,
        "profile_runs": int(args.runs),
        "warmup_runs": int(args.warmup_runs),
        "runs": runs,
        "viewer_fps_mean": float(np.mean(fps_values)),
        "viewer_fps_std": float(np.std(fps_values)),
        "rtf_mean": float(np.mean(rtf_values)),
        "rtf_std": float(np.std(rtf_values)),
        "wall_ms_mean": float(np.mean(wall_values)),
        "wall_ms_std": float(np.std(wall_values)),
        "ms_per_sim_second_mean": float(np.mean(ms_per_sim_sec_values)),
        "ms_per_sim_second_std": float(np.std(ms_per_sim_sec_values)),
        "step_wall_ms_mean": float(np.mean(step_values)),
        "render_wall_ms_mean": float(np.mean(render_values)),
        "ir": str(args.ir),
    }

    json_out = args.json_out.resolve() if args.json_out is not None else (args.out_dir / "summary.json")
    csv_out = args.csv_out.resolve() if args.csv_out is not None else (args.out_dir / "profile.csv")
    json_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_csv(csv_out, runs)
    print(f"Summary JSON: {json_out}")
    print(f"Profile CSV: {csv_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
