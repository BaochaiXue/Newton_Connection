# Status: self_collision_transfer

## Current State

Tracked as an active task with a canonical slug and a backfilled authoritative
chain.

The bridge now has a shared strict `phystwin` contact-stack implementation for
the PhysTwin-native cloth parity scene:

- pairwise self-collision uses the bridge-side PhysTwin operator
- ground contact uses a bridge-side implicit `z=0` PhysTwin-style integrator
- `off/native/custom` stay on their existing compatibility paths
- cloth+box `phystwin` is intentionally guarded as unsupported

## Last Completed Step

Landed the first shared strict `phystwin` stack wiring:

- `tools/core/phystwin_contact_stack.py`
- shared importer path via `tools/core/newton_import_ir.py`
- thin `tools/other/newton_import_ir_phystwin.py` wrapper
- cloth+box demo guard for unsupported `phystwin`

## Next Step

Record the post-refactor validation state:

- strict 60-frame cloth parity metrics
- full-length strict cloth parity metrics
- OFF non-regression results
- updated slide/task wording for the narrowed strict `phystwin` scope

## Blocking Issues

- strict self-collision parity still needs a fresh post-refactor full-length
  measurement against the `1e-5` gate
- strict `phystwin` scope is intentionally narrow and does not yet cover box or
  other Newton-only rigid-support contacts

## Artifact Paths

- `results_meta/tasks/self_collision_transfer.json`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/FINAL_STATUS.md`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/matrix/self_collision_decision.md`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/parity/strict_self_collision_parity_summary.json`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/video_qc/final_video_qc_report.md`
