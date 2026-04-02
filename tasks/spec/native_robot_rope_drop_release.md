# Task Spec: Native Robot Rope Drop/Release Sanity Baseline

## Goal

Create a simple, defensible baseline where a native Newton Franka supports a
rope, releases it, and the rope free-falls onto a real physical ground under
the semi-implicit pipeline.

## Non-Goals

- Modifying `Newton/newton/`
- Complex IK storytelling or contact manipulation
- Replacing the native robot with a proxy for the accepted run
- Visual-only ground or fake support surfaces
- Claiming final two-way coupling success

## Inputs

- task page:
  `docs/bridge/tasks/native_robot_rope_drop_release.md`
- current robot demo:
  `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- existing robot result bundle:
  `results/native_robot_rope_drop_release/`
- related validation:
  `scripts/validate_robot_rope_drop_release_physics.py`
  `scripts/validate_native_robot_rope_drop_release_video.py`

## Outputs

- dedicated result bundle under `results/native_robot_rope_drop_release/`
- documented A/B drag comparison
- physics validation artifact with gravity-like early fall metrics
- readable debug and presentation videos
- updated status/decision records

## Constraints

- Keep the solver family semi-implicit
- Keep the accepted run 1:1 time
- Keep the ground collider real
- Keep the robot visible but not story-dominant after release
- Record the release and impact timing explicitly

## Done When

- the baseline is visually readable and physically credible
- the early fall is plausibly gravity-driven
- the run bundle is self-describing and easy for the next agent to resume
