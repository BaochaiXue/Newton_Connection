# Spec: self_collision_transfer

## Goal

Finish the self-collision path as a bounded engineering decision task.

The current implementation focus is the shared bridge-side strict `phystwin`
contact stack for the PhysTwin-native cloth parity scene, plus a controlled
bridge-side `2 x 2` RMSE matrix that independently varies self-collision law
and ground-contact law on that same cloth+implicit-ground reference.

## Non-Goals

- Open-ended experimentation without a final A/B/C recommendation
- Newton core rewrites

## Inputs

- `docs/bridge/tasks/self_collision_transfer.md`
- self-collision demos, tools, and parity validators
- controlled box-matrix outputs and sanity-check demos

## Outputs

- explicit decision table
- controlled `2 x 2` cloth+ground RMSE matrix
- canonical bridge-side matrix runner with fairness check
- selected mode and rationale
- sanity-check and parity-regression evidence
- a reusable bridge-side `phystwin` contact-stack module
- explicit guardrails that keep cloth+box `phystwin` unsupported instead of
  silently mixing Newton box contact semantics

## Constraints

- keep the decision bounded to the defined A/B/C outcomes
- preserve the OFF-baseline mainline
- no `Newton/newton/` edits
- strict `phystwin` scope in v1 is self-collision + implicit `z=0` ground plane
- for the controlled law-isolation matrix, keep the scene fixed to the
  PhysTwin-native cloth + implicit-ground reference case

## Done When

- the task ends with one explicit self-collision recommendation
- the controlled `2 x 2` cloth+ground matrix is recorded with a fairness check
- parity/sanity-check evidence is recorded
- the selected mode has a slide-ready summary
- the shared strict `phystwin` stack is reusable from both the main importer and
  the dedicated `newton_import_ir_phystwin.py` wrapper
