# Plan: self_collision_transfer

## Goal

Drive self-collision work to one explicit engineering decision.

Current engineering milestone: use the reproducible fair cloth +
implicit-ground `2 x 2` matrix to explain the stable `case_3 > case_4`
ordering and close the task with an explicit A/B/C recommendation or a precise
blocker.

## Constraints

- no Newton core edits
- keep the cloth + implicit-ground PhysTwin reference case fixed for the
  controlled RMSE matrix
- keep cloth+box and bunny as secondary scene evidence only
- strict `phystwin` parity is limited to pairwise self-collision plus implicit
  `z=0` ground-plane contact
- cloth+box `phystwin` must fail fast instead of silently mixing box contact

## Milestones

1. make the fair `2 x 2` matrix ranking reproducible across repeated reruns at the same commit and environment
2. keep the determinism fix bridge-side only
3. preserve the fair matrix surface: same IR, same dt/substeps, same evaluator, same scene
4. keep cloth+box `phystwin` explicitly unsupported while preserving `off/native/custom`
5. explain the stable `case_3 > case_4` ordering on the reproducible matrix surface
6. translate that explanation into an explicit A/B/C recommendation or a precise blocker
7. keep any restart-from-frame continuation diagnostics bridge-side and local-only unless they change the authoritative comparison surface

## Validation

- the reproducibility audit root contains at least 5 repeated full matrix reruns
- ranking order is invariant across reruns
- residual metric drift is quantified; bitwise equality is preferred when achievable
- first-divergence localization exists on the stable matrix surface
- remaining blocker or recommendation is stated against the stable matrix surface, not against the older unstable ranking

## Notes

- Backfilled during the harness upgrade so the active task set has a full chain.
- The new matrix is not a promotion surface by itself; it is local blocked
  evidence until a new committed authority surface is chosen.
- Current diagnostic question after the repro fix: why the now-stable matrix
  still makes case 3 beat case 4, and whether that stable gap changes the final
  A/B/C self-collision recommendation.
- A frame-137 continuation matrix can be used as a bounded follow-up to test
  whether the late gap is mostly pre-137 history or post-137 branch semantics,
  but it does not replace the authoritative full-rollout surface.
