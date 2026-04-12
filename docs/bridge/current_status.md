> status: active
> canonical_replacement: none
> owner_surface: `bridge_control_plane`
> last_reviewed: `2026-04-11`
> review_interval: `7d`
> update_rule: `Update when active workstreams, blockers, promoted result meaning, or control-plane routing rules change. Keep detailed run notes in task status pages and results_meta.`
> notes: Short operational dashboard only. Keep this page map-like: current work, blockers, promoted surfaces, and where to go next.

# Current Status

Last updated: 2026-04-11

This page is the shortest operational dashboard for the bridge project.

Detailed result meaning belongs in:

- `results_meta/INDEX.md`
- `results_meta/LATEST.md`
- active task status pages under `tasks/status/`

## Current Priorities

- `bridge_code_structure_cleanup`
  - keep the bridge layer easier to navigate by extracting bounded helper modules without changing current experiment semantics
- `newton_robot_examples_kb_update`
  - move official Newton robot-example lessons into `docs/newton/` so future agents do not have to recover them from retired robot diagnostics
- `markdown_harness_maintenance_upgrade`
  - keep the harness fail-closed: progressive disclosure, archive-hub routing, root hygiene, local-only result wording, and write-strict/read-loose hook behavior
- `slide_deck_overhaul`
  - keep the 2026-04-01 meeting deck short, evidence-first, and source-grounded
- `meeting_20260408_recall_part`
  - keep the 2026-04-08 meeting bundle visible and aligned with the active task map
- `interactive_playground_profiling` / `rope_perf_apples_to_apples`
  - keep the rope replay benchmark story clean: fair no-render baseline first, optimization implications second
- `self_collision_transfer`
  - preserve the fair `2 x 2` cloth+ground matrix while strict parity remains blocked
- supporting tasks
  - `video_presentation_quality`
  - `data_collection_protocol`
  - `fast_foundation_stereo`

## Current Blockers

- `self_collision_transfer`
  - the fair matrix is reproducible, but strict parity is still blocked by the broader controller-spring / strict-parity mismatch
- `interactive_playground_profiling`
  - keep exploratory profiling separate from the committed rope benchmark truth under `rope_perf_apples_to_apples`

## Promoted Surfaces At A Glance

- `bunny_penetration_force_diagnostic`
  - meeting-facing bunny penetration board under the reopened `2 x 2` contract
- `rope_perf_apples_to_apples`
  - same-case no-render rope replay benchmark; viewer `E1` remains supporting context only
- full committed meaning:
  - `results_meta/INDEX.md`
  - `results_meta/LATEST.md`

## Recent Retirements

- robot + deformable PS-object demo line
  - retired on `2026-04-09`
  - strongest partial robot baselines remain archived as historical evidence only
  - canonical explanation lives in `docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`

## Active Workstreams

The full active task map lives in:

- `docs/bridge/tasks/README.md`
- `tasks/README.md`

Use those indexes for the complete active set. Keep this page as the short
dashboard, not a duplicate task ledger.

## History Routing

When historical context is needed, start from:

- `docs/archive/tasks/README.md`
- `docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`

Do not use deep local bundle README files or dated status notes as the first
entrypoint for current work.

## Authority Rule

- `results_meta/` is the committed authority for current/promoted/best run meaning
- tracked local result READMEs, `BEST_RUN` mirrors, and subtree status stubs are secondary/local-only surfaces
- active robot/demo predecessor branches that no longer drive the live task map belong in archive/history neighborhoods, not beside active chains
- active execution chains live in:
  - `tasks/spec/`
  - `tasks/implement/`
  - `tasks/status/`
  - `plans/active/`
- historical execution artifacts live in:
  - `tasks/history/`
  - `plans/completed/`
