# Task: robot_rope_franka_native_v2

## Question

Can the bridge replace the current stronger-task monolith with a smaller
native-style Franka tabletop rope demo that keeps the truthful controller path
 while starting cleanly and preserving direct-finger blocking and rope push?

## Why It Matters

The current stronger-task execution path keeps solver truth, but its startup and
reference staging are still tangled up with the old readable demo assumptions.
A fresh v2 path lets the project test the actual native-style control structure
the user asked for:

- Cartesian EE waypoints
- native Newton IK
- `control.joint_target_pos`
- solved `body_q` as the only body-truth surface

## Current Status

- In progress
- Old stronger-task path remains intact and non-authoritative
- V2 must land as a new bridge-layer demo and wrapper before any stronger claim

## Code Entry Points

- Main demo:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka_native_v2.py`
- Canonical wrapper:
  - `scripts/run_robot_rope_franka_native_v2.sh`
- Shared helper surface allowed for reuse:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
  - `Newton/phystwin_bridge/demos/bridge_deformable_common.py`
  - `Newton/phystwin_bridge/demos/rope_demo_common.py`
- Diagnostics / validation:
  - `scripts/diagnose_robot_rope_physical_blocking.py`
  - `scripts/validate_robot_rope_franka_physical_blocking.py`

## Canonical Commands

- Wrapper:
  - `scripts/run_robot_rope_franka_native_v2.sh --tag safe_start_baseline`
  - `scripts/run_robot_rope_franka_native_v2.sh --tag shallower_push_baseline ...`
  - `scripts/run_robot_rope_franka_native_v2.sh --tag clearer_rope_motion_baseline ...`

## Required Artifacts

- `summary.json`
- `command.txt`
- same-history:
  - `hero_presentation.mp4`
  - `hero_debug.mp4`
  - `validation_camera.mp4`
- `robot_table_contact_report.json`
- `nonfinger_table_contact_report.json`
- `blocking_validation.md`
- `sim/history/*.npy`

## Success Criteria

- Startup is visually clean: no visible settle-phase collapse
- Table really blocks the direct-finger robot path under solver truth
- Rope is visibly moved by real finger contact
- No visible tool / proxy / hidden helper
- At least one v2 candidate passes both numeric gates and skeptical video review

## Open Questions

- How much EE waypoint conservatism is needed to keep a clean start while still
  producing readable rope motion?
- Is `joint_target_vel` feedforward necessary in v2, or can position targets
  alone suffice at the current gains?

## Related Pages

- `docs/bridge/tasks/robot_rope_franka_physical_blocking.md`
- `docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
