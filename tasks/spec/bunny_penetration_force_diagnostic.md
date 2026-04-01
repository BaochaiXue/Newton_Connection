# Task Spec: Bunny Penetration Force Diagnostic

## Goal

Reopen the bunny penetration visualization task under a stricter meeting spec
and replace the old accepted final artifact with:

- a self-collision-OFF real-time `2 x 2` board
- only `cloth + box` and `cloth + bunny`
- all currently colliding cloth mass nodes in the main board
- fixed panel semantics:
  - `box penalty`
  - `box total`
  - `bunny penalty`
  - `bunny total`

## Constraints

- Do not modify `Newton/newton/`
- Keep all implementation in bridge/demo/scripts/report code
- Do not accept trigger-only or top-k-only visualization as success
- Do not treat the historical accepted run as the final meeting artifact
- Do not drift into rope, self-collision transfer, robot, or any unrelated
  scene

## Inputs

- task page:
  `docs/bridge/tasks/bunny_penetration_force_diagnostic.md`
- supporting presentation page:
  `docs/bridge/tasks/video_presentation_quality.md`
- main demo:
  `Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py`
- helper scripts:
  `scripts/run_bunny_force_case.py`
  `scripts/validate_bunny_force_visualization.py`
  `scripts/validate_experiment_artifacts.py`

## Required Outputs

- fresh promoted run under:
  `results/bunny_force_visualization/runs/<timestamp>_realtime_allcolliding_2x2_v1/`
- per-case rollout + detector bundles for:
  - `box_control`
  - `bunny_baseline`
- final `2 x 2` board MP4
- run-local `README.md`
- run-local `command.sh`
- run-local `summary.json`
- QA outputs and validator verdict
- updated bundle pointers only if the new run passes validation

## Done When

- the old accepted force package is clearly marked as superseded for meeting use
- a deterministic first-collision detector exists and is saved per frame
- the displayed node set is the force-active rigid-contact set
- penalty force and total force use strict documented definitions
- the final board runs from rollout start to `1.0 s` after first collision
- the board follows the exact requested panel semantics
- the board is meeting-readable
- validators pass
