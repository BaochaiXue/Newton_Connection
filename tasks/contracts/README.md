> status: canonical
> canonical_replacement: none
> owner_surface: `task_execution`
> last_reviewed: `2026-04-11`
> review_interval: `30d`
> update_rule: `Update when contract policy or the set of tasks that are expected to use contracts changes.`
> notes: Contracts are selectively load-bearing. They are required for the repo's explicit high-risk, multi-session, or result-bearing workflow class, not for every task by default.

# Task Contracts

This directory stores milestone-level contracts for non-trivial tasks.

Use a contract when a task needs a bounded acceptance target before major
implementation starts.

## Purpose

- define what "done" means for the next milestone
- make builder/evaluator expectations explicit
- reduce ambiguous reopen / rebuild cycles

## Current Usage Status

- current status: `partially load-bearing`
- required for:
  - high-risk result-bearing tasks
  - blocked result-bearing tasks
  - meeting-facing deck rebuilds with bounded acceptance
  - multi-session structural refactors
  - long-running maintenance passes that should not drift in scope
- not required for every lightweight task

Current required-contract exemplars:

- `markdown_harness_maintenance_upgrade`
- `slide_deck_overhaul`
- `bridge_code_structure_cleanup`
- `bunny_penetration_force_diagnostic`
- `rope_perf_apples_to_apples`
- `self_collision_transfer`

Use:

- [_contract_template.md](./_contract_template.md)
- [markdown_harness_maintenance_upgrade.md](./markdown_harness_maintenance_upgrade.md)
- [slide_deck_overhaul.md](./slide_deck_overhaul.md)
- [bridge_code_structure_cleanup.md](./bridge_code_structure_cleanup.md)
- [bunny_penetration_force_diagnostic.md](./bunny_penetration_force_diagnostic.md)
- [rope_perf_apples_to_apples.md](./rope_perf_apples_to_apples.md)
- [self_collision_transfer.md](./self_collision_transfer.md)
