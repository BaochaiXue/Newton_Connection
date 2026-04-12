> status: active
> canonical_replacement: none
> owner_surface: `native_robot_table_penetration_probe`
> last_reviewed: `2026-04-12`
> review_interval: `7d`
> update_rule: `Update after each meaningful implementation or run milestone.`
> notes: Live status log for the native robot/table penetration probe.

# Status: native_robot_table_penetration_probe

## Current State

- Active
- Demo and wrapper implemented
- First probe run completed
- Artifact validation succeeded
- Generated markdown inventory is refreshed
- Harness consistency lint passes

## What Changed In The Latest Pass

- created the canonical task chain:
  - `docs/bridge/tasks/native_robot_table_penetration_probe.md`
  - `tasks/spec/native_robot_table_penetration_probe.md`
  - `plans/active/native_robot_table_penetration_probe.md`
  - `tasks/implement/native_robot_table_penetration_probe.md`
  - `tasks/status/native_robot_table_penetration_probe.md`
- added the demo:
  - `Newton/phystwin_bridge/demos/demo_native_robot_table_penetration_probe.py`
- added the wrapper:
  - `scripts/run_native_robot_table_penetration_probe.sh`
- ran the first probe:
  - `tmp/native_robot_table_penetration_probe_20260412_135029`

## Problem Being Solved

- the repo needs a current native reference for robot-vs-table blocking without
  falling back to retired bridge robot controller semantics

## Findings / Conclusions So Far

- the correct upstream template is `robot_panda_hydro`, not the archived local
  bridge robot stack
- the first probe should stay minimal:
  - native Panda
  - native rigid table
  - intentionally bad target below table
  - clear blocking summary
- in the first run, the table does block the robot back under the native
  `robot_panda_hydro`-style control path:
  - `penetration_target_z_m = 0.04`
  - `table_top_z_m = 0.10`
  - `attempt_blocked = true`
  - `finger_table_contact_frames = 226`
  - `nonfinger_table_contact_frames = 0`
  - `mean_ee_error_during_attempt_m = 0.1872`
  - `final_actual_ee_z_m = 0.23196`
- this first result is a current native blocking reference, not a reopening of
  the retired bridge-side robot + deformable line

## Artifact Paths To Review

- `tmp/native_robot_table_penetration_probe_20260412_135029/summary.json`
- `tmp/native_robot_table_penetration_probe_20260412_135029/penetration_probe.mp4`
- `tmp/native_robot_table_penetration_probe_20260412_135029/penetration_probe.gif`
- `tmp/native_robot_table_penetration_probe_20260412_135029/contact_sheet.jpg`

## Next Step

- if needed, add a follow-up rigid-contact diagnostic that records exact
  contact pairs or gap metrics rather than only EE error plus contact counts
- if this probe becomes a reused reference, decide whether to move it from
  `tmp/` into a more durable local experiment neighborhood

## Validation

- `python -m py_compile Newton/phystwin_bridge/demos/demo_native_robot_table_penetration_probe.py`
- `bash scripts/run_native_robot_table_penetration_probe.sh`
- `python scripts/validate_experiment_artifacts.py tmp/native_robot_table_penetration_probe_20260412_135029 --require-video --require-gif --summary-field attempt_blocked`
- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
- current result after this pass: `PASS`
