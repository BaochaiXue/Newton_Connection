# Handoff: robot_table_rope_split_mujoco_semiimplicit

## Current Milestone

Milestone 1: truthful one-way direct-finger split demo.

## What Changed

- task/spec/plan/status surfaces were created
- the split demo and wrapper now exist:
  - `Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
  - `scripts/run_robot_table_rope_split_demo.sh`
- a support-only sweep wrapper now also exists:
  - `scripts/run_robot_table_rope_split_support_sweep.sh`
- a presentation-video wrapper now also exists:
  - `scripts/run_robot_table_rope_split_presentation_video.sh`
- the presentation wrapper now runs the staged pick-place path by default:
  - `--video-mode presentation_pick_place`
  - `--motion-pattern grasp_lift_place`
  - `--rope-rigid-contact-max 8192`
  - `--rope-soft-contact-max 8192`
  - `--no-presentation-grasp-assist`
  - `--presentation-gripper-geometry panda_fingers`
  - `--gripper-yaw 2.89159265359`
  - `--presentation-grasp-closed-opening 0.004`
  - `--presentation-edge-grasp-outset-y 0.000`
  - `--presentation-grasp-x-offset 0.030`
  - `--presentation-grasp-z-clearance 0.006`
  - `--presentation-table-shape-contact-scale 8.0`
- the best-known one-way artifact is:
  - `/tmp/robot_table_rope_split_one_way_fine_v5`
- the split demo now uses the shared bridge mass-scaling path and defaults the
  rope total object mass to `0.1kg`
- the split demo now also defaults the physical rope radius to `0.2x` of the
  previous value through `particle_radius_scale`
- the split demo now defaults to post-settle recording instead of recording the
  manual placement phase
- the current support-passing defaults are:
  - `ground_shape_contact_scale = 1e-3`
  - `ground_shape_contact_damping_multiplier = 64.0`
  - `table_shape_contact_scale = 1e-3`
  - `table_shape_contact_damping_multiplier = 64.0`
  - `finger_shape_contact_scale = 0.1`
  - `finger_shape_contact_damping_multiplier = 1.5`
  - `table_edge_inset_y = 0.17`
  - `overhang_drop_factor = 0.02`
- the default-mass validation artifact is:
  - `/tmp/robot_table_rope_split_weight_0p1_default`
- the default-radius validation artifact is:
  - `/tmp/robot_table_rope_split_radius_0p2_default`
- the authoritative default-support artifact is:
  - `tmp/robot_table_rope_split_support_default_authoritative_20260415`
- the old calibrated-default artifact is still preserved as a failed example:
  - `/tmp/robot_table_rope_split_candidate_c`
- the official `Newton/newton` core has now been refreshed to upstream
  `origin/main = b6a87995`, and the active split bridge path still passes a
  post-update smoke run:
  - `tmp/robot_table_rope_split_post_core_update_smoke_20260415`
- a real two-way bookkeeping bug was fixed:
  - rope reaction wrench is now read from the post-step rope state instead of
    the force-cleared pre-step state
- the previous `strict_contact_only_pass_20260426` video is demoted after
  visual review because it read as rope self-drop under the old, too-local
  lift gate
- the best physics-contact artifact is now:
  - `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427`
  - it is demoted from final meeting-video acceptance by visual review because
    the helper cradle and particle-rope render still look unnatural
- the best native-Panda-finger-only diagnostic is now:
  - `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428`
  - it uses `presentation_gripper_geometry = panda_fingers`, no
    `grasp_assist`, no `rope_cradle`, and no auxiliary pad mesh
  - it is not accepted because `strict_contact_only_pass = false`,
    `rope_lift_height_m = 0.0`, and the rope is contacted rather than carried

## Current Conclusion

The split architecture is now implemented and runs end-to-end. The current
best-known one-way result proves:

- truthful physical-only rope rendering
- simultaneous rope-ground and rope-table support contact
- stable robot path without scraping the table
- support defaults can now satisfy the non-burying gate without any extra
  support override flags

The old side-push motion layout missed `finger first contact`, so the next
presentation attempt changed strategy rather than continuing parameter-only
tuning. Two-way robot-rope reaction remains milestone 2.

There is now also a dedicated presentation path for meeting-facing rendering:

- `video_mode = "presentation_pick_place"`
- `motion_pattern = "grasp_lift_place"`
- `record_start_mode = "visible_opening"`
- `rope_preroll_seconds = 0.0`
- render length is derived from the motion phases instead of a fixed short
  support window
- camera framing is now dedicated to the contact region
- gripper-center-targeted IK is now wired in for the presentation path
- the selected rope segment is at the table edge, where the lower jaw has
  access and does not need to close through the table
- finite-force grasp assist is now disallowed by default for the meeting-video
  path

This fixes the old “wrong artifact type”, “hidden assist”, self-drop
false-positive, and side-suction false-positive problems at the metrics level.
The previous `rope_cradle` candidate remains a demoted physics-contact surface:
it had non-null contact, no assist, balanced contact, whole-rope visible lift,
clean release, and a skeptical-video `PASS`, but user visual review rejected it
because it depended on a visible helper fixture. The current default route is
now stricter: final acceptance requires real Panda finger meshes via
`presentation_gripper_geometry = panda_fingers`.

The new default mass is confirmed by summary fields:

- `rope_current_total_object_mass_kg ~= 0.1`
- `rope_weight_scale ~= 5.7e-05`

The support geometry and contact defaults have now been retuned around that
same `0.1kg` mass so the support gate passes under the current default setup.

The new default radius is also confirmed by summary fields:

- `particle_radius_scale = 0.2`
- `rope_physical_radius_m = rope_render_radius_m = 0.005200476`
- `rope_render_matches_physics = true`

The new default-support artifact confirms both stabilization and low support
penetration:

- `record_start_mode = "post_settle"`
- `rope_table_contact_frames_first_30 = 30`
- `rope_ground_contact_frames_first_30 = 30`
- `robot_table_contact_frames_first_30 = 0`
- `max_support_penetration_m = 0.000639`
- `final_support_penetration_p99_m = 0.0`

So the support-calibration blocker is cleared. `candidate_c` remains a failed
support-calibration example, not an accepted default.

## Exact Next Command

```bash
bash scripts/run_robot_table_rope_split_presentation_video.sh tmp/robot_table_rope_split_presentation_followup --width 960 --height 540
```

## Current Blocker

The blocker is no longer solver instability, support calibration, recording,
basic table-edge contact geometry, grasp assist, side-suction metrics, or the
visible helper route. The active blocker is now true native Panda finger carry:

- the support-default drape is now stable and non-burying
- the presentation video path records a complete visible process and keeps the
  contact window in frame
- the current native-only diagnostic records
  `first_finger_rope_contact_frame = 6` and
  `rope_motion_after_contact = true`
- the current native-only diagnostic records
  `lift_window_contact_balance_ratio = 0.337578` and
  `lift_window_unilateral_finger_rope_contact_frames = 0`, so the first-order
  side-suction metric is no longer the immediate issue
- the current native-only diagnostic still fails carry:
  `rope_lift_height_m = 0.0`,
  `grasp_particle_lift_during_lift_transfer_m = 0.010288`, and
  `nonfinger_table_contact_frames = 7`
- contact-buffer overflow warnings are gone in the latest candidate
- `strict_contact_only_pass = false`
- remaining meeting-video work is to make the native Panda finger pads form a
  real pinch/support structure that lifts and transfers the rope; continuous
  rope rendering remains useful but is secondary until physical carry works

## Last Failed Acceptance Criterion

- previous failed strict-contact artifact:
  - `tmp/robot_table_rope_split_strict_contact_default_20260426/summary.json`
- fail reasons:
  - both fingers did not maintain contact during the lift/transfer window
  - local grasp segment did not lift enough
- fail-closed skeptical review was `FAIL`:
  - `tmp/robot_table_rope_split_strict_contact_default_20260426/review_bundle/skeptical_audit.json`
- self-drop-fix replacement later demoted for side-suction visual:
  - `tmp/robot_table_rope_split_selfdrop_fix_contact_only_20260426/summary.json`
  - `strict_contact_only_pass = true`
  - `rope_lift_height_m = 0.116019`
  - `grasp_particle_lift_during_lift_transfer_m = 0.116898`
  - `tmp/robot_table_rope_split_selfdrop_fix_contact_only_20260426/review_bundle/skeptical_audit.json`
  - skeptical verdict is `PASS`
- demoted side-suction-fix replacement:
  - `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/summary.json`
  - `strict_contact_only_pass = true`
  - `lift_window_contact_balance_ratio = 0.310864`
  - `lift_window_unilateral_finger_rope_contact_frames = 0`
  - `rope_lift_height_m = 0.135920`
  - `grasp_particle_lift_during_lift_transfer_m = 0.153220`
  - `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/review_bundle/skeptical_audit.json`
  - skeptical verdict is `PASS`
- current native-finger diagnostic:
  - `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428/summary.json`
  - `presentation_gripper_geometry = panda_fingers`
  - `presentation_aux_panda_pad_geometry_enabled = false`
  - `strict_contact_only_pass = false`
  - `rope_lift_height_m = 0.0`
  - `grasp_particle_lift_during_lift_transfer_m = 0.010288`
  - `lift_window_contact_balance_ratio = 0.337578`
  - `lift_window_unilateral_finger_rope_contact_frames = 0`

## Key GIF / Artifact Paths

- `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/summary.json`
- `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/hero.mp4`
- `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/hero.gif`
- `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/review_bundle/contact_sheet.png`
- `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/review_bundle/skeptical_audit.json`
- `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428/summary.json`
- `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428/hero.mp4`
- `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428/hero.gif`
- `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428/contact_sheet.jpg`
- `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428/review_bundle/contact_sheet.png`
- `tmp/robot_table_rope_split_selfdrop_fix_contact_only_20260426/summary.json`
- `tmp/robot_table_rope_split_selfdrop_fix_contact_only_20260426/hero.mp4`
- `tmp/robot_table_rope_split_selfdrop_fix_contact_only_20260426/hero.gif`
- `tmp/robot_table_rope_split_strict_contact_default_20260426/summary.json`
- `tmp/robot_table_rope_split_strict_contact_default_20260426/hero.mp4`
- `tmp/robot_table_rope_split_strict_contact_default_20260426/hero.gif`
- `tmp/robot_table_rope_split_strict_contact_default_20260426/review_bundle/contact_sheet.png`
- `tmp/robot_table_rope_split_support_default_authoritative_20260415/summary.json`
- `tmp/robot_table_rope_split_support_default_authoritative_20260415/hero.mp4`
- `tmp/robot_table_rope_split_support_default_authoritative_20260415/first_30_frames_sheet.jpg`
- `tmp/robot_table_rope_split_presentation_smoke_v10_20260416/summary.json`
- `tmp/robot_table_rope_split_presentation_smoke_v10_20260416/hero.mp4`
- `tmp/robot_table_rope_split_presentation_smoke_v10_20260416/contact_sheet.jpg`
- `/tmp/robot_table_rope_split_one_way_fine_v5/summary.json`
- `/tmp/robot_table_rope_split_one_way_fine_v5/hero.mp4`
- `/tmp/robot_table_rope_split_one_way_fine_v5/contact_sheet.jpg`

## What Not To Redo

- do not rebuild this on the retired local robot controller stack
- do not widen rope render thickness for readability
- do not make two-way a hidden prerequisite for first acceptance
- do not go back to coarse rope stepping; the `64`-substep one-way runs were not
  stable enough to trust
- do not re-open support sweep unless the new default-support artifact regresses
- do not treat automatic QC alone as meeting-video acceptance; keep the
  skeptical review bundle attached to the accepted artifact
- do not re-enable, hide, or relabel grasp assist as pure contact-only physics

## Missing Evidence

- a two-way artifact with nonzero rope-to-robot wrench after contact

## Context Reset Recommendation

- recommended: yes
- reason:
  - the task chain now contains the implementation boundary; future agents
    should be able to continue without chat memory
