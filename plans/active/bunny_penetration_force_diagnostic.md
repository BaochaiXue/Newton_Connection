# Active Plan: Bunny Penetration Force Diagnostic

## Milestones

1. Reopen the task in docs/spec/status/current-status so the old accepted
   package is no longer treated as the final meeting visualization.
2. Audit the current detector, board renderer, wrapper, and validators against
   the stricter `2 x 2` all-colliding-node spec.
3. Implement a replayable per-frame collision-force detector bundle for:
   - `box_control`
   - `bunny_baseline`
4. Fix the board renderer so the main board uses:
   - force-active collision membership
   - strict penalty-vs-total force definitions
   - clip-wide force scaling
   - hold annotation when one case ends early
5. Extend validation so the promoted run checks:
   - board semantics
   - panel visibility / non-black / non-blank
   - duration rule
   - detector metadata
   - legend presence
6. Produce a fresh promoted run under
   `results/bunny_force_visualization/runs/<timestamp>_realtime_allcolliding_2x2_v1/`
   and only update latest pointers if that run passes.

## Canonical Commands

- case runner:
  `scripts/run_bunny_force_case.py ... --force-diagnostic --defer-force-artifacts`
- detector builder:
  `scripts/build_bunny_collision_force_bundle.py ...`
- board builder:
  `scripts/render_bunny_penetration_collision_board.py ...`
- promoted wrapper:
  `scripts/run_bunny_penetration_collision_board.sh [run_id]`
- validators:
  - `scripts/validate_bunny_force_visualization.py --run-dir <run_dir>`
  - `scripts/validate_experiment_artifacts.py <run_dir> ...`

## Stop-And-Fix Rule

If any of these fail, do not promote the run:

- board node set is top-k only
- first-collision detector is missing or not saved
- penalty / total force semantics are ambiguous
- one or more panels are black / blank / mislabeled
- board duration does not match start to one second after first collision
- validators do not explicitly pass
