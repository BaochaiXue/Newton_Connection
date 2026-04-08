#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


RAW_MATCHUPS = [
    {
        "newton_op": "controller_interp_cpu_ms",
        "phystwin_op": "n/a",
        "note": "Newton baseline CPU interpolation has no separate PhysTwin CPU-side counterpart.",
    },
    {
        "newton_op": "ctrl_target_assign_ms",
        "phystwin_op": "controller_target",
        "note": "Both sides upload per-frame controller targets before the substep loop.",
    },
    {
        "newton_op": "ctrl_vel_assign_ms",
        "phystwin_op": "n/a",
        "note": "PhysTwin keeps controller velocity implicit/zero in this path.",
    },
    {
        "newton_op": "write_kinematic_state",
        "phystwin_op": "set_control_points",
        "note": "Both apply controller motion inside each substep.",
    },
    {
        "newton_op": "particle_grid_build",
        "phystwin_op": "collision_grid_build",
        "note": "Broadphase grid build on each side.",
    },
    {
        "newton_op": "model_collide",
        "phystwin_op": "update_potential_collision",
        "note": "Candidate contact generation / collision bookkeeping.",
    },
    {
        "newton_op": "spring_forces",
        "phystwin_op": "eval_springs",
        "note": "Direct spring-force correspondence.",
    },
    {
        "newton_op": "triangle_forces",
        "phystwin_op": "n/a",
        "note": "No separate PhysTwin triangle-force kernel in this spring-mass path.",
    },
    {
        "newton_op": "bending_forces",
        "phystwin_op": "n/a",
        "note": "No separate PhysTwin bending-force kernel in this spring-mass path.",
    },
    {
        "newton_op": "tetra_forces",
        "phystwin_op": "n/a",
        "note": "No separate PhysTwin tetra-force kernel in this spring-mass path.",
    },
    {
        "newton_op": "body_joint_forces",
        "phystwin_op": "n/a",
        "note": "No separate body-joint force stage on the PhysTwin side.",
    },
    {
        "newton_op": "particle_contact_forces",
        "phystwin_op": "object_collision",
        "note": "Self-collision response stage.",
    },
    {
        "newton_op": "triangle_contact_forces",
        "phystwin_op": "n/a",
        "note": "No triangle-contact kernel on the PhysTwin spring-mass side.",
    },
    {
        "newton_op": "body_contact_forces",
        "phystwin_op": "n/a",
        "note": "No rigid-body contact force kernel in the PhysTwin interactive spring-mass path.",
    },
    {
        "newton_op": "particle_body_contact_forces",
        "phystwin_op": "n/a",
        "note": "No particle-vs-body contact kernel in the PhysTwin interactive spring-mass path.",
    },
    {
        "newton_op": "integrate_particles",
        "phystwin_op": "update_vel_from_force + integrate_ground_collision",
        "note": "PhysTwin folds force-to-velocity and ground integration into its own two-step path.",
    },
    {
        "newton_op": "integrate_bodies",
        "phystwin_op": "n/a",
        "note": "No separate rigid-body integration stage in the PhysTwin cloth interactive case.",
    },
    {
        "newton_op": "drag_correction",
        "phystwin_op": "update_vel_from_force",
        "note": "PhysTwin drag is baked into update_vel_from_force rather than a separate kernel.",
    },
]


