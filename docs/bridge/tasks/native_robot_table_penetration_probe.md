> status: active
> canonical_replacement: none
> owner_surface: `native_robot_table_penetration_probe`
> last_reviewed: `2026-04-12`
> review_interval: `14d`
> update_rule: `Update when the probe scope, code path, artifact contract, or conclusion changes.`
> notes: Active task for building a minimal robot_panda_hydro-style Newton-native robot + rigid-table probe that intentionally targets below the table and records whether the table blocks the robot.

# Task: Native Robot Table Penetration Probe

## Question

If we build a minimal Newton-native Panda + rigid-table demo in the style of
`robot_panda_hydro`, and deliberately place the target below the tabletop, does
the robot get physically blocked by the table or simply pass through it?

## Why It Matters

This probe is meant to answer a narrower mechanism question than the retired
bridge-side robot + deformable line:

- native robot
- native rigid table
- no deformable object
- intentionally bad target that tries to drive the robot through the table

That gives the repo a clean current reference for native robot blocking
behavior without reviving the old bridge-side robot stack as a recommended
baseline.

## Current Status

- Active
- New probe task opened on `2026-04-12`
- Demo and wrapper are implemented
- First run shows native rigid-table blocking under a deliberately bad
  below-table target

## Code Entry Points

- New demo:
  - `Newton/phystwin_bridge/demos/demo_native_robot_table_penetration_probe.py`
- New wrapper:
  - `scripts/run_native_robot_table_penetration_probe.sh`
- Upstream reference:
  - `Newton/newton/newton/examples/robot/example_robot_panda_hydro.py`

## Canonical Commands

```bash
bash scripts/run_native_robot_table_penetration_probe.sh
python scripts/validate_experiment_artifacts.py <out_dir> --require-video --require-gif --summary-field attempt_blocked
```

## Required Artifacts

- experiment directory with:
  - `README.md`
  - `command.sh`
  - `run.log`
  - `summary.json`
  - `scene.npz`
  - `penetration_probe.mp4`
  - `penetration_probe.gif`
  - `contact_sheet.jpg`
  - `timeseries.csv`

## Success Criteria

- the demo uses native Newton robot + rigid-table setup
- the target is intentionally below the table
- the run records whether actual robot motion is blocked
- the artifact directory is reproducible and validated
- the status page records the result and the exact artifact path

## Open Questions

- Is end-effector target error alone enough to summarize blocking, or should a
  follow-up add deeper rigid-contact diagnostics?
- Should this probe remain a lightweight `tmp/` experiment path, or should it
  be promoted into a more durable local results neighborhood if reused?

## Related Pages

- [../../newton/robot_example_patterns.md](../../newton/robot_example_patterns.md)
- [../../decisions/2026-04-09_robot_ps_interaction_retirement.md](../../decisions/2026-04-09_robot_ps_interaction_retirement.md)
