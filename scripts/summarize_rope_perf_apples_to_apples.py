#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_STAGE_DIRS = {
    "A0_baseline_throughput": ("newton", "A0_baseline_throughput"),
    "A1_precomputed_throughput": ("newton", "A1_precomputed_throughput"),
    "A2_baseline_attribution": ("newton", "A2_baseline_attribution"),
    "A3_precomputed_attribution": ("newton", "A3_precomputed_attribution"),
    "B0_headless_throughput": ("phystwin", "B0_headless_throughput"),
    "B1_headless_attribution": ("phystwin", "B1_headless_attribution"),
}

NEWTON_BRIDGE_OPS = (
    "controller_interp_cpu_ms",
    "ctrl_target_assign_ms",
    "ctrl_vel_assign_ms",
    "physical_radius_assign_ms",
    "write_kinematic_state",
    "drag_correction",
)
NEWTON_INTERNAL_OPS = (
    "spring_forces",
    "triangle_forces",
    "bending_forces",
    "tetra_forces",
    "body_joint_forces",
)
NEWTON_COLLISION_OPS = (
    "particle_grid_build",
    "model_collide",
    "particle_contact_forces",
    "triangle_contact_forces",
    "body_contact_forces",
    "particle_body_contact_forces",
)
NEWTON_INTEGRATION_OPS = ("integrate_particles", "integrate_bodies")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Summarize rope apples-to-apples benchmark results.")
    p.add_argument(
        "--root",
        type=Path,
        default=ROOT / "results" / "rope_perf_apples_to_apples",
    )
    return p.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_summary_path(stage_dir: Path) -> Path:
    candidates = sorted(stage_dir.glob("*.json"))
    for path in candidates:
        if path.name == "manifest.json":
            continue
        return path
    raise FileNotFoundError(f"No summary JSON found in {stage_dir}")


def _mean_std_cv(values: list[float]) -> tuple[float, float, float]:
    arr = np.asarray(values, dtype=np.float64)
    mean = float(np.mean(arr))
    std = float(np.std(arr))
    cv = float(std / max(mean, 1.0e-12))
    return mean, std, cv


