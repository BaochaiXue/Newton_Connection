> status: historical
> canonical_replacement: none
> owner_surface: `meeting_20260401_rope_profiling_rebuild`
> last_reviewed: `2026-04-01`
> review_interval: `90d`
> update_rule: `Keep only as the historical status log for the completed 2026-04-01 profiling-section rebuild.`
> notes: Historical one-off status moved out of `tasks/status/` so it no longer appears active.

# Status: Meeting 2026-04-01 Rope Profiling Rebuild

## Current State

- Completed for the 2026-04-01 meeting deck
- Scope locked to the TODO 2 rope profiling section
- Real-viewer relevance is now explicit through a new E1 benchmark row

## Latest Progress

- Created a dedicated viewer end-to-end benchmark script:
  - `scripts/benchmark_newton_rope_viewer_end_to_end.py`
- Added an explicit old-vs-new visible viewer comparison:
  - old baseline viewer path:
    - `results/rope_perf_apples_to_apples/newton/E0_viewer_baseline_end_to_end/`
    - `RTF ≈ 0.692x`
  - current precomputed viewer path:
    - `results/rope_perf_apples_to_apples/newton/E1_viewer_end_to_end/`
    - `RTF ≈ 1.262x`
- Refreshed canonical E1 under:
  - `results/rope_perf_apples_to_apples/newton/E1_viewer_end_to_end/`
- Regenerated the rope apples-to-apples summary so the profiling section can
  use E1/E2/E3/E4 in one story
- Rebuilt the profiling section in:
  - `formal_slide/meeting_2026_04_01/build_meeting_20260401.py`
  - `formal_slide/meeting_2026_04_01/transcript.md`
  - `formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx`

## Next Step

- Use the rebuilt six-page profiling section as the authoritative meeting
  version unless new rope benchmark evidence changes the conclusion

## Blocking Issues

- None for the current meeting milestone
