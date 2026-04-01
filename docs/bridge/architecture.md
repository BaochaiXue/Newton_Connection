# Bridge Architecture

## Purpose

Explain the project-specific runtime architecture from PhysTwin outputs to Newton
experiments.

## High-Level Flow

1. PhysTwin produces deformable-object state and related parameters.
2. The bridge exports a strict IR-like package.
3. The bridge imports that package into a native Newton model.
4. Demo scripts simulate, render, diagnose, and summarize results.

## Main Layers

### Export Layer

Transforms PhysTwin-side products into a bridge-consumable representation.

Main files:

- `Newton/phystwin_bridge/tools/core/export_ir.py`

### Import / Reconstruction Layer

Builds native Newton objects from exported fields.

Main files:

- `Newton/phystwin_bridge/tools/core/newton_import_ir.py`
- `Newton/phystwin_bridge/demos/bridge_bootstrap.py`

### Demo Composition Layer

Assembles a specific scene and research question:

- cloth vs bunny
- rope vs bunny
- robot vs rope
- multi-deformable contact
- one-way / two-way MPM

Main files:

- `Newton/phystwin_bridge/demos/*.py`

### Diagnostics Layer

Captures evidence for:

- contact mechanisms
- force decomposition
- performance profiling
- rollout comparisons

Main files:

- `Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py`
- `Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py`
- `Newton/phystwin_bridge/demos/rollout_storage.py`

## Core Bridge Design Choices

- Keep Newton core read-only.
- Prefer bridge-layer reconstruction and overrides.
- Keep object-only and controller-preserving modes separate.
- Expose research knobs explicitly through CLI.
- Save diagnostic artifacts as files, not just console output.

## Current Architectural Tension

The bridge tries to do two things at once:

- preserve PhysTwin semantics closely enough for meaningful transfer
- exploit Newton-native runtime features such as viewers, contact, MPM, and robot examples

Many research questions arise exactly at that boundary.
