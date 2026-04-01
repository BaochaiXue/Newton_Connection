# PhysTwin Architecture In This Project

## Purpose

Explain PhysTwin at the level that matters for the bridge project.

## High-Level Role

PhysTwin is the deformable-object source model. It is responsible for producing
object geometry/state and associated parameters from video/data pipelines. In the
current project, PhysTwin is the origin of:

- object particle positions / initial state
- object mass distribution
- spring topology
- spring parameters
- controller trajectories when present
- auxiliary reconstruction artifacts

## Layered View

### Upstream PhysTwin Layer

This includes:

- video/data processing
- reconstruction
- parameter optimization
- PhysTwin-native simulation and evaluation

### Export Layer

This is the boundary where PhysTwin products are converted into a stricter form
that the bridge can carry into Newton.

Representative code:

- `PhysTwin/export_topology.py`
- `Newton/phystwin_bridge/tools/core/export_ir.py`

### Bridge Consumption Layer

The bridge consumes the exported data and rebuilds a Newton-native model.

Representative code:

- `Newton/phystwin_bridge/tools/core/newton_import_ir.py`
- `Newton/phystwin_bridge/demos/*.py`

## Why This Matters

Most arguments in current meetings are not about "what PhysTwin is" in the
paper sense. They are about whether the PhysTwin outputs are being imported into
Newton in a physically meaningful way. So architecture documentation should keep
the export/import boundary explicit.

## Code Entry Points

- `PhysTwin/README.md`
- `PhysTwin/export_topology.py`
- `Newton/phystwin_bridge/tools/core/export_ir.py`

## Open Questions

- Which PhysTwin fields should become official bridge contracts?
- Which fields depend on case-specific preprocessing and should stay internal?
