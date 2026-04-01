# Status: Rope Perf Apples To Apples

## Current State

- Completed for the current rope meeting scope
- Canonical result root:
  - `results/rope_perf_apples_to_apples/`
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

## Next Step

- Follow-up optimization work should start from:
  - precomputed controller writes as the default replay baseline
  - graph-captured / batched Newton replay investigation
  - weak-contact profiling as a separate workstream

## Blocking Issues

- None for the current benchmark-closeout milestone
- Remaining work is no longer measurement setup; it is optimization and
  follow-up interpretation

## Artifact Paths

- Canonical benchmark tree:
  - `results/rope_perf_apples_to_apples/`
- Key outputs:
  - `results/rope_perf_apples_to_apples/index.csv`
  - `results/rope_perf_apples_to_apples/BEST_EVIDENCE.md`
  - `results/rope_perf_apples_to_apples/notes/methodology.md`
  - `results/rope_perf_apples_to_apples/notes/conclusions.md`
  - `results/rope_perf_apples_to_apples/notes/nsight.md`
  - `results/rope_perf_apples_to_apples/report/todo2_rope_perf_report.pdf`
