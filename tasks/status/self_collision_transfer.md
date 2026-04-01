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

Latest post-refactor validation:

- operator exactness still passes:
  - `Newton/phystwin_bridge/results/tmp_verify_phystwin_equivalence_after_refactor.json`
- strict cloth parity 60-frame smoke improved to:
  - `rmse_mean = 0.0015035003889352083`
  - `Newton/phystwin_bridge/results/tmp_strict_self_collision_refactor_60_v2/strict_self_collision/strict_self_collision_parity_rollout_report.json`
- strict cloth parity full 302-frame run improved to:
  - `rmse_mean = 0.010737196542322636`
  - `Newton/phystwin_bridge/results/tmp_strict_self_collision_refactor_full/strict_self_collision_parity_full_rollout_report.json`
- OFF regression remains acceptable:
  - `Newton/phystwin_bridge/results/tmp_off_ground_regression_60/off_ground_regression60_rollout_report.json`
- rope OFF importer smoke still passes:
  - `Newton/phystwin_bridge/results/tmp_rope_off_smoke_30/rope_off_smoke30_rollout_report.json`

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
