> status: historical
> canonical_replacement: `docs/bridge/tasks/markdown_harness_maintenance_upgrade.md`
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-01`
> review_interval: `90d`
> update_rule: `Do not update for current work; keep only as predecessor context for the current markdown-harness maintenance task.`
> notes: Historical predecessor cleanup task. The current active maintenance surface is `markdown_harness_maintenance_upgrade`.

# Task: Markdown Truthfulness Cleanup

## Question

Which Markdown surfaces in the repo control plane still sound current,
authoritative, or operational when they are actually stale, duplicated,
deprecated, historical, or only local convenience pointers?

## Why It Matters

This repo now depends on Markdown as part of the agent control system.
If a stale page sounds live, a future agent can update the wrong surface,
repeat superseded work, or cite the wrong run as current.

## Current Status

- Initial fail-closed cleanup pass completed on `2026-04-01`
- This task is now predecessor context rather than the live maintenance surface:
  - one canonical source per concept
  - explicit deprecated-pointer stubs
  - explicit historical archives
  - generated inventory and cleanup reports
  - mechanical lint for future drift

## Code Entry Points

- Canonical docs:
  - `AGENTS.md`
  - `docs/README.md`
  - `docs/bridge/current_status.md`
  - `docs/bridge/experiment_index.md`
  - `docs/generated/harness_audit.md`
  - `docs/generated/harness_deprecations.md`
- Results authority:
  - `results_meta/README.md`
  - `results_meta/INDEX.md`
  - `results_meta/LATEST.md`
  - `results_meta/tasks/*.json`
- Enforcement:
  - `scripts/lint_harness_consistency.py`
  - `.codex/hooks/`

## Canonical Commands

```bash
python scripts/generate_md_inventory.py
python scripts/lint_harness_consistency.py
rg -n --glob '*.md' 'authoritative|current|latest|promoted|best run|final' docs tasks plans results_meta .
```

## Required Artifacts

- `docs/generated/md_inventory.md`
- `docs/generated/md_inventory.json`
- `docs/generated/md_cleanup_report.md`
- `docs/generated/md_orphans.md`
- `docs/generated/md_deprecation_matrix.md`
- updated canonical / deprecated / historical Markdown surfaces
- updated lint / hook discipline

## Success Criteria

- every control-plane Markdown file is classified as canonical,
  deprecated-pointer, historical, generated, or delete-candidate
- retired root singleton docs are absent or explicit stubs
- active tasks keep one clean task/spec/plan/implement/status chain
- `docs/bridge/current_status.md` and active task status pages agree with
  `results_meta/` on authoritative run meaning
- deprecated and historical files are unmistakably marked
- markdown drift becomes mechanically lint-detectable

## Open Questions

- Which non-indexed dated one-off task chains should remain as historical files
  in place versus being moved later into a dedicated archive subtree?
- How strict should the lint be about non-canonical local pointer terms such as
  `BEST_RUN.md` inside historical notes?

## Related Pages

- [harness_engineering_upgrade.md](./harness_engineering_upgrade.md)
- [slide_deck_overhaul.md](../../bridge/tasks/slide_deck_overhaul.md)
