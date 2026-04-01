# Prompt

## Mission

Produce a truly meeting-ready, visually validated, native Newton robot +
deformable demo under the semi-implicit pipeline.

## Final Story

The final video must read as:

- a native Newton robot asset
- manipulating a deformable object loaded through the PhysTwin -> Newton bridge
- with visible two-way coupling
- in a stable semi-implicit scene

## Hard Constraints

- stay on the semi-implicit path
- do not switch solver family for the final result
- do not edit `Newton/newton/`
- prefer scene/controller/render/bridge-layer changes over core surgery
- do not accept black, cropped, or unreadable videos

## Authoritative Current Path

- final-path script:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- current authoritative best run:
  - `results/robot_deformable_demo/runs/20260330_213045_native_franka_lift_release_presentation/`
- not final:
  - `Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py`

## Important Audit Note

The mission text referenced `demo_robot_rope.py`, but that script is not present
in the current local repo. Only legacy outputs with that naming pattern remain
under `tmp/`.

## Done When

- a canonical best-run folder exists under `results/robot_deformable_demo/`
- the run has mp4 + validation artifacts + verdict
- the run is visually presentation-ready
- slide/material assets are updated to point to the chosen best result

## Latest Best Run

- `results/robot_deformable_demo/runs/20260330_213045_native_franka_lift_release_presentation/`

## Latest Best-Run Claim

- Native Newton Franka manipulates the bridged rope in a readable lift-and-release task.
- The run is presentation rendered at `1920x1080` and `30 fps`.
- The video bundle has automatic gate PASS plus explicit manual visual PASS.
- The summary now records a defensible finger-span contact window instead of the earlier all-zero or always-on contact failures.
