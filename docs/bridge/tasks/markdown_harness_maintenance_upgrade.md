> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-01`
> review_interval: `14d`
> update_rule: `Update when markdown authority, task taxonomy, inventory generation, or lint policy changes.`
> notes: Current canonical harness-maintenance task for markdown truthfulness, active-vs-historical separation, and registry-backed result authority.

# Task: Markdown Harness Maintenance Upgrade

## Question

How do we tighten the existing harness so Markdown truth surfaces stay
fail-closed, active execution directories stop accumulating historical
residue, and committed result authority remains legible without trusting local
bundle pointers?

## Why It Matters

This repo already has a real harness. The remaining risk is not missing
structure; it is semantic drift:

- dashboards growing into ledgers
- historical files living beside active task chains
- local bundle READMEs sounding canonical
- inventory/lint scripts detecting presence but missing stale meaning

## Current Scope

- markdown truthfulness and stale-doc garbage collection
- active-vs-historical task separation
- `results_meta/` completeness and local-only pointer hygiene
- markdown inventory / staleness / task-surface generation
- lint / hook reinforcement for ongoing maintenance

## Canonical Entry Points

- `docs/bridge/current_status.md`
- `docs/bridge/tasks/README.md`
- `tasks/README.md`
- `results_meta/README.md`
- `docs/runbooks/doc_gardening.md`
- `scripts/generate_md_inventory.py`
- `scripts/lint_harness_consistency.py`

## Required Outputs

- refreshed markdown inventory surfaces under `docs/generated/`
- new `md_staleness_report.md`
- new `task_surface_matrix.md`
- current-status dashboard split/trim
- active-vs-historical execution-directory cleanup
- stronger markdown maintenance policy and enforcement

## Success Criteria

- one active harness-maintenance task chain exists for the current pass
- completed predecessor harness tasks no longer sit in active execution dirs
- `docs/bridge/current_status.md` behaves like a dashboard/map again
- tracked local result surfaces are explicitly local-only or registry-backed
- generated inventory, staleness, and task-surface ledgers match the filesystem
- lint catches markdown truth drift mechanically

## Related Pages

- [interactive_playground_profiling.md](./interactive_playground_profiling.md)
- [rope_perf_apples_to_apples.md](./rope_perf_apples_to_apples.md)
- [robot_rope_franka_tabletop_push_hero.md](./robot_rope_franka_tabletop_push_hero.md)
