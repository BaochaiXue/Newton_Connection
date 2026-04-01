# Status: self_collision_transfer_decision

> status: deprecated
> canonical_replacement: `tasks/status/self_collision_transfer.md`
> owner_surface: `self_collision_transfer`
> last_reviewed: `2026-04-01`
> notes: Deprecated slug alias preserved only for discoverability; do not treat this file as live status.

## Current State

Decision tooling is now implemented:

- rollout-peak overlap metrics exist on the box self-contact summary path
- a box matrix runner exists
- a PhysTwin-style operator-equivalence verifier exists

The full decision matrix and follow-up sanity checks are still pending.

## Last Completed Step

Implemented the first decision-grade infrastructure and validated it with:

- a lightweight equivalence run
- a short no-render box matrix run
- artifact-validator pass on the matrix smoke directory

## Next Step

Run the full box decision matrix with render enabled and then attach:

- bunny sanity check on the provisional winner
- OFF-baseline regression check
- selected-mode profiler output

## Blocking Issues

- Final A/B/C cannot be declared until the full matrix and follow-up checks are done.
- The current thresholds are still provisional and may need one revision after the first full matrix.

## Artifact Paths

- `docs/bridge/tasks/self_collision_transfer.md`
- `tasks/spec/self_collision_transfer_decision.md`
- `plans/completed/self_collision_transfer_decision.md`
- `Newton/phystwin_bridge/tools/other/run_self_collision_matrix.py`
- `Newton/phystwin_bridge/tools/other/verify_phystwin_self_collision_equivalence.py`
- `tmp/self_collision_eq_smoke_20260330/equivalence.json`
- `tmp/self_collision_matrix_smoke_20260330/self_collision_decision_table.csv`
