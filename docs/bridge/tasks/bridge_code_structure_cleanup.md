> status: active
> canonical_replacement: none
> owner_surface: `bridge_code_structure_cleanup`
> last_reviewed: `2026-04-11`
> review_interval: `7d`
> update_rule: `Update when the cloth+bunny canonical package boundary or validation story changes.`
> notes: Canonical task page for the cloth+bunny family package reorg and shim transition.

# Bridge Code Structure Cleanup

## Goal

Replace the old flat cloth+bunny demo/helper layout with a canonical
family-specific package that is easier to navigate and closer to Newton's
official example organization.

## Current Focus

- cloth+bunny only
- package-first canonical path under `Newton/phystwin_bridge/demos/cloth_bunny/`
- keep legacy top-level demo/helper files as one-pass transition shims
- keep wrapper scripts functional while moving them to public package APIs

## Current State

The canonical cloth+bunny implementation now lives under:

- `Newton/phystwin_bridge/demos/cloth_bunny/offline.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/example.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/scene.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/render.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/outputs.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/config.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/runtime.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/diagnostics.py`

The old paths are still present, but only as compatibility wrappers.

## Why This Matters

- a new reader can finally find the cloth+bunny family in one place
- the package structure is much closer to Newton's family/example layout
- scripts no longer need to couple themselves to private helper names inside
  the old demo monolith

## Validation Snapshot

- canonical `--help`:
  - `python Newton/phystwin_bridge/demos/cloth_bunny/offline.py --help`
  - `python Newton/phystwin_bridge/demos/cloth_bunny/example.py --help`
- legacy `--help`:
  - `python Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py --help`
  - `python Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py --help`
- runtime smokes:
  - `python Newton/phystwin_bridge/demos/cloth_bunny/example.py --viewer null --num-frames 2 --mode off --out-dir tmp/cloth_bunny_example_smoke`
  - `python Newton/phystwin_bridge/demos/cloth_bunny/offline.py --out-dir tmp/cloth_bunny_offline_smoke --frames 2 --skip-render`
  - `python scripts/run_bunny_force_case.py --out-dir tmp/cloth_bunny_script_smoke --frames 2 --substeps 1 --skip-render`
- force-diagnostic wrapper coverage:
  - `python scripts/render_bunny_force_artifacts.py --bundle tmp/cloth_bunny_force_bundle_build_case/force_diagnostic/force_render_bundle.pkl --force-dump-dir tmp/cloth_bunny_force_artifacts_smoke`
  - `python scripts/build_bunny_collision_force_bundle.py --bundle tmp/cloth_bunny_force_bundle_build_case/force_diagnostic/force_render_bundle.pkl --out-dir tmp/cloth_bunny_collision_bundle_smoke`

## Next Step

Reduce how much force-diagnostic machinery still lives in
`cloth_bunny/offline.py`, so `runtime.py` and `diagnostics.py` become real
owners instead of public wrapper surfaces.
