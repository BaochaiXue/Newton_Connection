# Spec: self_collision_transfer

## Goal

Finish the self-collision path as a bounded engineering decision task.

The current implementation focus is the shared bridge-side strict `phystwin`
contact stack for the PhysTwin-native cloth parity scene.

## Non-Goals

- Open-ended experimentation without a final A/B/C recommendation
- Newton core rewrites

## Inputs

- `docs/bridge/tasks/self_collision_transfer.md`
- self-collision demos, tools, and parity validators
- controlled box-matrix outputs and sanity-check demos

## Outputs

- explicit decision table
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

## Done When

- the task ends with one explicit self-collision recommendation
- parity/sanity-check evidence is recorded
- the selected mode has a slide-ready summary
- the shared strict `phystwin` stack is reusable from both the main importer and
  the dedicated `newton_import_ir_phystwin.py` wrapper
