> status: active
> canonical_replacement: none
> owner_surface: `robot_table_rope_split_mujoco_semiimplicit`
> last_reviewed: `2026-04-13`
> review_interval: `14d`
> update_rule: `Update when the implementation sequence or canonical wrapper changes materially.`
> notes: Runbook for the split MuJoCo robot/table + SemiImplicit rope direct-finger demo.

# Implement: robot_table_rope_split_mujoco_semiimplicit

## Inputs To Re-read First

- `docs/bridge/tasks/robot_table_rope_split_mujoco_semiimplicit.md`
- `docs/newton/robot_example_patterns.md`
- `Newton/phystwin_bridge/demos/demo_native_robot_table_penetration_probe.py`
- `Newton/newton/newton/examples/robot/example_robot_panda_hydro.py`
- `Newton/newton/newton/examples/ik/example_ik_franka.py`

## Implementation Steps

1. Build a rigid-side Panda/table controller path by reusing the current native
   probe semantics.
2. Build a rope-side SemiImplicit model from PhysTwin IR with:
   - ground plane
   - native table
   - direct finger mirror bodies
3. Synchronize rigid finger body poses into rope-side mirror bodies each
   substep.
4. Render the rigid model through ViewerGL and overlay the rope points/lines
   manually using the rope solver state.
5. Emit one-way metrics and artifact bundle.
6. Validate the run and sync task status/docs.

## Validation Notes

- keep the first implementation strongly biased toward truthful one-way
  interaction
- do not widen rope render thickness for readability
