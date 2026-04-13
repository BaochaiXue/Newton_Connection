> status: active
> canonical_replacement: none
> owner_surface: `robot_table_rope_split_mujoco_semiimplicit`
> last_reviewed: `2026-04-13`
> review_interval: `14d`
> update_rule: `Update when milestones or validation commands for this task change.`
> notes: Active plan for the split MuJoCo robot/table + SemiImplicit rope demo.

# Plan: robot_table_rope_split_mujoco_semiimplicit

## Goal

Land a runnable one-way direct-finger split demo and leave a clean path toward
two-way rope reaction.

## Milestones

1. Create the task/spec/plan/status + contract/handoff chain.
2. Implement a split demo with:
   - MuJoCo rigid robot/table side
   - SemiImplicit rope side
   - rope-side finger mirror bodies
3. Add a canonical wrapper and render outputs.
4. Run one validated one-way experiment.
5. Tune the scene/motion geometry until `finger first contact` is detected
   without breaking truthful support-contact semantics.
6. Record the result and refresh generated harness ledgers.

## Validation

- `python -m py_compile Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
- `bash scripts/run_robot_table_rope_split_demo.sh`
- `python scripts/validate_experiment_artifacts.py <out_dir> --require-video --require-gif --summary-field rope_motion_after_contact --summary-field rope_render_matches_physics`
- `python scripts/lint_harness_consistency.py`

## Notes

- first acceptance is one-way only
- two-way is allowed in the CLI and code shape, but not required for the first
  passing artifact
- current best-known artifact is `/tmp/robot_table_rope_split_one_way_fine_v5`
- current blocker is not the split solver architecture; it is the remaining
  finger-to-rope geometry miss in the one-way motion layout
