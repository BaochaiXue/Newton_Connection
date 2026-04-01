# Task Status: Native Robot Rope Drop/Release Sanity Baseline

## State

- Status: provisional stage-0 baseline promoted; recoil-free follow-up still target
- Last updated: 2026-03-31

## Authoritative Path

- Task page:
  - `docs/bridge/tasks/native_robot_rope_drop_release.md`
- Result bundle:
  - `results/native_robot_rope_drop_release/`

## Current Promoted Run

- Run:
  - `results/native_robot_rope_drop_release/runs/20260331_040614_native_franka_drag_off_w5_readable`
- Presentation video:
  - `results/native_robot_rope_drop_release/runs/20260331_040614_native_franka_drag_off_w5_readable/final_presentation.mp4`
- Physics validation:
  - `results/native_robot_rope_drop_release/runs/20260331_040614_native_franka_drag_off_w5_readable/physics_validation.json`
- Video verdict:
  - `results/native_robot_rope_drop_release/runs/20260331_040614_native_franka_drag_off_w5_readable/qa/verdict.md`
- Drag comparison:
  - `results/native_robot_rope_drop_release/drag_ab_compare.json`

## Current Boundary

- The existing native Franka lift-release run remains the historical
  robot+deformable baseline
- This milestone is narrower and must be validated on its own terms
- The promoted result shows release, free fall, real ground contact, and
  1:1 presentation timing without claiming final two-way coupling
- The current promoted run still shows release recoil/catapulting, so it is
  only provisional until a recoil-free follow-up supersedes it

## Key Outcome

- Drag OFF and drag ON both remained gravity-like in the matched 5 kg baseline
- Drag changed impact timing/speed, but it was not the main cause of slow or
  non-gravity-like free fall
- The OFF run remains the provisional promoted baseline because the
  pre-release support story is clearer and the full QA bundle passes
- The actual acceptance target is a recoil-free release/drop run that can
  supersede this provisional baseline
