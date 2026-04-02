> status: canonical
> canonical_replacement: none
> owner_surface: `task_execution`
> last_reviewed: `2026-04-01`
> review_interval: `30d`
> update_rule: `Update when handoff policy or the set of tasks expected to use structured handoffs changes.`
> notes: Handoffs are selectively load-bearing. They are required for multi-session or blocked tasks, not as universal boilerplate.

# Task Handoffs

This directory stores structured state transfers for long-running work.

Use a handoff when a task is likely to span sessions, agents, or context
resets.

Each handoff should let a fresh agent resume without reconstructing hidden chat
state.

## Current Usage Status

- current status: `partially load-bearing`
- required when:
  - a task spans sessions
  - a task is blocked
  - a task has a nontrivial artifact tree that should not be rediscovered from chat
- not required for every short task

Use:

- [_handoff_template.md](./_handoff_template.md)
- [markdown_harness_maintenance_upgrade.md](./markdown_harness_maintenance_upgrade.md)
