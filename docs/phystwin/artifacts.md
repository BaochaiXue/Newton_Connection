# PhysTwin Artifacts

## Purpose

Document the main data products that flow from PhysTwin into the current bridge
workflow.

## Common Artifact Types

The exact filenames vary by case, but in the current project the important
artifact classes are:

- object initial state
- topology / edge lists
- learned or optimized physical parameters
- controller trajectories
- rendered evaluation outputs

## Artifacts That Matter To The Bridge

The bridge primarily cares about data that can be reinterpreted as a native
Newton deformable model:

- particle positions `x0`
- particle velocities `v0`
- mass
- collision radius / contact distance related fields
- spring edges
- spring rest lengths
- spring stiffness / damping related fields
- controller indices / trajectories when the demo keeps controllers

## Where These Show Up In Code

- `Newton/phystwin_bridge/tools/core/export_ir.py`
- `Newton/phystwin_bridge/tools/core/newton_import_ir.py`
- `Newton/phystwin_bridge/demos/cloth_bunny_common.py`
- `Newton/phystwin_bridge/demos/rope/common.py`
- `Newton/phystwin_bridge/demos/rope_demo_common.py` as a compatibility wrapper

## Documentation Rule

Whenever we discover a new artifact that becomes important to the bridge, add it
here with:

- producer
- consumer
- meaning
- whether it is stable or provisional

## Open Questions

- Do we want a formal artifact schema page for the strict IR package?
- Which PhysTwin-side fields should be treated as optional vs required?
