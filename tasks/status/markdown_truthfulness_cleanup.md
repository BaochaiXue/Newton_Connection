# Status: markdown_truthfulness_cleanup

## Current State

Completed. The control-plane Markdown layer now converges on explicit
canonical / deprecated-pointer / historical / generated states, and the
mechanical inventory + lint agree with the filesystem.

## Last Completed Step

Unified the inventory scope, added tracked local-only results/status surfaces
to the generated inventory, relinked canonical README/runbook entrypoints so
there are no orphan canonical control-plane docs, regenerated the markdown
truth artifacts, and reran lint to `PASS`.

## Next Step

No immediate execution step. Future markdown rename/deprecate/archive work
should follow `docs/runbooks/doc_gardening.md` and rerun the same inventory +
lint flow.

## Blocking Issues

- None

## Artifact Paths

- `docs/generated/`
- `docs/runbooks/doc_gardening.md`
- `results_meta/`
- `docs/generated/md_inventory.md`
- `docs/generated/md_inventory.json`
- `docs/generated/md_cleanup_report.md`
- `docs/generated/md_orphans.md`
- `docs/generated/md_deprecation_matrix.md`
