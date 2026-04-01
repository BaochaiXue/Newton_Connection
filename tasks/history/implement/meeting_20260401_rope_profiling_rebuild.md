> status: historical
> canonical_replacement: none
> owner_surface: `meeting_20260401_rope_profiling_rebuild`
> last_reviewed: `2026-04-01`
> review_interval: `90d`
> update_rule: `Keep only as the historical runbook for the completed 2026-04-01 profiling-section rebuild.`
> notes: Historical one-off runbook moved out of `tasks/implement/` so it no longer competes with live execution surfaces.

# Implement: meeting_20260401_rope_profiling_rebuild

## Canonical Steps

1. Refresh the rope performance root if E1 is missing or stale
2. Regenerate rope summary files with `scripts/summarize_rope_perf_apples_to_apples.py`
3. Rewrite profiling slides in `build_meeting_20260401.py`
4. Rebuild transcript through the deck builder
5. Update task/status docs to reflect the final storyline

## Canonical Commands

- `python scripts/benchmark_newton_rope_viewer_end_to_end.py ...`
- `python scripts/summarize_rope_perf_apples_to_apples.py --root results/rope_perf_apples_to_apples`
- `python formal_slide/meeting_2026_04_01/build_meeting_20260401.py`

## Output Paths

- `results/rope_perf_apples_to_apples/`
- `formal_slide/meeting_2026_04_01/`
