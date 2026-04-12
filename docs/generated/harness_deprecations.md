# Deprecated: harness_deprecations

> status: deprecated
> canonical_replacement: `docs/generated/md_deprecation_matrix.md`
> owner_surface: `generated_docs`
> last_reviewed: `2026-04-11`
> review_interval: `90d`
> update_rule: `Keep this file as a short backward-compatibility pointer only. Do not regrow a second long-form deprecation ledger here.`
> notes: Deprecated compatibility stub. The former long-form deprecation ledger was intentionally collapsed into `md_deprecation_matrix.md`.

This path is kept only so older links continue to resolve.

Current live deprecation surface:

- `docs/generated/md_deprecation_matrix.md`

Why this file is short now:

- the old content duplicated the live deprecation matrix
- keeping two full ledgers invited drift
- future deprecation changes should update `md_deprecation_matrix.md`, then regenerate the inventory set

Current regeneration command:

```bash
python scripts/generate_md_inventory.py
```
