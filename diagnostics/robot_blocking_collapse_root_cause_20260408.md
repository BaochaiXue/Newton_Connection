# Robot Blocking Collapse Root Cause (2026-04-08)

## Question

Why does the stronger `joint_target_drive` robot-blocking path visibly sag or
collapse into the table, while the accepted tabletop demo stays readable?

## Compared Surfaces

- Accepted readable demo:
  - `Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/summary.json`
  - `Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/run_command.txt`
- Stronger physical-blocking path:
  - `Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_194810_rope_integrated_c15_lowprofile_shortretract/summary.json`
  - `Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_194810_rope_integrated_c15_lowprofile_shortretract/robot_table_contact_report.json`
  - `Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260408_062738_rope_integrated_support_box_shortsettle_probe/summary.json`
  - `Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260408_062738_rope_integrated_support_box_shortsettle_probe/robot_table_contact_report.json`
- Isolating diagnostic run:
  - `tmp_vis/robot_drive_vs_hero_base_test/drive_hero_base_test_summary.json`
  - `tmp_vis/robot_drive_vs_hero_base_test/drive_hero_base_test.mp4`

## Findings

### 1. The accepted demo and the stronger demo do not use the same control semantics

- Accepted readable demo:
  - `--tabletop-control-mode joint_trajectory`
  - source path in `demo_robot_rope_franka.py`:
    - before `solver.step(...)`, it writes `state_in.joint_q/joint_qd`
    - after `solver.step(...)`, it writes the same target back to `state_out`
- Stronger blocking path:
  - `--tabletop-control-mode joint_target_drive`
  - it writes desired joints into `model.control().joint_target_pos`
  - after `solver.step(...)`, it only recovers reduced coordinates with
    `eval_ik(...)`

Conclusion:

- the accepted demo is effectively kinematic at the robot layer
- the stronger path is physically actuated and therefore preserves tracking
  error under gravity/contact

This alone explains why the accepted demo can stay visually clean while the
stronger path can sag.

### 2. The stronger path starts table contact almost immediately, during `settle`

Evidence:

- accepted readable demo:
  - `first_contact_phase = approach`
  - `first_contact_time_s = 1.6675`
  - `gripper_center_tracking_error_during_contact_mean_m ≈ 2.5e-6`
- stronger path `c15`:
  - `first_contact_phase = settle`
  - `first_contact_time_s = 0.10005`
  - `robot_table_first_contact_time_s = 0.1334`
  - `robot_table_contact_duration_s = 5.4694`
  - `ee_target_to_actual_error_during_block_mean_m = 0.0712`
- stronger path `support_box_shortsettle_probe`:
  - `first_contact_phase = settle`
  - `first_contact_time_s = 0.10005`
  - `robot_table_first_contact_time_s = 0.1334`
  - `robot_table_contact_duration_s = 5.50275`
  - `ee_target_to_actual_error_during_block_mean_m = 0.0660`

Conclusion:

- the stronger path is not failing because of a late random collapse
- it is already table-loaded almost from the start of the visible clip

### 3. The backstop/support box is not the first cause

The isolating diagnostic run keeps the accepted hero base offset
`(-0.56, -0.22, 0.10)` and uses `render_only` support geometry, but switches the
control mode to `joint_target_drive`:

- `tmp_vis/robot_drive_vs_hero_base_test/drive_hero_base_test_summary.json`
  - `first_contact_phase = settle`
  - `first_contact_time_s = 0.1334`
  - `table_contact_duration_s = 1.334`
  - `gripper_center_tracking_error_during_contact_mean_m = 0.0976`

Conclusion:

- even without the physical support box, `joint_target_drive` already sags into
  early settle contact
- support-box tuning matters later, but it is not the first root cause

### 4. The first root cause is under-supported articulation tracking at the chosen pre-pose

The same isolating diagnostic shows:

- target gripper `z` stays at `0.362 m` during early `settle`
- actual gripper `z` drops from `0.362` to about `0.279` within the first few
  frames
- the target is not moving yet, so this is not a path-following mistake

Conclusion:

- at the current pre-pose and current articulation gains, `joint_target_drive`
  does not hold the robot up against gravity/contact loading
- the accepted demo hides this because it is not using physically actuated
  robot tracking at all

### 5. Rewriting the controller surface alone is not enough

The repo already contains a more native-style rewrite:

- `Newton/phystwin_bridge/demos/demo_robot_rope_franka_native_v2.py`

That path already does the structurally correct things:

- Cartesian phase targets
- native Newton IK every step
- writes both `control.joint_target_pos` and `control.joint_target_vel`
- keeps `state_out.body_q` as truth and resyncs reduced coordinates with
  `eval_ik(...)`

But a short probe still sags immediately:

- `tmp_vis/native_v2_probe/native_v2_probe_body_q.npy`
- `tmp_vis/native_v2_probe/native_v2_probe_ee_target_pos.npy`

Observed:

- target gripper `z` stays at about `0.5079 m`
- actual gripper `z` drops to about `0.2549 m` within the first 8 frames
- target error grows to about `0.254 m`

Conclusion:

