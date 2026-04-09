# Spec: robot_rope_franka_semiimplicit_oneway

## Goal

Establish the simplest acceptable Newton-native deformable-interaction baseline:

- native Newton Franka
- native Newton tabletop
- bridged PhysTwin rope
- deformable interaction under `SolverSemiImplicit`
- readable one-way robot -> rope interaction
- conservative claim boundary with no physical-blocking or full two-way claim

## Scope

- prefer existing accepted direct-finger tabletop baseline
- preserve accepted geometry-truth fixes
- use the visible rigid tool baseline only if direct finger is not honest/readable enough
- do not modify `Newton/newton/`

## Must Prove

1. The chosen rope/deformable interaction path uses `SolverSemiImplicit`.
2. The visible contactor is the actual physical contactor.
3. Rope render thickness matches physical contact thickness.
4. The final claim does not overreach into physical blocking or full two-way coupling.

## Done Condition

The task is done only when a complete conservative bundle exists, solver and
geometry truth are documented explicitly, and results metadata truthfully
captures the narrower one-way SemiImplicit claim.
