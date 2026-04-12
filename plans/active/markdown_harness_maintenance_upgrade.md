> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-11`
> review_interval: `14d`
> update_rule: `Update when milestones or validation steps change materially.`
> notes: Active plan for the current markdown/control-plane maintenance pass, including progressive disclosure, root hygiene, and outcome-first reporting enforcement.

# Plan: markdown_harness_maintenance_upgrade

## Goal

Make markdown truth surfaces harder to misuse by tightening taxonomy,
authority, progressive disclosure, root hygiene, bundle-entry quarantine,
inventory generation, lint enforcement, hook semantics, and agent reporting
discipline.

## Constraints

- no edits under `Newton/newton/`
- do not create a parallel harness
- do not leave historical residue in active execution directories
- do not mass-relocate deep bundle trees when entry-surface quarantine is enough

## Milestones

1. audit markdown truth surfaces and current generator/lint behavior
2. compress live entrypoints into maps and route history through archive hubs
3. clean root-level tracked clutter and encode a root allowlist policy
4. keep deep bundle Markdown quarantined to approved entry surfaces only
5. trim `current_status.md` into a real dashboard and align result authority
6. normalize inventory generation, staleness reporting, and task-surface reporting
7. strengthen lint/hooks with write-strict/read-loose behavior and regenerate ledgers
8. enforce review metadata and outcome-first user reporting in AGENTS/runbook/hooks

## Validation

- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
- `python scripts/sync_results_registry.py` if registry JSON changed
- read-only hook smoke checks against watched harness files and release-gated filenames

## Notes

- this task is the current canonical home for markdown-harness maintenance
- predecessor cleanup/harness tasks remain historical context only
- report the maintenance outcomes, not only the maintenance mechanics
