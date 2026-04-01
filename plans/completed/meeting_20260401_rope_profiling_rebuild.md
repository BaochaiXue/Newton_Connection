> status: historical
> canonical_replacement: none
> owner_surface: `meeting_20260401_rope_profiling_rebuild`
> last_reviewed: `2026-04-01`
> review_interval: `90d`
> update_rule: `Keep only as a historical planning record for the completed 2026-04-01 profiling-section rebuild.`
> notes: Completed one-off plan moved out of `plans/active/` so it no longer competes with live planning surfaces.

# Plan: meeting_20260401_rope_profiling_rebuild

## Goal

Turn TODO 2 into a rope-only, real-viewer-relevant profiling story that a
meeting audience can understand quickly.

## Milestones

1. Audit the current profiling section against the real-viewer-focused review
   questions
2. Fill any missing experiment data needed for that story, especially E1
3. Rewrite the profiling slides in plain language
4. Rewrite the profiling transcript in normal spoken Chinese with English
   terminology preserved
5. Rebuild the deck and update task/status docs

## Validation

- `results/rope_perf_apples_to_apples/newton/E1_viewer_end_to_end/summary.json`
  contains valid nonzero viewer metrics
- profiling slides no longer use the banned shorthand
- transcript covers question, evidence, conclusion, practical value, and scope
- `bridge_meeting_20260401.pptx` regenerates successfully
