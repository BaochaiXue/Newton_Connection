# Task Spec: Bunny Force Visualization Full-Process Closure

## Goal

Reopen the bunny penetration visualization work under the stricter meeting
criteria and close it only when:

- the phenomenon video shows the full interpretable process,
- the force video shows the full interpretable process,
- the force video preserves both global cloth context and local force
  readability,
- the result bundle is organized so another agent can identify the latest valid
  run unambiguously.

## Constraints

- `Newton/newton/` is read-only.
- Do not accept trigger-window-only clips as final.
- Do not accept duration by frozen holds alone.
- Converge on `bunny_baseline` first, then propagate.

## Primary Code Paths

- `Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py`
- `scripts/run_bunny_force_case.py`
- `scripts/render_bunny_force_artifacts.py`
- `scripts/validate_bunny_force_visualization.py`

## Artifact Contract

Canonical root:

- `results/bunny_force_visualization/`

Per accepted run:

- `README.md`
- `manifest.json`
- `commands.sh`
- `logs/`
- `qa/`
- `artifacts/bunny_baseline/{phenomenon,force_mechanism}`

## Current Focus

Fix the canonical full-process path so the force video is composed from the
stable phenomenon render instead of relying on a second fragile force-viewer
render path.
