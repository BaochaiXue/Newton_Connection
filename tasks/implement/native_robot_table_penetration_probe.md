> status: active
> canonical_replacement: none
> owner_surface: `native_robot_table_penetration_probe`
> last_reviewed: `2026-04-12`
> review_interval: `14d`
> update_rule: `Update when the implementation steps or canonical commands for this probe change materially.`
> notes: Runbook for the minimal native Panda/table penetration probe.

# Implement: native_robot_table_penetration_probe

## Inputs To Re-read First

- `docs/bridge/tasks/native_robot_table_penetration_probe.md`
- `docs/newton/robot_example_patterns.md`
- `Newton/newton/newton/examples/robot/example_robot_panda_hydro.py`

## Implementation Steps

1. Build a minimal Panda + rigid-table scene in bridge code, reusing the
   native `robot_panda_hydro` control shape:
   - IK solves current reference
   - targets are written into `control`
   - rigid solver owns state progression
2. Set the penetration-attempt target below the tabletop.
3. Record a compact artifact bundle:
   - summary
   - scene/timeseries
   - video/gif/contact sheet
4. Add a wrapper under `scripts/` that writes `command.sh` and `run.log`.
5. Run the wrapper once.
6. Validate artifacts and record the conclusion in task status.

## Validation Notes

- prefer a minimal, readable probe over a heavily featured robot demo
- the first pass only needs to answer blocking vs pass-through clearly
