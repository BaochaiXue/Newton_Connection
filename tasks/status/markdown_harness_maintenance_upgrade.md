> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-01`
> review_interval: `7d`
> update_rule: `Update after each meaningful cleanup milestone and after final validation.`
> notes: Live status log for the current markdown/control-plane maintenance pass.

# Status: markdown_harness_maintenance_upgrade

## Current State

In progress.

## Last Completed Step

- Audited the current markdown/control plane and confirmed:
  - `docs/bridge/current_status.md` is overgrown for a dashboard role
  - execution-layer historical files still live beside active task files
  - `generate_md_inventory.py` vs `generate_md_truth_inventory.py` still reads like two public stories
  - `robot_rope_franka_tabletop_push_hero` local bundle surfaces still sound too canonical
  - at least one active task page (`interactive_playground_profiling`) still carries stale interpretation text

## Next Step

- finish moving historical execution files
- rewrite the main dashboard/index surfaces
- normalize inventory/lint/public-entrypoint behavior

## Blocking Issues

- none; current work is control-plane cleanup, not experiment reruns
