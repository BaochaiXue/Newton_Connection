> status: active
> canonical_replacement: none
> owner_surface: `robot_table_rope_split_mujoco_semiimplicit`
> last_reviewed: `2026-04-13`
> review_interval: `14d`
> update_rule: `Update when the implementation boundary or first-acceptance scope changes.`
> notes: Execution spec for the split MuJoCo robot/table + SemiImplicit rope direct-finger demo.

# Spec: robot_table_rope_split_mujoco_semiimplicit

## Goal

Implement the first truthful one-way direct-finger split demo:

- MuJoCo rigid robot/table side
- SemiImplicit rope side
- table-edge drape topology
- physical-only rope render thickness

## Non-Goals

- Editing `Newton/newton/`
- Reviving retired local robot controller semantics
- Treating full two-way robot-rope coupling as required for first acceptance

## Inputs

- `docs/newton/robot_example_patterns.md`
- `docs/bridge/tasks/robot_table_rope_split_mujoco_semiimplicit.md`
- `Newton/phystwin_bridge/demos/demo_native_robot_table_penetration_probe.py`
- the official reference examples listed on the task page

## Outputs

- new split demo and wrapper
- one validated one-way experiment run
- task/status/current-status/generated-doc updates

## Constraints

- robot side must stay solver-owned
- rope render thickness must stay physically truthful
- direct finger contact uses real finger/pad mesh, not a proxy sphere
- one-way is the first milestone; two-way may be scaffolded but does not block
  the first accepted run

## Done When

- the one-way split demo runs from its wrapper
- the run records finger-first-contact and rope motion timing
- the run proves rope-table and rope-ground contact are both active
- artifacts are validated and reflected in task status
