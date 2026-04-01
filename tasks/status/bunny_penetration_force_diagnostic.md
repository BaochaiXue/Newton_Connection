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
- The reopened all-colliding-node board path is now implemented bridge-side and
  promoted under:
  - `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5`
- The promoted `v5` run now includes:
  - per-frame detector bundles for `box_control` and `bunny_baseline`
  - target-only penalty force from explicit re-evaluation with
    `add_ground_plane=False`
  - a board-aware QA PASS
  - artifact-contract PASS
  - bundle pointers updated under `results/bunny_force_visualization/`

## Next Step

- optional slide refresh if the meeting deck should swap the older historical
  mechanism GIFs for the new `2 x 2` board
- otherwise keep `v5` as the canonical reopened-board result

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

## 2026-04-01 Promoted Run: `20260401_013500_realtime_allcolliding_2x2_v5`

- Promoted run root:
  - `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5`
- Final board artifact:
  - `artifacts/collision_force_board/collision_force_board_2x2.mp4`
- Detector semantics:
  - main node set:
    `rigid_force_contact_mask = geom_contact_mask AND target_force_contact_mask`
  - target-only penalty force:
    `f_external_total` from explicit re-evaluation with
    `add_ground_plane=False`
  - total force:
    `f_internal_total + f_external_total + mass * gravity_vec`
- First-collision indices:
  - `box_control = 4`
  - `bunny_baseline = 4`
- Validators:
  - `qa/report.json` -> `PASS`
  - `qa/verdict.md`
  - `scripts/validate_experiment_artifacts.py` -> `PASS`
- Secondary local-only pointer surfaces updated:
  - `results/bunny_force_visualization/LATEST_SUCCESS.txt`
  - `results/bunny_force_visualization/LATEST_ATTEMPT.txt`
  - `results/bunny_force_visualization/INDEX.md`

## 2026-04-01 Slide Update

- Updated the `2026-04-01` meeting deck source so the bunny force-analysis
  section now explicitly states the experiment setting on-slide:
  - cloth total mass = `0.1 kg`
  - rigid target mass = `0.5 kg`
- Applied this to the visible slide text for:
  - `Result F2`
  - `Result F3`
- Regenerated:
  - `formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx`
  - `formal_slide/meeting_2026_04_01/transcript.md`
  - `formal_slide/meeting_2026_04_01/transcript.pdf`
- Further slide refresh:
  - exported four single-panel mp4s from the current canonical board under:
    - `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5/artifacts/collision_force_board/panels/`
  - rewired `Result F2` so it now uses those current single-panel videos rather
    than the older historical force-mechanism gifs
  - kept `Result F3` on the full canonical `2 x 2` board
