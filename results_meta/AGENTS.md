# Results Metadata Rules

This subtree is the committed metadata mirror for authoritative local result
bundles whose heavy artifacts may remain outside git.

## Canonical Rule

Authoritative claim meaning must not live only in ignored local binaries.

Use this subtree as the first committed source of truth for:

- current authoritative run or bundle per task
- claim boundary
- why a run passed
- why older runs were superseded
- where the local heavy artifacts live

## Expected Surfaces

- `README.md`
- `schema.md`
- `_result_entry_template.json`
- `INDEX.md`
- `LATEST.md`
- `DEPRECATED.md`
- `tasks/<task_slug>.json`

## Path Discipline

- Use repo-relative paths.
- Treat bundle-local `BEST_RUN.md`, `LATEST_SUCCESS.txt`, and similar files as
  secondary/local-only unless explicitly promoted here.
