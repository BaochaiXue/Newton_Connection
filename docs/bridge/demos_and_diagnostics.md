> status: active
> canonical_replacement: none
> owner_surface: `bridge_demo_map`
> last_reviewed: `2026-04-09`
> review_interval: `30d`
> update_rule: `Update when a bridge demo family or diagnostic family becomes active, historical, or renamed.`
> notes: Short map of current demo families and shared diagnostics. Retired demo lines should be marked historical instead of described as active.

# Bridge Demos And Diagnostics

## Purpose

Document the major experiment families and the diagnostic tools used to reason
about them.

## Demo Families

### Cloth vs Bunny / Box

Main scripts:

- canonical package: `Newton/phystwin_bridge/demos/cloth_bunny/`
- `demo_cloth_bunny_drop_without_self_contact.py`
- `demo_cloth_box_drop_with_self_contact.py`
- `demo_cloth_bunny_realtime_viewer.py`

Layout note:

- `cloth_bunny/offline.py` and `cloth_bunny/example.py` are now the canonical
  cloth+bunny entrypoints
- the old top-level cloth+bunny files remain as transition shims for scripts
  and muscle memory

Main questions:

- particle-shape contact
- bunny penetration
- self-collision mismatch
- force diagnostics

### Rope vs Bunny / Multi-Rope / Sloth

Main scripts:

- canonical package skeleton: `Newton/phystwin_bridge/demos/rope/`
- `demo_rope_bunny_drop.py`
- `demo_two_ropes_ground_contact.py`
- `demo_two_ropes_ground_contact_box.py`
- `demo_rope_sloth_ground_contact.py`

Layout note:

- `rope/common.py` now owns the small shared helper implementation
- the package entrypoints currently delegate to the top-level `demo_rope_*`
  modules so active commands keep the same behavior while migration continues

Main questions:

- deformable-rigid interaction
- cross-object particle contact
- pair filtering
- shared rigid support

### Historical Robot + Deformable Line

- retired on `2026-04-09`
- canonical retrospective:
  - `docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`
- preserved only as historical evidence, not as a current demo family

### MPM / Sand

Main scripts:

- `demo_sloth_sand_one_way_mpm.py`
- `demo_sloth_sand_two_way_mpm.py`
- `demo_zebra_sand_one_way_mpm.py`

Main questions:

- one-way vs two-way coupling
- proxy collider strategy
- performance and visual clarity

## Diagnostic Families

### Force Diagnostic

Current main script:

- `demo_cloth_bunny_drop_without_self_contact.py`
- canonical package path: `Newton/phystwin_bridge/demos/cloth_bunny/diagnostics.py`

Current purpose:

- isolate a trigger substep
- split internal vs external contributions
- compare geometry-contact and force-contact evidence
- export machine-readable diagnostic artifacts

### Performance Profiling

Current main script:

- `demo_rope_control_realtime_viewer.py`

Current purpose:

- disable rendering
- measure no-render step timing
- separate collision, solver, and render interpretations

### Rollout Storage / Post-Processing

Main helper:

- `rollout_storage.py`

Current purpose:

- standardize saved rollouts and downstream analyses

## Output Philosophy

A good bridge demo should produce:

- scene/state artifact
- summary artifact
- render artifact when relevant
- diagnostic artifact when investigating a failure mode

## Open Questions

- Which diagnostics should be promoted into shared utilities?
- Which experiment families still rely too much on ad hoc script-local logic?
