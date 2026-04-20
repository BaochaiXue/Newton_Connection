> status: active
> canonical_replacement: none
> owner_surface: `bridge_control_plane`
> last_reviewed: `2026-04-15`
> review_interval: `7d`
> update_rule: `Update when active workstreams, blockers, promoted result meaning, or control-plane routing rules change. Keep detailed run notes in task status pages and results_meta.`
> notes: Short operational dashboard only. Keep this page map-like: current work, blockers, promoted surfaces, and where to go next.

# Current Status

Last updated: 2026-04-16

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
- `native_robot_table_penetration_probe`
  - build a minimal robot_panda_hydro-style bridge demo that intentionally targets below the table and records whether native rigid-table blocking holds
- `robot_table_rope_split_mujoco_semiimplicit`
  - split demo code is live; rope default total mass is `0.1kg`, default
    physical radius is `0.2x`, recording now starts post-settle, and the demo
    now measures support penetration explicitly instead of trusting contact
    counts alone; the validated default-support artifact now passes the
    non-burying gate, and a post-core-update smoke run still passes after
    refreshing `Newton/newton` to official upstream `origin/main`; the rigid-side
    builder is now aligned more closely with the newer upstream
    `example_robot_panda_hydro.py` config style, and the post-refactor smoke
    artifact also passed `validate_experiment_artifacts.py`; a separate
    presentation-video path now also exists with visible-opening recording,
    full-cycle rendering, dedicated camera framing, and pad-center-targeted IK,
    but it is not yet accepted as a meeting-facing artifact
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
- `robot_table_rope_split_mujoco_semiimplicit`
  - support calibration is no longer the blocker:
    the new default support artifact keeps `rope_table_contact_frames_first_30 = 30`
    and `rope_ground_contact_frames_first_30 = 30` while reducing
    `max_support_penetration_m` to `0.000639` in
    `tmp/robot_table_rope_split_support_default_authoritative_20260415`;
    the post-core-update smoke artifact also still runs on the refreshed core,
    and the new presentation path now fixes the old artifact-type mismatch, but
    the current best presentation run
    `tmp/robot_table_rope_split_presentation_smoke_v10_20260416` still fails
    because `first_finger_rope_contact_frame = null` and
    `min_leading_pad_to_rope_distance_m = 0.05427`; later presentation variants
    also started surfacing rope-side contact-buffer overflow warnings, so the
    blocker is now presentation contact targeting, not support or recording;
    the best current presentation artifact passes
    `validate_experiment_artifacts.py` and has a prepared review bundle at
    `tmp/review_bundle_presentation_smoke_v10_20260416`, but it is still not a
    skeptical-review `PASS`

## Promoted Surfaces At A Glance

- `bunny_penetration_force_diagnostic`
  - meeting-facing bunny penetration board under the reopened `2 x 2` contract
- `rope_perf_apples_to_apples`
  - same-case no-render rope replay benchmark; viewer `E1` remains supporting context only
- `robot_table_rope_split_mujoco_semiimplicit`
  - current authoritative partial surface: the split demo's default support
    parameters now satisfy the non-burying support gate, but finger-first
    contact is still unresolved
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
