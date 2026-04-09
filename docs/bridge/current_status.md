> status: active
> canonical_replacement: none
> owner_surface: `bridge_control_plane`
> last_reviewed: `2026-04-09`
> review_interval: `7d`
> update_rule: `Update when active workstreams, blockers, or promoted result meaning changes. Keep detailed run notes in task status pages and results_meta.`
> notes: Short operational dashboard only. Do not turn this page into a run ledger or changelog dump.

# Current Status

Last updated: 2026-04-09

This page is the shortest operational dashboard for the bridge project.

Detailed result meaning belongs in:

- `results_meta/INDEX.md`
- `results_meta/LATEST.md`
- active task status pages under `tasks/status/`

## Current Priorities

- `markdown_harness_maintenance_upgrade`
  - keep the markdown/control-plane harness fail-closed: active-vs-historical separation, dashboard scope, local-only result wording, and lint enforcement
- `slide_deck_overhaul`
  - keep the 2026-04-01 meeting deck short, evidence-first, and source-grounded
- `meeting_20260408_recall_part`
  - keep the 2026-04-08 meeting bundle visible and aligned with the active task map
- `interactive_playground_profiling` / `rope_perf_apples_to_apples`
  - keep the rope replay benchmark story clean: fair no-render baseline first, optimization implications second
- `self_collision_transfer`
  - preserve the fair `2 x 2` cloth+ground matrix while strict parity remains blocked
- robot demo cluster
  - preserve the accepted readable baselines
  - keep stronger direct-blocking work fail-closed until robot stability, real table blocking, and rope push all hold together
- supporting workflow tasks
  - `video_presentation_quality`
  - `data_collection_protocol`
  - `fast_foundation_stereo`
- `rope_perf_apples_to_apples`
  - keep the same-case rope replay benchmark as the committed performance reference

## Current Blockers

- `self_collision_transfer`
  - the fair matrix is reproducible, but strict parity is still blocked by the broader controller-spring / strict-parity mismatch
- `interactive_playground_profiling`
  - keep exploratory profiling separate from the committed rope benchmark truth under `rope_perf_apples_to_apples`
- `robot_rope_true_size_recalibration`
  - true-size repair is still exploratory and must not override the accepted `c12` baseline without a new honest pass
- `robot_rope_franka_physical_blocking`
  - accepted readable baselines exist, but no stronger direct-finger rope-integrated clip is promoted yet because robot stability, real table blocking, and rope push still do not hold together in one meeting-grade presentation
- `native_robot_physical_blocking_minimal`
  - Stage-0 rigid-only blocking proof is complete locally; rope-integrated follow-on remains open

## Promoted Surfaces At A Glance

- `bunny_penetration_force_diagnostic`
  - meeting-facing bunny penetration board under the reopened `2 x 2` contract
- `native_robot_rope_drop_release`
  - stage-0 native Franka support/release/free-fall baseline
- `robot_deformable_demo`
  - native Franka lift/release interaction baseline
- `robot_rope_franka_tabletop_push_hero`
  - readable tabletop-push hero baseline with the visible finger-contact claim re-certified
- `robot_visible_rigid_tool_baseline`
  - tool-mediated tabletop baseline where a visible rigid robot-mounted crossbar is the real physical contactor for the bridged rope
- `robot_rope_franka_semiimplicit_oneway`
  - conservative direct-finger tabletop baseline with an explicit one-way robot-to-rope claim only
- `rope_perf_apples_to_apples`
  - same-case no-render rope replay benchmark; viewer `E1` remains supporting context only
- full committed meaning:
  - `results_meta/INDEX.md`
  - `results_meta/LATEST.md`

## Active Workstreams

The full active task map lives in:

- `docs/bridge/tasks/README.md`
- `tasks/README.md`

Use those indexes for the complete active set. Keep this page as the short
dashboard, not a duplicate task ledger.

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
