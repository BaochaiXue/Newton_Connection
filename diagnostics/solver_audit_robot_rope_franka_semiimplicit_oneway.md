# Solver Audit: robot_rope_franka_semiimplicit_oneway

## Chosen Path

- Preferred path: `Path A` direct-finger tabletop baseline (`c12`).
- Fallback path: visible rigid tool baseline (`c08`) only if Path A cannot be kept honest/readable under the conservative claim.

## SemiImplicit Proof

- The rope/deformable interaction in the bridge demo is run through `newton.solvers.SolverSemiImplicit(...)` in [demo_robot_rope_franka.py](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py).
- The canonical Path A wrapper remains [run_robot_rope_franka_tabletop_hero.sh](/home/xinjie/Newton_Connection/scripts/run_robot_rope_franka_tabletop_hero.sh), which calls that same demo entrypoint and does not switch solver families.
- The accepted direct-finger bundle under [c12](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260401_203416_remotefix_truthcam_c12) is therefore a native Newton robot + native Newton table + PhysTwin rope scene whose deformable interaction path is SemiImplicit.

## Newton Examples Read

- I scanned all `66` Python example files under `Newton/newton/newton/examples/`.
- Inventory report: [newton_examples_solver_inventory_20260404.md](/home/xinjie/Newton_Connection/diagnostics/newton_examples_solver_inventory_20260404.md).
- Relevant signal from the examples:
  - `cloth/` and `diffsim/` families already use `SolverSemiImplicit` for native deformable scenes.
  - robot-heavy contact/manipulation examples mostly use `SolverMuJoCo`, not a cleaner native SemiImplicit robot+rope tabletop pattern we could simply swap in.
  - there is no stronger native example that makes the blocked physical-blocking claim an in-scope prerequisite for this task.

## Conservative Conclusion

- For the refocused one-way deformable goal, the existing bridge-side tabletop baseline is already the most direct Newton-native SemiImplicit path.
- No Newton core change is needed or allowed for this task.
- The remaining work is claim-boundary, geometry-truth, and result-surface cleanup around Path A, with Path B retained only as a documented fallback.
