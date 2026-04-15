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

## Current Conclusion

The split architecture is now implemented and runs end-to-end. The current
best-known one-way result proves:

- truthful physical-only rope rendering
- simultaneous rope-ground and rope-table support contact
- stable robot path without scraping the table
- support defaults can now satisfy the non-burying gate without any extra
  support override flags

But the current motion layout still misses `finger first contact`, so milestone
1 is not yet accepted. Two-way robot-rope reaction remains milestone 2.

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
bash scripts/run_robot_table_rope_split_demo.sh tmp/robot_table_rope_split_finger_targeting_next --num-frames 120 --coupling-mode one_way
```

## Current Blocker

The blocker is no longer solver instability or support calibration. The blocker
is geometric:

- the support-default drape is now stable and non-burying
- the finger path no longer scrapes the table
- but the leading finger still does not intersect the settled tabletop rope
  segment early enough to register first contact

## Last Failed Acceptance Criterion

- `first_finger_rope_contact_frame` is still `null` in the best-known one-way
  fine-step artifact
- the task still lacks a run where finger contact is detected before rope motion

## Key GIF / Artifact Paths

- `tmp/robot_table_rope_split_support_default_authoritative_20260415/summary.json`
- `tmp/robot_table_rope_split_support_default_authoritative_20260415/hero.mp4`
- `tmp/robot_table_rope_split_support_default_authoritative_20260415/first_30_frames_sheet.jpg`
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

## Missing Evidence

- a one-way artifact with non-null `first_finger_rope_contact_frame`
- a first-contact window where the leading pad is the purposeful contactor
- a two-way artifact with nonzero rope-to-robot wrench after contact

## Context Reset Recommendation

- recommended: yes
- reason:
  - the task chain now contains the implementation boundary; future agents
    should be able to continue without chat memory
