# Status: self_collision_transfer

## Current State

Tracked as an active task with a canonical slug and a backfilled authoritative
chain.

## Last Completed Step

Normalized the active slug to `self_collision_transfer`, marked the older
`self_collision_transfer_decision` files as deprecated aliases, and attached
the current campaign root to the committed results registry.

## Next Step

Write the decision-grade current state into this canonical status file:

- current campaign root:
  - `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0`
- current selected final mode:
  - `phystwin`
- blocker:
  - strict self-collision parity still fails the in-scope cloth reference gate
- next missing deliverable:
  - one explicit A/B/C decision state written here instead of only in the
    historical campaign folder

## Blocking Issues

- final A/B/C decision state is still not represented in a concise canonical
  task status file
- strict self-collision parity remains blocked in the current campaign root

## Artifact Paths

- `results_meta/tasks/self_collision_transfer.json`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/FINAL_STATUS.md`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/matrix/self_collision_decision.md`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/parity/strict_self_collision_parity_summary.json`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/video_qc/final_video_qc_report.md`
