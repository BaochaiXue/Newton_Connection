# Bridge Section

This section is the encyclopedia core for the current project.

If PhysTwin is the source model and Newton is the target simulator/runtime, the
bridge is where the actual project logic lives.

## What The Bridge Covers

- IR export/import
- object-only reconstruction
- parameter scaling rules
- demo entry points
- diagnostics
- profiling
- experiment patterns
- research-specific implementation choices

## Start Here

- [architecture.md](./architecture.md)
- [ir_and_import.md](./ir_and_import.md)
- [demos_and_diagnostics.md](./demos_and_diagnostics.md)
- [current_status.md](./current_status.md)
- [open_questions.md](./open_questions.md)
- [experiment_index.md](./experiment_index.md)
- [tasks/README.md](./tasks/README.md)

## Core Code Areas

### Tools / Core

- `Newton/phystwin_bridge/tools/core/export_ir.py`
- `Newton/phystwin_bridge/tools/core/newton_import_ir.py`
- `Newton/phystwin_bridge/tools/core/path_defaults.py`
- `Newton/phystwin_bridge/tools/core/validate_parity.py`

### Demo Bootstrap / Shared Helpers

- `Newton/phystwin_bridge/demos/bridge_bootstrap.py`
- `Newton/phystwin_bridge/demos/bridge_shared.py`
- `Newton/phystwin_bridge/demos/bridge_deformable_common.py`
- `Newton/phystwin_bridge/demos/cloth_bunny/`
  - canonical cloth+bunny family package
  - top-level `demo_cloth_bunny_*` and `cloth_bunny_*` files are transition shims
- `Newton/phystwin_bridge/demos/rope_demo_common.py`
- `Newton/phystwin_bridge/demos/rollout_storage.py`

### Kernel-Like Bridge Overrides

- `Newton/phystwin_bridge/demos/semiimplicit_bridge_kernels.py`
- `Newton/phystwin_bridge/demos/self_contact_bridge_kernels.py`

## Naming Note

There are both older `demo_*_common.py` names and newer `bridge_*` / shared
modules in the repo. When documenting a workflow, prefer the modules actually
imported by the current local demo entry points.

## Why This Section Is Primary

Most active research questions in this project are not pure PhysTwin questions
or pure Newton questions. They are bridge questions:

- what exactly gets imported?
- what gets scaled?
- which code path is native vs bridge-custom?
- which diagnostic result is trustworthy?

## Operational Pages

The encyclopedia also keeps three project-management pages inside the bridge
section so Codex and humans can share the same operational state:

- `current_status.md`
- `open_questions.md`
- `experiment_index.md`

Task-specific work should live under `tasks/`.
