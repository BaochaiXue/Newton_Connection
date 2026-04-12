> status: active
> owner_surface: `bridge_code_structure_cleanup`
> last_reviewed: `2026-04-11`
> review_interval: `7d`
> update_rule: `Update when the active implementation order, validation set, or remaining compatibility debt changes.`

# Plan: bridge_code_structure_cleanup

## Goal

Complete the cloth+bunny family package reorg, align the canonical entrypoints
with Newton-style example structure, and keep one round of top-level shim
compatibility for existing scripts.

## Constraints

- no edits under `Newton/newton/`
- no physics-semantic changes
- keep force-diagnostic workflows functional during the transition
- avoid touching rope/MPM families beyond passive import compatibility

## Milestones

1. establish `Newton/phystwin_bridge/demos/cloth_bunny/` as the canonical package
2. move cloth+bunny helper and entrypoint code under the new package
3. add typed config/runtime/diagnostic wrapper surfaces and slim canonical offline CLI
4. replace top-level cloth+bunny files with thin compatibility shims
5. update wrapper scripts to use package APIs instead of private helpers
6. sync task/docs/current-status surfaces and regenerate required workflow metadata

## Validation

- `python -m py_compile Newton/phystwin_bridge/demos/cloth_bunny/*.py Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py Newton/phystwin_bridge/demos/cloth_bunny_common.py Newton/phystwin_bridge/demos/cloth_bunny_force_viz.py Newton/phystwin_bridge/demos/cloth_bunny_outputs.py scripts/run_bunny_force_case.py scripts/render_bunny_force_artifacts.py scripts/build_bunny_collision_force_bundle.py`
- `python Newton/phystwin_bridge/demos/cloth_bunny/offline.py --help`
- `python Newton/phystwin_bridge/demos/cloth_bunny/example.py --help`
- `python Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py --help`
- `python Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py --help`
- `python Newton/phystwin_bridge/demos/cloth_bunny/example.py --viewer null --num-frames 2 --mode off --out-dir tmp/cloth_bunny_example_smoke`
- `python Newton/phystwin_bridge/demos/cloth_bunny/offline.py --out-dir tmp/cloth_bunny_offline_smoke --frames 2 --skip-render`
- `python scripts/run_bunny_force_case.py --out-dir tmp/cloth_bunny_script_smoke --frames 2 --substeps 1 --skip-render`

## Remaining Work

- reduce how much heavy logic still lives in `cloth_bunny/offline.py`
- consider the next extraction pass for force-diagnostic internals if we want a smaller runtime module
