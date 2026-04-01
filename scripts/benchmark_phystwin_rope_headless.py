#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import pickle
import random
import re
import subprocess
import sys
import time
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import torch
import warp as wp

warnings.filterwarnings(
    "ignore",
    message=r"Running the tape backwards may produce incorrect gradients.*",
)


ROOT = Path(__file__).resolve().parents[1]
PHYSTWIN_ROOT = ROOT / "PhysTwin"
DEFAULT_BASE_PATH = PHYSTWIN_ROOT / "data/different_types"
DEFAULT_CASE_NAME = "rope_double_hand"
DEFAULT_IR = (
    ROOT / "Newton/phystwin_bridge/ir/rope_double_hand/phystwin_ir_v2_bf_strict.npz"
)

if str(PHYSTWIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PHYSTWIN_ROOT))

from qqtt import InvPhyTrainerWarp  # noqa: E402
from qqtt.utils import cfg, logger  # noqa: E402


PROFILE_GROUPS = {
    "controller_update": ("controller_target",),
    "collision_bookkeeping": ("collision_graph_update",),
    "simulator_step": ("simulator_launch",),
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
        description="Headless PhysTwin rope replay benchmark without render/UI timing."
    )
    p.add_argument("--base-path", type=Path, default=DEFAULT_BASE_PATH)
    p.add_argument("--case-name", default=DEFAULT_CASE_NAME)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--prefix", default="phystwin_rope_headless")
    p.add_argument("--mode", choices=["throughput", "attribution"], default="throughput")
    p.add_argument("--runs", type=int, default=5)
    p.add_argument("--warmup-runs", type=int, default=1)
    p.add_argument("--frame-limit", type=int, default=None)
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--use-graph", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--csv-out", type=Path, default=None)
    p.add_argument("--ir", type=Path, default=DEFAULT_IR)
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
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total",
                "--format=csv,noheader",
            ],
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
        raise RuntimeError("No PhysTwin checkpoint matches the current rope topology.")
    matching.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return matching[0][2]


def _apply_checkpoint(trainer: InvPhyTrainerWarp, checkpoint_path: Path) -> dict[str, Any]:
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


def _sync() -> None:
    wp.synchronize_device()
    if torch.cuda.is_available():
        torch.cuda.synchronize()


def _time_call(fn, *args, **kwargs) -> float:
    _sync()
    t0 = time.perf_counter()
    fn(*args, **kwargs)
    _sync()
    return 1000.0 * (time.perf_counter() - t0)


