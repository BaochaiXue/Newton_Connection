# Plan: robot_rope_franka_physical_blocking

## Goal

Prove whether the current tabletop controller is effectively kinematic, then
replace it with a bridge/demo-level physically actuated path if possible so the
table can block the hand while preserving readable rope push.

## Milestones

1. Create a separate stronger task chain and diagnosis board.
2. Audit control update order and robot-table collider behavior.
3. Write a ranked root-cause report.
4. Implement the smallest truthful physical-actuation fix or prove the bridge
   layer limit.
5. Run a full stronger-task validation bundle and full-video review.
6. Promote only if the stronger physical-blocking claim is actually satisfied.

## Validation

- Existing hero validator pass
- New physical-blocking validator pass
- Full-video review pass on hero/debug/validation
- Explicit hidden-helper verdict remains `NO`
- Status/docs/results_meta updated truthfully

## Notes

- The old tabletop hero baseline remains authoritative unless a new stronger run
  actually lands.
