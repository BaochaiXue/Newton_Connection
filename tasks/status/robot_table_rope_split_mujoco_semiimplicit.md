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
- Best-known one-way fine-step artifact proves stable rope/table/ground support
  contact with physical-only rope rendering
- `finger first contact` is still not achieved, so milestone 1 is not yet
  accepted

## What Changed In The Latest Pass

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
- current blocker is geometric, not architectural:
  - the split stack, render truth, and support contacts are working together
  - the leading finger still misses the settled rope segment in the current
    scene/motion layout

## Artifact Paths To Review

- best-known one-way artifact:
  - `/tmp/robot_table_rope_split_one_way_fine_v5/summary.json`
  - `/tmp/robot_table_rope_split_one_way_fine_v5/hero.mp4`
  - `/tmp/robot_table_rope_split_one_way_fine_v5/hero.gif`
  - `/tmp/robot_table_rope_split_one_way_fine_v5/contact_sheet.jpg`
- comparison / failed tuning artifacts:
  - `/tmp/robot_table_rope_split_one_way_check`
  - `/tmp/robot_table_rope_split_one_way_fine`
  - `/tmp/robot_table_rope_split_one_way_fine_v6`

## Next Step

- keep the current solver split and render rules unchanged
- add better rope-segment targeting diagnostics, then retune the finger motion
  against the settled tabletop rope segment instead of continuing blind

## Validation

- `python -m py_compile Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
- `bash scripts/run_robot_table_rope_split_demo.sh /tmp/robot_table_rope_split_one_way_fine_v5 --num-frames 120 --coupling-mode one_way`
- `python scripts/validate_experiment_artifacts.py /tmp/robot_table_rope_split_one_way_fine_v5 --require-video --require-gif --summary-field rope_motion_after_contact --summary-field rope_render_matches_physics`
