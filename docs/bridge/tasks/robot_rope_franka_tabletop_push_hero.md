# Task: Native Newton Franka + Native Table + PhysTwin Rope Hero Demo

## Question

Can the bridge deliver a meeting-ready hero demo where a native Newton Franka
slowly pushes a PhysTwin-loaded rope across a native Newton tabletop, with the
contact zone visually readable and physically defensible?

## Why It Matters

This is the strongest robot + deformable chapter claim currently in scope.

It is narrower than "full manipulation" but stronger than the existing stage-0
drop/release baseline:

- native Newton robot asset
- native Newton tabletop support
- PhysTwin -> Newton rope deformation under robot contact
- slow, legible, presentation-ready contact story

## Current Status

- Not yet accepted.
- Existing entry point remains:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Existing canonical robot result bundle remains the historical reference:
  - `results/robot_deformable_demo/`
- Existing stage-0 sanity baseline remains separate:
  - `results/native_robot_rope_drop_release/`
- This task is the follow-on hero-demo workstream for a real tabletop push.

## Code Entry Points

- Main demo:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Local helpers:
  - `Newton/phystwin_bridge/demos/rope_demo_common.py`
  - `Newton/phystwin_bridge/demos/bridge_deformable_common.py`
  - `Newton/phystwin_bridge/demos/bridge_shared.py`
- Existing wrapper reference:
  - `scripts/run_robot_rope_franka.sh`

## Canonical Result Root

- `Newton/phystwin_bridge/results/robot_rope_franka/`

Expected layout:

- `BEST_RUN/`
- `candidates/<timestamp>_<short_tag>/`
- per candidate:
  - `manifest.json`
  - `run_command.txt`
  - `metrics.json`
  - `validation.md`
  - `hero_presentation.mp4`
  - `hero_debug.mp4`
  - `validation_camera.mp4`
  - `contact_sheet.png`
  - `keyframes/`

## Success Criteria

- robot is unmistakably the native Newton Franka
- support surface is unmistakably a native Newton tabletop
- rope begins in a settled tabletop configuration or another clearly justified
  support configuration
- robot performs a slow lateral push rather than a fling or scoop
- rope visibly deforms and slides because of robot contact
- presentation clip is between 6 and 12 seconds and readable on first viewing
- best run is promoted under `phystwin_bridge/results/robot_rope_franka/BEST_RUN/`

## Related Pages

- [robot_deformable_demo.md](./robot_deformable_demo.md)
- [native_robot_rope_drop_release.md](./native_robot_rope_drop_release.md)
- [video_presentation_quality.md](./video_presentation_quality.md)
