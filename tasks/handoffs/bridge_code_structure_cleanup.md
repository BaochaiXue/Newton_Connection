# Handoff: bridge_code_structure_cleanup

## Resume Point

The cloth+bunny line has been moved into `Newton/phystwin_bridge/demos/cloth_bunny/`.
Legacy top-level files now act as compatibility shims. Wrapper scripts have
been switched to the package APIs and smoke-tested.

The rope family has started the same transition with a package skeleton under
`Newton/phystwin_bridge/demos/rope/`. This pass intentionally keeps the large
legacy top-level rope demo scripts as the behavior owners.

## Canonical Files

- `Newton/phystwin_bridge/demos/cloth_bunny/offline.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/example.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/scene.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/render.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/outputs.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/config.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/runtime.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/diagnostics.py`
- `Newton/phystwin_bridge/demos/rope/common.py`
- `Newton/phystwin_bridge/demos/rope/control_viewer.py`
- `Newton/phystwin_bridge/demos/rope/bunny_drop.py`
- `Newton/phystwin_bridge/demos/rope/two_ropes_ground_contact.py`
- `Newton/phystwin_bridge/demos/rope/sloth_ground_contact.py`

## What Is Already Done

- canonical package path exists and imports cleanly
- canonical offline runner has a slim CLI
- canonical example exposes `ClothBunnyExample`
- legacy top-level paths still run `--help`
- wrapper scripts now use package modules instead of importing the old demo
  monolith directly
- runtime validation generated smoke outputs under `tmp/`
- `rope_demo_common.py` is now a compatibility wrapper over `rope.common`
- rope package entrypoint shims exist for the active rope demos, delegating to
  the existing top-level modules

## What Still Looks Ugly

- `cloth_bunny/offline.py` still contains a large amount of force-diagnostic
  machinery
- `runtime.py` and `diagnostics.py` are public wrappers today, not yet the full
  owner of all underlying logic
- the rope package entrypoints still delegate to large top-level scripts
- rope profiling/output/runtime logic has not yet been split into package-owned
  modules

## Recommended Next Pass

1. validate the rope package skeleton and legacy rope paths
2. move pure rope profiling/output helper logic into package-owned modules
3. keep top-level `demo_rope_*` files as wrappers until script references have
   migrated
4. continue shrinking cloth+bunny force-diagnostic internals in parallel only if
   needed for active bunny work

## Validation Snapshot

```bash
python -m py_compile \
  Newton/phystwin_bridge/demos/cloth_bunny/*.py \
  Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py \
  Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py \
  Newton/phystwin_bridge/demos/cloth_bunny_common.py \
  Newton/phystwin_bridge/demos/cloth_bunny_force_viz.py \
  Newton/phystwin_bridge/demos/cloth_bunny_outputs.py \
  scripts/run_bunny_force_case.py \
  scripts/render_bunny_force_artifacts.py \
  scripts/build_bunny_collision_force_bundle.py

python Newton/phystwin_bridge/demos/cloth_bunny/example.py --viewer null --num-frames 2 --mode off --out-dir tmp/cloth_bunny_example_smoke
python Newton/phystwin_bridge/demos/cloth_bunny/offline.py --out-dir tmp/cloth_bunny_offline_smoke --frames 2 --skip-render
python scripts/run_bunny_force_case.py --out-dir tmp/cloth_bunny_script_smoke --frames 2 --substeps 1 --skip-render
python scripts/render_bunny_force_artifacts.py --bundle tmp/cloth_bunny_force_bundle_build_case/force_diagnostic/force_render_bundle.pkl --force-dump-dir tmp/cloth_bunny_force_artifacts_smoke
python scripts/build_bunny_collision_force_bundle.py --bundle tmp/cloth_bunny_force_bundle_build_case/force_diagnostic/force_render_bundle.pkl --out-dir tmp/cloth_bunny_collision_bundle_smoke

python -m py_compile \
  Newton/phystwin_bridge/demos/rope/*.py \
  Newton/phystwin_bridge/demos/rope_demo_common.py

python Newton/phystwin_bridge/demos/rope/control_viewer.py --help
python Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py --help
```
