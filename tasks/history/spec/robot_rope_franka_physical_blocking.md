# Spec: robot_rope_franka_physical_blocking

## Goal

Upgrade the readable tabletop rope-push baseline into a stronger physical
robot-contact demo where robot-table contact can block the hand rather than
being overwritten by trajectory-following.

## Scope

- Audit the tabletop controller update order
- Audit robot-table collider setup and penetration
- Prove whether the current path is effectively kinematic
- Implement the smallest truthful bridge/demo-level fix if available
- Preserve readable visible finger-to-rope contact
- Add a separate stronger validator path for physical blocking

## Non-Goals

- Modifying `Newton/newton/`
- Faking blocking with a non-physical clamp
- Rewriting the old promoted tabletop task claim boundary
- Declaring success from a better-looking video alone

## Constraints

- Keep robot native to Newton
- Keep tabletop native to Newton
- Keep rope on the PhysTwin -> Newton bridge
- No hidden helper or invisible support patch
- No direct post-solve state overwrite as the accepted blocking mechanism
- If bridge/demo-level fixes are insufficient, prove that honestly

## Inputs

- `docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
- `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
- `scripts/run_robot_rope_franka_tabletop_hero.sh`
- `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`

## Outputs

- New task-local diagnostics proving or disproving physical blocking
- New wrapper and validator if needed
- Full candidate bundle for the stronger task
- A separate `results_meta` entry only if a true pass is achieved

## Done When

- Robot motion is physically actuated and contact can block it
- Robot-table tunneling is gone or reduced below a documented tiny tolerance
- Visible finger still pushes the rope
- Hero/debug/validation all support the same stronger claim
- New validator and full-video review pass
