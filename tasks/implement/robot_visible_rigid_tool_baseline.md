# Implement: robot_visible_rigid_tool_baseline

## Canonical Inputs

- `docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
- `docs/bridge/tasks/robot_rope_franka_physical_blocking.md`
- `docs/bridge/tasks/remote_interaction_root_cause.md`
- `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`

## Required Outputs

- dedicated wrapper under `scripts/`
- dedicated result root under `Newton/phystwin_bridge/results/`
- hero/debug/validation videos
- tool-truth reports
- event sheet and multimodal review

## Guardrails

- do not modify `Newton/newton/`
- do not hide the physical contactor
- do not silently change the old task authorities
