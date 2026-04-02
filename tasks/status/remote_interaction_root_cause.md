# Status: remote_interaction_root_cause

## Current State

- Completed
- Initial repo re-read completed on `2026-04-01`
- Root-cause investigation concluded with a promoted replacement run:
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260401_203416_remotefix_truthcam_c12/`

## Last Completed Step

- Re-read the authoritative control-plane files, wrapper, validator, demo entry
  points, and current promoted run metadata.
- Generated the initial diagnostic bundle under `diagnostics/` for the current
  `BEST_RUN`, including the hypothesis board, collider inventory, proxy
  timeseries, target-offset report, rope-thickness report, and ranked root
  cause report.
- Implemented the truth fix and reran the canonical bundle through c12.
- The winning c12 run passed:
  - strict validator objective gates
  - truthful manual review
  - full-video multimodal review
- The remote-interaction impression is no longer present in the accepted c12
  bundle.

## Next Step

- Keep the root-cause reports as the durable evidence bundle backing the c12
  promotion.

## Blocking Issues

- None.

## Artifact Paths

- Board:
  - `diagnostics/remote_interaction_hypothesis_board.md`
- Ranked report:
  - `diagnostics/root_cause_ranked_report.md`
- Current investigated run:
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260401_203416_remotefix_truthcam_c12/`
- Final review:
  - `diagnostics/multimodal_review_20260401_203416_remotefix_truthcam_c12.md`
