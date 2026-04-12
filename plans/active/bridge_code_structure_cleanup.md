> status: active
> canonical_replacement: none
> owner_surface: `bridge_code_structure_cleanup`
> last_reviewed: `2026-04-11`
> review_interval: `14d`
> update_rule: `Update when milestones or validation steps change materially.`
> notes: Active plan for bounded bridge-layer structure cleanup.

# Plan: bridge_code_structure_cleanup

## Goal

Make one bridge hotspot materially easier to read by extracting pure helper
logic into a dedicated module.

## Constraints

- no edits under `Newton/newton/`
- no semantic physics changes in the same pass
- keep the new structure demo-local unless there is a clear shared need

## Milestones

1. choose the highest-value extraction boundary inside the largest bridge demo
2. move pure visualization/helper logic into a dedicated module
3. validate imports and syntax
4. record the new structure and the next cleanup target

## Validation

- `python -m py_compile Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py Newton/phystwin_bridge/demos/cloth_bunny_force_viz.py`

## Notes

- first target is the cloth+bunny force-visualization helper cluster
