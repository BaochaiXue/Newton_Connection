# Task Status: Native Robot Rope Drop/Release Sanity Baseline

## State

- Status: recoil-fixed stage-0 baseline promoted
- Last updated: 2026-03-31

## Authoritative Path

- Task page:
  - `docs/bridge/tasks/native_robot_rope_drop_release.md`
- Result bundle:
  - `results/native_robot_rope_drop_release/`

## Authoritative Best Run

- Run:
  - `results/native_robot_rope_drop_release/runs/20260331_232106_native_franka_recoilfix_drag_off_w5`
- Presentation video:
  - `results/native_robot_rope_drop_release/runs/20260331_232106_native_franka_recoilfix_drag_off_w5/final_presentation.mp4`
- Physics validation:
  - `results/native_robot_rope_drop_release/runs/20260331_232106_native_franka_recoilfix_drag_off_w5/physics_validation.json`
- Video verdict:
  - `results/native_robot_rope_drop_release/runs/20260331_232106_native_franka_recoilfix_drag_off_w5/qa/verdict.md`
- Drag comparison:
  - `results/native_robot_rope_drop_release/drag_ab_compare.json`

## Current Boundary

- The existing native Franka lift-release run remains the historical
  robot+deformable baseline
- This milestone is narrower and must be validated on its own terms
- The promoted result shows release, free fall, real ground contact, and
  1:1 presentation timing without claiming final two-way coupling

## Key Outcome

- Both recoil-fixed OFF and ON runs now pass:
  - settle before release
  - low post-release horizontal kick
  - gravity-like early fall
  - real ground contact
  - video readability
- The drag effect on the recoil-fixed pair is currently minor
- The OFF run remains authoritative because it is the simpler baseline and
  already passes the full gate set
