#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import random
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import torch
import warp as wp


ROOT = Path(__file__).resolve().parents[1]
PHYSTWIN_ROOT = ROOT / "PhysTwin"
DEFAULT_BASE_PATH = PHYSTWIN_ROOT / "data" / "different_types"
DEFAULT_CASE_NAME = "blue_cloth_double_lift_around"
DEFAULT_IR = ROOT / "Newton" / "phystwin_bridge" / "ir" / DEFAULT_CASE_NAME / "phystwin_ir_v2_bf_strict.npz"

if str(PHYSTWIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PHYSTWIN_ROOT))

from qqtt import InvPhyTrainerWarp  # noqa: E402
from qqtt.utils import cfg, logger  # noqa: E402
from qqtt.model.diff_simulator import spring_mass_warp as smw  # noqa: E402


warnings.filterwarnings(
    "ignore",
    message=r"Running the tape backwards may produce incorrect gradients.*",
)


PROFILE_GROUPS = {
    "controller_upload": ("controller_target",),
    "controller_substep_apply": ("set_control_points",),
    "collision_candidate_generation": ("collision_grid_build", "update_potential_collision"),
    "spring_force": ("eval_springs",),
    "velocity_update": ("update_vel_from_force",),
    "self_collision_response": ("object_collision",),
    "integration_ground": ("integrate_ground_collision",),
    "state_reset": ("state_reset",),
}


def set_all_seeds(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Kernel-level headless PhysTwin profiling for the same interactive-playground case."
    )
    p.add_argument("--base-path", type=Path, default=DEFAULT_BASE_PATH)
    p.add_argument("--case-name", default=DEFAULT_CASE_NAME)
    p.add_argument("--ir", type=Path, default=DEFAULT_IR)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--prefix", default="phystwin_playground_kernel_profile")
    p.add_argument("--runs", type=int, default=1)
    p.add_argument("--warmup-runs", type=int, default=0)
    p.add_argument("--frame-limit", type=int, default=None)
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--csv-out", type=Path, default=None)
    return p.parse_args()


