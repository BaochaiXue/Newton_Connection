# Implementation: pure_semiimplicit_robot_loaded_object

## Current Approach

Build a new bridge demo that places Panda, a rigid table, ground, and an
object-only PhysTwin rope IR into one `newton.ModelBuilder`, then steps the
whole model with `newton.solvers.SolverSemiImplicit`.

Motion targets are scheduled by integrated `sim_time`, not by rendered frame
index. When using very small `--sim-dt`, choose `--sim-substeps` and
`--video-fps` so `sim_dt * sim_substeps` matches the intended rendered frame
time if the video should play at physical speed.

For the required positive two-way coupling demo, use the simplified dynamic
proxy robot pusher. It keeps the robot state solver-owned and uses the same
PhysTwin-like rope IR, but does not claim full Panda dynamics.

## Required Mechanics

- Use `add_urdf()` for Panda and follow the current Panda contact setup.
- Build SDF/hydroelastic contact only for finger/hand meshes where needed.
- Add PhysTwin object particles and springs with the shared IR importer.
- Reposition the object onto the table edge from its object-only bounding box.
- Drive the robot through IK and `control.joint_target_pos`.
- Step through `model.collide()` plus `SolverSemiImplicit.step()`.
- Collect rigid and soft contact counts from the same `contacts` object.
- Save summary, timeseries, scene, video, GIF, and contact sheet.

## Validation Commands

```bash
python -m py_compile Newton/phystwin_bridge/demos/demo_pure_semiimplicit_robot_loaded_object.py
bash -n scripts/run_pure_semiimplicit_robot_loaded_object_demo.sh
bash scripts/run_pure_semiimplicit_robot_loaded_object_demo.sh tmp/pure_semiimplicit_robot_loaded_object_timing_fixed_smoke --num-frames 60 --video-fps 1000 --sim-substeps 100 --sim-dt 1.0e-5 --settle-seconds 0.004 --approach-seconds 0.010 --push-seconds 0.030 --table-probe-seconds 0.010 --retract-seconds 0.006 --push-distance 0.06 --width 640 --height 360
python scripts/validate_experiment_artifacts.py tmp/pure_semiimplicit_robot_loaded_object_timing_fixed_smoke --require-video --require-gif --summary-field pure_semiimplicit --summary-field solver_owned_robot_state --summary-field rope_motion_after_contact --summary-field table_blocking_attempted --summary-field numerics_finite --summary-field ik_fallback_frames --summary-field motion_time_source

python -m py_compile Newton/phystwin_bridge/demos/demo_proxy_robot_rope_two_way.py
bash -n scripts/run_proxy_robot_rope_two_way_demo.sh
bash scripts/run_proxy_robot_rope_two_way_demo.sh tmp/proxy_robot_rope_two_way_soft --num-frames 360 --video-fps 60 --sim-substeps 20 --sim-dt 5.0e-5 --settle-seconds 0.02 --push-seconds 0.22 --hold-seconds 0.10 --robot-mass 0.5 --robot-drive-kp 70 --robot-drive-kd 8 --robot-drive-force-cap 5 --robot-shape-ke 450 --robot-shape-kd 8 --robot-shape-kf 8 --soft-contact-ke 450 --soft-contact-kd 8 --soft-contact-kf 8 --width 640 --height 360
python scripts/validate_experiment_artifacts.py tmp/proxy_robot_rope_two_way_soft --require-video --require-gif --summary-field pure_semiimplicit --summary-field solver_owned_robot_state --summary-field two_way_coupling_signal --summary-field robot_rope_contact_frames --summary-field rope_motion_after_robot_contact --summary-field robot_reaction_signal --summary-field numerics_finite
```

## Current Failure Mode

The timing-fixed smoke is an artifact-valid negative result. The full Panda body
state becomes non-finite before finger-object contact, while IK remains finite
(`ik_fallback_frames = 0`). Treat this as a blocker in the pure full-Panda
SemiImplicit path, not as a successful robot/object interaction demo.

## Current Positive Path

The proxy robot pusher artifact at
`tmp/proxy_robot_rope_two_way_soft_20260511` is the current positive two-way
coupling demo. It passes `two_way_coupling_signal`, but its `robot_model` is
`dynamic_proxy_pusher` and `full_panda_dynamic = false`, so report it with that
claim boundary.
