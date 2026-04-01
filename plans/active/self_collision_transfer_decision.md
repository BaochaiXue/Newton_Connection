# Plan: self_collision_transfer_decision

> Deprecated alias. Canonical slug: `self_collision_transfer`.  
> Canonical replacement: `plans/active/self_collision_transfer.md`.  
> Do not keep two active self-collision slugs alive.

## Goal

Produce a decision-grade self-collision task flow with measurable scene-level,
operator-level, and runtime evidence, without changing Newton core.

## Constraints

- `Newton/newton/` remains read-only
- box scene is the primary decision scene
- thresholds are provisional
- conclusion C requires operator-equivalence evidence

## Milestones

1. Add rollout-peak overlap and stability metrics to the box self-contact demo.
2. Add a matrix runner that executes the fixed box decision matrix and aggregates outputs.
3. Add a PhysTwin-style operator-equivalence verifier.
4. Validate the new scripts with compile checks and at least one lightweight equivalence run.

## Validation

- `python -m py_compile` passes for edited Python files
- matrix runner `--help` works
- equivalence verifier produces JSON output
- updated box summary contains rollout-peak fields

## Notes

- bunny remains a follow-up sanity check, not a primary decision scene
- `custom_h1` and `custom_h2` are separate rows in the matrix
