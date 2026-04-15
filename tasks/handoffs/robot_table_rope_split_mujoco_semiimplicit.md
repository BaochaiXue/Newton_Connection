# Handoff: robot_table_rope_split_mujoco_semiimplicit

## Current Milestone

Milestone 1: truthful one-way direct-finger split demo.

## What Changed

- task/spec/plan/status surfaces were created
- the split demo and wrapper now exist:
  - `Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
  - `scripts/run_robot_table_rope_split_demo.sh`
- the best-known one-way artifact is:
  - `/tmp/robot_table_rope_split_one_way_fine_v5`
- the split demo now uses the shared bridge mass-scaling path and defaults the
  rope total object mass to `0.1kg`
- the split demo now also defaults the physical rope radius to `0.2x` of the
  previous value through `particle_radius_scale`
- the split demo now defaults to post-settle recording instead of recording the
  manual placement phase
- the current calibrated defaults are:
  - `ground_shape_contact_scale = 1e-5`
  - `ground_shape_contact_damping_multiplier = 8.0`
  - `table_shape_contact_scale = 1e-5`
  - `table_shape_contact_damping_multiplier = 8.0`
  - `finger_shape_contact_scale = 0.1`
  - `finger_shape_contact_damping_multiplier = 1.5`
  - `table_edge_inset_y = 0.17`
  - `overhang_drop_factor = 0.15`
- the default-mass validation artifact is:
  - `/tmp/robot_table_rope_split_weight_0p1_default`
- the default-radius validation artifact is:
  - `/tmp/robot_table_rope_split_radius_0p2_default`
- the current calibrated-default artifact is:
  - `/tmp/robot_table_rope_split_candidate_c`
- a real two-way bookkeeping bug was fixed:
  - rope reaction wrench is now read from the post-step rope state instead of
    the force-cleared pre-step state

## Current Conclusion

The split architecture is now implemented and runs end-to-end. The current
best-known one-way result proves:

- truthful physical-only rope rendering
- simultaneous rope-ground and rope-table support contact
- stable robot path without scraping the table

But the current motion layout still misses `finger first contact`, so milestone
1 is not yet accepted. Two-way robot-rope reaction remains milestone 2.

The new default mass is confirmed by summary fields:

- `rope_current_total_object_mass_kg ~= 0.1`
- `rope_weight_scale ~= 5.7e-05`

but the current `0.1kg` default also weakens persistent table/ground support in
the existing scene layout, so that geometry must be retuned next.

The new default radius is also confirmed by summary fields:

- `particle_radius_scale = 0.2`
- `rope_physical_radius_m = rope_render_radius_m = 0.005200476`
- `rope_render_matches_physics = true`

The current calibrated-default artifact confirms the first-second stabilization:

- `record_start_mode = "post_settle"`
- `rope_table_contact_frames_first_30 = 30`
- `rope_ground_contact_frames_first_30 = 30`
- `robot_table_contact_frames_first_30 = 0`
- `max_rope_com_z_first_30 = -0.02668`

This is no longer sufficient. The task now also requires a non-burying gate.
The current candidate and the current default both fail it:

- `max_support_penetration_m = 0.05157`
- `final_support_penetration_p99_m = 0.04519`

So `candidate_c` must be treated as a failed support-calibration example, not
as an accepted default.

## Exact Next Command

```bash
bash scripts/run_robot_table_rope_split_demo.sh /tmp/robot_table_rope_split_one_way_fine_v5 --num-frames 120 --coupling-mode one_way
```

## Current Blocker

The blocker is no longer solver instability. The blocker is geometric:

- the current table-edge drape is stable
- the finger path no longer scrapes the table in the best-known run
- but the leading finger still does not intersect the settled tabletop rope
  segment early enough to register first contact

## Last Failed Acceptance Criterion

- `first_finger_rope_contact_frame` is still `null` in the best-known one-way
  fine-step artifact
- in the new default-mass validation run, support contact is only brief:
  - `rope_table_contact_frames = 1`
  - `rope_ground_contact_frames = 2`

## Key GIF / Artifact Paths

- `/tmp/robot_table_rope_split_one_way_fine_v5/summary.json`
- `/tmp/robot_table_rope_split_one_way_fine_v5/hero.mp4`
- `/tmp/robot_table_rope_split_one_way_fine_v5/contact_sheet.jpg`

## What Not To Redo

- do not rebuild this on the retired local robot controller stack
- do not widen rope render thickness for readability
- do not make two-way a hidden prerequisite for first acceptance
- do not go back to coarse rope stepping; the `64`-substep one-way runs were not
  stable enough to trust

## Missing Evidence

- a one-way artifact with non-null `first_finger_rope_contact_frame`
- a first-contact window where the leading pad is the purposeful contactor
- a two-way artifact with nonzero rope-to-robot wrench after contact

## Context Reset Recommendation

- recommended: yes
- reason:
  - the task chain now contains the implementation boundary; future agents
    should be able to continue without chat memory
