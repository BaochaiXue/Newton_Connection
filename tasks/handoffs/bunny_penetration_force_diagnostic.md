# Handoff: bunny_penetration_force_diagnostic

## Current Milestone

Preserve the promoted all-colliding-node bunny board as the current canonical
meeting surface.

## What Changed

- the task now has an explicit contract/handoff pair because it is a
  result-bearing visual-evidence workflow
- the active status page was shortened and the old rollout chronology moved to
  `tasks/history/status/bunny_penetration_force_diagnostic_log_20260401.md`

## Current Conclusion

`20260401_013500_realtime_allcolliding_2x2_v5` is the current promoted board.
Future work should treat it as stable unless a materially stronger board bundle
is ready to replace it.

## Exact Next Command

```bash
python scripts/validate_bunny_force_visualization.py results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5
```

## Current Blocker

No blocker on the current promoted board.

## Last Failed Acceptance Criterion

The task lacked an explicit contract/handoff even though it owns a promoted
visual result bundle.

## Key GIF / Artifact Paths

- `results_meta/tasks/bunny_penetration_force_diagnostic.json`
- `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5/artifacts/collision_force_board/collision_force_board_2x2.mp4`
- `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5/qa/verdict.md`

## What Not To Redo

- do not reopen the old synchronized four-case package as the live meeting surface
- do not widen the promoted board beyond the explicit `box_control` / `bunny_baseline` contract

## Missing Evidence

- none for the current promoted bundle

## Context Reset Recommendation

- recommended: yes
- reason:
  - this task has a nontrivial artifact tree and should not rely on chat memory
