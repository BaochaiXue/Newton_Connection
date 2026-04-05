> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-05`
> review_interval: `14d`
> update_rule: `Update when scope, constraints, or done criteria for the current markdown-maintenance pass change.`
> notes: Bounded spec for the current harness-maintenance upgrade; includes truthful user-facing reporting as part of harness enforcement.

# Spec: markdown_harness_maintenance_upgrade

## Goal

Upgrade the repo's existing markdown/control-plane harness so stale or
historical surfaces cannot plausibly masquerade as current truth, and so
future Codex updates report outcomes instead of bookkeeping.

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
- historical bridge task pages routed through `docs/archive/tasks/`
- refreshed generated markdown ledgers
- stronger lint/hook policy for markdown drift
- explicit outcome-first reporting policy for user-facing agent summaries
- outcome-first reporting contract encoded in durable repo instructions

## Constraints

- Keep `Newton/newton/` read-only
- Preserve historical value, but not in live-looking neighborhoods
- Treat `results_meta/` as the only committed authority for result meaning

## Done When

- active and historical task artifacts are separated intentionally
- current-status, task status pages, and `results_meta/` agree on authority
- generator/lint docs name one public inventory entrypoint
- active canonical task pages expose review metadata
- markdown maintenance becomes part of normal closeout instead of one-off cleanup
- future agent reports are steered toward outcomes instead of housekeeping
- user-facing Codex summaries are mechanically steered toward changes, resolved problems, findings, artifact pointers, and next step
