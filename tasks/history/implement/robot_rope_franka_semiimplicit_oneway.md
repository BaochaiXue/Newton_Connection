# Runbook: robot_rope_franka_semiimplicit_oneway

## Canonical Inputs

- `docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
- `docs/bridge/tasks/robot_visible_rigid_tool_baseline.md`
- `docs/bridge/tasks/robot_rope_franka_physical_blocking.md`
- `tasks/status/robot_rope_franka_tabletop_push_hero.md`
- `tasks/status/robot_visible_rigid_tool_baseline.md`
- `tasks/status/robot_rope_franka_physical_blocking.md`
- `scripts/run_robot_rope_franka_tabletop_hero.sh`
- `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`

## Working Order

1. Confirm the refocused task boundary and the scope decision.
2. Audit current accepted direct-finger tabletop baseline first.
3. Verify explicit `SolverSemiImplicit` usage for the deformable rope path.
4. Verify geometry truth:
   - visible contactor == actual contactor
   - rope render thickness == physical thickness
   - no hidden helper
5. Only if Path A fails honestly, document the switch to Path B visible-tool fallback.
6. Promote a conservative results surface only after the full audit bundle exists.
