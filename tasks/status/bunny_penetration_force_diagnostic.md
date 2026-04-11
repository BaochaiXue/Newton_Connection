> status: active
> canonical_replacement: none
> owner_surface: `bunny_penetration_force_diagnostic`
> last_reviewed: `2026-04-11`
> review_interval: `21d`
> update_rule: `Update when the promoted board package, accepted force semantics, or slide-facing artifact set changes. Move long rollout history into historical logs instead of expanding this page indefinitely.`
> notes: Active operational status for the bunny penetration task. Keep this file short and point detailed rollout chronology elsewhere.

# Status: Bunny Penetration Force Diagnostic

## Current State

Committed current meaning lives in:

- `results_meta/tasks/bunny_penetration_force_diagnostic.json`

Current promoted board package:

- `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5`

Current high-confidence state:

- the promoted `v5` run remains the canonical meeting-facing board
- the board uses:
  - self-collision OFF
  - `box_control`
  - `bunny_baseline`
  - all-colliding-node display
  - target-only penalty-force re-evaluation with `add_ground_plane=False`
- board-aware QA and artifact-contract validation both passed

Historical rollout / slide-refresh chronology moved out of the active page:

- `tasks/history/status/bunny_penetration_force_diagnostic_log_20260401.md`

## Last Completed Step

The last meaningful milestone was the stricter all-colliding-node board
promotion:

- detector semantics were tightened to the `rigid_force_contact_mask`
- the target-only penalty-force path was re-evaluated without ground-plane mixing
- the canonical board, panel GIFs, and slow-motion supplement were regenerated
- the `2026-04-01` meeting deck was rewired to use the current board assets

## Next Step

- keep `v5` as the canonical reopened-board result
- only refresh slide-local media if a future meeting bundle needs different crop,
  speed, or layout treatment
- only promote a new run if it materially changes the board semantics or closes
  a real mechanism gap

## Blocking Issues

- no blocker on the current promoted board surface
- only future blocker would be a new meeting requirement that changes the board
  contract or force semantics

## Artifact Paths

- `results_meta/tasks/bunny_penetration_force_diagnostic.json`
- `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5/summary.json`
- `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5/artifacts/collision_force_board/collision_force_board_2x2.mp4`
- `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5/artifacts/collision_force_board/collision_force_board_2x2.gif`
- `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5/artifacts/collision_force_board_slow4x/collision_force_board_2x2_slow4x.mp4`
- `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5/qa/report.json`
- `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5/qa/verdict.md`
