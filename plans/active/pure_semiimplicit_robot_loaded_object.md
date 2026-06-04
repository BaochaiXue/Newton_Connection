# Plan: pure_semiimplicit_robot_loaded_object

## Milestone 1: Rebuild The Clean Diagnostic

- Status: completed on `2026-05-11`.
- Created repo-native task surfaces.
- Implemented a single-SemiImplicit Panda + table + PhysTwin object demo.
- Added a canonical wrapper.
- Fixed motion scheduling to use integrated `sim_time`.
- Ran static checks and the timing-fixed artifact run.
- Validated the artifact contract.
- Recorded the result and current conclusion.

## Milestone 2: Decide The Claim Boundary

- Status: active.
- If the repaired diagnostic shows stable robot posture, table blocking, and
  object response, compare it against the split MuJoCo/SemiImplicit route.
- If it fails, preserve the failure as a clean negative result instead of
  reviving retired code.

Current result: it fails cleanly. The full Panda body state becomes non-finite
before finger-object contact, so this path should not be promoted as a
robot/object two-way interaction demo.
