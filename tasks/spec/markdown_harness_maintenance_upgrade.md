> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-01`
> review_interval: `14d`
> update_rule: `Update when scope, constraints, or done criteria for the current markdown-maintenance pass change.`
> notes: Bounded spec for the current harness-maintenance upgrade; supersedes broader predecessor cleanup tasks for active execution.

# Spec: markdown_harness_maintenance_upgrade

## Goal

Upgrade the repo's existing markdown/control-plane harness so stale or
historical surfaces cannot plausibly masquerade as current truth.

## Non-Goals

- Editing `Newton/newton/`
- Creating a second results registry outside `results_meta/`
- Rewriting deep local result bundles purely for archival aesthetics

## Inputs

- `AGENTS.md`
- `docs/bridge/current_status.md`
- `docs/generated/md_inventory.*`
- `docs/generated/md_cleanup_report.md`
- `results_meta/`
- `scripts/generate_md_inventory.py`
- `scripts/lint_harness_consistency.py`

## Outputs

- canonical markdown-maintenance task chain
- cleaned dashboard/index/task taxonomy surfaces
- refreshed generated markdown ledgers
- stronger lint/hook policy for markdown drift

## Constraints

- Keep `Newton/newton/` read-only
- Preserve historical value, but not in live-looking neighborhoods
- Treat `results_meta/` as the only committed authority for result meaning

## Done When

- active and historical task artifacts are separated intentionally
- current-status, task status pages, and `results_meta/` agree on authority
- generator/lint docs name one public inventory entrypoint
- markdown maintenance becomes part of normal closeout instead of one-off cleanup
