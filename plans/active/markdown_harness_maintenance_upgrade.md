> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-01`
> review_interval: `14d`
> update_rule: `Update when milestones or validation steps change materially.`
> notes: Active plan for the current markdown/control-plane maintenance pass.

# Plan: markdown_harness_maintenance_upgrade

## Goal

Make markdown truth surfaces harder to misuse by tightening taxonomy,
authority, inventory generation, and lint enforcement.

## Constraints

- no edits under `Newton/newton/`
- do not create a parallel harness
- do not leave historical residue in active execution directories

## Milestones

1. audit markdown truth surfaces and current generator/lint behavior
2. retire predecessor task pages into `docs/archive/tasks/` and keep execution artifacts out of active dirs
3. trim `current_status.md` into a real dashboard and align result authority
4. normalize inventory generation, staleness reporting, and task-surface reporting
5. strengthen lint/hooks and regenerate ledgers
6. enforce review metadata on active canonical task pages

## Validation

- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
- `python scripts/sync_results_registry.py` if registry JSON changed

## Notes

- this task is the current canonical home for markdown-harness maintenance
- predecessor cleanup/harness tasks remain historical context only
