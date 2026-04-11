> status: active
> canonical_replacement: none
> owner_surface: `self_collision_transfer`
> last_reviewed: `2026-04-11`
> review_interval: `21d`
> update_rule: `Update when the strict-scope interpretation, committed blocked surface, or decision boundary changes.`
> notes: Active canonical task page for the self-collision decision and strict parity blocker analysis. Keep this page decision-oriented rather than turning it into a long experiment diary.

# Task: Self-Collision Transfer Decision

## Primary Question

Without breaking the current Newton bridge mainline, which self-collision path
is the smallest, most stable, and most sufficient to support meeting-quality
demos?

This task must still end with one explicit decision:

- **A. Native Newton is enough**
- **B. Bridge-side custom filtered penalty is enough**
- **C. Bridge-side PhysTwin-style self-collision is necessary**

## Why This Matters

The advisor constraint is unchanged:

- exact collision parity is not the main project goal
- but the mechanism still has to be understood before deciding what to override

So the real deliverable is a defendable engineering decision, not an endless
parameter sweep.

## Current State

Committed blocked surface:

- `results_meta/tasks/self_collision_transfer.json`

Current supported reading:

- the fair cloth+implicit-ground `2 x 2` matrix ranking is reproducible
- the old large `case_3 > case_4` gap was largely driven by hidden whole-step timing differences
- after the explicit ground-law isolation fix, the remaining blocker is the broader controller-spring / rollout parity gap
- strict `phystwin` remains a narrow law swap:
  - pairwise self-collision
  - implicit `z=0` ground
  - not generic box-support contact

## Main Code Paths

- `Newton/phystwin_bridge/demos/demo_cloth_box_drop_with_self_contact.py`
  - box-support decision demo for `off/native/custom`
  - strict `phystwin` remains intentionally unsupported there
- `Newton/phystwin_bridge/demos/self_contact_bridge_kernels.py`
  - bridge-side PhysTwin-style self-collision / ground-law kernels
- `Newton/phystwin_bridge/tools/core/phystwin_contact_stack.py`
  - shared strict bridge-side `phystwin` contact stack
- `Newton/phystwin_bridge/tools/core/validate_parity.py`
  - OFF-baseline regression thresholds and parity checks
- `Newton/phystwin_bridge/tools/other/run_ground_contact_self_collision_rmse_matrix.py`
  - canonical fair `2 x 2` matrix runner
- `Newton/phystwin_bridge/tools/other/run_ground_contact_self_collision_repro_audit.py`
  - ranking reproducibility runner
- `Newton/phystwin_bridge/tools/other/run_ground_contact_self_collision_visual_bundle.py`
  - stable labeled video bundle
- `Newton/phystwin_bridge/tools/other/run_ground_contact_self_collision_restart_matrix.py`
  - restart-state continuation runner
- `Newton/phystwin_bridge/tools/other/diagnose_controller_spring_semantics.py`
  - controller-spring mismatch evidence

## Controlled Decision Surfaces

Main box-support matrix:

- `--self-contact-mode off`
- `--self-contact-mode native`
- `--self-contact-mode custom --custom-self-contact-hops 1`
- `--self-contact-mode custom --custom-self-contact-hops 2`

Strict parity matrix on the PhysTwin-native cloth + implicit-ground scene:

- `case_1_self_off_ground_native`
- `case_2_self_off_ground_phystwin`
- `case_3_self_phystwin_ground_native`
- `case_4_self_phystwin_ground_phystwin`

The strict matrix must stay on the PhysTwin-native cloth + implicit-ground
scene. Do not substitute cloth+box, bunny, rope, or robot scenes.

## Acceptance Boundary

Meeting-ready minimum:

1. no visible self-explosion or numerical collapse
2. controlled overlap and penetration metrics stay within the particle-radius bounds
3. wall-time overhead vs `off` stays within `2.0x`
4. one clean `8-15 s` MP4 exists for slides

Promote-to-mainline only if:

5. bunny sanity check does not worsen rigid-contact behavior
6. OFF-baseline parity still passes

## Decision Logic

- if native passes: stop there
- if native fails but custom passes: pair filtering is enough
- only if native fails, custom fails, and strict `phystwin` passes: choose bridge-side PhysTwin-style self-collision

## Current Evidence Roots

- committed blocked surface:
  - `Newton/phystwin_bridge/results/ground_contact_self_collision_repro_fix_20260404_200830_aa5e607`
- post-isolation-fix full matrix:
  - `Newton/phystwin_bridge/results/ground_contact_self_collision_rmse_matrix_20260408_070232_eb0d80b`
- post-isolation-fix restart@137 continuation matrix:
  - `Newton/phystwin_bridge/results/ground_contact_self_collision_restart137_matrix_20260408_070609_eb0d80b`
- stable case-3-vs-case-4 follow-up:
  - `Newton/phystwin_bridge/results/self_collision_transfer_case3_vs_case4_followup_20260404_210334_ac9ec33`
- stable visual bundle:
  - `Newton/phystwin_bridge/results/ground_contact_self_collision_visual_bundle_20260408_042645_00feebe`

Detailed historical scratch notes now live in:

- `tasks/history/status/self_collision_transfer_diagnostic_log_20260401_20260408.md`

## Current Recommendation For Execution Order

1. Keep the cloth+box `off/native/custom` matrix as the main decision surface.
2. Keep the controlled cloth+ground `2 x 2` matrix as the strict parity / interaction diagnostic surface.
3. Treat the reproducible matrix root as the committed blocked surface and newer post-isolation roots as local mechanism evidence.
4. Use the bunny force-diagnostic only as a post-selection sanity check.
5. Rerun the OFF-baseline parity validator before any final recommendation is declared.
