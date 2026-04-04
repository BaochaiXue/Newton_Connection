# Suspected Kinematic Override

Last updated: 2026-04-03

## Claim

The tabletop `joint_trajectory` path is not merely "stiff PD". It is a direct
joint-state override path.

## Strongest Proof

For [c20_clean](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260403_010241_true0p1_shallowcurve_bx054_by020_bz006_c20_clean),
the new blocking diagnostic reports:

- `robot_table_penetration_min_m = -0.037999`
- `ee_target_to_actual_error_during_block_mean_m = 2.5e-6`

Those two numbers are incompatible with honest physical blocking. If contact
were truly blocking the robot, several centimeters of table penetration would
not coexist with micrometer-scale target-tracking error.

## Likely Resolution

Keep the tabletop joint path as the desired reference, but stop writing joint
state directly. Drive the articulation through `model.control()` /
`control.joint_target_pos` / `control.joint_target_vel`, and allow solver
contact to create tracking error.