- the problem is deeper than “our old controller shape was wrong”
- on the current bridge-side `SolverSemiImplicit` robot path, articulation
  target tracking is still too weak against gravity/contact even under the
  cleaner native-style command structure

### 6. Why official Newton robot demos do not show the same collapse

Official Newton Franka examples are not using the same rigid-body control path.

For example:

- `Newton/newton/newton/examples/contacts/example_brick_stacking.py`
- `Newton/newton/newton/examples/ik/example_ik_cube_stacking.py`

Those examples:

- use `SolverMuJoCo`, not `SolverSemiImplicit`
- enable explicit gravity compensation through
  `mujoco:jnt_actgravcomp` and `mujoco:gravcomp`
- use much larger joint target gains than the current bridge defaults

Therefore the official demos are not a proof that the current bridge-side
SemiImplicit Franka path should remain upright automatically under the same
conditions.

## Final Root-Cause Statement

The robot “collapses” in the stronger demo because that demo is the first path
that actually exposes robot-side dynamics.

The accepted demo does not collapse because it uses `joint_trajectory`, which
forces joint state directly and therefore suppresses the same tracking error.

Within the stronger path, the immediate sag is caused primarily by:

1. `joint_target_drive` preserving real tracking error instead of overwriting it
2. a pre-pose / approach family that is not gravity-stable under the current
   articulation tracking gains
3. lack of MuJoCo-style gravity compensation on the current bridge-side
   SemiImplicit articulation path
4. later support-box contact only as a secondary contributor

## Fix Plan

### Immediate honesty fix

- A rope-integrated blocking run must no longer pass if:
  - `first_contact_phase = settle`, or
  - first contact happens before the end of `tabletop_settle_seconds`

This is now enforced in `scripts/validate_robot_rope_franka_physical_blocking.py`.

### Minimal bridge-layer motion fix

Do not reuse the current `blocking_lowprofile` family as the presentation path.

Instead:

1. build a new `joint_target_drive` reference family from solver-compatible
   high-clearance poses
2. require first finger-table contact to begin in `approach` or `push`, not in
   `settle`
3. keep the support box off or `render_only` until the direct-finger path has a
   clean late-onset contact story again

### Recommended next implementation step

Create a new blocking reference family derived from the accepted hero waypoints
rather than from the current lowprofile joint arrays alone, but do not expect
that change alone to solve the whole issue:

- keep `joint_target_drive`
- keep bridge-layer truth (no post-solve overwrite)
- fit a new pre/approach pose family that stays above the table during
  `settle`
- only then reintroduce bounded later support-box contact if needed

### Secondary improvement

After the pose family is fixed, test velocity feedforward on the drive path:

- write nonzero `joint_target_vel` from the phase delta

This may improve tracking during motion, but it is not the first fix because it
does not explain the sag that already appears while the target pose is static.

### Likely Real Repair

If the goal is to satisfy all three simultaneously:

1. robot stays upright
2. table can physically block it
3. finger still pushes the rope

then the bridge likely needs one more ingredient beyond pose cleanup:

- bridge-side gravity-compensation or equivalent feedforward through
  `control.joint_f`

Without that, the current SemiImplicit articulation path keeps showing the same
failure even after controller-structure cleanup.

## Current Practical Fix

The canonical stronger-task wrapper now defaults to the first verified
bridge-layer mitigation:

- no physical support box by default
- short visible settle: `tabletop_settle_seconds = 0.05`
- accepted-hero base offset: `(-0.56, -0.22, 0.10)`

Validated candidate:

- `Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260408_092911_rope_integrated_auto_fix_20260408`

Observed:

- `blocking_metrics.json -> overall_pass = true`
- `robot_table_first_contact_phase = approach`
- `frame0_table_overlap_absent = true`
- `nonfinger_table_contact_duration_s = 0.0`
- `collapse_after_retract_detected = false`
- `rope_com_displacement_m = 0.01887`

Interpretation:

- this is a real improvement to the default stronger-demo entrypoint at the
  numeric gate level
- however stricter visual review of the full clip still shows a visibly
  collapsed low posture by the middle of the video
- therefore this is not yet sufficient as the final meeting-grade direct-finger
  stronger demo

## Latest Negative Results

### Accepted-family retry

Probe:

- `tmp_vis/accepted_family_probe/accepted_family_probe.mp4`

Result:

- rope motion remains real
- but the robot is still visibly collapsed by the middle of the clip

Conclusion:

- changing back from `blocking_lowprofile` to the accepted joint family alone
  does not solve the stricter display problem

### First bridge-side gravity-compensation attempt

Implementation:

- `demo_robot_rope_franka.py`
- new knob: `--joint-gravity-comp-scale`

Tests:

- `tmp_vis/gravcomp_probe/gravcomp_probe.mp4`
  - `joint_gravity_comp_scale = 1.0`
- `tmp_vis/gravcomp_pos5/gravcomp_pos5.mp4`
  - `joint_gravity_comp_scale = 5.0`

Result:

- scale `1.0` still shows visible collapse
- scale `5.0` suppresses rope contact entirely

Conclusion:

- the first simple `J^T m g` feedforward approximation is not yet a working
  repair
