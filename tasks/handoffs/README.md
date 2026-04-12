> status: canonical
> canonical_replacement: none
> owner_surface: `task_execution`
> last_reviewed: `2026-04-11`
> review_interval: `30d`
> update_rule: `Update when handoff policy or the set of tasks expected to use structured handoffs changes.`
> notes: Handoffs are selectively load-bearing. They are required for the repo's explicit multi-session, blocked, or result-bearing workflow class, not as universal boilerplate.

# Task Handoffs

This directory stores structured state transfers for long-running work.

Use a handoff when a task is likely to span sessions, agents, or context
resets.

Each handoff should let a fresh agent resume without reconstructing hidden chat
state.

Keep the handoff outcome-first: what changed, what conclusion now holds, which
artifacts matter, and what exact command comes next.

## Current Usage Status

- current status: `partially load-bearing`
- required when:
  - a task spans sessions
  - a task is blocked
  - a task has a nontrivial artifact tree that should not be rediscovered from chat
- not required for every short task

Current required-handoff exemplars:

- `markdown_harness_maintenance_upgrade`
- `slide_deck_overhaul`
- `bridge_code_structure_cleanup`
- `bunny_penetration_force_diagnostic`
- `rope_perf_apples_to_apples`
- `self_collision_transfer`

Use:

- [_handoff_template.md](./_handoff_template.md)
- [markdown_harness_maintenance_upgrade.md](./markdown_harness_maintenance_upgrade.md)
- [slide_deck_overhaul.md](./slide_deck_overhaul.md)
- [bridge_code_structure_cleanup.md](./bridge_code_structure_cleanup.md)
- [bunny_penetration_force_diagnostic.md](./bunny_penetration_force_diagnostic.md)
- [rope_perf_apples_to_apples.md](./rope_perf_apples_to_apples.md)
- [self_collision_transfer.md](./self_collision_transfer.md)
