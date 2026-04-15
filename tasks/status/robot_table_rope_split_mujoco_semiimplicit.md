> status: active
> canonical_replacement: none
> owner_surface: `robot_table_rope_split_mujoco_semiimplicit`
> last_reviewed: `2026-04-13`
> review_interval: `7d`
> update_rule: `Update after each meaningful milestone or experiment run.`
> notes: Live status log for the split MuJoCo robot/table + SemiImplicit rope demo.

# Status: robot_table_rope_split_mujoco_semiimplicit

## Current State

- Active
- Split demo and canonical wrapper are implemented
- Default one-way recording now starts from post-settle state instead of the
  manual placement frame
- The split demo now measures support penetration explicitly and rejects buried
  support candidates
- No current parameter set has yet passed the full `no fly-away + no burying`
  gate
- `finger first contact` is still not achieved, so milestone 1 is not yet
  accepted

## What Changed In The Latest Pass

- added bridge-side support penetration proxy metrics:
  - `max_ground_penetration_m`
  - `max_table_penetration_m`
  - `max_support_penetration_m`
  - `final_ground_penetration_p99_m`
  - `final_table_penetration_p99_m`
  - `final_support_penetration_p99_m`
- changed the support calibration gate:
  - support contact counts alone are no longer enough
  - buried candidates now fail closed
- downgraded `candidate_c` from provisional success to failed support
  candidate:
  - it keeps rope-table and rope-ground contact
  - but fails the new burying gate with large ground penetration
- ran a new default-parameter validation artifact with the penetration gate:
  - `/tmp/robot_table_rope_split_penetration_gate_default`
- added hidden pre-roll and post-settle recording:
  - default `rope_preroll_seconds = 2.0`
  - `record_start_mode = "post_settle"`
- added split-local shape-contact scaling controls for:
  - ground
  - table
  - finger mirror bodies
- fixed initial table placement so the on-table rope particles no longer start
  inside the tabletop
- added support-stability metrics to `summary.json`:
  - `rope_table_contact_frames_first_30`
  - `rope_ground_contact_frames_first_30`
  - `max_rope_com_z_first_30`
  - `max_abs_delta_rope_com_z_first_30`
- added `first_30_frames_sheet.jpg`
- implemented a light-rope calibration path; the first previously accepted
  candidate is no longer accepted under the new gate:
  - `ground_shape_contact_scale = 1e-5`
  - `ground_shape_contact_damping_multiplier = 8.0`
  - `table_shape_contact_scale = 1e-5`
  - `table_shape_contact_damping_multiplier = 8.0`
  - `finger_shape_contact_scale = 0.1`
  - `finger_shape_contact_damping_multiplier = 1.5`
  - `table_edge_inset_y = 0.17`
  - `overhang_drop_factor = 0.15`
- former candidate artifact now treated as a failed calibration example:
  - `/tmp/robot_table_rope_split_candidate_c`
- changed the split demo default physical rope radius to `0.2x` of the old
  value by setting `--particle-radius-scale` default to `0.2`
- kept physical/render consistency intact:
  - `rope_physical_radius_m == rope_render_radius_m`
  - `rope_render_matches_physics == true`
- added `particle_radius_scale` to `summary.json`
- ran the new default-radius validation artifact:
  - `/tmp/robot_table_rope_split_radius_0p2_default`
- connected the split demo to the shared bridge mass-scaling path:
  - `auto_set_weight`
  - `mass_spring_scale`
  - `object_mass`
  - `_effective_spring_scales(...)`
- changed the split demo default rope total object mass to `0.1kg`
- added summary fields:
  - `rope_original_total_object_mass_kg`
  - `rope_current_total_object_mass_kg`
  - `rope_weight_scale`
  - `rope_mass_spring_scale`
  - `rope_object_mass_per_particle_kg`
- ran the new default-weight check:
  - `/tmp/robot_table_rope_split_weight_0p1_default`
