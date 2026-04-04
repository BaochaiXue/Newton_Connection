# Status: robot_visible_rigid_tool_baseline

## Current State

- Active
- New intermediary baseline task between the readable finger-push hero and the
  blocked physical-contact follow-on

## Last Completed Step

- Re-read the control plane and preserved the claim boundary:
  - old promoted tabletop finger baseline remains authoritative
  - blocked physical-blocking task remains separate
  - this task is only the honest visible-tool intermediary baseline
- Implemented the first visible-tool bridge path in [demo_robot_rope_franka.py](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py):
  - visible-tool parser args
  - actual capsule shape attachment in the Newton model
  - render path using the same finalized capsule dimensions/transform
  - tool-aware summary metrics
- Added the new task-local wrapper and diagnostics:
  - [run_robot_visible_rigid_tool_baseline.sh](/home/xinjie/Newton_Connection/scripts/run_robot_visible_rigid_tool_baseline.sh)
  - [diagnose_robot_visible_rigid_tool_baseline.py](/home/xinjie/Newton_Connection/scripts/diagnose_robot_visible_rigid_tool_baseline.py)
- Ran the current smoke bundle [20260404_134258_smoke](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/results/robot_visible_rigid_tool_baseline/candidates/20260404_134258_smoke) and rejected it:
  - the visible tool exists and is the reported proof surface in summary (`contact_peak_proxy = visible_tool_capsule`)
  - but it is not yet an honest baseline because bare finger boxes still contact earlier than the tool
  - measured evidence:
    - `actual_finger_box_first_contact_time_s = 0.30015 s`
    - `actual_tool_first_contact_time_s = 0.86710 s`
    - `tool_contact_onset_report.json` flags multi-frame stand-off because rope motion/deformation starts before visible tool contact
- Ran bounded geometry/attachment diagnostics on top of the smoke rollout and rejected the tested branches:
  - right-finger-mounted tool: the opposite bare finger touches first
  - left-finger-mounted tool: the other bare finger then becomes the first contactor
  - mild central `link7` tool on the old joint-trajectory body poses still contacts later than the bare fingers
  - `IK + closed gripper` without tool-aware trajectory re-calibration still starts in contact or collapses back to bare-finger-first contact
- Extended the tool-geometry search and current repo evidence now shows a more promising branch:
  - [20260404_135151_c03_offsetsolve](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/results/robot_visible_rigid_tool_baseline/candidates/20260404_135151_c03_offsetsolve) achieved `actual_tool_contact_started = true` with a tool offset override of `(-0.004, 0.0076, 0.049)`
  - [20260404_135230_c04_smoke2_full](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/results/robot_visible_rigid_tool_baseline/candidates/20260404_135230_c04_smoke2_full) achieved `actual_tool_contact_started = true` with a slightly thicker tool (`radius = 0.0065`, `half_height = 0.0070`, `offset = (0.0, 0.0076, 0.0620)`)
- Removed the duplicate visible-tool rendering path in [demo_robot_rope_franka.py](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py): the capsule is now shown via the actual model collision shape plus shape-color rules rather than being drawn twice
- Current blocker:
  - the workstation is simultaneously running multiple visible-tool experiments in parallel
  - under that load, a clean rerun of the promising `c04` geometry ([20260404_140300_preview_c04geom](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/results/robot_visible_rigid_tool_baseline/candidates/20260404_140300_preview_c04geom)) did not yet reproduce tool contact
  - until one promising branch is rerun in isolation and reviewed, the task is still fail-closed and not promotable

## Next Step

- Wait for or create a clean single-run execution window, then rerun the best current full-duration visible-tool branch in isolation.
- Current strongest branches to retry under clean conditions:
  - `c03_offsetsolve`
  - `c04_smoke2_full`
- Only after that: complete the root-level artifact bundle, run validator + tool diagnostics, and do fail-closed full-video review.

## Current Guardrail

- Do not change `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
- Do not create `results_meta/tasks/robot_visible_rigid_tool_baseline.json`
  until a real pass exists
- Do not claim direct finger contact or physical blocking in this task
