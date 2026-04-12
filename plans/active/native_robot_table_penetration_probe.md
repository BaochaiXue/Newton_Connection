> status: active
> canonical_replacement: none
> owner_surface: `native_robot_table_penetration_probe`
> last_reviewed: `2026-04-12`
> review_interval: `14d`
> update_rule: `Update when milestones or validation expectations for this probe change.`
> notes: Active plan for the minimal native robot/table penetration probe.

# Plan: native_robot_table_penetration_probe

## Goal

Answer the narrow question of whether a robot_panda_hydro-style native robot
gets blocked by a native rigid table when its target is intentionally placed
below the tabletop.

## Milestones

1. Create the task scaffold and route it through the active task index.
2. Implement a minimal bridge-layer demo based on the native Panda/table
   control pattern.
3. Add a canonical wrapper that writes a reproducible experiment directory.
4. Run the probe once and inspect the result.
5. Validate artifacts and update status/docs/generated surfaces.

## Validation

- `python scripts/validate_experiment_artifacts.py <out_dir> --require-video --require-gif --summary-field attempt_blocked`
- `python scripts/lint_harness_consistency.py`

## Notes

- keep the first conclusion focused on blocking behavior, not on rope or
  broader robot-deformable claims
