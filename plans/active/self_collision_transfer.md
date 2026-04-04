# Plan: self_collision_transfer

## Goal

Drive self-collision work to one explicit engineering decision.

Current engineering milestone: expose a fair bridge-side `2 x 2` RMSE matrix
on the PhysTwin-native cloth + implicit-ground reference case, so self-collision
law and ground-contact law can be varied independently before the next rollout
mismatch diagnosis.

## Constraints

- no Newton core edits
- keep the cloth + implicit-ground PhysTwin reference case fixed for the
  controlled RMSE matrix
- keep cloth+box and bunny as secondary scene evidence only
- strict `phystwin` parity is limited to pairwise self-collision plus implicit
  `z=0` ground-plane contact
- cloth+box `phystwin` must fail fast instead of silently mixing box contact

## Milestones

1. expose independent `self_collision_law` and `ground_contact_law` controls in the bridge layer
2. add the canonical `2 x 2` cloth+ground RMSE matrix runner with fairness check
3. run all four cases on the same strict cloth IR and record the matrix
4. use the matrix to quantify main effects and interaction before further blocker diagnosis
5. keep cloth+box `phystwin` explicitly unsupported while preserving `off/native/custom`
6. write the updated task status and blocker interpretation

## Validation

- the matrix is a fair controlled comparison
- the matrix root satisfies the artifact contract
- remaining blocker is stated against the matrix evidence, not guessed

## Notes

- Backfilled during the harness upgrade so the active task set has a full chain.
- The new matrix is not a promotion surface by itself; it is local blocked
  evidence until a new committed authority surface is chosen.
