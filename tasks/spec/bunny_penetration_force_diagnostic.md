# Task Spec: Bunny Penetration Force Diagnostic

## Goal

Make the bunny penetration visualization package meeting-ready under the
stricter full-process criteria:

- phenomenon video shows approach -> contact -> penetration growth -> max
  penetration -> landing / settle or rebound
- force mechanism video preserves both full-cloth global context and a readable
  local force panel
- the baseline bunny case passes visual QA before propagating to the 4-case
  matrix

## Constraints

- Do not modify `Newton/newton/`
- Keep all implementation in bridge/demo/scripts/report code
- Do not accept short trigger-centric clips as success
- Do not accept file existence as success; videos must pass QA and visual review

## Inputs

- task page:
  `docs/bridge/tasks/bunny_penetration_force_diagnostic.md`
- main demo:
  `Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py`
- helper scripts:
  `scripts/run_bunny_force_case.py`
  `scripts/render_bunny_force_artifacts.py`
  `scripts/validate_bunny_force_visualization.py`

## Required Outputs

- canonical run under `results/bunny_force_visualization/runs/<timestamp>_<slug>/`
- accepted `bunny_baseline` phenomenon + full-process force video
- QA contact sheets and verdict
- propagated 4-case package only after baseline passes
- updated `INDEX.md`, `LATEST_ATTEMPT.txt`, and `LATEST_SUCCESS.txt`

## Done When

- bunny baseline passes all strict gates, including duration
- full-process force video is not trigger-only and keeps the full cloth visible
- the 4-case package exists and is organized under one canonical run
- the result folder README explains why the run passes
