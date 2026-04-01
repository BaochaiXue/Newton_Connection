# Implement: markdown_truthfulness_cleanup

## Preconditions

- Read the canonical harness/docs surfaces named in the task spec
- Audit Markdown state before deleting or stubbing anything

## Canonical Commands

```bash
python scripts/lint_harness_consistency.py
rg --files -g '*.md' .
rg -n 'authoritative|current|latest|promoted|best run|final' . -g '*.md'
```

## Step Sequence

1. Inventory Markdown control-plane surfaces and classify them
2. Record contradictions between filesystem state, docs, and `results_meta/`
3. Convert misleading surfaces into canonical docs, deprecated stubs, or
   historical/archive pages
4. Generate Markdown cleanup artifacts and deprecation/orphan reports
5. Extend lint/hooks/runbook coverage so the same drift becomes mechanically
   detectable
6. Validate and update task status

## Validation

- root singleton docs are absent or explicit stubs only
- no canonical Markdown surface contains machine-local absolute paths
- `current_status.md` and `results_meta/` agree on run authority
- every deprecated/historical file has a banner and replacement/migration note
- inventory/report artifacts exist and lint passes

## Output Paths

- `docs/generated/md_inventory.md`
- `docs/generated/md_inventory.json`
- `docs/generated/md_cleanup_report.md`
- `docs/generated/md_orphans.md`
- `docs/generated/md_deprecation_matrix.md`
- `docs/runbooks/doc_gardening.md`