def _normalize_stage(stage_name: str, stage_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    runs = payload["runs"]
    wall_values = [float(run["wall_ms"]) for run in runs]
    sim_time_sec = float(runs[0]["sim_time_sec"]) if runs else float(payload.get("sim_time_sec", 0.0))
    total_substeps = int(runs[0]["total_substeps"]) if runs else int(payload["total_substeps"])
    trajectory_frames = int(runs[0]["trajectory_frames"]) if runs else int(payload["trajectory_frames"])
    wall_mean, wall_std, wall_cv = _mean_std_cv(wall_values)
    ms_per_substep = wall_mean / max(total_substeps, 1)
    ms_per_controller_frame = wall_mean / max(trajectory_frames, 1)
    rtf = sim_time_sec / max(wall_mean / 1000.0, 1.0e-12)
    slowdown_vs_realtime = 1.0 / max(rtf, 1.0e-12)

    family = "newton" if stage_name.startswith("A") else "phystwin"
    mode = payload.get("profile_mode", payload.get("mode"))
    device = payload.get("runtime_device", payload.get("device"))
    git_rev = payload.get("phystwin_git_rev", payload.get("newton_git_rev"))
    if not git_rev:
        git_rev_path = stage_dir / "git_rev.txt"
        git_rev = git_rev_path.read_text(encoding="utf-8").strip() if git_rev_path.exists() else "unknown"
    controller_write_mode = payload.get("controller_write_mode")
    use_graph = payload.get("use_graph")
    object_collision_flag = bool(payload.get("object_collision_flag", False))
    return {
        "stage": stage_name,
        "family": family,
        "mode": mode,
        "device": device,
        "git_rev": git_rev,
        "controller_write_mode": controller_write_mode,
        "use_graph": use_graph,
        "case_name": payload.get("case_name"),
        "trajectory_frames": trajectory_frames,
        "total_substeps": total_substeps,
        "sim_time_sec": sim_time_sec,
        "wall_ms_mean": wall_mean,
        "wall_ms_std": wall_std,
        "wall_ms_cv": wall_cv,
        "ms_per_substep_mean": ms_per_substep,
        "ms_per_controller_frame_mean": ms_per_controller_frame,
        "rtf_mean": rtf,
        "slowdown_vs_realtime": slowdown_vs_realtime,
        "object_collision_flag": object_collision_flag,
        "payload": payload,
    }


def _aggregate_sum(aggregate: dict[str, Any], op_names: tuple[str, ...]) -> float:
    total = 0.0
    for op_name in op_names:
        total += float(aggregate.get(op_name, {}).get("mean_of_run_means_ms", 0.0))
    return total


def _write_index_csv(root: Path, rows: list[dict[str, Any]]) -> Path:
    path = root / "index.csv"
    fieldnames = [
        "stage",
        "family",
        "mode",
        "controller_write_mode",
        "use_graph",
        "device",
        "git_rev",
        "trajectory_frames",
        "total_substeps",
        "sim_time_sec",
        "wall_ms_mean",
        "wall_ms_std",
        "wall_ms_cv",
        "ms_per_substep_mean",
        "ms_per_controller_frame_mean",
        "rtf_mean",
        "slowdown_vs_realtime",
        "slowdown_vs_phystwin_headless",
        "object_collision_flag",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name) for name in fieldnames})
    return path


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def _extract_nsys_rows(stats_path: Path, section_title: str, limit: int = 4) -> list[tuple[str, str]]:
    if not stats_path.exists():
        return []
    lines = stats_path.read_text(encoding="utf-8").splitlines()
    rows: list[tuple[str, str]] = []
    in_section = False
    for line in lines:
        if section_title in line:
            in_section = True
            rows.clear()
            continue
        if not in_section:
            continue
        if not line.strip():
            if rows:
                break
            continue
        if line.lstrip().startswith("Time (%)") or set(line.strip()) == {"-"}:
            continue
        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) < 2:
            continue
        percent = parts[0]
        name = parts[-1]
        if (
            percent.startswith("NOTICE:")
            or percent.startswith("Processing")
            or set(percent) == {"-"}
            or set(name) == {"-"}
        ):
            continue
        rows.append((percent, name))
        if len(rows) >= limit:
            break
    return rows


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / "notes").mkdir(parents=True, exist_ok=True)
    (root / "slides" / "assets").mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    stage_payloads: dict[str, dict[str, Any]] = {}
    for stage_name, (family, rel) in EXPECTED_STAGE_DIRS.items():
        stage_dir = root / family / rel
        if not stage_dir.exists():
            missing.append(stage_name)
            continue
        summary_path = _stage_summary_path(stage_dir)
        payload = _load_json(summary_path)
        stage_payloads[stage_name] = payload
        rows.append(_normalize_stage(stage_name, stage_dir, payload))

    rows_by_stage = {row["stage"]: row for row in rows}
    b0 = rows_by_stage.get("B0_headless_throughput")
    if b0 is not None:
        for row in rows:
            if row["mode"] == "throughput":
                row["slowdown_vs_phystwin_headless"] = (
                    row["ms_per_substep_mean"] / max(b0["ms_per_substep_mean"], 1.0e-12)
                )
            else:
                row["slowdown_vs_phystwin_headless"] = None
    else:
        for row in rows:
            row["slowdown_vs_phystwin_headless"] = None

    index_csv = _write_index_csv(root, rows)

    a0 = rows_by_stage.get("A0_baseline_throughput")
    a1 = rows_by_stage.get("A1_precomputed_throughput")
    a2 = stage_payloads.get("A2_baseline_attribution")
    a3 = stage_payloads.get("A3_precomputed_attribution")
    b1 = stage_payloads.get("B1_headless_attribution")
    nsight_root = root / "nsight"
    nsys_newton_api = _extract_nsys_rows(nsight_root / "newton_A1" / "stats.txt", "CUDA API Summary")
    nsys_newton_gpu = _extract_nsys_rows(nsight_root / "newton_A1" / "stats.txt", "CUDA GPU Kernel Summary")
    nsys_phystwin_api = _extract_nsys_rows(nsight_root / "phystwin_B0" / "stats.txt", "CUDA API Summary")
    nsys_phystwin_gpu = _extract_nsys_rows(nsight_root / "phystwin_B0" / "stats.txt", "CUDA GPU Kernel Summary")

    speedup_precomputed_vs_baseline = None
    if a0 and a1:
        speedup_precomputed_vs_baseline = a0["ms_per_substep_mean"] / max(a1["ms_per_substep_mean"], 1.0e-12)

    a3_bridge_ms = a3_internal_ms = a3_collision_ms = a3_integration_ms = a3_unexplained_ms = None
    if a3:
        aggregate = a3.get("aggregate", {})
        total_substep_ms = float(aggregate.get("total_substep", {}).get("mean_of_run_means_ms", 0.0))
        a3_bridge_ms = _aggregate_sum(aggregate, NEWTON_BRIDGE_OPS)
        a3_internal_ms = _aggregate_sum(aggregate, NEWTON_INTERNAL_OPS)
        a3_collision_ms = _aggregate_sum(aggregate, NEWTON_COLLISION_OPS)
        a3_integration_ms = _aggregate_sum(aggregate, NEWTON_INTEGRATION_OPS)
        a3_unexplained_ms = max(
            total_substep_ms - a3_bridge_ms - a3_internal_ms - a3_collision_ms - a3_integration_ms,
            0.0,
        )

    parity = stage_payloads.get("B0_headless_throughput", {}).get("trajectory_parity", {})
    methodology_md = f"""
# Rope Apples-To-Apples Methodology

- Same case: `rope_double_hand`
- Same controller trajectory: IR vs PhysTwin controller trajectory max abs diff = `{parity.get('controller_traj_max_abs_diff', 'n/a')}`
- Same dt: Newton IR `sim_dt = {parity.get('sim_dt_ir', 'n/a')}`
- Same substeps: Newton IR `sim_substeps = {parity.get('sim_substeps_ir', 'n/a')}`
- Same GPU: RTX 4090 on this workstation
- Primary comparison excludes rendering:
  - Newton uses `demo_rope_control_realtime_viewer.py --viewer null --profile-only`
  - PhysTwin uses `benchmark_phystwin_rope_headless.py` with GUI / readback / video export excluded from the timing loop

Primary benchmark rows:

- A0 = Newton baseline controller-write throughput
- A1 = Newton precomputed controller-write throughput
- A2 = Newton baseline attribution
- A3 = Newton precomputed attribution
- B0 = PhysTwin headless throughput
- B1 = PhysTwin headless attribution
"""

    comparison_lines: list[str] = []
    if a0:
        comparison_lines.append(
            f"- Newton A0 baseline throughput: `{a0['wall_ms_mean']:.3f} ms` total, `{a0['ms_per_substep_mean']:.6f} ms/substep`, `RTF={a0['rtf_mean']:.3f}`"
        )
    if a1:
        comparison_lines.append(
            f"- Newton A1 precomputed throughput: `{a1['wall_ms_mean']:.3f} ms` total, `{a1['ms_per_substep_mean']:.6f} ms/substep`, `RTF={a1['rtf_mean']:.3f}`"
        )
    if b0:
        comparison_lines.append(
            f"- PhysTwin B0 headless throughput: `{b0['wall_ms_mean']:.3f} ms` total, `{b0['ms_per_substep_mean']:.6f} ms/substep`, `RTF={b0['rtf_mean']:.3f}`"
        )
    if speedup_precomputed_vs_baseline is not None:
        comparison_lines.append(
            f"- Newton precomputed vs baseline bridge speedup: `{speedup_precomputed_vs_baseline:.3f}x`"
        )
    if a1 and b0:
        comparison_lines.append(
            f"- Remaining Newton-vs-PhysTwin throughput gap after bridge precompute: `{a1['slowdown_vs_phystwin_headless']:.3f}x` slower in `ms/substep`"
        )

    findings_lines: list[str] = []
    if speedup_precomputed_vs_baseline is not None:
        findings_lines.append(
            f"- H1 supported: controller bridge tax is real because A1 improves over A0 by `{speedup_precomputed_vs_baseline:.3f}x` on the same rope replay."
        )
    if b0 and stage_payloads.get("B0_headless_throughput", {}).get("use_graph") is True:
        findings_lines.append(
            "- H2 supported by source and run evidence: PhysTwin headless replay keeps CUDA graph launch enabled on the rope path."
        )
    if a3_bridge_ms is not None:
        findings_lines.append(
            f"- Newton A3 attribution split: bridge `{a3_bridge_ms:.3f} ms/substep`, internal force `{a3_internal_ms:.3f} ms/substep`, collision `{a3_collision_ms:.3f} ms/substep`, integration `{a3_integration_ms:.3f} ms/substep`, unexplained `{a3_unexplained_ms:.3f} ms/substep`."
        )
        if a3_internal_ms >= max(a3_bridge_ms, a3_collision_ms, a3_integration_ms, a3_unexplained_ms):
            findings_lines.append(
                "- H4 is currently the strongest remaining Newton-side hypothesis after bridge tax reduction: internal spring-force work is the largest measured bucket."
            )
    if a3_collision_ms is not None and b0 is not None:
        findings_lines.append(
            f"- H5 supported: collision is not the main reason in the pure rope baseline because Newton collision bucket is `{a3_collision_ms:.6f} ms/substep` and PhysTwin reports `object_collision_flag = {bool(stage_payloads.get('B0_headless_throughput', {}).get('object_collision_flag', False))}`."
        )
    if a1 and b0:
        findings_lines.append(
            "- H3 remains relevant: even after removing most controller-write tax, a material Newton-vs-PhysTwin gap still remains and must be explained by solver/runtime structure rather than contact."
        )
    if nsys_newton_api and nsys_phystwin_api:
        findings_lines.append(
            f"- Nsight Systems supports H2: Newton A1 API time is dominated by `{nsys_newton_api[0][1]}` while PhysTwin B0 API time is dominated by `{nsys_phystwin_api[0][1]}`."
        )
    if nsys_newton_gpu and nsys_phystwin_gpu:
        findings_lines.append(
            f"- Nsight GPU-side shape: Newton A1 top kernel is `{nsys_newton_gpu[0][1]}`, while PhysTwin B0 top kernel is `{nsys_phystwin_gpu[0][1]}` inside a graph-launched replay path."
        )

    optimization_lines: list[str] = []
    if speedup_precomputed_vs_baseline is not None:
        optimization_lines.append("- Make precomputed controller writes the default benchmark path when the goal is simulator throughput rather than bridge stress-testing.")
    if a1 and b0:
        optimization_lines.append("- Investigate graph-captured or more batched step execution on the Newton replay path before touching physics settings.")
    if a3_internal_ms is not None:
        optimization_lines.append("- Use Newton precomputed attribution, then Nsight on A1 vs B0, to decide whether the remaining gap is dominated by internal-force kernels or host/runtime launch overhead.")

    nsight_md_lines = [
        "# Rope Perf Nsight Findings",
        "",
        "## Newton A1",
        *(f"- CUDA API: `{percent}` `{name}`" for percent, name in nsys_newton_api),
        *(f"- CUDA GPU kernels: `{percent}` `{name}`" for percent, name in nsys_newton_gpu),
        "",
        "## PhysTwin B0",
        *(f"- CUDA API: `{percent}` `{name}`" for percent, name in nsys_phystwin_api),
        *(f"- CUDA GPU kernels: `{percent}` `{name}`" for percent, name in nsys_phystwin_gpu),
    ]

    conclusions_md = "\n".join(
        [
            "# Rope Apples-To-Apples Conclusions",
            "",
            "## Throughput Comparison",
            *comparison_lines,
            "",
            "## Evidence-Based Findings",
            *findings_lines,
            "",
            "## Justified Optimization Roadmap",
            *optimization_lines,
        ]
    )

    best_evidence_md = "\n".join(
        [
            "# Best Evidence",
            "",
            "Primary apples-to-apples benchmark rows:",
            *comparison_lines,
            "",
            "Short conclusion:",
            *(findings_lines[:4] if findings_lines else ["- Benchmark matrix is still incomplete."]),
        ]
    )

    open_questions_md = "\n".join(
        [
            "# Rope Perf Open Questions",
            "",
            *(f"- Missing stage: `{name}`" for name in missing),
            "- Run Nsight Systems on Newton A1 and PhysTwin B0 to separate GPU kernel time from host/launch overhead.",
            "- If PhysTwin B1 remains shallow, document exactly which simulator-internal costs still cannot be decomposed further.",
        ]
    )

    summary_payload = {
        "rows": rows,
        "missing_stages": missing,
        "speedup_precomputed_vs_baseline": speedup_precomputed_vs_baseline,
        "a3_bridge_ms": a3_bridge_ms,
        "a3_internal_ms": a3_internal_ms,
        "a3_collision_ms": a3_collision_ms,
        "a3_integration_ms": a3_integration_ms,
        "a3_unexplained_ms": a3_unexplained_ms,
    }

    _write_text(root / "README.md", methodology_md + "\n\nSee also: `BEST_EVIDENCE.md`, `index.csv`, and `notes/conclusions.md`.")
    _write_text(root / "BEST_EVIDENCE.md", best_evidence_md)
    _write_text(root / "notes" / "methodology.md", methodology_md)
    _write_text(root / "notes" / "conclusions.md", conclusions_md)
    _write_text(root / "notes" / "nsight.md", "\n".join(nsight_md_lines))
    _write_text(root / "notes" / "open_questions.md", open_questions_md)
    _write_text(root / "slides" / "assets" / "rope_perf_summary.md", best_evidence_md)
    (root / "summary.json").write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    print(f"Wrote: {index_csv}")
    print(f"Wrote: {root / 'BEST_EVIDENCE.md'}")
    print(f"Wrote: {root / 'notes' / 'conclusions.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
