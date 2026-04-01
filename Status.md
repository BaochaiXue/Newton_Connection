# Status

Last updated: 2026-03-30

## Current Authoritative Code Path

- `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`

## Current Authoritative Best Run

- `/home/xinjie/Newton_Connection/results/robot_deformable_demo/runs/20260330_213045_native_franka_lift_release_presentation`

## Final Gate Snapshot

- semi-implicit path: PASS
- native Newton robot path: PASS
- canonical run folder: PASS
- final mp4 present: PASS
- ffprobe / contact sheet / event sheet / validation / verdict present: PASS
- automatic video gates: PASS
- manual multimodal review recorded: PASS
- slide source updated to authoritative run: PASS
- March 25 deck/transcript regenerated against authoritative run: PASS

## Best-Run Summary

- task:
  - `lift_release`
- render mode:
  - `presentation`
- first contact:
  - `0.0884 s`
- contact duration:
  - `0.0904 s`
- contact-active frames:
  - `226`
- rope COM displacement:
  - `0.1563 m`
- peak midpoint lift:
  - `9.1 mm`

## Rejected / Superseded Canonical Runs

- `results/robot_deformable_demo/rejected/20260330_214036_native_franka_lift_release_presentation/`
- `results/robot_deformable_demo/rejected/20260330_213805_native_franka_lift_release_presentation/`
- `results/robot_deformable_demo/rejected/20260330_213324_native_franka_lift_release_presentation/`
- `results/robot_deformable_demo/rejected/20260330_212830_native_franka_lift_release_presentation/`
- `results/robot_deformable_demo/rejected/20260330_211903_native_franka_lift_release_presentation/`
- `results/robot_deformable_demo/rejected/20260330_211618_native_franka_lift_release_presentation/`

## Remaining Notes

- `demo_robot_rope.py` is still absent from the local repo; that mission reference remains a legacy name only.
- `demo_rope_control_realtime_viewer.py` remains a profiling/replay support path, not the final demo path.
- Meeting artifacts refreshed from the current authoritative run:
  - `formal_slide/meeting_2026_03_25/bridge_meeting_20260325.pptx`
  - `formal_slide/meeting_2026_03_25/transcript.md`
  - `formal_slide/meeting_2026_03_25/transcript.pdf`
  - `formal_slide/meeting_2026_03_25/gif/robot_rope_franka_lift_release_v1.gif`
