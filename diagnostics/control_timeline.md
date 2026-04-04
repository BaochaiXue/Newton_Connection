# Control Timeline

Last updated: 2026-04-03

## Current Tabletop Joint-Trajectory Order

1. Start substep with `state_in`.
2. Compute desired tabletop joint target via `_joint_phase_state(...)`.
3. Directly assign `state_in.joint_q` and `state_in.joint_qd`.
4. Recompute FK from that imposed joint state.
5. Run collision generation.
6. Run `solver.step(state_in, state_out, None, contacts, sim_dt)`.
7. Immediately assign `state_out.joint_q` and `state_out.joint_qd` back to the
   commanded target.
8. Recompute FK again.
9. Swap `state_in` and `state_out`.

## Why This Breaks Blocking

Physical blocking requires:

- desired motion continues
- actual hand pose is allowed to lag or stop
- target-to-actual error grows under contact

The current order instead enforces:

- desired pose == pre-solve actual pose
- desired pose == post-solve actual pose

So contact cannot persistently block the robot articulation.
