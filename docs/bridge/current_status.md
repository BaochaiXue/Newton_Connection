> status: active
> canonical_replacement: none
> owner_surface: `bridge_control_plane`
> last_reviewed: `2026-04-04`
> review_interval: `7d`
> update_rule: `Update when active workstreams, blockers, or promoted result meaning changes. Keep detailed run notes in task status pages and results_meta.`
> notes: Short operational dashboard only. Do not turn this page into a run ledger or changelog dump.

# Current Status

Last updated: 2026-04-04

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
- `meeting_20260408_recall_part`
  - keep the new 2026-04-08 recall bundle visible in the active task map until the later meeting sections are ready
- `rope_perf_apples_to_apples`
  - maintain the same-case rope replay benchmark as the committed performance reference, now with an explicit real-viewer E1 row
- `self_collision_transfer`
  - keep the new fair `2 x 2` cloth+ground matrix visible while strict parity remains blocked
- `robot_rope_franka_tabletop_push_hero`
  - preserve the truth-fixed tabletop-push hero bundle and keep its authority routing truthful
- `robot_rope_franka_semiimplicit_oneway`
  - preserve the new conservative one-way SemiImplicit baseline and keep it clearly de-scoped from both physical blocking and full two-way-coupling claims
- `robot_visible_rigid_tool_baseline`
  - preserve the newly promoted tool-mediated tabletop baseline; keep it clearly separate from both the direct-finger tabletop baseline and the blocked physical-blocking task, and keep its canonical rerender path single-history so hero/debug/validation cannot drift apart
- `robot_rope_franka_physical_blocking`
  - stronger follow-on task has been re-opened: the old bridge-layer limit proof is no longer sufficient after identifying stale post-step FK overwrite plus destabilizing default articulation attachment gains in the `joint_target_drive` path

## Current Blockers

- `self_collision_transfer`
  - operator exactness is strong and the fair `2 x 2` matrix ranking is now reproducible after a bridge-side determinism fix; the stable `case_3 > case_4` gap is now localized as rollout-level interaction mismatch plus controller-spring semantics mismatch, not as an isolated self-collision-law issue
- `interactive_playground_profiling`
  - the exploratory profiling page must stay clearly separate from the committed rope benchmark truth under `rope_perf_apples_to_apples`
- `robot_rope_franka_physical_blocking`
  - readable tabletop rope-push baseline exists, but the stronger physical robot-blocking follow-on still lacks a Stage-0 rigid-only proof; the bridge-layer path is now under re-test rather than being treated as definitively impossible
- `robot_visible_rigid_tool_baseline`
  - no blocker at the current conservative claim boundary; the promoted run is now the tool-mediated meeting-safe intermediary
- `robot_rope_franka_semiimplicit_oneway`
  - no blocker at the current conservative claim boundary; the promoted Path A bundle reuses the accepted c12 rollout under a narrower SemiImplicit one-way claim

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
  - current meaning: readable tabletop-push hero baseline under fixed `sim_dt = 5e-5`, `substeps = 667`, now with the rope render thickness aligned to the physical contact thickness and the visible finger-contact claim re-certified
- `robot_visible_rigid_tool_baseline`
  - task status: `tasks/status/robot_visible_rigid_tool_baseline.md`
  - committed authority: `results_meta/tasks/robot_visible_rigid_tool_baseline.json`
  - current meaning: promoted tool-mediated tabletop baseline where a visible rigid robot-mounted crossbar is the real physical contactor for the bridged rope, now backed by separate skeptical video audits and a single-rollout three-view bundle
- `robot_rope_franka_semiimplicit_oneway`
  - task status: `tasks/status/robot_rope_franka_semiimplicit_oneway.md`
  - committed authority: `results_meta/tasks/robot_rope_franka_semiimplicit_oneway.json`
  - current meaning: promoted conservative direct-finger tabletop baseline re-certified from the accepted c12 rollout, with explicit SolverSemiImplicit deformable interaction and a truthful one-way robot->rope claim only
- `robot_rope_franka_physical_blocking`
  - task status: `tasks/status/robot_rope_franka_physical_blocking.md`
  - committed authority: none yet
  - current meaning: stronger follow-on task where the old overwrite path is still proven non-physical, but the previous bridge-layer impossibility claim is under reassessment after fixing stale FK overwrite and lowering destabilizing articulation attachment gains
- `rope_perf_apples_to_apples`
  - task status: `tasks/status/rope_perf_apples_to_apples.md`
  - committed authority: `results_meta/tasks/rope_perf_apples_to_apples.json`
  - current meaning: same-case no-render rope replay benchmark; visible-viewer `E1` exists only as practical supporting context, and Newton A1 remains slower than PhysTwin B0 on the committed baseline

## Active Workstreams

- `markdown_harness_maintenance_upgrade`
  - inventory/lint/hook discipline now converges on one public markdown-maintenance path; follow-up is routine review-age cleanup rather than structural rescue
- `slide_deck_overhaul`
- `meeting_20260408_recall_part`
- `bunny_penetration_force_diagnostic`
- `video_presentation_quality`
- `robot_deformable_demo`
- `robot_rope_franka_tabletop_push_hero`
- `robot_rope_franka_semiimplicit_oneway`
- `robot_visible_rigid_tool_baseline`
- `robot_rope_franka_physical_blocking`
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
