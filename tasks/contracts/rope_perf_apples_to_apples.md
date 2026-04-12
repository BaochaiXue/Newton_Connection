# Contract: rope_perf_apples_to_apples / preserve benchmark authority

## Goal

Keep the same-case no-render rope replay benchmark as the canonical performance
authority surface unless a future benchmark update is explicitly promoted.

## Scope Boundary

- In scope:
  - preserving the benchmark claim boundary
  - future updates to methodology, attribution, or promoted evidence
  - keeping task/status/results_meta aligned
- Out of scope:
  - optimization implementation itself
  - viewer-only practical context as a replacement for the benchmark

## Required Inputs

- `docs/bridge/tasks/rope_perf_apples_to_apples.md`
- `tasks/status/rope_perf_apples_to_apples.md`
- `results_meta/tasks/rope_perf_apples_to_apples.json`

## Required Outputs

- stable benchmark authority
- aligned task/status/registry wording
- verdict-backed benchmark notes if a new result is promoted

## Hard-Fail Conditions

- viewer-facing context regrows into the committed benchmark scope
- a new promoted run is claimed without registry alignment
- optimization claims get promoted before the apples-to-apples benchmark changes

## Acceptance Criteria

- the no-render same-case rope replay scope remains the committed authority
- task page, status page, and `results_meta` agree on the same benchmark claim
- supporting viewer rows remain clearly secondary

## Evaluator Evidence Required

- validator command(s):
  - benchmark bundle verdicts recorded under `results/rope_perf_apples_to_apples/`
- artifact paths:
  - `results_meta/tasks/rope_perf_apples_to_apples.json`
  - `results/rope_perf_apples_to_apples/BEST_EVIDENCE.md`
- skeptical review required: no

## Next Command After Acceptance

```bash
python scripts/generate_md_inventory.py
```
