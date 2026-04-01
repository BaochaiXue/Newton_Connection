# Bridge IR And Import

## Purpose

Document the contract between PhysTwin-side outputs and Newton-side
reconstruction.

## Main Files

- `Newton/phystwin_bridge/tools/core/export_ir.py`
- `Newton/phystwin_bridge/tools/core/newton_import_ir.py`

## What The IR Needs To Carry

At minimum, the bridge must preserve enough information to rebuild a deformable
object in Newton:

- particle positions `x0`
- particle velocities `v0`
- particle masses
- collision / contact radius related fields
- spring edges
- spring rest lengths
- spring stiffness / damping related fields
- controller metadata when the demo keeps controllers

## Import Responsibilities

The import layer is responsible for:

- device resolution
- coordinate convention handling
- gravity/up-axis interpretation
- particle construction
- spring construction
- ground-plane insertion when requested
- rigid-body / mesh or box insertion when requested
- contact-parameter mapping

## Scaling Semantics

One of the project's most important bridge-level ideas is that mass scaling
should not be treated as an isolated knob. In several demos, the bridge
deliberately exposes unified scaling concepts so mass and spring/contact-related
parameters can remain physically interpretable.

Representative code paths:

- `cloth_bunny_common.py`
- `rope_demo_common.py`
- demo-specific scaling logic in the main scripts

## Documentation Rule

Whenever a new field becomes required by import or diagnostics, update this page
and say:

- producer
- consumer
- meaning
- scaling behavior
- whether it is optional or mandatory
