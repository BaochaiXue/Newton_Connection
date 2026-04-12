# Contract: bridge_code_structure_cleanup / cloth+bunny package reorg

## Scope Boundary

- in scope:
  - `Newton/phystwin_bridge/demos/cloth_bunny/` as the new canonical cloth+bunny package
  - cloth+bunny top-level shims
  - cloth+bunny wrapper scripts under `scripts/`
  - task/docs/current-status updates required by the package reorg
- out of scope:
  - edits under `Newton/newton/`
  - rope/MPM family reorganization
  - semantic physics changes

## Hard-Fail Conditions

- canonical cloth+bunny logic still primarily lives in the old top-level files
- the legacy shims stop accepting the prior `--help` surfaces
- wrapper scripts still depend on underscore-private helper names from the old demo module
- canonical offline/example entrypoints cannot be executed directly as files

## Acceptance Criteria

- canonical cloth+bunny code is package-first under `demos/cloth_bunny/`
- top-level cloth+bunny files are thin wrappers only
- a typed config surface exists for cloth+bunny
- a public runner surface exists as `run_offline_case(...) -> ClothBunnyArtifacts`
- a Newton-style example class exists as `ClothBunnyExample`
- compile/help/smoke validation passes for canonical and legacy paths

## Evaluator Evidence Required

- compile pass across package, shims, and wrapper scripts
- `--help` for canonical offline/example and both legacy shims
- one realtime headless smoke
- one offline skip-render smoke
- wrapper-script smoke coverage using package APIs

## Exact Next Command After Acceptance

```bash
python scripts/generate_md_inventory.py
python scripts/lint_harness_consistency.py
```
