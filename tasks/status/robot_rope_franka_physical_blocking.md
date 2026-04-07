# Status: robot_rope_franka_physical_blocking

## Current State

- Active
- This is a new stronger task, separate from the accepted tabletop-push
  baseline
- Current state is now: `Stage-0 direct-finger rigid-only blocking passes on
  the repaired bridge-layer joint_target_drive path; Stage-1 rope-integrated
  runs now preserve body-truth and artifact truth, but the best current
  candidates still fail visual acceptance because the arm settles into a long
  table-loaded posture / late-scene collapse rather than a clean,
  presentation-ready finger-blocking push`

## Last Completed Step

- Repaired the bridge-layer `joint_target_drive` truth path so the solver owns
  `state_out.body_q`:
  - no pre/post hard overwrite in the blocking path
  - reduced-state resync now comes from `eval_ik(...)` after `solver.step(...)`
- Added stage-aware blocking support directly in
  [demo_robot_rope_franka.py](../../Newton/phystwin_bridge/demos/demo_robot_rope_franka.py):
  - `--blocking-stage rigid_only|rope_integrated`
  - `rigid_only` removes the rope while keeping the same direct-finger
    controller truth
  - `rope_integrated` keeps the rope and reuses the same same-history render
    chain
- Added hidden-preroll robot reset support for the blocking path:
  - `--tabletop-reset-robot-after-preroll`
  - used only to keep rope settle hidden from the visible clip; visible-frame
    control truth remains `joint_target_drive`
- Reworked the canonical wrapper and validators:
  - [run_robot_rope_franka_physical_blocking.sh](../../scripts/run_robot_rope_franka_physical_blocking.sh)
  - [diagnose_robot_rope_physical_blocking.py](../../scripts/diagnose_robot_rope_physical_blocking.py)
  - [validate_robot_rope_franka_physical_blocking.py](../../scripts/validate_robot_rope_franka_physical_blocking.py)
  - wrapper now produces `command.txt`, same-history hero/debug/validation,
    direct-finger diagnostics, and artifact-contract validation
- Produced the first truthful Stage-0 pass:
  - [c08_stage0_directfinger_renderfix](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_165753_rigid_only_c08_stage0_directfinger_renderfix)
  - key metrics:
    - `robot_table_first_contact_time_s = 0.1334`
    - `robot_table_penetration_min_m = -9.76e-4`
    - `ee_target_to_actual_error_during_block_mean_m = 6.98e-2`
    - `proof_surface = actual_multi_box_finger_colliders`
    - blocking validator: PASS
- Produced the first rope-integrated bridge-layer candidates on the same
  architecture:
  - [c10_stage1_prerollreset](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_170744_rope_integrated_c10_stage1_prerollreset)
  - [c11_stage1_holdtune](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_171151_rope_integrated_c11_stage1_holdtune)
  - [c12_stage1_basez09](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_171603_rope_integrated_c12_stage1_basez09)
  - [c13_stage1_higherhold](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_171950_rope_integrated_c13_stage1_higherhold)

## Latest Findings

- The current promoted tabletop hero remains a readable baseline only
- The old overwrite path is definitively non-physical and remains out of scope
  for the stronger claim.
- The repaired bridge-layer path is now strong enough to prove Stage-0 direct
  finger blocking without touching `Newton/newton/`.
- Stage-0 direct-finger proof surface is now explicit and stable:
  - actual imported finger-box colliders against the native table box
  - `ee_contact_radius` stays diagnostic-only and is not part of final proof
- The rope-integrated path now has working body-truth / artifact-truth
  infrastructure:
  - same-history hero/debug/validation
  - stage-aware blocking validator
  - artifact validator passes
  - `blocking_stage` is now written into the normal `summary.json`
- The main remaining blocker is no longer “can bridge-layer target drive create
  blocking error?”; it is now a presentation/geometry issue:
  - `c10` removes the hidden-preroll preloaded table penetration, but still
    leaves the arm in a long table-loaded posture
  - `c11` / `c12` / `c13` preserve blocking error and rope contact, but the arm
    still ends up visually resting on the table or collapsing late in the clip
  - `c13` raises hold gains enough that mid-clip finger clearances stay
    positive for much longer, but it still fails penetration tolerance late in
    retract (`robot_table_penetration_min_m = -0.00279`)
- Current best truthful interpretation:
  - Stage-0 is solved at the bridge layer
  - Stage-1 is no longer blocked by controller truth
  - Stage-1 is still blocked by a geometry/reference issue in the current
    tabletop joint-space waypoint path when used as a physical blocking
    controller

## Next Step

- Keep the repaired `joint_target_drive` bridge path; do not revert to state
  overwrite and do not touch `Newton/newton/`.
- Retune the direct-finger joint-space waypoint reference itself for the
  blocking task:
  - keep `joint_target_drive` as the execution surface
  - keep actual finger boxes as the proof surface
  - change the blocking task’s desired joint-space reference so only the finger
    reaches the table/rope, not the whole hand/forearm
- Preserve the stronger-task docs truthful and keep the old readable tabletop
  baseline as the only accepted robot-rope authority until a rope-integrated
  candidate is visually honest as well as numerically passing.

## Authority Rule

- Do not modify `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
  from this task
- Only add `results_meta/tasks/robot_rope_franka_physical_blocking.json` after
  a real stronger-task pass
