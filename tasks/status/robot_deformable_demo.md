# Task Status: Robot + Deformable Demo

## State

- Status: complete for the current meeting-ready baseline
- Last updated: 2026-03-31

## Authoritative Path

- Script:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Canonical wrapper:
  - `scripts/run_robot_rope_franka.sh`
- Committed results metadata:
  - `results_meta/tasks/robot_deformable_demo.json`

## Authoritative Best Run

- Run:
  - `results/robot_deformable_demo/runs/20260331_030148_native_franka_lift_release_presentation`
- Video:
  - `results/robot_deformable_demo/runs/20260331_030148_native_franka_lift_release_presentation/media/final.mp4`
- Validation:
  - `results/robot_deformable_demo/runs/20260331_030148_native_franka_lift_release_presentation/qa/validation.json`
  - `results/robot_deformable_demo/runs/20260331_030148_native_franka_lift_release_presentation/qa/verdict.md`

## Reproduction

```bash
scripts/run_robot_rope_franka.sh
```

## Key Metrics

- first contact:
  - `0.0880 s`
- contact duration:
  - `0.2060 s`
- contact-active frames:
  - `515`
- rope COM displacement:
  - `0.2007 m`
- peak midpoint lift:
  - `9.1 mm`

## Notes

- The summary/contact mismatch was repaired by switching from a
  gripper-center-only proxy to the final `finger_span` contact proxy.
- The final slide source now points at the canonical run under `results/`,
  not the old `tmp/demo_robot_rope_franka_lift_release_presentation_full`.
- Rejected canonical attempts were archived under
  `results/robot_deformable_demo/rejected/`.
- The current canonical tuning keeps the original lift_release geometry and
  adds phase-gated drag on `pre_approach + release_retract` only.
- The narrower stage-0 drop/release sanity baseline is tracked separately at
  `docs/bridge/tasks/native_robot_rope_drop_release.md` and should not be
  conflated with this lift-release baseline.
- The promoted result bundle now also has a run-local `README.md`,
  a stricter `manifest.json` plus `manifest.template.json`, and a
  `SLIDE_READY.md` checklist so
  future runs can be promoted without guessing the required layout.
- The canonical committed meaning for this baseline now lives in:
  - `results_meta/tasks/robot_deformable_demo.json`
