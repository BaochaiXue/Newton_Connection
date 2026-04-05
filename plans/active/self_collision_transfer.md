# Plan: self_collision_transfer

## Goal

Drive self-collision work to one explicit engineering decision.

Current engineering milestone: keep the fair cloth + implicit-ground `2 x 2`
matrix reproducible first, then resume mechanism diagnosis on top of the
stable comparison surface.

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
5. once reproducibility is fixed, resume case-3-vs-case-4 mechanism diagnosis on the stable matrix surface

## Validation

- the reproducibility audit root contains at least 5 repeated full matrix reruns
- ranking order is invariant across reruns
- residual metric drift is quantified; bitwise equality is preferred when achievable
- remaining blocker is stated against the reproducible matrix surface, not against an unstable ranking

## Notes

- Backfilled during the harness upgrade so the active task set has a full chain.
- The new matrix is not a promotion surface by itself; it is local blocked
  evidence until a new committed authority surface is chosen.
- Current diagnostic question after the repro fix: why the now-stable matrix
  still makes case 3 beat case 4.
