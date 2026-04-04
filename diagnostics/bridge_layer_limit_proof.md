# Bridge-Layer Limit Proof

Last updated: 2026-04-03

## Question

Can the stronger `robot_rope_franka_physical_blocking` claim be completed
honestly from the bridge/demo layer alone, without touching `Newton/newton/`?

## Short Answer

Not with the currently accessible SemiImplicit articulation control surfaces.

## What Was Exhausted

### 1. Existing tabletop overwrite path

The old readable tabletop path is not physically blocked:

- pre-solve it writes `state_in.joint_q/joint_qd`
- post-solve it writes `state_out.joint_q/joint_qd` back to the target

See:

- [control_update_order_report.md](/home/xinjie/Newton_Connection/diagnostics/control_update_order_report.md)
- [control_timeline.md](/home/xinjie/Newton_Connection/diagnostics/control_timeline.md)
- [suspected_kinematic_override.md](/home/xinjie/Newton_Connection/diagnostics/suspected_kinematic_override.md)

And the stronger blocking diagnostic confirms the failure mode:

- [c20_clean robot_table_contact_report.json](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260403_010241_true0p1_shallowcurve_bx054_by020_bz006_c20_clean/diagnostics_blocking/robot_table_contact_report.json)
  reports:
  - `robot_table_penetration_min_m = -0.037999`
  - `ee_target_to_actual_error_during_block_mean_m = 2.5e-6`

That is deep table penetration with effectively zero tracking error.

### 2. `joint_target_drive` bridge-layer path

A stronger bridge/demo-only path was added:

- new control mode:
  [demo_robot_rope_franka.py](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py)
  `--tabletop-control-mode joint_target_drive`
- new wrapper:
  [run_robot_rope_franka_physical_blocking.sh](/home/xinjie/Newton_Connection/scripts/run_robot_rope_franka_physical_blocking.sh)
- new blocking diagnostic:
  [diagnose_robot_rope_physical_blocking.py](/home/xinjie/Newton_Connection/scripts/diagnose_robot_rope_physical_blocking.py)
- new blocking validator:
  [validate_robot_rope_franka_physical_blocking.py](/home/xinjie/Newton_Connection/scripts/validate_robot_rope_franka_physical_blocking.py)

Observed outcomes:

- early drive attempts (`c01/c02`) became numerically unstable and yielded
  `nan/inf`
- lower-gain retries (`c03/c04/c05`) stabilized numerically, but the robot
  still did not physically reach the rope

Example:

- [c04 presentation summary](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260403_104425_jointdrive_c04_copyfix_lowgains/presentation/work/robot_rope_tabletop_hero_summary.json)
  reports:
  - `tabletop_control_mode = joint_target_drive`
  - `gripper_center_tracking_error_mean_m = 0.07086`
  - `gripper_center_path_length_m = 0.0`
  - `actual_finger_box_contact_started = false`

Interpretation:

- the new path stopped faking zero error
- but the accessible bridge-layer target path still did not yield actual
  articulated motion into the rope-contact line

### 3. Isolated control-surface smokes

I also tested minimal isolated actuation on the same native Franka build path by
setting a clearly different desired joint target and stepping SemiImplicit for
hundreds of substeps.

Tested surfaces:

- `control.joint_target_pos`
- `model.joint_target_pos`
- `control.joint_f` using a simple PD torque law
- with and without contacts

Observed result:

- `joint_q` remained unchanged in all variants
- measured `delta_norm = 0.0` after 500 substeps in every tested case

Interpretation:

- the currently accessible bridge/demo articulation actuation surfaces are not
  producing actual joint motion on this SemiImplicit native Franka path

## Conclusion

At the bridge/demo layer we can:

- diagnose the old kinematic overwrite correctly
- validate table penetration and target-vs-actual error honestly
- add stronger-task tooling and result structure

But we cannot currently complete the stronger physically blocked robot-contact
claim honestly because the needed SemiImplicit articulation actuation path does
not produce real robot motion from the accessible bridge/demo surfaces.

That is a bridge-layer limit and should not be papered over with more camera or
trajectory tweaks.
