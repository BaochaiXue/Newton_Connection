# Contract: self_collision_transfer / blocked parity decision surface

## Goal

Keep the reproducible self-collision comparison as a stable blocked surface
while the remaining controller-spring / rollout parity mismatch is still open.

## Scope Boundary

- In scope:
  - preserving the blocked comparison surface
  - future bridge-side fixes that may change the blocked state
  - keeping task/status/results_meta aligned
- Out of scope:
  - broad collision-stack rewrites without a bounded comparison target
  - replacing the current blocked surface with scratch notes

## Required Inputs

- `docs/bridge/tasks/self_collision_transfer.md`
- `tasks/status/self_collision_transfer.md`
- `results_meta/tasks/self_collision_transfer.json`

## Required Outputs

- stable blocked comparison surface
- aligned task/status/registry wording
- verdict-backed evidence if a future run changes the blocked state

## Hard-Fail Conditions

- reproducibility and blocker interpretation drift apart across task/status/registry
- scratch diagnostics are treated as the new blocked authority without promotion
- a future fix is claimed without comparison against the current blocked roots

## Acceptance Criteria

- the reproducible matrix root remains the committed blocked surface until a stronger run is promoted
- task page, status page, and `results_meta` agree on the blocker
- the current next-step path compares any future fix against the committed blocked roots

## Evaluator Evidence Required

- validator command(s):
  - matrix / reproducibility validators recorded under the current result root
- artifact paths:
  - `results_meta/tasks/self_collision_transfer.json`
  - `Newton/phystwin_bridge/results/ground_contact_self_collision_repro_fix_20260404_200830_aa5e607/final_verdict.json`
- skeptical review required: no

## Next Command After Acceptance

```bash
python scripts/generate_md_inventory.py
```
