> status: historical
> canonical_replacement: `../../decisions/2026-04-09_robot_ps_interaction_retirement.md`
> owner_surface: `native_robot_physical_blocking_minimal`
> last_reviewed: `2026-04-09`
> review_interval: `90d`
> update_rule: `Historical evidence only. Do not record new active state here.`
> notes: Archived Stage-0 native blocking study after the 2026-04-09 retirement decision.

# Task: Native Robot Physical Blocking Minimal

## Question

What is the smallest truthful native Newton setup that proves an articulated
robot-side contactor can be physically blocked by a rigid tabletop under
`SolverSemiImplicit`, with visible geometry matching the real collision
geometry?

## Why It Matters

The existing readable tabletop baselines establish honest contact stories, but
they do not prove articulated robot-table physical blocking. This task narrows
the scope to the simplest native truth test:

- native Newton Franka
- native Newton rigid tabletop
- simplest honest visible rigid contactor
- same geometry in render and solver
- no rope until blocking itself is proven

## Current Status

- Newly opened on `2026-04-04`.
- It preserves:
  - the accepted tabletop finger-push baseline
  - the accepted visible-tool intermediary baseline
  - the currently blocked stronger rope-integrated physical-blocking task
- It is the new minimal native workstream for proving real blocking first.

## Code Entry Points

- Main demo:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Current stronger-task wrapper/validator:
  - `scripts/run_robot_rope_franka_physical_blocking.sh`
  - `scripts/validate_robot_rope_franka_physical_blocking.py`
- Existing stronger-task diagnostics:
  - `diagnostics/bridge_layer_limit_proof.md`
  - `diagnostics/minimal_core_change_proposal.md`

## Canonical Commands

- Existing stronger-task audit surfaces:
  - `scripts/run_robot_rope_franka_physical_blocking.sh`
  - `scripts/validate_robot_rope_franka_physical_blocking.py`
- New minimal Stage-0 wrapper/validator should live under `scripts/` once the
  task reaches implementation.

## Required Artifacts

- `diagnostics/geometry_truth_inventory.md`
- Stage-0 candidate bundle with:
  - `hero_presentation.mp4`
  - `hero_debug.mp4`
  - `validation_camera.mp4`
  - `geometry_overlay_debug.mp4` or equivalent
  - `robot_table_contact_report.json`
  - `ee_target_vs_actual_report.json`
  - `penetration_report.json`
  - `geometry_truth_report.md`
- Stage-1 rope reintegration bundle only after Stage 0 passes

## Success Criteria

- Stage 0 proves robot-table physical blocking under truthful geometry
- visible contactor and actual physical contactor are the same geometry
- same-rollout hero/debug/validation support the same blocking story
- only after Stage 0 passes, Stage 1 reintroduces the rope without regressing
  geometry truth or blocking truth

## Open Questions

- Is a bridge/demo-level actuation fix still sufficient, or is the smallest
  honest path now a minimal Newton core/API change?
- Which robot-side geometry is the simplest honest Stage-0 contactor:
  explicit rigid crossbar/capsule or direct finger colliders?

## Related Pages

- [robot_rope_franka_physical_blocking.md](./robot_rope_franka_physical_blocking.md)
- [robot_visible_rigid_tool_baseline.md](./robot_visible_rigid_tool_baseline.md)
- [robot_rope_franka_tabletop_push_hero.md](./robot_rope_franka_tabletop_push_hero.md)
