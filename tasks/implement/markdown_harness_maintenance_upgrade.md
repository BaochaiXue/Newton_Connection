> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-11`
> review_interval: `14d`
> update_rule: `Update when the execution sequence or canonical commands change.`
> notes: Runbook for the current markdown/control-plane maintenance pass, including progressive-disclosure hardening, root hygiene, and reporting-discipline hardening.

# Implement: markdown_harness_maintenance_upgrade

## Preconditions

- Read `AGENTS.md`, `docs/README.md`, and `TODO.md`
- Read `docs/bridge/tasks/README.md` and the active markdown-harness task page
- Read current markdown inventory, cleanup, and deprecation ledgers
- Treat `results_meta/` as the committed authority for result meaning

## Canonical Commands

```bash
python scripts/generate_md_inventory.py
python scripts/lint_harness_consistency.py
python scripts/sync_results_registry.py
python scripts/demote_results_markdown.py --dry-run
git ls-files | awk -F/ '{print $1}' | sort -u
rg -n --glob '*.md' 'authoritative|current|latest|promoted|best|final|canonical' docs tasks plans results_meta results Newton/phystwin_bridge/results
rg -n 'docs/archive/tasks|meeting_20260401_rope_profiling_rebuild' docs tasks plans
```

## Step Sequence

1. audit misleading or overgrown markdown surfaces
2. compress active indexes into maps and route history through archive hubs
3. move or ignore root-level tracked clutter so repo entry surfaces stay obvious
4. align local result surfaces with `results_meta/` and quarantine deep bundle indexing to approved entry surfaces
5. demote deep local `results/` Markdown into `.txt` browsing files while preserving one family-root `README.md` per family
6. trim/realign canonical dashboards and task/status routing
7. add or refresh review metadata on touched canonical control-plane pages
8. narrow hooks to write-strict/read-loose behavior
9. encode outcome-first user reporting in AGENTS/runbooks/hooks
10. regenerate ledgers and rerun lint

## Validation

- generated inventory covers all in-scope control-plane markdown files
- active indexes no longer enumerate archived task pages inline
- tracked root files outside the allowlist no longer compete at repo root
- read-only inspection of watched harness paths is no longer blocked by hook path matches alone
- `results/` keeps only family-root `README.md` files as Markdown entry surfaces
- `current_status.md` is short enough to function as a dashboard
- no local result pointer still sounds canonical without registry backing
- no completed historical task chain remains in an active execution directory
- no historical bridge task page remains in `docs/bridge/tasks/`
- reporting rules now steer future agents toward outcomes instead of process-only summaries
