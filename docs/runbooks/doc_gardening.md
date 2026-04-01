# Markdown Maintenance Runbook

Use this runbook whenever a Markdown control-plane surface is renamed,
deprecated, archived, promoted, or superseded.

## Core Rule

Markdown truthfulness is part of the harness. When the filesystem and the docs
disagree, make them converge immediately.

## Closeout Flow

1. Update the task status file.
2. Update the canonical replacement surface.
3. Add or refresh the deprecated/historical banner if the old file remains.
4. Refresh `docs/generated/harness_deprecations.md` when the deprecation set changes.
5. Update `results_meta/` if run meaning changed.
6. Run `python scripts/sync_results_registry.py` when registry JSON changed.
7. Run `python scripts/generate_md_inventory.py`.
8. Run `python scripts/lint_harness_consistency.py`.
9. Refresh local bundle pointers only if they still add local convenience.

## Required Metadata For Deprecated / Historical Files

At the top of the file, expose:

- `status`
- `canonical_replacement`
- `owner_surface`
- `last_reviewed`
- `notes`

## Delete vs Stub vs Archive

- Delete:
  - only when the file is redundant, reproducible, unreferenced, and not historically useful
- Stub:
  - when the old path still matters for discoverability
- Archive:
  - when the file remains historically useful but should stop living in a live-looking location
