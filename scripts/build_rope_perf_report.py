#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import markdown
from weasyprint import HTML


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "results" / "rope_perf_apples_to_apples"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build a standalone Todo 2 rope performance report.")
    p.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    p.add_argument("--out-dir", type=Path, default=None)
    return p.parse_args()


def _read_rows(index_csv: Path) -> list[dict[str, str]]:
    with index_csv.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _row_map(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["stage"]: row for row in rows}


def _f(row: dict[str, str], key: str, digits: int = 3) -> str:
    return f"{float(row[key]):.{digits}f}"


def _markdown_to_pdf(md_text: str, html_path: Path, pdf_path: Path) -> None:
    html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 32px 40px;
      color: #1f2328;
      line-height: 1.45;
      font-size: 12pt;
    }}
    h1, h2, h3 {{ color: #0f2b46; }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin: 12px 0 20px;
      font-size: 10.5pt;
    }}
    th, td {{
      border: 1px solid #c8d1dc;
      padding: 6px 8px;
      vertical-align: top;
    }}
    th {{
      background: #eaf1f8;
      text-align: left;
    }}
    code {{
      font-family: "DejaVu Sans Mono", monospace;
      background: #f6f8fa;
      padding: 1px 4px;
      border-radius: 3px;
    }}
    ul {{ margin-top: 6px; }}
  </style>
</head>
<body>
{html_body}
</body>
</html>
"""
    html_path.write_text(html, encoding="utf-8")
    HTML(filename=str(html_path)).write_pdf(str(pdf_path))


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    out_dir = (args.out_dir or (root / "report")).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = _read_rows(root / "index.csv")
    stage = _row_map(rows)
    summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
    rich_rows = {row["stage"]: row for row in summary.get("rows", [])}
    methodology = (root / "notes" / "methodology.md").read_text(encoding="utf-8").strip()
    conclusions = (root / "notes" / "conclusions.md").read_text(encoding="utf-8").strip()
    nsight = (root / "notes" / "nsight.md").read_text(encoding="utf-8").strip()

    a0 = stage["A0_baseline_throughput"]
    a1 = stage["A1_precomputed_throughput"]
    b0 = stage["B0_headless_throughput"]
    a2 = stage["A2_baseline_attribution"]
    a3 = stage["A3_precomputed_attribution"]
    b1 = stage["B1_headless_attribution"]
    b1_payload = rich_rows["B1_headless_attribution"]["payload"]

    bridge_speedup = summary["speedup_precomputed_vs_baseline"]
    a3_bridge = summary["a3_bridge_ms"]
    a3_internal = summary["a3_internal_ms"]
    a3_collision = summary["a3_collision_ms"]
    a3_integration = summary["a3_integration_ms"]
    a3_unexplained = summary["a3_unexplained_ms"]

    md = f"""# Todo 2 Report: Rope Apples-To-Apples Performance Investigation

## Executive Summary

This report answers three questions in order.

1. For the same `rope_double_hand` replay case, same controller trajectory, same `dt`, same substeps, same GPU, and rendering disabled, Newton is slower than PhysTwin.
2. A meaningful part of the Newton slowdown is controller bridge tax, but not all of it.
3. After removing most bridge tax, the remaining gap is better explained by execution structure and launch style than by collision.

## Benchmark Scope

- Same case: `rope_double_hand`
- Same controller trajectory: PhysTwin vs IR controller trajectory max abs diff = `0.0`
- Same physics settings: `dt = 5e-05`, `substeps = 667`
- Same hardware: RTX 4090
- Primary comparison excludes rendering, GUI, and video export

## Main Benchmark Table

| Stage | Meaning | ms/substep | RTF | Relative point |
| --- | --- | ---: | ---: | --- |
| Newton A0 | baseline controller write | {_f(a0, "ms_per_substep_mean", 6)} | {_f(a0, "rtf_mean")} | bridge tax on |
| Newton A1 | precomputed controller write | {_f(a1, "ms_per_substep_mean", 6)} | {_f(a1, "rtf_mean")} | same replay, bridge tax reduced |
| PhysTwin B0 | headless replay | {_f(b0, "ms_per_substep_mean", 6)} | {_f(b0, "rtf_mean")} | same replay, graph-enabled |