GROUP_MATCHUPS = [
    {
        "concept": "controller_target_upload",
        "newton_ops": ["controller_interp_cpu_ms", "ctrl_target_assign_ms", "ctrl_vel_assign_ms"],
        "phystwin_ops": ["controller_target"],
        "note": "Per-frame controller target preparation before the substep loop.",
    },
    {
        "concept": "controller_substep_application",
        "newton_ops": ["write_kinematic_state"],
        "phystwin_ops": ["set_control_points"],
        "note": "Substep-level controller interpolation/application.",
    },
    {
        "concept": "collision_candidate_generation",
        "newton_ops": ["particle_grid_build", "model_collide"],
        "phystwin_ops": ["collision_grid_build", "update_potential_collision"],
        "note": "Broadphase and collision candidate generation.",
    },
    {
        "concept": "spring_force_evaluation",
        "newton_ops": ["spring_forces"],
        "phystwin_ops": ["eval_springs"],
        "note": "Main spring force kernel.",
    },
    {
        "concept": "self_collision_response",
        "newton_ops": ["particle_contact_forces"],
        "phystwin_ops": ["object_collision"],
        "note": "Self-collision response kernel after candidates are known.",
    },
    {
        "concept": "integration_and_drag",
        "newton_ops": ["integrate_particles", "integrate_bodies", "drag_correction"],
        "phystwin_ops": ["update_vel_from_force", "integrate_ground_collision"],
        "note": "Velocity update, drag, and state integration.",
    },
    {
        "concept": "newton_only_extra_internal_or_contact",
        "newton_ops": [
            "triangle_forces",
            "bending_forces",
            "tetra_forces",
            "body_joint_forces",
            "triangle_contact_forces",
            "body_contact_forces",
            "particle_body_contact_forces",
        ],
        "phystwin_ops": [],
        "note": "Stages present in the Newton semi-implicit path without a separate PhysTwin spring-mass counterpart.",
    },
    {
        "concept": "phystwin_only_state_reset",
        "newton_ops": [],
        "phystwin_ops": ["state_reset"],
        "note": "Explicit frame-to-frame state reset on the PhysTwin side.",
    },
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare Newton and PhysTwin interactive-playground profiling outputs.")
    p.add_argument("--newton-baseline-throughput", type=Path, required=True)
    p.add_argument("--newton-precomputed-throughput", type=Path, required=True)
    p.add_argument("--newton-baseline-attribution", type=Path, required=True)
    p.add_argument("--newton-precomputed-attribution", type=Path, required=True)
    p.add_argument("--phystwin-throughput", type=Path, required=True)
    p.add_argument("--phystwin-kernel-attribution", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    return p.parse_args()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.expanduser().resolve().read_text(encoding="utf-8"))


def _safe_mean(values: list[float]) -> float:
    return float(np.mean(np.asarray(values, dtype=np.float64))) if values else 0.0


def _safe_std(values: list[float]) -> float:
    return float(np.std(np.asarray(values, dtype=np.float64))) if len(values) > 1 else 0.0


def _throughput_row(label: str, payload: dict[str, Any]) -> dict[str, Any]:
    runs = payload["runs"]
    wall_ms = [float(run["wall_ms"]) for run in runs]
    total_substeps = float(payload["total_substeps"])
    sim_time_sec = [float(run["sim_time_sec"]) for run in runs]
    ms_per_substep = [float(run["wall_ms"]) / max(total_substeps, 1.0e-12) for run in runs]
    rtf = [float(run["sim_time_sec"]) / max(float(run["wall_ms"]) / 1000.0, 1.0e-12) for run in runs]
    return {
        "label": label,
        "profile_mode": str(payload.get("profile_mode", payload.get("mode", ""))),
        "trajectory_frames": int(payload["trajectory_frames"]),
        "total_substeps": int(payload["total_substeps"]),
        "wall_ms_mean": _safe_mean(wall_ms),
        "wall_ms_std": _safe_std(wall_ms),
        "sim_time_sec_mean": _safe_mean(sim_time_sec),
        "ms_per_substep_mean": _safe_mean(ms_per_substep),
        "ms_per_substep_std": _safe_std(ms_per_substep),
        "rtf_mean": _safe_mean(rtf),
        "rtf_std": _safe_std(rtf),
    }


def _aggregate_op_metric(payload: dict[str, Any], op_name: str) -> dict[str, float] | None:
    stats = payload.get("aggregate", {}).get(op_name)
    if not stats:
        return None
    if int(stats.get("call_count_total", 0)) <= 0:
        return None
    total_substeps_all_runs = float(payload["total_substeps"]) * float(payload.get("profile_runs", 1))
    total_elapsed_ms = float(stats["mean_over_all_calls_ms"]) * float(stats["call_count_total"])
    return {
        "mean_of_run_means_ms": float(stats["mean_of_run_means_ms"]),
        "mean_over_all_calls_ms": float(stats["mean_over_all_calls_ms"]),
        "call_count_total": int(stats["call_count_total"]),
        "amortized_ms_per_substep": total_elapsed_ms / max(total_substeps_all_runs, 1.0e-12),
    }


def _sum_ops(payload: dict[str, Any], op_names: list[str]) -> dict[str, float] | None:
    found = []
    for name in op_names:
        metric = _aggregate_op_metric(payload, name)
        if metric is not None:
            found.append(metric)
    if not found:
        return None
    return {
        "mean_of_run_means_ms": float(sum(item["mean_of_run_means_ms"] for item in found)),
        "mean_over_all_calls_ms": float(sum(item["mean_over_all_calls_ms"] for item in found)),
        "call_count_total": int(sum(item["call_count_total"] for item in found)),
        "amortized_ms_per_substep": float(sum(item["amortized_ms_per_substep"] for item in found)),
    }


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _top_ops(rows: list[dict[str, Any]], *, mode_key: str | None = None, topn: int = 10) -> list[dict[str, Any]]:
    filtered = rows
    if mode_key is not None:
        filtered = [row for row in rows if row.get("newton_mode") == mode_key]
    filtered = [
        row
        for row in filtered
        if str(row.get("op_name", "")) not in {"total_step", "total_substep", "total_frame", "total_frame_start_marker"}
    ]
    ordered = sorted(filtered, key=lambda row: float(row["amortized_ms_per_substep"]), reverse=True)
    return [
        {
            "op_name": row["op_name"],
            "amortized_ms_per_substep": float(row["amortized_ms_per_substep"]),
            "mean_of_run_means_ms": float(row["mean_of_run_means_ms"]),
            "call_count_total": int(row["call_count_total"]),
        }
        for row in ordered[:topn]
    ]


def main() -> int:
    args = parse_args()
    args.out_dir = args.out_dir.expanduser().resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    newton_baseline_tp = _load(args.newton_baseline_throughput)
    newton_precomputed_tp = _load(args.newton_precomputed_throughput)
    newton_baseline_attr = _load(args.newton_baseline_attribution)
    newton_precomputed_attr = _load(args.newton_precomputed_attribution)
    phystwin_tp = _load(args.phystwin_throughput)
    phystwin_attr = _load(args.phystwin_kernel_attribution)

    throughput_rows = [
        _throughput_row("newton_baseline", newton_baseline_tp),
        _throughput_row("newton_precomputed", newton_precomputed_tp),
        _throughput_row("phystwin_graph_headless", phystwin_tp),
    ]

    for row in throughput_rows:
        if row["label"] == "newton_baseline":
            row["slowdown_vs_phystwin"] = row["ms_per_substep_mean"] / max(throughput_rows[-1]["ms_per_substep_mean"], 1.0e-12)
        elif row["label"] == "newton_precomputed":
            row["slowdown_vs_phystwin"] = row["ms_per_substep_mean"] / max(throughput_rows[-1]["ms_per_substep_mean"], 1.0e-12)
            row["speedup_vs_newton_baseline"] = throughput_rows[0]["ms_per_substep_mean"] / max(row["ms_per_substep_mean"], 1.0e-12)
        else:
            row["slowdown_vs_phystwin"] = 1.0
            row["speedup_vs_newton_baseline"] = None

    newton_raw_rows = []
    for payload_name, payload in (
        ("baseline", newton_baseline_attr),
        ("precomputed", newton_precomputed_attr),
    ):
        for op_name in sorted(payload.get("aggregate", {}).keys()):
            metric = _aggregate_op_metric(payload, op_name)
            if metric is None:
                continue
            newton_raw_rows.append(
                {
                    "newton_mode": payload_name,
                    "op_name": op_name,
                    "mean_of_run_means_ms": metric["mean_of_run_means_ms"],
                    "mean_over_all_calls_ms": metric["mean_over_all_calls_ms"],
                    "call_count_total": metric["call_count_total"],
                    "amortized_ms_per_substep": metric["amortized_ms_per_substep"],
                }
            )

    phystwin_raw_rows = []
    for op_name in sorted(phystwin_attr.get("aggregate", {}).keys()):
        metric = _aggregate_op_metric(phystwin_attr, op_name)
        if metric is None:
            continue
        phystwin_raw_rows.append(
            {
                "op_name": op_name,
                "mean_of_run_means_ms": metric["mean_of_run_means_ms"],
                "mean_over_all_calls_ms": metric["mean_over_all_calls_ms"],
                "call_count_total": metric["call_count_total"],
                "amortized_ms_per_substep": metric["amortized_ms_per_substep"],
            }
        )

    raw_match_rows = []
    for row in RAW_MATCHUPS:
        nb = _aggregate_op_metric(newton_baseline_attr, row["newton_op"])
        np_ = _aggregate_op_metric(newton_precomputed_attr, row["newton_op"])
        ph_ops = [] if row["phystwin_op"] == "n/a" else [op.strip() for op in row["phystwin_op"].split("+")]
        ph_metric = _sum_ops(phystwin_attr, ph_ops)
        raw_match_rows.append(
            {
                "newton_op": row["newton_op"],
                "phystwin_op": row["phystwin_op"],
                "newton_baseline_ms_per_call": None if nb is None else nb["mean_of_run_means_ms"],
                "newton_baseline_amortized_ms_per_substep": None if nb is None else nb["amortized_ms_per_substep"],
                "newton_precomputed_ms_per_call": None if np_ is None else np_["mean_of_run_means_ms"],
                "newton_precomputed_amortized_ms_per_substep": None if np_ is None else np_["amortized_ms_per_substep"],
                "phystwin_ms_per_call": None if ph_metric is None else ph_metric["mean_of_run_means_ms"],
                "phystwin_amortized_ms_per_substep": None if ph_metric is None else ph_metric["amortized_ms_per_substep"],
                "note": row["note"],
            }
        )

    grouped_rows = []
    for row in GROUP_MATCHUPS:
        nb = _sum_ops(newton_baseline_attr, row["newton_ops"])
        np_ = _sum_ops(newton_precomputed_attr, row["newton_ops"])
        ph = _sum_ops(phystwin_attr, row["phystwin_ops"])
        grouped_rows.append(
            {
                "concept": row["concept"],
                "newton_ops": " + ".join(row["newton_ops"]) if row["newton_ops"] else "n/a",
                "phystwin_ops": " + ".join(row["phystwin_ops"]) if row["phystwin_ops"] else "n/a",
                "newton_baseline_amortized_ms_per_substep": None if nb is None else nb["amortized_ms_per_substep"],
                "newton_precomputed_amortized_ms_per_substep": None if np_ is None else np_["amortized_ms_per_substep"],
                "phystwin_amortized_ms_per_substep": None if ph is None else ph["amortized_ms_per_substep"],
                "note": row["note"],
            }
        )

    summary = {
        "case_name": str(phystwin_tp["case_name"]),
        "trajectory_frames": int(phystwin_tp["trajectory_frames"]),
        "total_substeps": int(phystwin_tp["total_substeps"]),
        "throughput": throughput_rows,
        "top_newton_baseline_ops": _top_ops(newton_raw_rows, mode_key="baseline"),
        "top_newton_precomputed_ops": _top_ops(newton_raw_rows, mode_key="precomputed"),
        "top_phystwin_ops": _top_ops(phystwin_raw_rows, mode_key=None),
        "newton_baseline_group_shares": newton_baseline_attr.get("group_shares", {}),
        "newton_precomputed_group_shares": newton_precomputed_attr.get("group_shares", {}),
        "phystwin_group_shares": phystwin_attr.get("group_shares", {}),
        "raw_matchup_rows": raw_match_rows,
        "grouped_matchup_rows": grouped_rows,
    }

    summary_path = args.out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    _write_csv(
        args.out_dir / "throughput_summary.csv",
        throughput_rows,
        [
            "label",
            "profile_mode",
            "trajectory_frames",
            "total_substeps",
            "wall_ms_mean",
            "wall_ms_std",
            "sim_time_sec_mean",
            "ms_per_substep_mean",
            "ms_per_substep_std",
            "rtf_mean",
            "rtf_std",
            "slowdown_vs_phystwin",
            "speedup_vs_newton_baseline",
        ],
    )
    _write_csv(
        args.out_dir / "newton_raw_ops.csv",
        newton_raw_rows,
        [
            "newton_mode",
            "op_name",
            "mean_of_run_means_ms",
            "mean_over_all_calls_ms",
            "call_count_total",
            "amortized_ms_per_substep",
        ],
    )
    _write_csv(
        args.out_dir / "phystwin_raw_ops.csv",
        phystwin_raw_rows,
        [
            "op_name",
            "mean_of_run_means_ms",
            "mean_over_all_calls_ms",
            "call_count_total",
            "amortized_ms_per_substep",
        ],
    )
    _write_csv(
        args.out_dir / "operation_matchup_raw.csv",
        raw_match_rows,
        [
            "newton_op",
            "phystwin_op",
            "newton_baseline_ms_per_call",
            "newton_baseline_amortized_ms_per_substep",
            "newton_precomputed_ms_per_call",
            "newton_precomputed_amortized_ms_per_substep",
            "phystwin_ms_per_call",
            "phystwin_amortized_ms_per_substep",
            "note",
        ],
    )
    _write_csv(
        args.out_dir / "operation_matchup_grouped.csv",
        grouped_rows,
        [
            "concept",
            "newton_ops",
            "phystwin_ops",
            "newton_baseline_amortized_ms_per_substep",
            "newton_precomputed_amortized_ms_per_substep",
            "phystwin_amortized_ms_per_substep",
            "note",
        ],
    )

    md_lines = [
        "# Interactive Playground One-To-One Performance Comparison",
        "",
        f"- case: `{summary['case_name']}`",
        f"- trajectory frames: `{summary['trajectory_frames']}`",
        f"- total substeps: `{summary['total_substeps']}`",
        "",
        "## Throughput",
        "",
        "| Label | ms/substep | RTF | Note |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in throughput_rows:
        note = ""
        if row["label"] == "newton_baseline":
            note = f"{row['slowdown_vs_phystwin']:.3f}x slower than PhysTwin"
        elif row["label"] == "newton_precomputed":
            note = (
                f"{row['slowdown_vs_phystwin']:.3f}x slower than PhysTwin; "
                f"{row['speedup_vs_newton_baseline']:.3f}x faster than Newton baseline"
            )
        else:
            note = "reference"
        md_lines.append(
            f"| {row['label']} | {row['ms_per_substep_mean']:.6f} | {row['rtf_mean']:.3f} | {note} |"
        )

    md_lines.extend(
        [
            "",
            "## Grouped One-To-One Matchup",
            "",
            "| Concept | Newton baseline ms/substep | Newton precomputed ms/substep | PhysTwin ms/substep |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in grouped_rows:
        md_lines.append(
            f"| {row['concept']} | {_fmt(row['newton_baseline_amortized_ms_per_substep'])} | {_fmt(row['newton_precomputed_amortized_ms_per_substep'])} | {_fmt(row['phystwin_amortized_ms_per_substep'])} |"
        )

    md_lines.extend(
        [
            "",
            "## Raw Newton->PhysTwin Matchup",
            "",
            "| Newton op | PhysTwin op | Newton baseline ms/substep | Newton precomputed ms/substep | PhysTwin ms/substep | Note |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in raw_match_rows:
        md_lines.append(
            f"| {row['newton_op']} | {row['phystwin_op']} | {_fmt(row['newton_baseline_amortized_ms_per_substep'])} | {_fmt(row['newton_precomputed_amortized_ms_per_substep'])} | {_fmt(row['phystwin_amortized_ms_per_substep'])} | {row['note']} |"
        )

    (args.out_dir / "comparison.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Comparison summary: {summary_path}")
    print(f"Comparison markdown: {args.out_dir / 'comparison.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