def _git_rev(repo_root: Path) -> str:
    try:
        return (
            subprocess.check_output(["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True)
            .strip()
        )
    except Exception:
        return "unknown"


def _gpu_info() -> dict[str, Any]:
    info = {
        "torch_cuda_available": bool(torch.cuda.is_available()),
        "device_name": None,
        "driver": None,
    }
    if torch.cuda.is_available():
        info["device_name"] = torch.cuda.get_device_name(0)
    try:
        raw = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            text=True,
        ).strip()
        info["driver"] = raw
    except Exception:
        pass
    return info


def _load_case_config(case_name: str) -> None:
    config_name = "cloth.yaml" if ("cloth" in case_name or "package" in case_name) else "real.yaml"
    cfg.load_from_yaml(str((PHYSTWIN_ROOT / "configs" / config_name).resolve()))


def _load_optimal_params(case_name: str) -> dict[str, Any]:
    import pickle

    optimal_path = (PHYSTWIN_ROOT / "experiments_optimization" / case_name / "optimal_params.pkl").resolve()
    with optimal_path.open("rb") as fh:
        optimal_params = pickle.load(fh)
    cfg.set_optimal_params(optimal_params)
    return optimal_params


def _select_checkpoint(case_name: str, trainer: InvPhyTrainerWarp) -> Path:
    base_dir = (PHYSTWIN_ROOT / "experiments" / case_name / "train").resolve()
    expected_springs = trainer.simulator.n_springs
    expected_edges = trainer.init_springs.detach().cpu()
    expected_rest = trainer.init_rest_lengths.detach().cpu()

    def _extract_epoch(path: Path) -> int | None:
        import re

        match = re.fullmatch(r"best_(\d+)\.pth", path.name)
        return int(match.group(1)) if match else None

    candidates = sorted(base_dir.glob("best_*.pth"))
    if not candidates:
        raise FileNotFoundError(f"No checkpoint found under {base_dir}")

    matching: list[tuple[int, float, Path]] = []
    for path in candidates:
        epoch = _extract_epoch(path)
        if epoch is None:
            continue
        checkpoint = torch.load(path, map_location=cfg.device)
        spring_len = len(checkpoint.get("spring_Y", []))
        if spring_len != expected_springs:
            continue
        if "spring_edges" in checkpoint and "spring_rest_lengths" in checkpoint:
            ck_edges = checkpoint["spring_edges"].detach().cpu()
            ck_rest = checkpoint["spring_rest_lengths"].detach().cpu()
            edges_ok = ck_edges.shape == expected_edges.shape and torch.equal(
                ck_edges.to(dtype=expected_edges.dtype), expected_edges
            )
            rest_ok = ck_rest.shape == expected_rest.shape and torch.allclose(
                ck_rest.to(dtype=torch.float32),
                expected_rest.to(dtype=torch.float32),
                atol=1e-8,
                rtol=0.0,
            )
            if not (edges_ok and rest_ok):
                continue
        matching.append((epoch, path.stat().st_mtime, path))

    if not matching:
        raise RuntimeError("No PhysTwin checkpoint matches the current topology.")
    matching.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return matching[0][2]


def _apply_checkpoint(trainer: InvPhyTrainerWarp, checkpoint_path: Path) -> dict[str, Any]:
    import re

    checkpoint = torch.load(checkpoint_path, map_location=cfg.device)
    trainer.simulator.set_spring_Y(torch.log(checkpoint["spring_Y"]).detach().clone())
    trainer.simulator.set_collide(
        checkpoint["collide_elas"].detach().clone(),
        checkpoint["collide_fric"].detach().clone(),
    )
    trainer.simulator.set_collide_object(
        checkpoint["collide_object_elas"].detach().clone(),
        checkpoint["collide_object_fric"].detach().clone(),
    )
    return {
        "checkpoint_path": str(checkpoint_path),
        "checkpoint_epoch": int(re.fullmatch(r"best_(\d+)\.pth", checkpoint_path.name).group(1)),
        "num_object_springs": int(checkpoint["num_object_springs"]),
    }


def _reset_simulator(trainer: InvPhyTrainerWarp) -> None:
    trainer.simulator.set_init_state(
        trainer.simulator.wp_init_vertices,
        trainer.simulator.wp_init_velocities,
    )


def _frame_len(trainer: InvPhyTrainerWarp, frame_limit: int | None) -> int:
    return int(min(trainer.dataset.frame_len, frame_limit) if frame_limit else trainer.dataset.frame_len)


def _controller_parity(trainer: InvPhyTrainerWarp, ir_path: Path) -> dict[str, Any]:
    ir = np.load(ir_path, allow_pickle=False)
    ctrl_ir = np.asarray(ir["controller_traj"], dtype=np.float64)
    ctrl_phys = trainer.controller_points.detach().cpu().numpy().astype(np.float64)
    diff = ctrl_ir - ctrl_phys
    return {
        "controller_traj_shape_ir": list(ctrl_ir.shape),
        "controller_traj_shape_phystwin": list(ctrl_phys.shape),
        "controller_traj_max_abs_diff": float(np.max(np.abs(diff))),
        "controller_traj_mean_abs_diff": float(np.mean(np.abs(diff))),
        "sim_dt_ir": float(ir["sim_dt"]),
        "sim_substeps_ir": int(ir["sim_substeps"]),
        "num_object_points_ir": int(ir["num_object_points"]),
    }


def _enqueue_timed_call(
    pending: list[tuple[str, torch.cuda.Event, torch.cuda.Event]],
    stream: torch.cuda.Stream,
    name: str,
    fn,
    *args,
    **kwargs,
) -> None:
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record(stream)
    fn(*args, **kwargs)
    end.record(stream)
    pending.append((name, start, end))


def _flush_pending(
    pending: list[tuple[str, torch.cuda.Event, torch.cuda.Event]],
    samples: dict[str, list[float]],
) -> None:
    torch.cuda.synchronize()
    for name, start, end in pending:
        samples.setdefault(name, []).append(float(start.elapsed_time(end)))
    pending.clear()


def _profile_frame(
    trainer: InvPhyTrainerWarp,
    frame_idx: int,
    stream: torch.cuda.Stream,
    samples: dict[str, list[float]],
) -> None:
    sim = trainer.simulator
    pending: list[tuple[str, torch.cuda.Event, torch.cuda.Event]] = []
    warp_stream = wp.stream_from_torch(stream)
    with wp.ScopedStream(warp_stream):
        _enqueue_timed_call(pending, stream, "total_frame_start_marker", lambda: None)

        frame_start = torch.cuda.Event(enable_timing=True)
        frame_end = torch.cuda.Event(enable_timing=True)
        frame_start.record(stream)

        _enqueue_timed_call(
            pending,
            stream,
            "controller_target",
            sim.set_controller_target,
            frame_idx,
            True,
        )

        if sim.object_collision_flag:
            _enqueue_timed_call(
                pending,
                stream,
                "collision_grid_build",
                sim.collision_grid.build,
                sim.wp_states[0].wp_x,
                sim.collision_dist * 5.0,
            )
            sim.wp_collision_number.zero_()
            _enqueue_timed_call(
                pending,
                stream,
                "update_potential_collision",
                wp.launch,
                smw.update_potential_collision,
                dim=sim.num_object_points,
                inputs=[
                    sim.wp_states[0].wp_x,
                    sim.wp_masks,
                    sim.collision_dist,
                    sim.collision_grid.id,
                ],
                outputs=[sim.wp_collision_indices, sim.wp_collision_number],
            )

        for substep_idx in range(sim.num_substeps):
            sub_start = torch.cuda.Event(enable_timing=True)
            sub_end = torch.cuda.Event(enable_timing=True)
            sub_start.record(stream)

            state = sim.wp_states[substep_idx]
            next_state = sim.wp_states[substep_idx + 1]
            state.clear_forces()

            if sim.controller_points is not None:
                _enqueue_timed_call(
                    pending,
                    stream,
                    "set_control_points",
                    wp.launch,
                    smw.set_control_points,
                    dim=sim.num_control_points,
                    inputs=[
                        sim.num_substeps,
                        sim.wp_original_control_point,
                        sim.wp_target_control_point,
                        substep_idx,
                    ],
                    outputs=[state.wp_control_x],
                )

            _enqueue_timed_call(
                pending,
                stream,
                "eval_springs",
                wp.launch,
                kernel=smw.eval_springs,
                dim=sim.n_springs,
                inputs=[
                    state.wp_x,
                    state.wp_v,
                    state.wp_control_x,
                    state.wp_control_v,
                    sim.num_object_points,
                    sim.wp_springs,
                    sim.wp_rest_lengths,
                    sim.wp_spring_Y,
                    sim.dashpot_damping,
                    sim.spring_Y_min,
                    sim.spring_Y_max,
                ],
                outputs=[state.wp_vertice_forces],
            )

            output_v = state.wp_v_before_collision if sim.object_collision_flag else state.wp_v_before_ground
            _enqueue_timed_call(
                pending,
                stream,
                "update_vel_from_force",
                wp.launch,
                kernel=smw.update_vel_from_force,
                dim=sim.num_object_points,
                inputs=[
                    state.wp_v,
                    state.wp_vertice_forces,
                    sim.wp_masses,
                    sim.dt,
                    sim.drag_damping,
                    sim.reverse_factor,
                ],
                outputs=[output_v],
            )

            if sim.object_collision_flag:
                _enqueue_timed_call(
                    pending,
                    stream,
                    "object_collision",
                    wp.launch,
                    kernel=smw.object_collision,
                    dim=sim.num_object_points,
                    inputs=[
                        state.wp_x,
                        state.wp_v_before_collision,
                        sim.wp_masses,
                        sim.wp_masks,
                        sim.wp_collide_object_elas,
                        sim.wp_collide_object_fric,
                        sim.collision_dist,
                        sim.wp_collision_indices,
                        sim.wp_collision_number,
                    ],
                    outputs=[state.wp_v_before_ground],
                )

            _enqueue_timed_call(
                pending,
                stream,
                "integrate_ground_collision",
                wp.launch,
                kernel=smw.integrate_ground_collision,
                dim=sim.num_object_points,
                inputs=[
                    state.wp_x,
                    state.wp_v_before_ground,
                    sim.wp_collide_elas,
                    sim.wp_collide_fric,
                    sim.dt,
                    sim.reverse_factor,
                ],
                outputs=[next_state.wp_x, next_state.wp_v],
            )
            sub_end.record(stream)
            pending.append(("total_substep", sub_start, sub_end))

        _enqueue_timed_call(
            pending,
            stream,
            "state_reset",
            sim.set_init_state,
            sim.wp_states[-1].wp_x,
            sim.wp_states[-1].wp_v,
        )
        frame_end.record(stream)
        pending.append(("total_frame", frame_start, frame_end))

    _flush_pending(pending, samples)


def _run_episode(
    trainer: InvPhyTrainerWarp,
    frame_limit: int | None,
    *,
    record: bool,
) -> dict[str, Any]:
    _reset_simulator(trainer)
    frame_len = _frame_len(trainer, frame_limit)
    total_substeps = int((frame_len - 1) * cfg.num_substeps)
    sim_time_sec = float(total_substeps * cfg.dt)
    samples: dict[str, list[float]] = {}

    if record:
        stream = torch.cuda.current_stream()
        for frame_idx in range(1, frame_len):
            _profile_frame(trainer, frame_idx, stream, samples)
    else:
        for frame_idx in range(1, frame_len):
            trainer.simulator.set_controller_target(frame_idx, pure_inference=True)
            if trainer.simulator.object_collision_flag:
                trainer.simulator.update_collision_graph()
            wp.capture_launch(trainer.simulator.forward_graph)
            trainer.simulator.set_init_state(
                trainer.simulator.wp_states[-1].wp_x,
                trainer.simulator.wp_states[-1].wp_v,
            )
        wp.synchronize_device()
        torch.cuda.synchronize()

    return {
        "sim_time_sec": sim_time_sec,
        "trajectory_frames": int(frame_len),
        "total_substeps": total_substeps,
        "samples": {k: [float(v) for v in vals] for k, vals in samples.items()},
    }


def _summarize_profile_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    sample_names: list[str] = []
    for run in runs:
        for name in run.get("samples", {}):
            if name not in sample_names:
                sample_names.append(name)

    for name in sample_names:
        run_means = [float(np.mean(run["samples"][name])) for run in runs if run.get("samples", {}).get(name)]
        all_calls = [float(v) for run in runs for v in run.get("samples", {}).get(name, [])]
        call_count_total = sum(len(run.get("samples", {}).get(name, [])) for run in runs)
        summary[name] = {
            "call_count_total": int(call_count_total),
            "call_count_per_run": [len(run.get("samples", {}).get(name, [])) for run in runs],
            "run_mean_ms": run_means,
            "mean_of_run_means_ms": float(np.mean(run_means)) if run_means else 0.0,
            "std_of_run_means_ms": float(np.std(run_means)) if len(run_means) > 1 else 0.0,
            "mean_over_all_calls_ms": float(np.mean(all_calls)) if all_calls else 0.0,
            "std_over_all_calls_ms": float(np.std(all_calls)) if len(all_calls) > 1 else 0.0,
        }
    return summary


def _op_amortized_ms_per_substep(payload: dict[str, Any], op_name: str) -> float:
    stats = payload.get("aggregate", {}).get(op_name, {})
    call_count_total = float(stats.get("call_count_total", 0.0))
    mean_over_all_calls_ms = float(stats.get("mean_over_all_calls_ms", 0.0))
    total_substeps_all_runs = float(payload["total_substeps"]) * float(payload.get("profile_runs", 1))
    if call_count_total <= 0.0 or total_substeps_all_runs <= 0.0:
        return 0.0
    return mean_over_all_calls_ms * call_count_total / total_substeps_all_runs


def _rank_profile_ops(payload: dict[str, Any]) -> list[dict[str, Any]]:
    aggregate = payload.get("aggregate", {})
    excluded = {"total_substep", "total_frame", "total_frame_start_marker"}
    ranked = []
    for name, stats in aggregate.items():
        if name in excluded:
            continue
        ranked.append(
            {
                "op_name": name,
                "mean_of_run_means_ms": float(stats["mean_of_run_means_ms"]),
                "call_count_total": int(stats["call_count_total"]),
                "amortized_ms_per_substep": float(_op_amortized_ms_per_substep(payload, name)),
            }
        )
    ranked.sort(key=lambda item: item["amortized_ms_per_substep"], reverse=True)
    return ranked


def _group_shares(payload: dict[str, Any]) -> dict[str, float]:
    total = float(_op_amortized_ms_per_substep(payload, "total_substep"))
    if total <= 0.0:
        return {}
    shares = {}
    for group_name, op_names in PROFILE_GROUPS.items():
        subtotal = 0.0
        for op_name in op_names:
            subtotal += float(_op_amortized_ms_per_substep(payload, op_name))
        shares[group_name] = subtotal / total
    return shares


def _write_payload(args: argparse.Namespace, payload: dict[str, Any]) -> tuple[Path, Path]:
    json_path = args.json_out.resolve() if args.json_out is not None else (args.out_dir / f"{args.prefix}.json").resolve()
    csv_path = args.csv_out.resolve() if args.csv_out is not None else (args.out_dir / f"{args.prefix}.csv").resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "op_name",
                "call_count_total",
                "mean_of_run_means_ms",
                "std_of_run_means_ms",
                "mean_over_all_calls_ms",
                "std_over_all_calls_ms",
            ]
        )
        for op_name, stats in payload["aggregate"].items():
            writer.writerow(
                [
                    op_name,
                    stats["call_count_total"],
                    stats["mean_of_run_means_ms"],
                    stats["std_of_run_means_ms"],
                    stats["mean_over_all_calls_ms"],
                    stats["std_over_all_calls_ms"],
                ]
            )
    return json_path, csv_path


