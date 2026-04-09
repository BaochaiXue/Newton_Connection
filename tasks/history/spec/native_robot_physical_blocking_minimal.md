# Spec: native_robot_physical_blocking_minimal

## Goal

Establish the smallest truthful native Newton robot-table physical-blocking
baseline first, then only after that succeeds reintroduce the rope while
preserving the same actuation and geometry truth.

## Scope

- Stage 0: native Franka + native rigid tabletop + simplest honest visible
  robot-side contactor + no rope
- Stage 1: same truthful robot-side geometry and actuation path + add the
  PhysTwin -> Newton rope back
- Geometry-truth validation, physical-blocking validation, and full-video review
- Minimal Newton core/API change only if the existing bridge-layer limit proof
  still reproduces cleanly

## Non-Goals

- Declaring success from the old readable tabletop baseline
- Claiming direct finger contact if the honest contactor is a mounted rigid tool
- Camera-only, trajectory-only, or render-only fixes
- Any large Newton core refactor

## Constraints

- Preserve accepted `robot_rope_franka_tabletop_push_hero`
- Preserve accepted `robot_visible_rigid_tool_baseline`
- Keep every visible geometry consistent with the actual physical geometry
- No hidden helper, invisible extension, or fake shell
- Same-rollout rule for hero/debug/validation
- If `Newton/newton/` must change, keep the diff minimal, isolated, and
  documented

## Inputs

- `docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
- `docs/bridge/tasks/robot_visible_rigid_tool_baseline.md`
- `docs/bridge/tasks/robot_rope_franka_physical_blocking.md`
- `diagnostics/minimal_core_change_proposal.md`
- `scripts/run_robot_rope_franka_physical_blocking.sh`
- `scripts/validate_robot_rope_franka_physical_blocking.py`
- `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`

## Outputs

- new task-local diagnosis board and status surfaces
- `diagnostics/geometry_truth_inventory.md`
- Stage-0 minimal blocking bundle and validator outputs
- Stage-1 rope reintegration bundle only after Stage 0 passes
- `diagnostics/minimal_native_core_change_report.md` if `Newton/newton/`
  changes

## Done When

- Stage 0 proves truthful native robot-table blocking
- Stage 1 reintroduces the rope without losing truthful blocking or geometry
  honesty
- validators and full-video review pass
- docs/status/results metadata remain truthful
