# Task Spec: robot_rope_franka_tabletop_push_hero

## Goal

Produce a meeting-ready hero demo of a native Newton Franka slowly pushing a
PhysTwin-loaded rope across a native Newton tabletop.

## Non-Goals

- Modifying `Newton/newton/`
- Reframing the deliverable as a drop, bunny, or self-collision demo
- Claiming final full manipulation or haptic-feedback success

## Inputs

- `docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
- `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- `scripts/run_robot_rope_franka.sh`

## Outputs

- updated hero-demo entry path and wrapper logic
- canonical candidate/best-run tree under
  `Newton/phystwin_bridge/results/robot_rope_franka/`
- validated `hero_presentation.mp4`, `hero_debug.mp4`, and
  `validation_camera.mp4`
- updated `Newton/phystwin_bridge/STATUS.md`

## Constraints

- keep the deformable object on the PhysTwin -> Newton bridge path
- keep the robot and tabletop native to Newton
- prefer scene/timing/camera improvements before deep contact changes
- do not touch `Newton/newton/`

## Done When

- one promoted run passes the technical, plausibility, readability, and
  artifact gates from the task page
