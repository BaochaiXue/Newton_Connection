# Implement Runbook: Bunny Penetration Force Diagnostic

## Current Execution Order

1. Render `bunny_baseline` phenomenon with full rollout coverage
2. Build force artifacts from the same rollout states
3. Validate the baseline case with sampled frames and contact sheets
4. Only then replicate to:
   - `box_control`
   - `bunny_low_inertia`
   - `bunny_larger_scale`

## Current Risks

- stale helper path assumptions still point to `self_off/force_diagnostic`
- split/matrix scripts may still encode short old-style windows
- latest success pointers may still refer to runs that pass only the old QA

## Artifact Expectations

- `phenomenon/*.mp4`
- `force_mechanism/self_off/force_diagnostic/*.mp4`
- `qa/metrics.json`
- `qa/verdict.md`
- `README.md`
