# Plan: self_collision_transfer

## Goal

Drive self-collision work to one explicit engineering decision.

Current engineering milestone: explain the `case_3_self_phystwin_ground_native`
vs `case_4_self_phystwin_ground_phystwin` gap with mechanism evidence rather
than just matrix numbers.

## Constraints

- no Newton core edits
- keep the cloth + implicit-ground PhysTwin reference case fixed for the
  controlled RMSE matrix
- keep cloth+box and bunny as secondary scene evidence only
- strict `phystwin` parity is limited to pairwise self-collision plus implicit
  `z=0` ground-plane contact
- cloth+box `phystwin` must fail fast instead of silently mixing box contact

## Milestones

1. reproduce case 3 and case 4 exactly and verify whether the old ranking is stable
2. localize the first frame and the first persistent regime where case 4 becomes worse than case 3 in the original matrix
3. instrument the bridge step around those regions to see whether the difference enters before self-collision, after self-collision, or at ground / integration
4. test the smallest bridge-side timing hypothesis directly
5. keep cloth+box `phystwin` explicitly unsupported while preserving `off/native/custom`
6. write the updated task status and blocker interpretation

## Validation

- the diagnosis root contains explicit hypotheses, reproducibility evidence, first-divergence evidence, and a cause classification
- remaining blocker is stated against mechanism evidence, not guessed

## Notes

- Backfilled during the harness upgrade so the active task set has a full chain.
- The new matrix is not a promotion surface by itself; it is local blocked
  evidence until a new committed authority surface is chosen.
- Current diagnostic question: why the old matrix made case 3 beat case 4, and
  whether that ranking is stable enough to trust causally.
