> status: active
> canonical_replacement: none
> owner_surface: `generated_docs`
> last_reviewed: `2026-04-11`
> review_interval: `30d`
> update_rule: `Update when generated control-plane files or their public regeneration command changes.`
> notes: Canonical README for in-repo generated docs. Use the public generator wrapper, not the compatibility alias.

# Generated Docs And Machine Outputs

This directory is reserved for generated documentation artifacts or machine-made
indexes that should live inside the repo.

Rules:

- Do not hand-edit generated files unless clearly marked otherwise.
- If a generated file becomes authoritative, document how it is regenerated.

Current public generated/control-plane files include:

- `md_inventory.md`
- `md_inventory.json`
- `md_cleanup_report.md`
- `md_orphans.md`
- `md_deprecation_matrix.md`
- `md_staleness_report.md`
- `task_surface_matrix.md`

Historical / compatibility leftovers:

- `harness_audit.md` keeps the original audit narrative as a historical snapshot
- `harness_deprecations.md` is now only a deprecated compatibility stub pointing at `md_deprecation_matrix.md`

Regenerate the Markdown truth artifacts with:

```bash
python scripts/generate_md_inventory.py
```

`scripts/generate_md_truth_inventory.py` remains only as a compatibility alias.
