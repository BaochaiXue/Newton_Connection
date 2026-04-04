# Status: robot_visible_rigid_tool_baseline

## Current State

- Active with a promoted run
- New intermediary baseline task between the readable finger-push hero and the
  blocked physical-contact follow-on

## Last Completed Step

- Preserved the task boundary:
  - old promoted tabletop finger baseline remains authoritative
  - blocked physical-blocking task remains separate
  - this task is only the honest visible-tool intermediary baseline
- Implemented the visible-tool bridge path in [demo_robot_rope_franka.py](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py):
  - visible-tool parser args
  - actual capsule shape attachment in the Newton model
  - render path using the same finalized capsule dimensions/transform
  - tool-aware summary metrics and contact proof surface
  - visible-tool-specific camera presets for tabletop hero
- Added the canonical tool wrapper and diagnostics:
  - [run_robot_visible_rigid_tool_baseline.sh](/home/xinjie/Newton_Connection/scripts/run_robot_visible_rigid_tool_baseline.sh)
  - [diagnose_robot_visible_rigid_tool_baseline.py](/home/xinjie/Newton_Connection/scripts/diagnose_robot_visible_rigid_tool_baseline.py)
- Rejected early branches fail-closed:
  - finger-mounted vertical tool variants (`c01`..`c06`) either hid the tool inside the finger silhouette, let bare finger geometry read as the true contactor, or left the hero contact patch too ambiguous
- Promoted [20260404_141534_c07_link7_bar](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/results/robot_visible_rigid_tool_baseline/candidates/20260404_141534_c07_link7_bar):
  - visible red crossbar-style capsule mounted on `fr3_link7`
  - `actual_tool_first_contact_time_s = 1.7342`
  - `tool_contact_duration_s = 2.96815`
  - `first_rope_lateral_motion_time_s = 2.30115`
  - `first_rope_deformation_time_s = 2.3345`
  - `tool_contact_onset_report.json` reports `multi_frame_standoff_detected = false`
  - `tool_vs_collider_report.md` passes with collider/render geometry match
  - `rope_visual_vs_physical_thickness_report.md` confirms rope render thickness equals physical thickness
  - standard hero validator now passes truthfully after manual review was completed

## Next Step

- Preserve the promoted visible-tool baseline and keep its claim boundary conservative.
- If this baseline is used in slides/materials, describe it as **tool-mediated contact**, not direct finger contact or physical blocking.
- Any follow-on stronger claim should branch from:
  - `robot_rope_franka_physical_blocking`
  - or a later direct-finger re-certification task if needed

## Current Guardrail

- Do not change `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
- Do not create `results_meta/tasks/robot_visible_rigid_tool_baseline.json`
  until a real pass exists
- Do not claim direct finger contact or physical blocking in this task
