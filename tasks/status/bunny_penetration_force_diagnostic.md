# Status: Bunny Penetration Force Diagnostic

## 2026-04-01

- Reopened the task under a stricter meeting spec.
- Explicitly marked the old accepted full-process synchronized package as
  historical rather than final for meeting visualization.
- Re-scoped the main deliverable to:
  - self-collision OFF
  - `box_control`
  - `bunny_baseline`
  - real-time `2 x 2`
  - all currently colliding cloth mass nodes
- Updated the repo-native task page, spec, plan, and implement runbook so the
  new deliverable is the source of truth rather than an add-on note.

## Current Technical State

- Historical trigger/full-process force diagnostics already exist.
- Historical committed results metadata now records the sync-safe 4-case
  mechanism package under:
  - `results_meta/tasks/bunny_penetration_force_diagnostic.json`
- Existing board/render code also exists, but it is still short of the stricter
  spec in at least these ways:
  - main board currently follows geometry-contact membership instead of the
    force-active collision set
  - the current board path does not yet save a formal per-frame detector bundle
    as a promoted artifact
  - board-level validation is not yet strict enough for the new semantics
  - the old docs still overstated the historical accepted run as final

## Next Step

- harden detector persistence
- harden board semantics
- extend validator coverage
- produce a fresh promoted run under a new
  `*_realtime_allcolliding_2x2_v1` directory

## 2026-04-01 Attempt: `20260401_011336_realtime_allcolliding_2x2_v1`

- A fresh run now exists under:
  - `results/bunny_force_visualization/runs/20260401_011336_realtime_allcolliding_2x2_v1`
- That run successfully produced:
  - per-case OFF rollout artifacts for:
    - `box_control`
    - `bunny_baseline`
  - per-frame detector bundles
  - final board video:
    - `artifacts/collision_force_board/collision_force_board_2x2.mp4`
  - validator outputs under:
    - `qa/report.json`
    - `qa/verdict.md`
- The board-aware visual QA now passes on that run.
- However the task is still NOT closed, because one strict semantic blocker
  remains:
  - the current detector / board path uses `f_external_total` as penalty force
    without a per-target shape decomposition
  - in the current scene this can still mix the target rigid shape with other
    shape-contact contributors such as ground-support contact
  - evidence:
    - both cases currently report `first_force_contact_frame_index = 1`
    - both cases also report near-global active-node counts immediately after
      start, which is inconsistent with the intended “first target collision”
      semantics
- Therefore the current run is a useful visual attempt, but it cannot yet be
  promoted as the final strict-spec success.
- once promoted, update:
  - `results_meta/tasks/bunny_penetration_force_diagnostic.json`
  - `results_meta/LATEST.md`
