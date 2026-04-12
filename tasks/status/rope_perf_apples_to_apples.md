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
- Committed claim boundary remains:
  - same-case, no-render, apples-to-apples rope replay benchmark
- The visible-viewer `E1` row is supporting practical context only; it is not the registry-backed promoted scope by itself
- Latest local refresh candidate:
  - `results/rope_perf_apples_to_apples_refresh/20260411_221904/`
- Promotion decision for the 2026-04-11 refresh:
  - not promoted to `results_meta/`
  - refreshed numbers reproduced the same conclusion but stayed within the same qualitative band as the 2026-04-01 promoted bundle

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
  - sending target uses the repo-configured default recipient in `scripts/send_pdf_via_yahoo.py`

## 2026-04-11 Local Refresh Candidate

- Refreshed the same `rope_double_hand` benchmark matrix into:
  - `results/rope_perf_apples_to_apples_refresh/20260411_221904/`
- Fixed the rope benchmark harness so PhysTwin stages now run under the expected conda environment:
  - `scripts/run_rope_perf_apples_to_apples.sh`
  - `scripts/run_rope_perf_nsight.sh`
  - new behavior: `PHYSTWIN_ENV` defaults to `phystwin`
- Refreshed practical local realtime result on `cuda:0`:
  - Newton `E1` visible viewer remained realtime:
    - `viewer FPS ≈ 32.02`
    - `RTF ≈ 1.068x`
- Refreshed no-render comparison:
  - Newton `A1` precomputed throughput:
    - `0.041002 ms/substep`
    - `RTF ≈ 1.219x`
  - PhysTwin `B0` headless throughput:
    - `0.010986 ms/substep`
    - `RTF ≈ 4.551x`
  - Newton `A1` remained `3.732x` slower than PhysTwin `B0`
- Refreshed explanation remained aligned with the promoted 2026-04-01 story:
  - controller replay overhead is still real:
    - Newton `A0 -> A1` speedup `≈ 1.732x`
  - render is still secondary on this rope case:
    - `E1 / A1 ≈ 1.142x`
  - collision is still small on the clean rope baseline:
    - Newton `A3` collision bucket `≈ 0.004787 ms/substep`
    - PhysTwin `object_collision_flag = False`
  - the residual gap still points mainly to runtime organization / launch structure after controller precompute
- Artifact validation result:
  - ran `python scripts/validate_experiment_artifacts.py results/rope_perf_apples_to_apples_refresh/20260411_221904`
  - validator failed on `scene_or_rollout`
  - reason: this benchmark bundle is a multi-stage profiling tree with summaries/logs and no single `scene.npz` or `sim/history/` payload at the root
- Promotion judgment:
  - do not replace `results_meta/tasks/rope_perf_apples_to_apples.json`
  - the refreshed candidate is slower than the 2026-04-01 promoted snapshot, but it does not change the decision-level conclusion

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

## 2026-04-01 Real-Viewer Relevance Update (Supporting Context)

- Added an explicit old visible-viewer baseline:
  - `results/rope_perf_apples_to_apples/newton/E0_viewer_baseline_end_to_end/`
  - old visible viewer path was sub-realtime:
    - `viewer FPS ≈ 20.75`
    - `RTF ≈ 0.692x`
- Added a new E1 benchmark row:
  - `results/rope_perf_apples_to_apples/newton/E1_viewer_end_to_end/`
- E1 now uses the visible `ViewerGL` render path on the same rope replay:
  - `viewer FPS ≈ 37.85`
  - `RTF ≈ 1.26x`
- The key enabling method is now stated explicitly in the deck:
  - switch from the baseline controller replay path to precomputed controller
    replay feeding, so each substep no longer repeats controller interpolation
    and state writes
- The rebuilt deck now makes the practical point explicit:
  - on this rope case, render ON is only about `1.11x` slower than the same
    replay with render OFF
  - therefore the profiling story is valuable to the viewer because it shows
    render is not the first optimization target on this clean rope baseline
- This row is supporting viewer-facing context for the slide story.
- The committed promoted benchmark meaning still lives in the no-render
  apples-to-apples scope recorded in `results_meta/tasks/rope_perf_apples_to_apples.json`.

## Next Step

- Follow-up optimization work should start from:
  - precomputed controller writes as the default replay baseline
  - more batched or more graph-like Newton replay investigation
  - weak-contact profiling as a separate workstream
- If this refresh needs to become a promoted bundle later:
  - either extend the artifact contract for multi-stage benchmark bundles
  - or add an explicit root-level rollout/history pointer that satisfies `validate_experiment_artifacts.py`

## Blocking Issues

- None for the current benchmark-closeout milestone
- Remaining work is no longer measurement setup; it is optimization and
  follow-up interpretation
- The generic artifact validator does not currently pass on this refresh bundle
  shape because it expects a root `scene.npz` or `sim/history/`

## Artifact Paths

- Canonical benchmark tree:
  - `results/rope_perf_apples_to_apples/`
- Local refresh candidate:
  - `results/rope_perf_apples_to_apples_refresh/20260411_221904/`
- Committed results metadata:
  - `results_meta/tasks/rope_perf_apples_to_apples.json`
- Key outputs:
  - `results/rope_perf_apples_to_apples/index.csv`
  - `results/rope_perf_apples_to_apples/BEST_EVIDENCE.md` (local-only pointer)
  - `results/rope_perf_apples_to_apples/notes/methodology.md`
  - `results/rope_perf_apples_to_apples/notes/conclusions.md`
  - `results/rope_perf_apples_to_apples/notes/nsight.md`
  - `results/rope_perf_apples_to_apples/report/todo2_rope_perf_report.pdf`
- Local refresh outputs:
  - `results/rope_perf_apples_to_apples_refresh/20260411_221904/BEST_EVIDENCE.md`
  - `results/rope_perf_apples_to_apples_refresh/20260411_221904/index.csv`
  - `results/rope_perf_apples_to_apples_refresh/20260411_221904/notes/conclusions.md`
