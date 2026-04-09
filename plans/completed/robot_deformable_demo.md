# Plan: Robot + Deformable Demo Tuning

## Goal

Stabilize the native Franka rope demo so the current meeting-ready baseline
keeps contact, looks less abrupt, and reduces rope-through-table artifacts.

## Constraints

- Do not touch `Newton/newton/`
- Keep the demo in the bridge layer
- Keep semi-implicit as the solver family
- Validate the result with the canonical wrapper before calling it a success

## Milestones

1. Tune the `lift_release` task path to reduce lateral sweep and table overlap
2. Smooth the IK controller targets and suspend drag during active manipulation
3. Run the canonical wrapper and inspect the resulting QA bundle

## Validation

- `scripts/run_robot_rope_franka.sh`
- `scripts/validate_robot_deformable_demo.py <run_dir>`

## Notes

- The local-only best-run convenience pointer remains
  `results/robot_deformable_demo/BEST_RUN.md`
- If the tuned run regresses contact or interaction quality, keep the previous
  run as the local fallback while updating `results_meta/` for any committed
  authoritative change
