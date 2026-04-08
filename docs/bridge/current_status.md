> status: active
> canonical_replacement: none
> owner_surface: `bridge_control_plane`
> last_reviewed: `2026-04-08`
> review_interval: `7d`
> update_rule: `Update when active workstreams, blockers, or promoted result meaning changes. Keep detailed run notes in task status pages and results_meta.`
> notes: Short operational dashboard only. Do not turn this page into a run ledger or changelog dump.

# Current Status

Last updated: 2026-04-08

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
  - stronger follow-on task now has fail-closed stage labeling, direct-finger non-finger-loading diagnostics, a real physical support-box path, a thin-slab scout-fit workflow, and a practical visible-settle mitigation in the canonical wrapper; the deeper blocker remains gravity-stable robot actuation under `joint_target_drive`, not support-box truth
- `robot_rope_franka_native_v2`
  - new native-style rewrite path now exists as a separate bridge demo and
    wrapper; it removes the old overwrite path and uses Cartesian waypoints +
    native IK + `control.joint_target_pos`, but the current bridge-side solver
    route still sags into table contact during `pre`
- `native_robot_physical_blocking_minimal`
  - keep the Stage-0 rigid-only blocking proof separate from the rope-integrated blocking follow-on
- `remote_interaction_root_cause`
  - keep the true-size regression diagnosis explicit so recalibration work does not hide inside the tabletop hero chain

## Current Blockers

- `self_collision_transfer`
  - operator exactness is strong and the fair `2 x 2` matrix ranking is now reproducible after a bridge-side determinism fix; a new bridge-side ground-law isolation fix removes the old hidden gravity/drag timing difference from the explicit matrix surface, shrinking the old large `case_3 > case_4` gap to a small residual and moving the blocker back to the broader controller-spring / strict-parity mismatch
- `interactive_playground_profiling`
  - the exploratory profiling page must stay clearly separate from the committed rope benchmark truth under `rope_perf_apples_to_apples`
  - latest same-case exploratory bundle now exists for `rope_double_hand`
    controller replay on both Newton and PhysTwin
- `robot_rope_franka_physical_blocking`
  - readable tabletop rope-push baseline exists, Stage-0 direct-finger blocking is proven, the new rope-integrated path now fails closed on settle-onset collapse, and the canonical Stage-1 wrapper currently mitigates the visible static-collapse failure with `settle=0.05`, `support_box=none`, and the safer hero-style base offset `(-0.56, -0.22, 0.10)`; no rope-integrated candidate is promoted yet because the deeper gravity-stability issue is still open even though the current local candidate now preserves some rope motion again
- `robot_rope_franka_native_v2`
  - the native-style rewrite has removed the old monolithic overwrite path, but
    no v2 candidate is promoted yet because even the seed-based reachable phase
    generator still drops into `pre`-phase table contact before readable
    finger-to-rope interaction starts
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
- `robot_rope_franka_native_v2`
  - task status: `tasks/status/robot_rope_franka_native_v2.md`
  - committed authority: none yet
  - current meaning: new native-style tabletop rope demo rewrite path; code and
    wrapper exist locally, but no candidate yet satisfies startup stability +
    real table blocking + readable rope push at the same time
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
- `robot_rope_franka_native_v2`
- `remote_interaction_root_cause`
- `native_robot_rope_drop_release`
- `interactive_playground_profiling`
  - latest exploratory bundle:
    - `results/interactive_playground_profiling/runs/20260408_090500_rope_interactive_one_to_one_v1`
  - meeting-facing summary surface:
    - `formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx`
      slide `9`
  - current exploratory meaning:
    - rope same-case no-render baseline:
      - Newton baseline is about `6.66x` slower than PhysTwin
      - Newton precomputed replay is still about `3.54x` slower
      - controller upload is real on rope (`~1.88x` baseline -> precomputed speedup), but it is not the whole story
      - rope does not show the cloth-case collision-generation bottleneck; on rope the remaining gap is better explained by broader solver/runtime structure around the same controller-driven spring-mass path
    - older cloth counterexample remains useful because it shows a different regime:
      - `results/interactive_playground_profiling/runs/20260408_075949_blue_cloth_interactive_one_to_one_v1`
      - there, collision candidate generation dominates the cross-system gap
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
