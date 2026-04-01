# Status: Rope Perf Apples To Apples

## Current State

- Completed for the current rope meeting scope
- Committed current run id:
  - `20260401_rope_perf_meeting_bundle`
- Canonical result root:
  - `results/rope_perf_apples_to_apples/`
- Committed results metadata:
  - `results_meta/tasks/rope_perf_apples_to_apples.json`
- Slides/transcript updated:
  - `formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx`
  - `formal_slide/meeting_2026_04_01/transcript.md`
  - `formal_slide/meeting_2026_04_01/transcript.pdf`

## Last Completed Step

- Completed the full apples-to-apples benchmark matrix:
  - Newton A0/A1 throughput
  - Newton A2/A3 attribution
  - PhysTwin B0 headless throughput
  - PhysTwin B1 headless attribution
  - Nsight A1/B0 traces
  - summary + notes + slide update
- Built a standalone Todo 2 rope performance report for external sharing:
  - `results/rope_perf_apples_to_apples/report/todo2_rope_perf_report.md`
  - `results/rope_perf_apples_to_apples/report/todo2_rope_perf_report.pdf`
- Release decision:
  - user explicitly requested email send
  - sending target uses the repo-configured default recipient in `send_pdf_via_yahoo.py`

## 2026-04-01 Profiling Section Rebuild

- Rebuilt the TODO 2 profiling section in
  `formal_slide/meeting_2026_04_01/` around a stricter evidence hierarchy:
  - why this matters to the real viewer
  - controlled rope benchmark definition
  - throughput result
  - controller replay overhead vs residual gap
  - runtime-organization interpretation
  - optimization implication
- Downgraded wrapper / benchmark-entry references to methodology notes only.
- Upgraded slide citations to Newton core + PhysTwin core:
  - `Newton/newton/newton/_src/solvers/semi_implicit/kernels_particle.py`
  - `Newton/newton/newton/_src/solvers/semi_implicit/solver_semi_implicit.py`
  - `PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py`
- Added a file-backed audit for the rebuild:
  - `formal_slide/meeting_2026_04_01/todo2_rope_profiling_rebuild_audit_20260401.md`

## 2026-04-01 Real-Viewer Relevance Update

- Added a new E1 benchmark row:
  - `results/rope_perf_apples_to_apples/newton/E1_viewer_end_to_end/`
- E1 now uses the visible `ViewerGL` render path on the same rope replay:
  - `viewer FPS ≈ 37.85`
  - `RTF ≈ 1.26x`
- The rebuilt deck now makes the practical point explicit:
  - on this rope case, render ON is only about `1.11x` slower than the same
    replay with render OFF
  - therefore the profiling story is valuable to the viewer because it shows
    render is not the first optimization target on this clean rope baseline

## Next Step

- Follow-up optimization work should start from:
  - precomputed controller writes as the default replay baseline
  - more batched or more graph-like Newton replay investigation
  - weak-contact profiling as a separate workstream

## Blocking Issues

- None for the current benchmark-closeout milestone
- Remaining work is no longer measurement setup; it is optimization and
  follow-up interpretation

## Artifact Paths

- Canonical benchmark tree:
  - `results/rope_perf_apples_to_apples/`
- Committed results metadata:
  - `results_meta/tasks/rope_perf_apples_to_apples.json`
- Key outputs:
  - `results/rope_perf_apples_to_apples/index.csv`
  - `results/rope_perf_apples_to_apples/BEST_EVIDENCE.md` (local-only pointer)
  - `results/rope_perf_apples_to_apples/notes/methodology.md`
  - `results/rope_perf_apples_to_apples/notes/conclusions.md`
  - `results/rope_perf_apples_to_apples/notes/nsight.md`
  - `results/rope_perf_apples_to_apples/report/todo2_rope_perf_report.pdf`
