# Bridge Demos And Diagnostics

## Purpose

Document the major experiment families and the diagnostic tools used to reason
about them.

## Demo Families

### Cloth vs Bunny / Box

Main scripts:

- `demo_cloth_bunny_drop_without_self_contact.py`
- `demo_cloth_box_drop_with_self_contact.py`
- `demo_cloth_bunny_realtime_viewer.py`

Main questions:

- particle-shape contact
- bunny penetration
- self-collision mismatch
- force diagnostics

### Rope vs Bunny / Multi-Rope / Sloth

Main scripts:

- `demo_rope_bunny_drop.py`
- `demo_two_ropes_ground_contact.py`
- `demo_two_ropes_ground_contact_box.py`
- `demo_rope_sloth_ground_contact.py`

Main questions:

- deformable-rigid interaction
- cross-object particle contact
- pair filtering
- shared rigid support

### Robot + Deformable

Main scripts:

- `demo_robot_rope_franka.py`
- `demo_rope_control_realtime_viewer.py`

Main questions:

- controlled rigid-body actuation
- two-way robot/deformable interaction
- realtime viewer behavior

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

Current purpose:

- isolate a trigger substep
- split internal vs external contributions
- compare geometry-contact and force-contact evidence
- export machine-readable diagnostic artifacts

### Performance Profiling

Current main script:

- `demo_cloth_bunny_realtime_viewer.py`

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
