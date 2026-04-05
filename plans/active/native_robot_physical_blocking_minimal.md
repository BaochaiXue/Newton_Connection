# Plan: native_robot_physical_blocking_minimal

## Goal

Prove native robot-table physical blocking first in the simplest honest scene,
then reintroduce the rope only after the blocking micro-benchmark is validated.

## Milestones

1. Create the separate minimal task chain and geometry-truth inventory.
2. Reproduce or clear the existing bridge-layer actuation limit.
3. Decide whether the smallest honest fix is bridge/demo-level or a minimal
   Newton core/API change.
4. Build Stage 0: native rigid-only blocking micro-benchmark and validate it.
5. Build Stage 1: rope reintegration with the same truthful actuation and
   geometry path.
6. Promote only if both stages pass strict geometry-truth and blocking gates.

## Validation

- geometry-truth inventory complete
- Stage-0 physical-blocking validator pass
- same-rollout hero/debug/validation pass
- no hidden helper or render/collider mismatch
- Stage-1 rope push remains honest and readable

## Notes

- The existing blocked `robot_rope_franka_physical_blocking` task remains an
  important diagnosis surface, but this new task narrows the first success gate
  to Stage 0 blocking before any rope reintegration.
