# Runbook: robot_sphere_inflation_root_cause

## Canonical Inputs

- `docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
- `docs/bridge/tasks/robot_visible_rigid_tool_baseline.md`
- `docs/bridge/tasks/robot_rope_franka_physical_blocking.md`
- `scripts/run_robot_rope_franka_tabletop_hero.sh`
- `scripts/run_robot_visible_rigid_tool_baseline.sh`
- `scripts/validate_robot_rope_franka_hero.py`
- `scripts/diagnose_robot_visible_rigid_tool_baseline.py`
- `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`

## Expected Working Steps

1. Build the sphere/proxy geometry inventory.
2. Extract current promoted-run evidence from tabletop finger and visible-tool baselines.
3. Run bounded disambiguating experiments:
   - sphere/proxy sweep
   - contact-reference / Z-stack sweep
   - XY sweep
   - visible-tool control comparison
4. Prepare fail-closed video evidence bundles when the explanation depends on
   visible timing.
5. Write the ranked root-cause report and update status.

## Output Contract

- diagnostics listed on the task page
- updated task status
- no authority change to unrelated tasks
