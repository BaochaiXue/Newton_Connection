# Status: robot_rope_franka_semiimplicit_oneway

## Current State

- Accepted
- Conservative SemiImplicit deformable-interaction task is now promoted on Path A direct finger

## Last Completed Step

- Re-read the current control plane and accepted robot baselines
- Read the Newton examples map at the repo level and extracted the relevant
  solver patterns
- Created the refocused task chain
- Promoted a conservative Path A bundle that reuses the accepted c12 rollout
  under a narrower claim:
  - `Newton/phystwin_bridge/results/robot_rope_franka_semiimplicit_oneway/BEST_RUN/`
  - `results_meta/tasks/robot_rope_franka_semiimplicit_oneway.json`
- Added explicit bundle-local truth surfaces:
  - `solver_audit.md`
  - `geometry_truth_report.md`
  - `multimodal_review.md`
- Re-ran:
  - `validate_robot_rope_franka_hero.py`
  - `validate_experiment_artifacts.py`
  on the promoted conservative bundle

## Scope Decision

- `SolverSemiImplicit` deformable rope interaction is the target
- one-way robot -> rope is acceptable
- robot-table physical blocking is out of scope
- self-collision parity is out of scope
- direct finger is preferred
- visible rigid tool is fallback only if direct finger fails honestly

## Next Step

- Preserve the promoted Path A conservative bundle.
- If a future direct-finger regression appears, either:
  - re-certify direct finger honestly, or
  - document the switch to Path B visible-tool fallback
- Do not revive physical blocking or full two-way coupling under this task.

## Guardrail

- Do not revive physical-blocking as the target for this task
- Do not modify `Newton/newton/`
- Do not silently switch to Path B without documenting the reason

## Current Authority

- Task page:
  - `docs/bridge/tasks/robot_rope_franka_semiimplicit_oneway.md`
- Registry entry:
  - `results_meta/tasks/robot_rope_franka_semiimplicit_oneway.json`
- Promoted local artifact root:
  - `Newton/phystwin_bridge/results/robot_rope_franka_semiimplicit_oneway/BEST_RUN/`

## Accepted Claim

- native Newton Franka
- native Newton tabletop
- PhysTwin -> Newton bridged rope
- deformable interaction under `SolverSemiImplicit`
- one-way robot -> rope interaction is acceptable
- no articulated physical-blocking claim
- no full two-way-coupling claim
- no self-collision parity claim
