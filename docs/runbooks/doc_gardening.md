# Doc Gardening Runbook

This runbook is the standard closeout flow for Markdown truth surfaces.

Use it whenever a task or result surface is:

- renamed
- deprecated
- archived
- promoted
- superseded

## Rule

Markdown truthfulness is part of the harness control system.

If a file sounds authoritative, it must be one of:

- canonical
- deprecated pointer stub
- historical record
- generated surface

Do not leave an ambiguous live-looking fourth state.

## Closeout Flow

1. Update the task status file.
2. Update the canonical task page if the task question, scope, or state changed.
3. If the slug or surface changed, add or update the deprecation marker:
   - top-of-file metadata block with:
     - `status`
     - `canonical_replacement`
     - `owner_surface`
     - `last_reviewed`
     - `notes`
4. Move completed plans out of `plans/active/` into `plans/completed/`.
5. Update `docs/generated/harness_deprecations.md` if the change adds a new deprecated or historical family.
6. If authoritative result meaning changed, update:
   - `results_meta/tasks/<task_slug>.json`
   - `results_meta/INDEX.md`
   - `results_meta/LATEST.md`
7. Refresh the Markdown truth inventory:

```bash
python scripts/generate_md_inventory.py
```

8. Run the harness/doc lint:

```bash
python scripts/lint_harness_consistency.py
```

9. Refresh local-only bundle pointers optionally, but never treat them as the canonical committed truth.

## Status Markers

### Canonical

Canonical files may sound authoritative.

### Deprecated Pointer Stub

Keep a deprecated file only when discoverability still matters.

Required properties:

- strong top-of-file metadata block
- explicit `status: deprecated`
- explicit canonical replacement
- explicit note that no new current state belongs there

### Historical

Historical files may preserve details, but they must stop sounding live.

Required properties:

- strong top-of-file metadata block
- `status: historical`
- canonical replacement if one exists, otherwise `none`
- note explaining why the file still exists

### Generated

Generated files must say how they are regenerated.

## Common Failure Modes

- completed plans left in `plans/active/`
- review-only task files that still say `In progress`
- local-only bundle README/BEST_RUN pages that sound more authoritative than `results_meta/`
- stale `current_status.md` claims that contradict registry state
- deprecated task aliases left without a replacement path
