> status: active
> owner_surface: `bridge_code_structure_cleanup`
> last_reviewed: `2026-04-11`
> review_interval: `7d`
> update_rule: `Update when the canonical cloth+bunny package boundary, public API, or validation contract changes.`

# Spec: bridge_code_structure_cleanup

## Goal

Restructure the cloth+bunny bridge/demo line into a dedicated family package
that is easier to read, closer to Newton official example organization, and no
longer centered on one giant top-level demo file.

## Non-Goals

- editing `Newton/newton/`
- changing the cloth+bunny physics semantics in the same pass
- broad rope/MPM family cleanup in the same milestone

## Inputs

- `docs/bridge/tasks/bridge_code_structure_cleanup.md`
- `Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py`
- `Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py`
- wrapper scripts under `scripts/` that depend on cloth+bunny internals

## Outputs

- canonical package under `Newton/phystwin_bridge/demos/cloth_bunny/`
- thin legacy shims at the old top-level cloth+bunny paths
- a typed config surface and public runner surface for cloth+bunny
- updated task/docs surfaces reflecting the package-first structure

## Constraints

- behavior-preserving refactor only
- keep `Newton/newton/` read-only
- preserve legacy entrypoints for one transition pass
- move advanced force-diagnostic controls out of the canonical public CLI surface

## Done When

- canonical cloth+bunny logic lives under `demos/cloth_bunny/`
- top-level legacy demo/helper files are compatibility layers, not the main implementation
- wrapper scripts use the package API instead of private underscore helpers
- canonical and legacy `--help` entrypoints pass
- one realtime headless smoke, one offline smoke, and wrapper-script smoke coverage are recorded
