# Contract: markdown_harness_maintenance_upgrade / semantic-hardening-pass

## Goal

Finish the current semantic-hardening pass so the markdown/result-authority
harness is quieter, more truthful, and mechanically enforceable.

## Scope Boundary

- In scope:
  - report/actionability cleanup for generated maintenance surfaces
  - active-vs-historical task-index consistency
  - result-authority drift between local manifests and `results_meta/`
  - honest status for contract/handoff usage
- Out of scope:
  - Newton core changes
  - new experiment reruns
  - large content rewrites unrelated to harness truthfulness

## Required Inputs

- `docs/generated/md_inventory.*`
- `docs/generated/md_cleanup_report.md`
- `docs/generated/md_staleness_report.md`
- `docs/generated/task_surface_matrix.md`
- `results_meta/tasks/*.json`
- `docs/bridge/current_status.md`
- active task status pages affected by authority drift

## Required Outputs

- regenerated generated ledgers
- corrected robot-tabletop local manifest authority surfaces
- explicit active-task indexing for `remote_interaction_root_cause`
- at least one real contract and one real handoff artifact under the task-execution scaffolding

## Hard-Fail Conditions

- `results_meta/` and generated task/result summaries disagree on the current run
- a local result surface still overclaims committed authority
- `md_staleness_report.md` remains a permanently noisy red wall
- the lint still passes only because the report scope is hidden instead of documented

## Acceptance Criteria

- `python scripts/generate_md_inventory.py` regenerates without ambiguity
- `python scripts/lint_harness_consistency.py` passes
- `robot_rope_franka` local manifests no longer drift from `results_meta/`
- `remote_interaction_root_cause` is either indexed as active or no longer lives as a hidden active chain
- `task_surface_matrix.md` shows real contract/handoff usage for at least one active task

## Evaluator Evidence Required

- validator command(s):
  - `python scripts/generate_md_inventory.py`
  - `python scripts/sync_results_registry.py` if registry JSON changes
  - `python scripts/lint_harness_consistency.py`
- artifact paths:
  - `docs/generated/md_cleanup_report.md`
  - `docs/generated/md_staleness_report.md`
  - `docs/generated/task_surface_matrix.md`
- skeptical review required: no

## Next Command After Acceptance

```bash
python scripts/generate_md_inventory.py && python scripts/lint_harness_consistency.py
```
