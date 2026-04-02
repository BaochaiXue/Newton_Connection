> status: canonical
> canonical_replacement: none
> owner_surface: `task_execution`
> last_reviewed: `2026-04-01`
> review_interval: `30d`
> update_rule: `Update when contract policy or the set of tasks that are expected to use contracts changes.`
> notes: Contracts are selectively load-bearing. They are required for high-risk or expensive iteration loops, not for every task by default.

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
  - meeting-facing deck rebuilds with bounded acceptance
  - long-running maintenance passes that should not drift in scope
- not required for every lightweight task

Use:

- [_contract_template.md](./_contract_template.md)
- [markdown_harness_maintenance_upgrade.md](./markdown_harness_maintenance_upgrade.md)
