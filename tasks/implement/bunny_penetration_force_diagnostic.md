# Implement Runbook: Bunny Penetration Force Diagnostic

## Current Execution Order

1. Run `box_control` and `bunny_baseline` through the OFF path.
2. Preserve the rollout states and phenomenon render frames.
3. Build a per-frame detector bundle from the saved rollout states:
   - geometry-contact mask
   - force-contact mask
   - penalty force
   - total force
   - first-collision frame index
4. Render the final `2 x 2` board from:
   - detector bundle
   - saved phenomenon frames
5. Run board-aware QA and artifact validation.
6. Promote only if the run passes.

## Current Risks

- the old accepted package can still confuse agents if docs are not explicit
- force-active collision membership must not silently fall back to geometry-only
  membership in the main board
- total force must include gravity to stay faithful to the update equation
- one case may end earlier than the other; the board must hold the shorter case
  without leaving a blank panel
- bunny-side render cost can dominate iteration time, so replayable detector
  bundles are important

## Artifact Expectations

- run root:
  - `README.md`
  - `command.sh`
  - `summary.json`
- per case:
  - rollout summary / scene
  - detector bundle
  - detector summary
  - phenomenon video and/or replayable saved frames
- board:
  - `collision_force_board_2x2.mp4`
  - summary / notes explaining scaling and force definitions
- QA:
  - `qa/report.json`
  - `qa/metrics.json`
  - `qa/verdict.md`
  - contact sheets