def main() -> int:
    args = parse_args()
    set_all_seeds(int(args.seed))
    args.out_dir = args.out_dir.expanduser().resolve()
    args.base_path = args.base_path.expanduser().resolve()
    args.ir = args.ir.expanduser().resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    _load_case_config(args.case_name)
    cfg.use_graph = True
    optimal_params = _load_optimal_params(args.case_name)

    data_path = (args.base_path / args.case_name / "final_data.pkl").resolve()
    logger.set_log_file(path=str(args.out_dir), name=f"{args.prefix}_log")
    trainer = InvPhyTrainerWarp(
        data_path=str(data_path),
        base_dir=str(args.out_dir),
        pure_inference_mode=True,
        device=args.device,
    )
    checkpoint_path = _select_checkpoint(args.case_name, trainer)
    checkpoint_meta = _apply_checkpoint(trainer, checkpoint_path)
    parity = _controller_parity(trainer, args.ir.resolve())

    for _ in range(int(args.warmup_runs)):
        _run_episode(trainer, args.frame_limit, record=False)

    runs = [_run_episode(trainer, args.frame_limit, record=True) for _ in range(int(args.runs))]
    aggregate = _summarize_profile_runs(runs)

    payload: dict[str, Any] = {
        "case_name": str(args.case_name),
        "mode": "kernel_attribution",
        "device": str(args.device),
        "base_path": str(args.base_path),
        "data_path": str(data_path),
        "ir": str(args.ir),
        "phystwin_git_rev": _git_rev(PHYSTWIN_ROOT),
        "gpu_info": _gpu_info(),
        "optimal_params_path": str(
            (PHYSTWIN_ROOT / "experiments_optimization" / args.case_name / "optimal_params.pkl").resolve()
        ),
        "optimal_params": {
            k: float(v) if isinstance(v, (np.floating, float)) else int(v) if isinstance(v, (np.integer, int)) else v
            for k, v in optimal_params.items()
        },
        "controller_count": int(trainer.controller_points.shape[1]),
        "n_obj": int(trainer.num_all_points),
        "spring_count": int(trainer.simulator.n_springs),
        "sim_dt": float(cfg.dt),
        "segment_substeps": int(cfg.num_substeps),
        "trajectory_frames": int(_frame_len(trainer, args.frame_limit)),
        "total_substeps": int((_frame_len(trainer, args.frame_limit) - 1) * cfg.num_substeps),
        "profile_runs": int(args.runs),
        "warmup_runs": int(args.warmup_runs),
        "object_collision_flag": bool(trainer.simulator.object_collision_flag),
        "self_collision": bool(cfg.self_collision),
        "collision_dist": float(cfg.collision_dist),
        "drag_damping": float(cfg.drag_damping),
        "checkpoint": checkpoint_meta,
        "trajectory_parity": parity,
        "runs": runs,
        "aggregate": aggregate,
        "bottleneck_ranked_ops": [],
        "group_shares": {},
        "profiling_note": (
            "Throughput claims should come from the graph-on headless benchmark. "
            "This kernel attribution run mirrors spring_mass_warp.step() explicitly and "
            "uses CUDA events on a shared torch/warp stream to avoid per-op synchronize() in the hot loop."
        ),
    }
    payload["bottleneck_ranked_ops"] = _rank_profile_ops(payload)
    payload["group_shares"] = _group_shares(payload)
    json_path, csv_path = _write_payload(args, payload)
    print(f"PhysTwin kernel profile JSON: {json_path}")
    print(f"PhysTwin kernel profile CSV: {csv_path}")
    for rank in payload["bottleneck_ranked_ops"][:8]:
        print(f"top op: {rank['op_name']} mean={rank['mean_of_run_means_ms']:.6f} ms calls={rank['call_count_total']}")
    print(f"group shares: {payload['group_shares']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
