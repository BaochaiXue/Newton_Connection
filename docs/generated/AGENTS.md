# Generated Docs Rules

This subtree stores generated or machine-maintained control-plane artifacts.

## Rule

- Prefer regenerating these files over hand-editing them.
- If a generated file is committed, document the script that refreshes it.
- Generated files may be authoritative only when their regeneration path is
  explicit and linted.

## Current High-Signal Surfaces

- `md_inventory.md`
- `md_inventory.json`
- `md_cleanup_report.md`
- `md_orphans.md`
- `md_deprecation_matrix.md`
- `md_staleness_report.md`
- `task_surface_matrix.md`

## Historical / Compatibility Files

- `harness_audit.md` is a historical snapshot, not a live operating ledger.
- `harness_deprecations.md` is a deprecated compatibility stub; update
  `md_deprecation_matrix.md` instead of expanding it.
