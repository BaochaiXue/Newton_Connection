> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-01`
> review_interval: `7d`
> update_rule: `Update after each meaningful cleanup milestone and after final validation.`
> notes: Live status log for the current markdown/control-plane maintenance pass.

# Status: markdown_harness_maintenance_upgrade

## Current State

Completed for the 2026-04-01 maintenance pass.

## Last Completed Step

- Landed the full maintenance pass:
  - trimmed `docs/bridge/current_status.md` back into a dashboard
  - made `python scripts/generate_md_inventory.py` the only public inventory entrypoint
  - refreshed `docs/generated/` with inventory, staleness, orphan, deprecation, and task-surface ledgers
  - aligned robot-tabletop local result surfaces with `results_meta/`
  - rewrote `interactive_playground_profiling` as methodology-only rather than a competing authority surface
  - tightened hooks and the `doc-gardener` skill around inventory + lint closeout
  - verified `python scripts/lint_harness_consistency.py` passes after regeneration

## Next Step

- keep this task as the active maintenance line for future markdown/control-plane follow-up
- use `docs/generated/md_staleness_report.md` and `docs/generated/task_surface_matrix.md` for routine upkeep rather than ad hoc cleanup passes

## Blocking Issues

- none for this completed maintenance pass

## Validation

- `python scripts/sync_results_registry.py`
- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
