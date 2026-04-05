# Scope Decision: robot_rope_franka_semiimplicit_oneway

Last updated: 2026-04-04

## In Scope

- native Newton Franka
- native Newton tabletop
- PhysTwin -> Newton rope
- deformable rope interaction under `SolverSemiImplicit`
- readable one-way robot -> rope interaction
- direct finger preferred if it stays honest

## Out Of Scope

- robot-table physical blocking
- full two-way coupling
- self-collision parity with PhysTwin
- any Newton core change

## Path Policy

- `Path A` preferred:
  - accepted direct-finger tabletop baseline
  - actual finger-box contact remains the proof surface
- `Path B` fallback only if needed:
  - promoted visible rigid tool baseline
  - explicitly tool-mediated claim

## Truth Policy

- visible contactor must equal the actual physical contactor
- rope render thickness must match rope physical contact thickness
- `ee_contact_radius` and related proxy radii remain diagnostic-only
- no hidden helper
- no overclaim beyond one-way SemiImplicit deformable interaction
