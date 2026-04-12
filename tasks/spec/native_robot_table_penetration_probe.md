> status: active
> canonical_replacement: none
> owner_surface: `native_robot_table_penetration_probe`
> last_reviewed: `2026-04-12`
> review_interval: `14d`
> update_rule: `Update when the probe goal, scope boundary, or done criteria change.`
> notes: Execution spec for the minimal robot_panda_hydro-style native robot/table blocking probe.

# Spec: native_robot_table_penetration_probe

## Goal

Implement and run a minimal Newton-native Panda + rigid-table demo that pushes
its target below the tabletop and records whether the table blocks the robot.

## Non-Goals

- Reopening the retired bridge-side robot + deformable line
- Adding a deformable object
- Editing `Newton/newton/`

## Inputs

- `docs/newton/robot_example_patterns.md`
- `Newton/newton/newton/examples/robot/example_robot_panda_hydro.py`
- `docs/archive/tasks/native_robot_physical_blocking_minimal.md`

## Outputs

- new bridge-layer demo and wrapper
- one validated experiment directory
- updated task/status/dashboard/generated-doc surfaces

## Constraints

- keep the robot/table scene Newton-native
- do not depend on the retired bridge robot controller path
- keep the first probe minimal and explainable

## Done When

- the demo exists and runs from a wrapper script
- the run saves the expected artifacts
- the result clearly states whether the table blocks the robot back
- status/docs/generated surfaces reflect the run
