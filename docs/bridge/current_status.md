> status: active
> canonical_replacement: none
> owner_surface: `bridge_control_plane`
> last_reviewed: `2026-04-05`
> review_interval: `7d`
> update_rule: `Update when active workstreams, blockers, or promoted result meaning changes. Keep detailed run notes in task status pages and results_meta.`
> notes: Short operational dashboard only. Do not turn this page into a run ledger or changelog dump.

# Current Status

Last updated: 2026-04-05

This page is the shortest operational dashboard for the bridge project.

Detailed result meaning belongs in:

- `results_meta/INDEX.md`
- `results_meta/LATEST.md`
- active task status pages under `tasks/status/`

## Current Priorities

- `markdown_harness_maintenance_upgrade`
  - keep the markdown/control-plane harness fail-closed: dashboard scope, inventory generation, local-only result wording, lint enforcement, and outcome-first agent reporting
- `slide_deck_overhaul`
  - keep the 2026-04-01 meeting deck hypothesis-driven and evidence-first
- `meeting_20260408_recall_part`
  - keep the new 2026-04-08 meeting bundle visible in the active task map; it now includes recall, stable self-collision, and conservative robot slides
- `rope_perf_apples_to_apples`
  - maintain the same-case rope replay benchmark as the committed performance reference, now with an explicit real-viewer E1 row
- `self_collision_transfer`
  - keep the new fair `2 x 2` cloth+ground matrix visible while strict parity remains blocked
- `robot_rope_franka_tabletop_push_hero`
  - preserve the truth-fixed tabletop-push hero bundle and keep its authority routing truthful
- `robot_rope_true_size_recalibration`
  - keep the true-size recovery task explicit while the thinner physical-radius default remains exploratory and non-authoritative
- `robot_rope_franka_semiimplicit_oneway`
  - preserve the new conservative one-way SemiImplicit baseline and keep it clearly de-scoped from both physical blocking and full two-way-coupling claims
- `robot_visible_rigid_tool_baseline`
  - preserve the newly promoted tool-mediated tabletop baseline; keep it clearly separate from both the direct-finger tabletop baseline and the blocked physical-blocking task, and keep its canonical rerender path single-history so hero/debug/validation cannot drift apart
- `robot_rope_franka_physical_blocking`
  - stronger follow-on task now has fail-closed stage labeling, direct-finger non-finger-loading diagnostics, a new blocking-specific low-profile joint reference family, and a real physical support-box path; the current blocker is support-box geometry overlap, not whether the box is in physics
- `native_robot_physical_blocking_minimal`
  - keep the Stage-0 rigid-only blocking proof separate from the rope-integrated blocking follow-on
- `remote_interaction_root_cause`
  - keep the true-size regression diagnosis explicit so recalibration work does not hide inside the tabletop hero chain

## Current Blockers

- `self_collision_transfer`
  - operator exactness is strong and the fair `2 x 2` matrix ranking is now reproducible after a bridge-side determinism fix; the stable `case_3 > case_4` gap is now localized as rollout-level interaction mismatch plus controller-spring semantics mismatch, not as an isolated self-collision-law issue
- `interactive_playground_profiling`
  - the exploratory profiling page must stay clearly separate from the committed rope benchmark truth under `rope_perf_apples_to_apples`
- `robot_rope_franka_physical_blocking`
  - readable tabletop rope-push baseline exists, Stage-0 direct-finger blocking is proven, the new rope-integrated `blocking_lowprofile` family removes measured non-finger table loading, and the rear support box is now a real static collider; the remaining blocker is that current support-box geometry starts in deep overlap
- `robot_visible_rigid_tool_baseline`
  - no blocker at the current conservative claim boundary; the promoted run is now the tool-mediated meeting-safe intermediary
- `robot_rope_franka_semiimplicit_oneway`
  - no blocker at the current conservative claim boundary; the promoted Path A bundle reuses the accepted c12 rollout under a narrower SemiImplicit one-way claim
- `robot_rope_true_size_recalibration`
  - true-size repair is still exploratory and must not override the accepted `c12` baseline without a new honest pass
- `native_robot_physical_blocking_minimal`
  - Stage-0 rigid-only blocking proof is complete locally; the stronger rope-integrated direct-finger follow-on still lacks a visually honest pass

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
- `native_robot_physical_blocking_minimal`
  - task status: `tasks/status/native_robot_physical_blocking_minimal.md`
  - committed authority: none yet
  - current meaning: Stage-0 native rigid-only blocking workstream that must pass before any stronger rope-integrated blocking claim
- `robot_rope_franka_physical_blocking`
  - task status: `tasks/status/robot_rope_franka_physical_blocking.md`
  - committed authority: none yet
  - current meaning: stronger follow-on task where the repaired bridge-layer `joint_target_drive` path now supports Stage-0 direct-finger blocking and local rope-integrated candidates under a new blocking-specific joint family, with no measured non-finger table loading on the latest `c14/c15/c16` runs
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
- `robot_rope_true_size_recalibration`
- `robot_rope_franka_semiimplicit_oneway`
- `robot_visible_rigid_tool_baseline`
- `native_robot_physical_blocking_minimal`
- `robot_rope_franka_physical_blocking`
- `remote_interaction_root_cause`
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
