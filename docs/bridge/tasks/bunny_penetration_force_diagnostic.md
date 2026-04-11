> status: active
> canonical_replacement: none
> owner_surface: `bunny_penetration_force_diagnostic`
> last_reviewed: `2026-04-11`
> review_interval: `21d`
> update_rule: `Update when the promoted board contract, accepted workpoint, or meeting-facing force semantics change.`
> notes: Active canonical task page for the bunny penetration mechanism and meeting-facing board workflow. Keep this page on the current deliverable rather than repeating the full experimental history.

# Task: Bunny Penetration Mechanism Diagnostic

## Primary Question

Can the project defend bunny penetration as a mechanism claim with a clean
meeting-facing artifact, rather than as a vague visual symptom?

The task is complete only when the repo keeps both:

- a defendable mechanism reading
- a reusable, clearly validated visualization package

## Current Deliverable

Promoted meeting-facing board package:

- `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5`

Historical mechanism bundle kept for context:

- `results/bunny_force_visualization/runs/20260331_231500_fullprocess_sync_matrix_manual_v2`

The current task target is the stricter real-time board:

- self-collision OFF
- only `cloth + box` and `cloth + bunny`
- one real-time `2 x 2` board
- all currently colliding cloth mass nodes shown in the main board
- fixed panel semantics:
  - top-left = `box penalty`
  - top-right = `box total`
  - bottom-left = `bunny penalty`
  - bottom-right = `bunny total`
- clip timing from rollout start to `1.0 s` after deterministic first collision

## Why This Matters

The old synchronized full-process package was useful for mechanism study, but it
was not the right final meeting artifact. The stricter board keeps the force
story readable without relying on older probe-centric overlays.

## Main Code Paths

- `Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py`
- `scripts/run_bunny_force_case.py`
- `scripts/run_bunny_penetration_collision_board.sh`
- `scripts/render_bunny_penetration_collision_board.py`
- validators:
  - `scripts/validate_bunny_force_visualization.py`
  - `scripts/validate_experiment_artifacts.py`

## Scope

Included:

- one deformable cloth
- one rigid target:
  - `box`
  - `bunny`
- bridge-side rigid-contact force decomposition
- deterministic first-collision detection
- per-frame collision-node persistence
- one real-time `2 x 2` board

Excluded:

- self-collision transfer or resolution
- Newton core kernel rewrites
- rope / MPM / robot-side transfer
- unrelated scenes outside `cloth + box` and `cloth + bunny`

## Force Definitions

Penalty force:

- rigid-collision force only
- target-only rigid-contact contribution on that cloth node

Total force:

- full resultant force entering the particle update
- `f_internal_total + f_external_total + mass * gravity_vec`

The exact force definition used by the promoted run must be written into the
run-local summary and stay consistent with the board labels.

## Detector Requirement

For every simulation frame in the promoted clip window, the pipeline must save:

- `geom_contact_mask`
- `force_contact_mask`
- cloth node world positions
- penalty force vectors
- total force vectors
- penalty and total force magnitudes
- first-collision flags

Preferred node-selection rule:

- display the `force_contact_mask`

Geometry contact can remain a debugging surface, but not the main board rule.

## Required Deliverables

Per-case artifacts:

- rollout `summary.json`
- rollout scene artifact
- detector bundle with per-frame masks and force vectors
- detector summary with first-collision notes

Main visualization artifact:

- one promoted self-collision-OFF `2 x 2` board video with the fixed panel semantics
- optional `4x` slow-motion supplement using the same board semantics

Validation artifacts:

- validator outputs
- QA verdict
- contact sheet or sampled frames
- artifact-validator pass

## Acceptance Criteria

Detector KPI:

- first-collision detector is deterministic and saved
- both geometry and force-active rigid contact are recorded
- displayed node set matches the force-active collision set

Force-semantics KPI:

- penalty panels show rigid-collision force only
- total panels show the full resultant force
- direction, magnitude, and color scale stay consistent across cases

Visualization KPI:

- the main board is not trigger-only or top-k-only
- cloth and rigid target remain readable through pre-contact, first contact, and post-contact development
- a viewer can understand the difference between box and bunny without reading code

Contract KPI:

- promoted run follows the artifact contract
- validators pass
- task/status/current-status surfaces all point to the same promoted run

## Current State

Committed authority lives in:

- `results_meta/tasks/bunny_penetration_force_diagnostic.json`

The promoted board under `20260401_013500_realtime_allcolliding_2x2_v5` now
uses:

- self-collision OFF
- only `box_control` and `bunny_baseline`
- all-colliding-node display
- target-only penalty-force re-evaluation

Historical force-mechanism evidence remains useful, but the current meeting
surface is the stricter `2 x 2` board.

## Definition Of Done

The task is done only when:

- the promoted run remains reproducible and clearly labeled
- the board, validators, and bundle pointers stay aligned
- docs/status/current-status surfaces all point at the same promoted run
- the promoted run can be reused in slides without extra manual explanation
