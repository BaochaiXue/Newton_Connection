> status: historical
> canonical_replacement: `../../../docs/bridge/tasks/robot_rope_franka_physical_blocking.md`
> owner_surface: `robot_rope_franka_native_v2`
> last_reviewed: `2026-04-09`
> notes: Historical exploratory runbook archived out of `tasks/implement/`.

# Implement: robot_rope_franka_native_v2

## Canonical Commands

- Build and run:
  - `scripts/run_robot_rope_franka_native_v2.sh --tag safe_start_baseline`
  - `scripts/run_robot_rope_franka_native_v2.sh --tag shallower_push_baseline ...`
  - `scripts/run_robot_rope_franka_native_v2.sh --tag clearer_rope_motion_baseline ...`

## Required Diagnostics

- robot-table direct-finger blocking report
- non-finger table-loading report
- same-history hero/debug/validation videos
- summary and validation markdown
- visual startup audit on the first ~15 frames

## Expected Run Shape

- `Newton/phystwin_bridge/results/robot_rope_franka_native_v2/candidates/<run_id>/`
- `summary.json`
- `command.txt`
- `hero_presentation.mp4`
- `hero_debug.mp4`
- `validation_camera.mp4`
- `sim/history/*.npy`
- `robot_table_contact_report.json`
- `nonfinger_table_contact_report.json`
- `blocking_validation.md`

## Guardrails

- No edits under `Newton/newton/`
- No support box by default in v2 milestone 1
- No visible tool / proxy / hidden helper
- No direct joint state overwrite in the simulation loop
