# Spec: pure_semiimplicit_robot_loaded_object

## Goal

Rebuild a pure `SolverSemiImplicit` robot + PhysTwin-loaded object diagnostic
without reviving the retired robot demo stack. The first repaired artifact
should prove whether the bridge can run Panda, table, ground, and an imported
deformable object in one SemiImplicit model with solver-owned robot state and
auditable contact/reaction metrics.

## Constraints

- Do not modify `Newton/newton/`.
- Do not use MuJoCo in this demo.
- Do not overwrite robot state after solver steps.
- Keep object import through the existing PhysTwin IR bridge.
- Keep artifact output contract-compatible.
- Treat this as diagnostic until metrics and visual review justify a stronger
  claim.

## Deliverables

- `Newton/phystwin_bridge/demos/demo_pure_semiimplicit_robot_loaded_object.py`
- `scripts/run_pure_semiimplicit_robot_loaded_object_demo.sh`
- validated artifact directory
- status update with run path and conclusion

## Acceptance

- Script compiles.
- Wrapper runs.
- Artifact validator passes with required summary fields.
- Summary distinguishes:
  - pure solver architecture
  - robot drive mode
  - table-blocking attempt
  - object motion after contact
  - same-solver finger-force diagnostics

