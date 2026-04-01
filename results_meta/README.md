# Results Metadata Mirror

This subtree stores committed metadata for authoritative local result bundles.

## Purpose

Heavy binaries may remain ignored under local `results/` roots, but the meaning
of those results must remain legible from committed repo state.

Use this subtree to answer:

1. Which run or bundle is currently authoritative for a task?
2. What exact claim boundary does it support?
3. Why did it pass?
4. Which prior runs were rejected or superseded, and why?

## Structure

- `schema.md`
  - field definitions and expectations
- `_result_entry_template.json`
  - template for new task entries
- `tasks/<task_slug>.json`
  - committed machine-readable metadata per task
- [INDEX.md](./INDEX.md)
  - generated summary across tasks
- [LATEST.md](./LATEST.md)
  - generated latest-update view across tasks
- [DEPRECATED.md](./DEPRECATED.md)
  - local-only pointer surfaces that are no longer canonical
- [AGENTS.md](./AGENTS.md)
  - local rules for the committed results registry

## Regeneration

After editing any `tasks/*.json` entry, run:

```bash
python scripts/sync_results_registry.py
```

Then run:

```bash
python scripts/lint_harness_consistency.py
```

## Rule

Do not claim a run is authoritative in task/status/current-status docs unless
the corresponding `results_meta/tasks/<task_slug>.json` entry is updated.
