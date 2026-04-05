# Implement: native_robot_physical_blocking_minimal

## Canonical Inputs

- `docs/bridge/tasks/native_robot_physical_blocking_minimal.md`
- `docs/bridge/tasks/robot_rope_franka_physical_blocking.md`
- `tasks/status/robot_rope_franka_physical_blocking.md`
- `diagnostics/bridge_layer_limit_proof.md`
- `diagnostics/minimal_core_change_proposal.md`
- `scripts/run_robot_rope_franka_physical_blocking.sh`
- `scripts/validate_robot_rope_franka_physical_blocking.py`
- `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`

## Expected Working Steps

1. Build a strict geometry-truth inventory before changing behavior.
2. Reproduce the bridge-layer limit or clear it quickly and honestly.
3. If needed, implement the smallest native actuation fix.
4. Build Stage 0 native rigid-only blocking micro-benchmark.
5. Add Stage-0-specific geometry/blocking validators.
6. Only after Stage 0 passes, reintroduce the rope for Stage 1.

## Output Contract

- `diagnostics/geometry_truth_inventory.md`
- Stage-0 run-local blocking artifacts
- Stage-1 rope-integrated artifacts only after Stage 0 passes
- `diagnostics/minimal_native_core_change_report.md` if `Newton/newton/`
  changes

## Guardrails

- Preserve the accepted direct-finger and visible-tool baselines
- Do not fake blocking with a clamp or render mismatch
- Keep any Newton core change minimal and fully documented
