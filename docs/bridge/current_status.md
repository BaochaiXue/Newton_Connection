> status: active
> canonical_replacement: none
> owner_surface: `bridge_control_plane`
> last_reviewed: `2026-05-21`
> review_interval: `7d`
> update_rule: `Update when active workstreams, blockers, promoted result meaning, or control-plane routing rules change. Keep detailed run notes in task status pages and results_meta.`
> notes: Short operational dashboard only. Keep this page map-like: current work, blockers, promoted surfaces, and where to go next.

# Current Status

Last updated: 2026-05-11

Detailed result meaning belongs in:

- `results_meta/INDEX.md`
- `results_meta/LATEST.md`
- `tasks/status/`

## Current Priorities

- `bridge_code_structure_cleanup`
  - keep the bridge layer easier to navigate by extracting bounded helper modules without changing current experiment semantics; cloth+bunny is already package-first, and rope now has a transitional package skeleton under `Newton/phystwin_bridge/demos/rope/`
- `newton_robot_examples_kb_update`
  - move official Newton robot-example lessons into `docs/newton/` so future agents do not have to recover them from retired robot diagnostics
- `native_robot_table_penetration_probe`
  - build a minimal robot_panda_hydro-style bridge demo that intentionally targets below the table and records whether native rigid-table blocking holds
- `pure_semiimplicit_robot_loaded_object`
  - full-Panda pure-SemiImplicit remains a clean negative result, but the
    proxy robot pusher now gives a finite positive two-way coupling demo with
    the PhysTwin-like rope IR
- `robot_table_rope_split_mujoco_semiimplicit`
  - split demo remains the main meeting-video route; default support passes the
    non-burying gate, native Panda fingers are now the presentation default,
    and the current native-only rope diagnostic still fails strict carry; the
    rank-1 native rigid capsule sanity now passes with corrected yaw/target,
    so the next interpretation hinge is native rope under that corrected
    gripper trajectory
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
  - `video_presentation_quality`, `data_collection_protocol`,
    `fast_foundation_stereo`, `phystwin_local_harness_engineering`,
    `phystwin_four_new_cases_pipeline`, and `phystwin_upstream_sync_review`

## Current Blockers

- `self_collision_transfer`
  - the fair matrix is reproducible, but strict parity is still blocked by the broader controller-spring / strict-parity mismatch
- `interactive_playground_profiling`
  - keep exploratory profiling separate from the committed rope benchmark truth under `rope_perf_apples_to_apples`
- `robot_table_rope_split_mujoco_semiimplicit`
  - active meeting-video blocker is true native Panda finger carry:
    `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428`
    records native fingers and contact-driven rope motion, but still
    `strict_contact_only_pass = false` and `rope_lift_height_m = 0.0`; rank-1
    native rigid capsule sanity passes, which rules out a blanket
    "Panda cannot carry any cylinder-like object" failure for the corrected
    yaw/target
- `pure_semiimplicit_robot_loaded_object`
  - the repaired diagnostic confirms the full-Panda pure-SemiImplicit path is
    still blocked: in
    `tmp/pure_semiimplicit_robot_loaded_object_timing_fixed_smoke_20260511`,
    `pure_semiimplicit = true`, `solver_owned_robot_state = true`,
    `motion_time_source = sim_time`, but `numerics_finite = false`,
    `finger_object_contact_frames = 0`, and
    `rope_motion_after_contact = false`; do not claim two-way robot/object
    reaction from the full-Panda path

## Latest Validation Note

- `pure_semiimplicit_robot_loaded_object`
  - proxy two-way artifact:
    `tmp/proxy_robot_rope_two_way_soft_20260511`; validator passed with
    `two_way_coupling_signal = true`, `numerics_finite = true`,
    `robot_rope_contact_frames = 117`, and
    `rope_motion_after_robot_contact = true`
- `robot_table_rope_split_mujoco_semiimplicit`
  - rank-1 native rigid capsule pass:
    `tmp/robot_table_rope_native_finger_ablation_rank1_capsule_yawpi_20260511_184520`;
    native rope under that corrected gripper trajectory is still pending

## Promoted Surfaces At A Glance

- `bunny_penetration_force_diagnostic`
  - meeting-facing bunny penetration board under the reopened `2 x 2` contract
- `rope_perf_apples_to_apples`
  - same-case no-render rope replay benchmark; viewer `E1` remains supporting context only
- `robot_table_rope_split_mujoco_semiimplicit`
  - current best native-Panda-finger-only diagnostic, not final meeting video:
    `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428`;
    it removes `grasp_assist`, `rope_cradle`, and auxiliary pad geometry, but
    fails strict carry because the rope is contacted rather than lifted; the
    previous default-support artifact remains the supporting non-burying
    calibration surface
- `pure_semiimplicit_robot_loaded_object`
  - positive proxy robot two-way artifact:
    `tmp/proxy_robot_rope_two_way_soft_20260511`; full-Panda negative
    diagnostic remains:
    `tmp/pure_semiimplicit_robot_loaded_object_timing_fixed_smoke_20260511`;
    inspect both `hero.mp4` files and `summary.json`
- full committed meaning:
  - `results_meta/INDEX.md`
  - `results_meta/LATEST.md`

## Recent Retirements

- robot + deformable PS-object demo line retired on `2026-04-09`; canonical
  explanation lives in `docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`

## Active Workstreams

The full active task map lives in `docs/bridge/tasks/README.md` and
`tasks/README.md`.

Use those indexes for the complete active set. Keep this page as the short
dashboard, not a duplicate task ledger.

## History Routing

When historical context is needed, start from `docs/archive/tasks/README.md`
and `docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`, not deep
local bundle README files.

## Authority Rule

- `results_meta/` is the committed authority for current/promoted/best run meaning
- tracked local result READMEs, `BEST_RUN` mirrors, and subtree status stubs are secondary/local-only
- active execution chains live in `tasks/spec/`, `tasks/implement/`,
  `tasks/status/`, and `plans/active/`
- historical execution artifacts live in `tasks/history/` and
  `plans/completed/`
