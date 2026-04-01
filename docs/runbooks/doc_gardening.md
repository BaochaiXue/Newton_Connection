# Doc Gardening Runbook

## Purpose

Use this runbook whenever a task, result, or Markdown control-plane surface is:

- renamed
- deprecated
- archived
- promoted
- superseded

Markdown truthfulness is part of the harness. Do not treat it as optional
cleanup after the fact.

## Metadata Convention

For non-trivial deprecated or historical Markdown files, add a top-of-file
front matter block:

```yaml
---
status: deprecated
canonical_replacement: docs/bridge/tasks/example.md
owner_surface: example_task
last_reviewed: 2026-04-01
notes: Kept only as a discoverability stub. Do not use as source of truth.
---
```

Allowed `status` values for control-plane Markdown:

- `active`
- `deprecated`
- `historical`
- `generated`

## Closeout Flow

1. Update the relevant task status page.
2. If the change affects result meaning, update `results_meta/tasks/<task_slug>.json`.
3. Run `python scripts/sync_results_registry.py` when a registry entry changed.
4. Add or update deprecation / historical metadata and a strong banner.
5. Refresh the Markdown inventory:
   - `python scripts/generate_md_inventory.py`
6. Run the harness/doc lint:
   - `python scripts/lint_harness_consistency.py`
7. Refresh only secondary local pointers optionally:
   - `BEST_RUN.md`
   - `LATEST_SUCCESS.txt`
   - `LATEST_ATTEMPT.txt`

## Rename Rule

When renaming a task slug:

- keep one canonical slug,
- convert the old slug family into deprecated pointers,
- update `docs/bridge/tasks/README.md`,
- update task-chain links,
- update `results_meta/` if the task has committed result meaning.

## Promotion Rule

When promoting a result:

- `results_meta/` is the committed authority,
- task status pages may summarize the promotion,
- local bundle pointers are secondary convenience surfaces only.

## Archive Rule

If a file is no longer live but still useful:

- either keep it in place as a deprecated stub,
- or move it under `docs/archive/` as a historical record.

Do not leave a fourth ambiguous state.
