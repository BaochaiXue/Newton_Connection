# Status: native_robot_physical_blocking_minimal

## Current State

- Active
- Newly opened minimal native-blocking workstream

## Last Completed Step

- Re-read the current control plane and confirmed:
  - accepted direct-finger tabletop baseline remains separate
  - accepted visible-tool baseline remains separate
  - stronger rope-integrated physical-blocking task is still blocked at the
    currently accessible bridge/demo actuation layer
- Created the new minimal task chain focused on Stage 0 blocking first
- Added:
  - [geometry_truth_inventory.md](/home/xinjie/Newton_Connection/diagnostics/geometry_truth_inventory.md)
  - [native_robot_physical_blocking_minimal_board.md](/home/xinjie/Newton_Connection/diagnostics/native_robot_physical_blocking_minimal_board.md)
- Reproduced a stronger local diagnosis against the current repo state:
  - in `joint_target_drive`, `solver.step(...)` changes `state_out.body_q`
  - the subsequent `newton.eval_fk(state_out.joint_q, ...)` in the demo path
    resets that body motion back to the stale pre-step joint pose
  - this means the current bridge-layer limit proof is no longer sufficient to
    justify a core change before re-testing the path without that overwrite
- Reproduced a second local diagnosis against the current repo state:
  - `SolverSemiImplicit` default `joint_attach_ke=1e4` / `joint_attach_kd=1e2`
    destabilizes a simple single-revolute articulation control smoke
  - the same default attachment gains also destabilize a pure-robot Franka-only
    `joint_target_pos` smoke
  - lowering attachment gains to about `50 / 5` stabilizes the pure-robot
    Franka smoke and yields non-zero recovered `joint_q` motion after
    `eval_ik`
- Added the stronger recheck note:
  - [bridge_layer_limit_recheck_20260404.md](/home/xinjie/Newton_Connection/diagnostics/bridge_layer_limit_recheck_20260404.md)
  - current interpretation now includes:
    - stable bridge/demo-level Franka SemiImplicit build with
      `ignore_inertial_definitions=True`
    - stable no-table target-drive motion with the same visible tool geometry
    - early no-table vs with-table probes already showing the expected
      blocking-vs-no-blocking split

## Next Step

- Re-test the bridge-layer path with:
  - post-step reduced-state resync through `eval_ik`
  - lower `SolverSemiImplicit` articulation attachment gains
- Turn that stabilized path into a rigid-only Stage-0 blocking benchmark before
  touching `Newton/newton/`.
- Only if Stage 0 still fails honestly after that should the task escalate to
  the smallest Newton core/API change.

## Guardrail

- Do not claim rope-integrated success before Stage 0 blocking is proven
- Do not allow any visible-vs-physical geometry mismatch
- Do not use hidden helpers or fake clamps
- If `Newton/newton/` changes, document the exact reason and file scope

## Current Lean

- A Newton core/API change is **not yet justified**.
- The current best bridge-layer interpretation is:
  - `SolverSemiImplicit` articulation actuation is not obviously absent
  - the stronger path was undermined by stale post-step reduced-state handling
    and destabilizing attachment gains
- Stage 0 still needs to prove that this bridge-layer repair survives real
  table contact with honest geometry.