def _run_episode(
    trainer: InvPhyTrainerWarp,
    mode: str,
    frame_limit: int | None,
    record: bool,
) -> dict[str, Any]:
    _reset_simulator(trainer)
    frame_len = _frame_len(trainer, frame_limit)
    total_substeps = int((frame_len - 1) * cfg.num_substeps)
    sim_time_sec = float(total_substeps * cfg.dt)
    samples: dict[str, list[float]] = defaultdict(list)

    if mode == "throughput":
        _sync()
        t0 = time.perf_counter()
        for i in range(1, frame_len):
            trainer.simulator.set_controller_target(i, pure_inference=True)
            if trainer.simulator.object_collision_flag:
                trainer.simulator.update_collision_graph()
            if cfg.use_graph:
                wp.capture_launch(trainer.simulator.forward_graph)
            else:
                trainer.simulator.step()
            trainer.simulator.set_init_state(
                trainer.simulator.wp_states[-1].wp_x,
                trainer.simulator.wp_states[-1].wp_v,
            )
        _sync()
        wall_ms = 1000.0 * (time.perf_counter() - t0)
        return {
            "wall_ms": float(wall_ms),
            "sim_time_sec": sim_time_sec,
            "trajectory_frames": int(frame_len),
            "total_substeps": total_substeps,
            "samples": {},
        }

    _sync()
    t0 = time.perf_counter()
    for i in range(1, frame_len):
        if record:
            samples["controller_target"].append(
                _time_call(trainer.simulator.set_controller_target, i, pure_inference=True)
            )
        else:
            trainer.simulator.set_controller_target(i, pure_inference=True)

        if trainer.simulator.object_collision_flag:
            if record:
                samples["collision_graph_update"].append(
                    _time_call(trainer.simulator.update_collision_graph)
                )
            else:
                trainer.simulator.update_collision_graph()

        if cfg.use_graph:
            if record:
                samples["simulator_launch"].append(
                    _time_call(wp.capture_launch, trainer.simulator.forward_graph)
                )
            else:
                wp.capture_launch(trainer.simulator.forward_graph)
        else:
            if record:
                samples["simulator_launch"].append(_time_call(trainer.simulator.step))
            else:
                trainer.simulator.step()

        if record:
            samples["state_reset"].append(
                _time_call(
                    trainer.simulator.set_init_state,
                    trainer.simulator.wp_states[-1].wp_x,
                    trainer.simulator.wp_states[-1].wp_v,
                )
            )
            frame_total = (
                samples["controller_target"][-1]
                + samples.get("collision_graph_update", [0.0])[-1]
                + samples["simulator_launch"][-1]
                + samples["state_reset"][-1]
            )
            samples["total_frame"].append(float(frame_total))
        else:
            trainer.simulator.set_init_state(
                trainer.simulator.wp_states[-1].wp_x,
                trainer.simulator.wp_states[-1].wp_v,
            )
    _sync()
    wall_ms = 1000.0 * (time.perf_counter() - t0)
    return {
        "wall_ms": float(wall_ms),
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
        per_run_means = [
            float(np.mean(run["samples"][name])) for run in runs if run.get("samples", {}).get(name)
        ]
        if not per_run_means:
            continue
        summary[name] = {
            "mean_of_run_means_ms": float(np.mean(per_run_means)),
            "std_of_run_means_ms": float(np.std(per_run_means)),
            "cv_of_run_means": float(np.std(per_run_means) / max(np.mean(per_run_means), 1.0e-12)),
            "call_count_total": int(sum(len(run["samples"].get(name, [])) for run in runs)),
        }
    return summary


def _rank_profile_ops(aggregate: dict[str, Any]) -> list[dict[str, Any]]:
    ranked = []
    for name, stats in aggregate.items():
        if name == "total_frame":
            continue
        ranked.append({"op_name": name, **stats})
    ranked.sort(key=lambda item: item["mean_of_run_means_ms"], reverse=True)
    return ranked


def _group_shares(aggregate: dict[str, Any]) -> dict[str, float]:
    total = float(aggregate.get("total_frame", {}).get("mean_of_run_means_ms", 0.0))
    if total <= 0.0:
        return {}
    shares = {}
    for group_name, op_names in PROFILE_GROUPS.items():
        subtotal = 0.0
        for op_name in op_names:
            subtotal += float(aggregate.get(op_name, {}).get("mean_of_run_means_ms", 0.0))
        shares[group_name] = subtotal / total
    return shares


def _write_payload(args: argparse.Namespace, payload: dict[str, Any]) -> tuple[Path, Path]:
    json_path = args.json_out.resolve() if args.json_out is not None else (args.out_dir / f"{args.prefix}.json").resolve()
    csv_path = args.csv_out.resolve() if args.csv_out is not None else (args.out_dir / f"{args.prefix}.csv").resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if payload["aggregate"]:
            writer.writerow(["op_name", "mean_of_run_means_ms", "std_of_run_means_ms", "cv_of_run_means", "call_count_total"])
            for op_name, stats in payload["aggregate"].items():
                writer.writerow(
                    [
                        op_name,
                        stats["mean_of_run_means_ms"],
                        stats["std_of_run_means_ms"],
                        stats["cv_of_run_means"],
                        stats["call_count_total"],
                    ]
                )
        else:
            writer.writerow(["run_index", "wall_ms", "sim_time_sec", "trajectory_frames", "total_substeps"])
            for idx, run in enumerate(payload["runs"]):
                writer.writerow(
                    [
                        idx,
                        run["wall_ms"],
                        run["sim_time_sec"],
                        run["trajectory_frames"],
                        run["total_substeps"],
                    ]
                )
    return json_path, csv_path


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


def main() -> int:
    args = parse_args()
    set_all_seeds(int(args.seed))
    args.out_dir = args.out_dir.expanduser().resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    _load_case_config(args.case_name)
    cfg.use_graph = bool(args.use_graph)
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
        _run_episode(trainer, args.mode, args.frame_limit, record=False)

    runs = [
        _run_episode(trainer, args.mode, args.frame_limit, record=True)
        for _ in range(int(args.runs))
    ]
    aggregate = _summarize_profile_runs(runs) if args.mode == "attribution" else {}
    payload: dict[str, Any] = {
        "case_name": str(args.case_name),
        "mode": str(args.mode),
        "device": str(args.device),
        "use_graph": bool(cfg.use_graph),
        "base_path": str(args.base_path.resolve()),
        "data_path": str(data_path),
        "ir": str(args.ir.resolve()),
        "phystwin_git_rev": _git_rev(PHYSTWIN_ROOT),
        "gpu_info": _gpu_info(),
        "optimal_params_path": str(
            (PHYSTWIN_ROOT / "experiments_optimization" / args.case_name / "optimal_params.pkl").resolve()
        ),
        "optimal_params": {k: float(v) if isinstance(v, (np.floating, float)) else int(v) if isinstance(v, (np.integer, int)) else v for k, v in optimal_params.items()},
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
        "bottleneck_ranked_ops": _rank_profile_ops(aggregate) if aggregate else [],
        "group_shares": _group_shares(aggregate) if aggregate else {},
    }
    json_path, csv_path = _write_payload(args, payload)
    print(f"PhysTwin summary JSON: {json_path}")
    print(f"PhysTwin summary CSV: {csv_path}")
    print(f"Graph enabled: {cfg.use_graph}")
    print(f"Object collision active: {trainer.simulator.object_collision_flag}")
    print(f"Controller trajectory max abs diff vs IR: {parity['controller_traj_max_abs_diff']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
