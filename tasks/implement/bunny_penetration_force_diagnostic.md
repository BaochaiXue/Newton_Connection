# Implement Runbook: Bunny Penetration Force Diagnostic

## Current Execution Order

1. Render `bunny_baseline` phenomenon with full rollout coverage
2. Build force artifacts from the same rollout states
3. Validate the baseline case with sampled frames and contact sheets
4. Only then replicate to:
   - `box_control`
   - `bunny_low_inertia`
   - `bunny_larger_scale`
5. If the mechanism review specifically asks for all-contact-node evidence:
   - run `box_control` and `bunny_baseline` through the OFF path on the
     standard supported setup
   - reuse the saved rollout states and saved phenomenon frames
   - rebuild per-frame rigid-contact masks from rollout state
   - render separate penalty-force and total-force overlays for all contact
     nodes
   - compose the four panels into one `2 x 2` board video

## Current Risks

- stale helper path assumptions still point to `self_off/force_diagnostic`
- split/matrix scripts may still encode short old-style windows
- latest success pointers may still refer to runs that pass only the old QA
- all-contact-node overlays can become visually dense on the box control, so
  arrow normalization and panel HUD must stay readable
- because the current board path filters nodes by target contact rather than
  decomposing per-shape contact forces, later-phase mixed target+ground contact
  on the same node remains a semantic caveat to watch

## Artifact Expectations

- `phenomenon/*.mp4`
- `force_mechanism/self_off/force_diagnostic/*.mp4`
- `qa/metrics.json`
- `qa/verdict.md`
- `README.md`
- for the new board path:
  - `artifacts/collision_force_board/collision_force_board_2x2.mp4`
  - `artifacts/collision_force_board/summary.json`
