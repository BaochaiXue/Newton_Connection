# Plan: self_collision_transfer

## Goal

Drive self-collision work to one explicit engineering decision.

Current engineering milestone: land a shared strict bridge-side `phystwin`
contact stack for the PhysTwin-native cloth self-collision case without
changing any default `off` behavior.

## Constraints

- no Newton core edits
- use box-support as the main decision scene
- keep bunny as a sanity check, not the primary decision scene
- strict `phystwin` parity is limited to pairwise self-collision plus implicit
  `z=0` ground-plane contact
- cloth+box `phystwin` must fail fast instead of silently mixing box contact

## Milestones

1. run the controlled box decision matrix
2. land the shared strict `phystwin` bridge stack and wire it into the importer
3. keep cloth+box `phystwin` explicitly unsupported while preserving `off/native/custom`
4. run sanity-check and parity-regression passes on the selected mode
5. write the final decision summary

## Validation

- the task ends in A, B, or C
- decision evidence is slide-ready

## Notes

- Backfilled during the harness upgrade so the active task set has a full chain.
