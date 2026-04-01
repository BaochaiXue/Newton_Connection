# Implement: markdown_truthfulness_cleanup

## Preconditions

- Read `AGENTS.md`, `docs/README.md`, and `TODO.md`
- Read the current harness audit/deprecation surfaces before changing them
- Treat `results_meta/` as the committed source of truth for current run meaning

## Canonical Commands

```bash
python scripts/generate_md_inventory.py
python scripts/lint_harness_consistency.py
rg -n --glob '*.md' 'authoritative|current|latest|promoted|best run|final' docs tasks plans results_meta .
rg -n --glob '*.md' '/home/' docs tasks plans results_meta .
```

## Step Sequence

1. Build the Markdown inventory and classify in-scope files
2. Fix misleading surfaces by making them canonical, deprecated-pointer, or
   historical
3. Align current-status and task status pages with `results_meta/`
4. Add runbook, lint, and hook enforcement for future Markdown drift
5. Regenerate inventory/report artifacts and update task status

## Validation

- generated inventory covers every in-scope Markdown file
- no canonical surface contains machine-local absolute paths
- no active task keeps a competing stale alias alive
- root singleton docs are absent or explicit stubs only

## Output Paths

- `docs/generated/md_inventory.md`
- `docs/generated/md_inventory.json`
- `docs/generated/md_cleanup_report.md`
- `docs/generated/md_orphans.md`
- `docs/generated/md_deprecation_matrix.md`
- `docs/runbooks/doc_gardening.md`
