# Contact Reference Offset Report

- promoted c12 target semantics: `joint_trajectory_fk_gripper_center`
- c12 mean target -> gripper center offset: `0.000003 m`
- c12 mean target -> left finger center offset: `0.040000 m`
- c12 mean target -> right finger center offset: `0.040000 m`
- c12 mean target -> nearest finger-box surface distance: `0.042400 m`

## Interpretation

The commanded tabletop reference is aligned to gripper-center semantics, while the real contact-capable geometry lives on the finger boxes several centimeters away.
This is the clearest primary mechanism explaining why a sphere centered on the reference point could appear necessary.
- c12 first-contact gripper-center -> actual contact surface distance: `0.078049 m`
  XY component: `0.048853 m`
  Z component: `0.060869 m`