## Direct Answers

### Q1. Is Newton slower or faster than PhysTwin?

Newton is slower on the fair rope baseline.

- Newton A0 vs PhysTwin B0: `{_f(a0, "slowdown_vs_phystwin_headless")}x` slower in `ms/substep`
- Newton A1 vs PhysTwin B0: `{_f(a1, "slowdown_vs_phystwin_headless")}x` slower in `ms/substep`

So even after reducing bridge tax with precomputed controller writes, Newton still remains materially slower than PhysTwin on the same rope replay.

### Q2. If Newton is slower, where is the time going?

First, bridge tax is real.

- A0 -> A1 speedup: `{bridge_speedup:.3f}x`

So a substantial part of the original Newton slowdown comes from controller bridge work.

But that is not the whole story.

Newton A3 precomputed attribution:

- bridge/controller-write-related: `{a3_bridge:.3f} ms/substep`
- spring/internal-force path: `{a3_internal:.3f} ms/substep`
- integration: `{a3_integration:.3f} ms/substep`
- collision/contact: `{a3_collision:.3f} ms/substep`
- unexplained/runtime overhead: `{a3_unexplained:.3f} ms/substep`

PhysTwin B1 headless attribution:

- controller target update: `{float(b1_payload["aggregate"]["controller_target"]["mean_of_run_means_ms"]):.3f} ms/frame`
- simulator launch: `{float(b1_payload["aggregate"]["simulator_launch"]["mean_of_run_means_ms"]):.3f} ms/frame`
- state reset: `{float(b1_payload["aggregate"]["state_reset"]["mean_of_run_means_ms"]):.3f} ms/frame`

Interpretation:

- Collision is not the main cause on the pure rope replay baseline.
- Newton still spends meaningful time in internal-force + integration + runtime overhead after bridge tax is reduced.
- PhysTwin headless replay is dominated by simulator launch on a graph-enabled path, not by GUI or rendering.

### Q3. What optimization path is justified now?

Only after the benchmark and attribution are complete, the justified roadmap is:

1. Keep precomputed controller writes as the default replay baseline for throughput work.
2. Investigate graph-captured or more batched Newton replay execution before touching physics settings.
3. Use A1 vs B0 Nsight evidence to separate host/launch structure from true kernel cost.
4. Keep weak-contact profiling as a separate workstream instead of mixing it into the pure rope baseline.

## Why The Gap Is Not A Collision Story

- Newton pure rope replay keeps ground and shape contact disabled in the benchmark configuration.
- Newton A3 collision bucket is only `{a3_collision:.6f} ms/substep`.
- PhysTwin headless benchmark reports `object_collision_flag = False`.

So the clean rope replay baseline is not contact-heavy. Blaming collision here would not be evidence-based.

## Nsight Systems Support

Newton A1:

- CUDA API dominated by `cuLaunchKernel`
- Top GPU kernels are spring, integrate-particles, kinematic write, and drag correction

PhysTwin B0:

- CUDA API dominated by `cudaGraphLaunch_v10000`
- Top GPU kernels execute inside the captured replay graph

This supports a graph-launch / execution-structure explanation for the remaining gap.

## Canonical Artifact Paths

- Benchmark root: `{root}`
- Main table: `{root / "index.csv"}`
- Best evidence: `{root / "BEST_EVIDENCE.md"}`
- Methodology: `{root / "notes" / "methodology.md"}`
- Conclusions: `{root / "notes" / "conclusions.md"}`
- Nsight notes: `{root / "notes" / "nsight.md"}`
- Slides: `{ROOT / "formal_slide" / "meeting_2026_04_01" / "bridge_meeting_20260401.pptx"}`

## Appendix

### Methodology

{methodology}

### Conclusions

{conclusions}

### Nsight Notes

{nsight}
"""

    md_path = out_dir / "todo2_rope_perf_report.md"
    html_path = out_dir / "todo2_rope_perf_report.html"
    pdf_path = out_dir / "todo2_rope_perf_report.pdf"
    md_path.write_text(md, encoding="utf-8")
    _markdown_to_pdf(md, html_path, pdf_path)
    print(f"MD: {md_path}")
    print(f"HTML: {html_path}")
    print(f"PDF: {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
