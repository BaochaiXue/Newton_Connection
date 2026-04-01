# Project Map

This page is the shortest possible map of the repository.

## Top-Level Directories

- `PhysTwin/`
  - Upstream PhysTwin codebase and experiments.
  - Source of reconstructed deformable-object state, training outputs, and data-processing pipelines.
- `Newton/newton/`
  - Upstream Newton simulator core.
  - Read-only in this workspace.
- `Newton/phystwin_bridge/`
  - Project-specific bridge layer between PhysTwin and Newton.
  - This is the main code area for demos, diagnostics, import/export glue, and local research experiments.
- `formal_slide/`
  - Meeting-specific slide bundles, scripts, templates, and transcript outputs.
- `tmp/`
  - Experiment outputs, profiling dumps, diagnostic snapshots, and ad hoc results.
- `docs/`
  - This encyclopedia.
- `plans/`
  - Active and completed execution plans for long-running work.
- `tasks/`
  - Execution-facing task specs, runbooks, and status logs.
- `scripts/`
  - Canonical wrapper scripts and validators.
- `.codex/`
  - Repo-local Codex control plane: config and hooks.
- `.agents/skills/`
  - Repo-local reusable Codex workflows.

## Most Important Code Roots

### PhysTwin

- `PhysTwin/README.md`
- `PhysTwin/export_topology.py`
- `PhysTwin/qqtt/`

### Newton Core

- `Newton/newton/newton/`
- `Newton/newton/newton/examples/`

### Bridge Core

- `Newton/phystwin_bridge/tools/core/export_ir.py`
- `Newton/phystwin_bridge/tools/core/newton_import_ir.py`
- `Newton/phystwin_bridge/tools/core/validate_parity.py`

### Bridge Demo Helpers

- `Newton/phystwin_bridge/demos/bridge_bootstrap.py`
- `Newton/phystwin_bridge/demos/bridge_shared.py`
- `Newton/phystwin_bridge/demos/bridge_deformable_common.py`
- `Newton/phystwin_bridge/demos/cloth_bunny_common.py`
- `Newton/phystwin_bridge/demos/rope_demo_common.py`
- `Newton/phystwin_bridge/demos/rollout_storage.py`
- `Newton/phystwin_bridge/demos/semiimplicit_bridge_kernels.py`
- `Newton/phystwin_bridge/demos/self_contact_bridge_kernels.py`

### Harness

- `AGENTS.md`
- `docs/README.md`
- `docs/runbooks/`
- `docs/evals/`
- `docs/decisions/`
- `plans/`
- `tasks/`
- `scripts/`
- `.codex/`
- `.agents/skills/`

Retired root singleton docs:

- do not recreate `Plan.md`
- do not recreate `Status.md`
- do not recreate `Prompt.md`
- do not recreate `DecisionLog.md`
- use task-local files under `docs/bridge/tasks/`, `plans/`, and `tasks/`

## Main Demo Families

- Cloth vs bunny / box
  - `demo_cloth_bunny_drop_without_self_contact.py`
  - `demo_cloth_box_drop_with_self_contact.py`
  - `demo_cloth_bunny_realtime_viewer.py`
- Rope vs bunny / rope / sloth / robot
  - `demo_rope_bunny_drop.py`
  - `demo_two_ropes_ground_contact.py`
  - `demo_two_ropes_ground_contact_box.py`
  - `demo_rope_sloth_ground_contact.py`
  - `demo_robot_rope_franka.py`
  - `demo_rope_control_realtime_viewer.py`
- MPM / sand
  - `demo_sloth_sand_one_way_mpm.py`
  - `demo_sloth_sand_two_way_mpm.py`
  - `demo_zebra_sand_one_way_mpm.py`

## Where To Edit

Allowed by project rule:

- `Newton/phystwin_bridge/`
- `docs/`
- `plans/`
- `tasks/`
- `scripts/`
- slide / transcript generation code

Not allowed by default:

- `Newton/newton/`

## How To Use This Map

Use this page only to find the right place to read next. Do not try to turn this
page into detailed design documentation; detailed explanations belong in the
topic pages under `phystwin/`, `newton/`, and `bridge/`.
