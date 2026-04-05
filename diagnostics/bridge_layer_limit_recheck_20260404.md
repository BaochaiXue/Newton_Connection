# Bridge-Layer Limit Recheck

Last updated: 2026-04-04

## Why This Recheck Exists

The older stronger-task limit proof concluded that bridge/demo-level actuation
surfaces were insufficient and that a Newton core/API change was likely
required.

After re-reading the current repo and reproducing the current code path, that
conclusion is no longer the default assumption.

## New Findings

### 1. `joint_target_drive` body motion was being erased in the demo layer

On the current repo state, a minimal reproduction using the existing
`joint_target_drive` path shows:

- after `solver.step(...)`, the articulated `body_q` state changes
- the subsequent `newton.eval_fk(state_out.joint_q, state_out.joint_qd, state_out)`
  in the demo path resets that body motion back to the stale pre-step joint pose

Observed numbers from the local reproduction:

- `body_motion_after_solver_norm = 0.01554`
- `body_motion_after_fk_norm = 0.0`
- `body_delta_solver_to_fk_norm = 0.01554`
- `joint_q_change_after_solver_norm = 0.0`

Interpretation:

- the bridge/demo layer was erasing the solver-integrated body motion
- a core change is **not** justified before removing that overwrite

### 2. The original fixed-base Franka build is numerically unstable in SemiImplicit

With the old build settings:

- fixed-base Franka
- no table
- no target change
- SemiImplicit

the robot still produced `nan` body state at about step 10.

Interpretation:

- the older physical-blocking failure was not purely a control-surface issue
- the imported Franka build itself was not yet a stable SemiImplicit benchmark

### 3. A stable bridge/demo-level Franka build now exists

Using the same native Franka asset but with:

- `ignore_inertial_definitions=True`
- `default_body_armature = 0.01`
- `default_joint_cfg.armature = 0.01`

the same fixed-base Franka becomes stable under SemiImplicit in a no-table,
no-target baseline.

It also remains stable under a non-trivial `joint_target_pos` command.

### 4. Stage-0 blocking looks feasible without touching `Newton/newton/`

Using the stable build plus the visible-tool capsule geometry:

- no-table run:
  - tool center vertical progress: about `-0.01348 m`
  - target error: about `0.0970 m`
- with-table run:
  - tool center vertical progress: about `+0.00034 m`
  - target error: about `0.2513 m`
  - minimum tool-table clearance: about `-0.00629 m`

Interpretation:

- with the same target, the no-table case descends materially
- with the table present, the same target no longer descends and instead
  deflects/slides laterally
- this is already the right qualitative blocking signature for Stage 0
- penetration is still too large for final acceptance, but the mechanism is now
  a benchmark/tuning problem, not a proven need for a core change

## Updated Conclusion

- Do **not** touch `Newton/newton/` yet.
- First complete a truthful Stage-0 rigid-only blocking benchmark using:
  - the bridge-layer `joint_target_drive` path without the post-step FK overwrite
  - the stable Franka SemiImplicit build (`ignore_inertial_definitions` + small
    armature)
  - the visible rigid tool as the Stage-0 contactor

Only if that Stage-0 benchmark still fails honestly should the task escalate to
the smallest Newton-native core/API change.
