# Contract: bridge_code_structure_cleanup / demo-family package reorg

## Scope Boundary

- in scope:
  - `Newton/phystwin_bridge/demos/cloth_bunny/` as the new canonical cloth+bunny package
  - `Newton/phystwin_bridge/demos/rope/` as the new rope-family package skeleton
  - cloth+bunny top-level shims
  - rope top-level shims / package entrypoint shims
  - cloth+bunny wrapper scripts under `scripts/`
  - rope wrapper scripts under `scripts/` when their import paths are migrated
  - task/docs/current-status updates required by the package reorg
- out of scope:
  - edits under `Newton/newton/`
  - full rope behavior rewrites before the package skeleton is validated
  - MPM family reorganization
  - semantic physics changes

## Hard-Fail Conditions

- canonical cloth+bunny logic still primarily lives in the old top-level files
- the legacy shims stop accepting the prior `--help` surfaces
- wrapper scripts still depend on underscore-private helper names from the old demo module
- canonical offline/example entrypoints cannot be executed directly as files
- rope package entrypoints change CLI defaults or simulation behavior during the
  skeleton pass

## Acceptance Criteria

- canonical cloth+bunny code is package-first under `demos/cloth_bunny/`
- top-level cloth+bunny files are thin wrappers only
- a typed config surface exists for cloth+bunny
- a public runner surface exists as `run_offline_case(...) -> ClothBunnyArtifacts`
- a Newton-style example class exists as `ClothBunnyExample`
- rope shared helpers have a package home under `demos/rope/common.py`
- top-level `rope_demo_common.py` remains as a compatibility wrapper
- rope package entrypoints exist for the current active rope demos without
  changing their implementation semantics
- compile/help/smoke validation passes for canonical and legacy paths

## Evaluator Evidence Required

- compile pass across package, shims, and wrapper scripts
- `--help` for canonical offline/example and both legacy shims
- one realtime headless smoke
- one offline skip-render smoke
- wrapper-script smoke coverage using package APIs
- compile pass for the rope package and legacy rope common shim
- `--help` for at least the rope controller package entrypoint and its legacy
  top-level path

## Exact Next Command After Acceptance

```bash
python scripts/generate_md_inventory.py
python scripts/lint_harness_consistency.py
```
