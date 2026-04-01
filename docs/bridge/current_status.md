> status: active
> canonical_replacement: none
> owner_surface: `bridge_control_plane`
> last_reviewed: `2026-04-01`
> review_interval: `7d`
> update_rule: `Update when active workstreams, blockers, or promoted result meaning changes. Keep detailed run notes in task status pages and results_meta.`
> notes: Short operational dashboard only. Do not turn this page into a run ledger or changelog dump.

# Current Status

Last updated: 2026-04-01

This page is the shortest operational dashboard for the bridge project.

Detailed result meaning belongs in:

- `results_meta/INDEX.md`
- `results_meta/LATEST.md`
- active task status pages under `tasks/status/`

## Current Priorities

- `markdown_harness_maintenance_upgrade`
  - keep the markdown/control-plane harness fail-closed: dashboard scope, inventory generation, local-only result wording, and lint enforcement
- `slide_deck_overhaul`
  - keep the 2026-04-01 meeting deck hypothesis-driven and evidence-first
- `rope_perf_apples_to_apples`
  - maintain the same-case rope replay benchmark as the committed performance reference, now with an explicit real-viewer E1 row
- `self_collision_transfer`
  - separate demo-ready progress from blocked strict parity
- `robot_rope_franka_tabletop_push_hero`
  - preserve the promoted tabletop-push hero bundle and keep its authority routing truthful

## Current Blockers

- `self_collision_transfer`
  - operator exactness is strong, but full strict rollout parity remains blocked
- `interactive_playground_profiling`
  - the exploratory profiling page must stay clearly separate from the committed rope benchmark truth under `rope_perf_apples_to_apples`

## Promoted Surfaces At A Glance

- `bunny_penetration_force_diagnostic`
  - task status: `tasks/status/bunny_penetration_force_diagnostic.md`
  - committed authority: `results_meta/tasks/bunny_penetration_force_diagnostic.json`
  - current meaning: meeting-facing bunny penetration board under the reopened `2 x 2` contract
- `native_robot_rope_drop_release`
  - task status: `tasks/status/native_robot_rope_drop_release.md`
  - committed authority: `results_meta/tasks/native_robot_rope_drop_release.json`
  - current meaning: stage-0 native Franka support/release/free-fall baseline
- `robot_deformable_demo`
  - task status: `tasks/status/robot_deformable_demo.md`
  - committed authority: `results_meta/tasks/robot_deformable_demo.json`
  - current meaning: native Franka lift/release interaction baseline
- `robot_rope_franka_tabletop_push_hero`
  - task status: `tasks/status/robot_rope_franka_tabletop_push_hero.md`
  - committed authority: `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
  - current meaning: readable tabletop-push hero baseline under fixed `sim_dt = 5e-5`, `substeps = 667`
- `rope_perf_apples_to_apples`
  - task status: `tasks/status/rope_perf_apples_to_apples.md`
  - committed authority: `results_meta/tasks/rope_perf_apples_to_apples.json`
  - current meaning: same-case rope replay benchmark with both visible-viewer E1 and no-render A0/A1/B0 rows; Newton A1 remains slower than PhysTwin B0 on the committed baseline

## Active Workstreams

- `markdown_harness_maintenance_upgrade`
  - inventory/lint/hook discipline now converges on one public markdown-maintenance path; follow-up is routine review-age cleanup rather than structural rescue
- `slide_deck_overhaul`
- `meeting_20260408_recall_part`
- `bunny_penetration_force_diagnostic`
- `video_presentation_quality`
- `robot_deformable_demo`
- `robot_rope_franka_tabletop_push_hero`
- `native_robot_rope_drop_release`
- `interactive_playground_profiling`
- `rope_perf_apples_to_apples`
- `self_collision_transfer`
- `data_collection_protocol`
- `fast_foundation_stereo`

## Authority Rule

- `results_meta/` is the committed authority for current/promoted/best run meaning
- tracked local result READMEs, `BEST_RUN` mirrors, and subtree status stubs are secondary/local-only surfaces
- active execution chains live in:
  - `tasks/spec/`
  - `tasks/implement/`
  - `tasks/status/`
  - `plans/active/`
- historical execution artifacts live in:
  - `tasks/history/`
  - `plans/completed/`
