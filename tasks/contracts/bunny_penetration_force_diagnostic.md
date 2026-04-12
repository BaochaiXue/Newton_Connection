# Contract: bunny_penetration_force_diagnostic / preserved board authority

## Goal

Keep the promoted bunny `2 x 2` board as a stable, clearly bounded
meeting-facing result surface.

## Scope Boundary

- In scope:
  - preserving the promoted board contract
  - future updates to detector semantics, media packaging, or bundle authority
  - keeping slides/status/results_meta aligned
- Out of scope:
  - unrelated bunny geometry experiments
  - robot/self-collision work
  - Newton core changes

## Required Inputs

- `docs/bridge/tasks/bunny_penetration_force_diagnostic.md`
- `tasks/status/bunny_penetration_force_diagnostic.md`
- `results_meta/tasks/bunny_penetration_force_diagnostic.json`

## Required Outputs

- stable promoted bundle meaning
- aligned task/status/registry surfaces
- evaluator-backed media bundle if the promoted board is changed

## Hard-Fail Conditions

- the promoted board contract changes without registry/status alignment
- automatic artifact checks are treated as final acceptance without verdict evidence
- a new run is promoted without preserving the all-colliding-node board semantics

## Acceptance Criteria

- the promoted `v5` bundle remains the current authority unless a stronger run is explicitly promoted
- task page, status page, and `results_meta` agree on the same claim boundary
- verdict evidence exists for any newly promoted board bundle

## Evaluator Evidence Required

- validator command(s):
  - `python scripts/validate_bunny_force_visualization.py <run_dir>`
  - `python scripts/validate_experiment_artifacts.py <run_dir>`
- artifact paths:
  - `results/bunny_force_visualization/README.md`
  - `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5/`
- skeptical review required: yes

## Next Command After Acceptance

```bash
python scripts/validate_bunny_force_visualization.py results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5
```
