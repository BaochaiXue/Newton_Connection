> status: active
> canonical_replacement: none
> owner_surface: `robot_rope_franka_tabletop_push_hero`
> last_reviewed: `2026-04-01`
> review_interval: `21d`
> update_rule: `Update when the task boundary, promoted run meaning, or local-only result-tree policy changes.`
> notes: Active task page for the tabletop-push hero baseline. Committed promoted-run authority lives in `results_meta/`.

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

- Accepted on `2026-04-01`.
- Committed promoted-run authority now lives in:
  - `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
- Existing entry point remains:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Existing canonical robot result bundle remains the historical reference:
  - `results/robot_deformable_demo/`
- Existing stage-0 sanity baseline remains separate:
  - `results/native_robot_rope_drop_release/`
- This task is the follow-on hero-demo workstream for a real tabletop push.
- Accepted run:
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260401_081639_fixeddt_c08_gatepass`
- Local convenience mirror:
  - `Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/`

Accepted implementation note:

- the winning run keeps the robot native to Newton and the rope on the
  PhysTwin -> Newton bridge, but uses a tabletop-only native joint-space
  waypoint controller because the earlier tabletop IK path did not reliably
  hit the contact line under the fixed timestep

## Code Entry Points

- Main demo:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Local helpers:
  - `Newton/phystwin_bridge/demos/rope_demo_common.py`
  - `Newton/phystwin_bridge/demos/bridge_deformable_common.py`
  - `Newton/phystwin_bridge/demos/bridge_shared.py`
- Canonical wrapper:
  - `scripts/run_robot_rope_franka_tabletop_hero.sh`

## Canonical Result Root

- committed authority:
  - `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
- local bundle root for navigation only:
  - `Newton/phystwin_bridge/results/robot_rope_franka/`

Expected layout:

- local-only `BEST_RUN/`
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
- local bundle mirror may remain under
  `phystwin_bridge/results/robot_rope_franka/BEST_RUN/`, but committed
  current/best/promoted meaning must stay in `results_meta/`

## Related Pages

- [robot_deformable_demo.md](./robot_deformable_demo.md)
- [native_robot_rope_drop_release.md](./native_robot_rope_drop_release.md)
- [video_presentation_quality.md](./video_presentation_quality.md)
