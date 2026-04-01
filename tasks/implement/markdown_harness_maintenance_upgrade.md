> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-01`
> review_interval: `14d`
> update_rule: `Update when the execution sequence or canonical commands change.`
> notes: Runbook for the current markdown/control-plane maintenance pass.

# Implement: markdown_harness_maintenance_upgrade

## Preconditions

- Read `AGENTS.md`, `docs/README.md`, and `TODO.md`
- Read current markdown inventory, cleanup, and deprecation ledgers
- Treat `results_meta/` as the committed authority for result meaning

## Canonical Commands

```bash
python scripts/generate_md_inventory.py
python scripts/lint_harness_consistency.py
python scripts/sync_results_registry.py
rg -n --glob '*.md' 'authoritative|current|latest|promoted|best|final|canonical' docs tasks plans results_meta results Newton/phystwin_bridge/results
```

## Step Sequence

1. audit misleading or overgrown markdown surfaces
2. move historical execution docs out of active directories
3. trim/realign canonical dashboards and indexes
4. align local result surfaces with `results_meta/`
5. regenerate ledgers and rerun lint

## Validation

- generated inventory covers all in-scope control-plane markdown files
- `current_status.md` is short enough to function as a dashboard
- no local result pointer still sounds canonical without registry backing
- no completed historical task chain remains in an active execution directory