- added:
  - `Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
  - `scripts/run_robot_table_rope_split_demo.sh`
- implemented the split runtime:
  - native Panda + native rigid table on `SolverMuJoCo`
  - PhysTwin rope on `SolverSemiImplicit`
  - rope-side finger mirror bodies using direct finger/pad mesh
  - physical-only rope render radius
- fixed a real two-way scaffold bug:
  - rope-side reaction wrench is now read from the post-step rope state instead
    of the pre-step force-cleared state
- ran multiple one-way and two-way experiments; the current best-known artifact
  is:
  - `/tmp/robot_table_rope_split_one_way_fine_v5`

## Problem Being Solved

- the repo needs a current direct-finger robot/table/rope path that follows
  official native patterns instead of retired local robot semantics

## Findings / Conclusions So Far

- first acceptance should be one-way
- robot/table should stay on the MuJoCo rigid path already proven by the native
  penetration probe
- rope-side finger contact must use direct finger/pad mesh and physical render
  thickness
- coarse rope stepping is not good enough for this split scene:
  - `sim-substeps-rope=64` let the rope drift badly and is not an acceptance path
- the truthful one-way baseline needs the fine rope timestep:
  - best-known stable run used `rope_substep_dt_s = 4.9975e-05`
- current best-known one-way result is:
  - `robot_table_contact_frames = 0`
  - `rope_table_contact_frames = 120`
  - `rope_ground_contact_frames = 117`
  - `rope_render_matches_physics = true`
  - `first_finger_rope_contact_frame = null`
- new default mass result confirms the mass change is live:
  - `rope_original_total_object_mass_kg = 1753.0`
  - `rope_current_total_object_mass_kg = 0.100000016`
  - `rope_weight_scale = 5.7045e-05`
  - `rope_render_matches_physics = true`
- new default radius result confirms the physical-thin rope path is live:
  - `particle_radius_scale = 0.2`
  - `rope_physical_radius_m = 0.005200476`
  - `rope_render_radius_m = 0.005200476`
  - `rope_render_matches_physics = true`
- the former `candidate_c` result is now known to be buried:
  - `rope_table_contact_frames_first_30 = 30`
  - `rope_ground_contact_frames_first_30 = 30`
  - `robot_table_contact_frames_first_30 = 0`
  - `max_rope_com_z_first_30 = -0.02668`
  - `max_support_penetration_m = 0.05157`
  - `final_support_penetration_p99_m = 0.04519`
- the current default parameter set is also not acceptable under the new gate:
  - `/tmp/robot_table_rope_split_penetration_gate_default`
  - `rope_table_contact_frames_first_30 = 30`
  - `rope_ground_contact_frames_first_30 = 30`
  - `max_support_penetration_m = 0.05157`
  - `final_support_penetration_p99_m = 0.04519`
- current blocker is geometric, not architectural:
  - the split stack, render truth, and support contacts are working together
  - the current support-parameter search still needs a truly non-burying
    support candidate before finger-targeting should resume

## Artifact Paths To Review

- best-known one-way artifact:
  - `/tmp/robot_table_rope_split_one_way_fine_v5/summary.json`
  - `/tmp/robot_table_rope_split_one_way_fine_v5/hero.mp4`
  - `/tmp/robot_table_rope_split_one_way_fine_v5/hero.gif`
  - `/tmp/robot_table_rope_split_one_way_fine_v5/contact_sheet.jpg`
- default-weight validation artifact:
  - `/tmp/robot_table_rope_split_weight_0p1_default/summary.json`
  - `/tmp/robot_table_rope_split_weight_0p1_default/hero.mp4`
  - `/tmp/robot_table_rope_split_weight_0p1_default/hero.gif`
  - `/tmp/robot_table_rope_split_weight_0p1_default/contact_sheet.jpg`
- default-radius validation artifact:
  - `/tmp/robot_table_rope_split_radius_0p2_default/summary.json`
  - `/tmp/robot_table_rope_split_radius_0p2_default/hero.mp4`
  - `/tmp/robot_table_rope_split_radius_0p2_default/hero.gif`
  - `/tmp/robot_table_rope_split_radius_0p2_default/contact_sheet.jpg`
- current calibrated-default artifact:
  - `/tmp/robot_table_rope_split_candidate_c/summary.json`
  - `/tmp/robot_table_rope_split_candidate_c/hero.mp4`
  - `/tmp/robot_table_rope_split_candidate_c/hero.gif`
  - `/tmp/robot_table_rope_split_candidate_c/contact_sheet.jpg`
  - `/tmp/robot_table_rope_split_candidate_c/first_30_frames_sheet.jpg`
- penetration-gate default artifact:
  - `/tmp/robot_table_rope_split_penetration_gate_default/summary.json`
  - `/tmp/robot_table_rope_split_penetration_gate_default/hero.mp4`
  - `/tmp/robot_table_rope_split_penetration_gate_default/contact_sheet.jpg`
- comparison / failed tuning artifacts:
  - `/tmp/robot_table_rope_split_one_way_check`
  - `/tmp/robot_table_rope_split_one_way_fine`
  - `/tmp/robot_table_rope_split_one_way_fine_v6`

## Next Step

- keep the current solver split and render rules unchanged
- the next step is support recalibration under the new non-burying gate:
  find the first candidate with
  - persistent table + ground support
  - `max_support_penetration_m <= 0.003`
  - `final_support_penetration_p99_m <= 0.001`
- only after that should finger-targeting resume

## Validation

- `python -m py_compile Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
- `bash scripts/run_robot_table_rope_split_demo.sh /tmp/robot_table_rope_split_one_way_fine_v5 --num-frames 120 --coupling-mode one_way`
- `python scripts/validate_experiment_artifacts.py /tmp/robot_table_rope_split_one_way_fine_v5 --require-video --require-gif --summary-field rope_motion_after_contact --summary-field rope_render_matches_physics`
- `bash scripts/run_robot_table_rope_split_demo.sh /tmp/robot_table_rope_split_weight_0p1_default --num-frames 120 --coupling-mode one_way`
- `python scripts/validate_experiment_artifacts.py /tmp/robot_table_rope_split_weight_0p1_default --require-video --require-gif --summary-field rope_current_total_object_mass_kg --summary-field rope_weight_scale --summary-field rope_render_matches_physics`
- `bash scripts/run_robot_table_rope_split_demo.sh /tmp/robot_table_rope_split_radius_0p2_default --num-frames 120 --coupling-mode one_way`
- `python scripts/validate_experiment_artifacts.py /tmp/robot_table_rope_split_radius_0p2_default --require-video --require-gif --summary-field rope_current_total_object_mass_kg --summary-field particle_radius_scale --summary-field rope_render_matches_physics`
- `bash scripts/run_robot_table_rope_split_demo.sh /tmp/robot_table_rope_split_candidate_c --num-frames 30 --coupling-mode one_way --ground-shape-contact-scale 1e-5 --ground-shape-contact-damping-multiplier 8.0 --table-shape-contact-scale 1e-5 --table-shape-contact-damping-multiplier 8.0 --finger-shape-contact-scale 0.1 --finger-shape-contact-damping-multiplier 1.5 --table-edge-inset-y 0.17 --overhang-drop-factor 0.15`
- `bash scripts/run_robot_table_rope_split_demo.sh /tmp/robot_table_rope_split_penetration_gate_default --num-frames 30 --coupling-mode one_way`
