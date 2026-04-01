> status: canonical
> canonical_replacement: none
> owner_surface: `results_registry`
> last_reviewed: `2026-04-01`
> review_interval: `30d`
> update_rule: `Update when local-only pointer surfaces are added, retired, or re-scoped relative to results_meta.`
> notes: Canonical deprecation ledger for result-authority surfaces that must no longer sound committed-truth.

# Results Metadata Deprecations

Updated: 2026-04-01

This page records local results surfaces that may remain useful, but are no
longer the canonical committed truth.

## Secondary / Local-Only Result Surfaces

- `results/README.md`
- `results/bunny_force_visualization/README.md`
- `results/bunny_force_visualization/INDEX.md`
- `results/bunny_force_visualization/LATEST_ATTEMPT.txt`
- `results/bunny_force_visualization/LATEST_SUCCESS.txt`
- `results/robot_deformable_demo/README.md`
- `results/robot_deformable_demo/BEST_RUN.md`
- `results/robot_deformable_demo/LEGACY_CANDIDATES.md`
- `results/native_robot_rope_drop_release/README.md`
- `results/native_robot_rope_drop_release/BEST_RUN.md`
- `results/native_robot_rope_drop_release/LATEST_ATTEMPT.txt`
- `results/native_robot_rope_drop_release/LATEST_SUCCESS.txt`
- `results/rope_perf_apples_to_apples/README.md`
- `results/rope_perf_apples_to_apples/BEST_EVIDENCE.md`
- `Newton/phystwin_bridge/results/robot_rope_franka/README.md`
- `Newton/phystwin_bridge/results/robot_rope_franka/manifest.json`
- `Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/README.md`
- `Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/manifest.json`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260330_205935_4fdef39/README.md`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/README.md`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/FINAL_STATUS.md`

## Canonical Replacement

- `results_meta/tasks/*.json`
- `results_meta/INDEX.md`
- `results_meta/LATEST.md`

## Migration Rule

When a task promotes, supersedes, or blocks a run:

1. update the task status file
2. update `results_meta/tasks/<task_slug>.json`
3. run `python scripts/sync_results_registry.py`
4. run `python scripts/generate_md_inventory.py`
5. run `python scripts/lint_harness_consistency.py`
6. optionally refresh local bundle pointers for convenience
