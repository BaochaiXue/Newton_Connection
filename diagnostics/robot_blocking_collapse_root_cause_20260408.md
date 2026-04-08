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

## Final Root-Cause Statement

The robot “collapses” in the stronger demo because that demo is the first path
that actually exposes robot-side dynamics.

The accepted demo does not collapse because it uses `joint_trajectory`, which
forces joint state directly and therefore suppresses the same tracking error.

Within the stronger path, the immediate sag is caused primarily by:

1. `joint_target_drive` preserving real tracking error instead of overwriting it
2. a pre-pose / approach family that is not gravity-stable under the current
   articulation tracking gains
3. later support-box contact only as a secondary contributor

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
rather than from the current lowprofile joint arrays alone:

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
