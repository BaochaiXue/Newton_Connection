# Task: Native Robot + Native Table + PhysTwin Rope Hero Demo

## Question

Can a native Newton Franka push a PhysTwin-loaded rope across a native Newton
table in a way that is slow, readable, and defensible in a meeting?

## Why It Matters

This is the meeting-ready robot-deformable hero path. It is narrower than a
full manipulation claim, but stronger than a probe clip because the table,
robot, and rope interaction all need to read as real.

## Current Status

- Dedicated workstream scaffolded.
- Main implementation path remains `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`.
- Canonical result root reserved at:
  - `Newton/phystwin_bridge/results/robot_rope_franka/`
- No promoted candidate yet.

## Code Entry Points

- Main demo:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Shared helpers:
  - `Newton/phystwin_bridge/demos/rope_demo_common.py`
  - `Newton/phystwin_bridge/demos/bridge_deformable_common.py`
  - `Newton/phystwin_bridge/demos/bridge_shared.py`
- Canonical wrapper to add or extend:
  - `scripts/run_robot_rope_franka.sh`

## Canonical Command

Expected hero entry point:

```bash
python Newton/phystwin_bridge/demos/demo_robot_rope_franka.py \
  --task tabletop_push_hero \
  --render-mode presentation
```

## Required Artifacts

- `hero_presentation.mp4`
- `hero_debug.mp4`
- `validation_camera.mp4`
- `metrics.json`
- `validation.md`
- `contact_sheet.png`
- `keyframes/`

## Success Criteria

- native Newton Franka is unmistakable
- native Newton table / support surface is unmistakable
- PhysTwin rope is visibly settled on the table before contact
- the robot visibly pushes the rope without flinging it
- the contact zone stays readable for most of the push
- the presentation clip is 6-12 seconds and meeting-ready

## Open Questions

- Do we need a dedicated `tabletop_push_hero` task preset, or can the current
  `push_probe` path be tuned into the hero demo without losing readability?
- Is a hidden preroll settle phase enough to make the rope start pose read as
  settled rather than staged?

## Related Pages

- [robot_deformable_demo.md](./robot_deformable_demo.md)
- [video_presentation_quality.md](./video_presentation_quality.md)
