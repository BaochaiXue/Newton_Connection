> status: active
> canonical_replacement: none
> owner_surface: `pure_semiimplicit_robot_loaded_object`
> last_reviewed: `2026-05-21`
> review_interval: `7d`
> update_rule: `Update when the claim boundary, demo entrypoint, artifact contract, or conclusion for the pure SemiImplicit robot/object repair line changes.`
> notes: Active reopened repair line for a single-SemiImplicit robot + PhysTwin-loaded object diagnostic. This does not supersede the split MuJoCo/SemiImplicit meeting-video line unless the strict evidence catches up.

# Task: Pure SemiImplicit Robot Loaded Object

## Question

Can the repo rebuild a pure `SolverSemiImplicit` robot + table +
PhysTwin-loaded object demo in a way that avoids the retired robot stack's
state-overwrite semantics and produces auditable evidence for:

- solver-owned robot motion
- native table blocking diagnostics
- robot contact with a PhysTwin-loaded deformable object
- measurable object response after robot contact
- explicit reaction-force diagnostics from the same SemiImplicit solve

## Why It Matters

The previous robot + deformable line was retired because the final combined
claim was stronger than the evidence. The split MuJoCo/SemiImplicit route is
still the best meeting-facing path, but a clean pure-SemiImplicit diagnostic is
useful if it can be rebuilt around official Newton patterns and fail-closed
metrics instead of the old monolithic bridge robot code.

## Current Status

- Reopened on `2026-05-11`.
- Initial target is a narrow repair diagnostic, not a final meeting-video
  replacement.
- A clean single-`SolverSemiImplicit` diagnostic now exists with Panda, table,
  ground, and an object-only PhysTwin IR rope.
- The demo uses IK-to-control targets and solver-owned state. Direct post-step
  robot state overwrite is not allowed.
- Motion targets now advance on integrated `sim_time`, avoiding the earlier
  failure mode where tiny SemiImplicit timesteps made frame-indexed targets
  move unrealistically fast.
- Current conclusion: the diagnostic is repaired, but the full-Panda pure
  SemiImplicit physical claim is still blocked because Panda body state becomes
  non-finite before credible finger-object interaction.
- A simplified dynamic proxy robot pusher now provides the positive pure
  SemiImplicit two-way coupling demo: solver-owned robot body, PhysTwin-like
  rope IR, robot-rope contact, rope motion after contact, and robot-side
  reaction signal all pass in one finite artifact.

## Code Entry Points

- Main script:
  - `Newton/phystwin_bridge/demos/demo_pure_semiimplicit_robot_loaded_object.py`
  - `Newton/phystwin_bridge/demos/demo_proxy_robot_rope_two_way.py`
- Wrapper:
  - `scripts/run_pure_semiimplicit_robot_loaded_object_demo.sh`
  - `scripts/run_proxy_robot_rope_two_way_demo.sh`
- Reference code:
  - `Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
  - `Newton/phystwin_bridge/demos/demo_native_robot_table_penetration_probe.py`
  - `Newton/newton/newton/examples/robot/example_robot_panda_hydro.py`
  - `Newton/newton/newton/examples/cloth/example_cloth_franka.py`

## Canonical Commands

```bash
bash scripts/run_pure_semiimplicit_robot_loaded_object_demo.sh <out_dir> --num-frames 60 --video-fps 1000 --sim-substeps 100 --sim-dt 1.0e-5 --settle-seconds 0.004 --approach-seconds 0.010 --push-seconds 0.030 --table-probe-seconds 0.010 --retract-seconds 0.006 --push-distance 0.06 --width 640 --height 360
python scripts/validate_experiment_artifacts.py <out_dir> --require-video --require-gif --summary-field pure_semiimplicit --summary-field solver_owned_robot_state --summary-field rope_motion_after_contact --summary-field table_blocking_attempted --summary-field numerics_finite --summary-field ik_fallback_frames --summary-field motion_time_source

bash scripts/run_proxy_robot_rope_two_way_demo.sh <out_dir> --num-frames 360 --video-fps 60 --sim-substeps 20 --sim-dt 5.0e-5 --settle-seconds 0.02 --push-seconds 0.22 --hold-seconds 0.10 --robot-mass 0.5 --robot-drive-kp 70 --robot-drive-kd 8 --robot-drive-force-cap 5 --robot-shape-ke 450 --robot-shape-kd 8 --robot-shape-kf 8 --soft-contact-ke 450 --soft-contact-kd 8 --soft-contact-kf 8 --width 640 --height 360
python scripts/validate_experiment_artifacts.py <out_dir> --require-video --require-gif --summary-field pure_semiimplicit --summary-field solver_owned_robot_state --summary-field two_way_coupling_signal --summary-field robot_rope_contact_frames --summary-field rope_motion_after_robot_contact --summary-field robot_reaction_signal --summary-field numerics_finite

python scripts/lint_harness_consistency.py
```

Latest artifact:

- `tmp/pure_semiimplicit_robot_loaded_object_timing_fixed_smoke_20260511`
- `tmp/proxy_robot_rope_two_way_soft_20260511`

Important latest fields:

- `pure_semiimplicit = true`
- `solver_owned_robot_state = true`
- `post_step_robot_state_overwrite = false`
- `motion_time_source = sim_time`
- `numerics_finite = false`
- `finger_object_contact_frames = 0`
- `rope_motion_after_contact = false`
- `two_way_coupling_signal = true` for the proxy robot artifact
- `robot_rope_contact_frames = 117`
- `rope_motion_after_robot_contact = true`
- `robot_reaction_signal = true`

## Required Artifacts

- `README.md`
- `command.sh`
- `run.log`
- `summary.json`
- `scene.npz`
- `timeseries.csv`
- `hero.mp4`
- `hero.gif`
- `contact_sheet.jpg`

## Success Criteria

- The wrapper runs end-to-end without changing `Newton/newton/`.
- `summary.json` records `pure_semiimplicit == true`.
- `summary.json` records `solver_owned_robot_state == true`.
- The robot is driven through `control.joint_target_pos`, not by post-step
  state overwrite.
- The run records finger-table, non-finger-table, finger-object,
  table-object, and ground-object contact counts.
- The run records whether object motion begins after detectable finger-object
  contact.
- The run records same-solver body-force diagnostics on the Panda fingers.
- The proxy robot run records `two_way_coupling_signal == true`,
  `robot_rope_contact_frames > 0`, `rope_motion_after_robot_contact == true`,
  and `robot_reaction_signal == true` without post-step state overwrite.

## Open Questions

- Can the full Panda articulation be made finite under `SolverSemiImplicit`
  without modifying `Newton/newton/`?
- Can the proxy robot be upgraded from a pusher into a two-finger dynamic
  gripper while preserving the passing two-way metrics?
- Are same-solver finger body-force diagnostics large and stable enough to
  support a later two-way reaction claim?
- Does the clean pure-SemiImplicit path ever catch up to the split
  MuJoCo/SemiImplicit meeting-video route, or should it remain diagnostic only?

## Related Pages

- [robot_table_rope_split_mujoco_semiimplicit.md](./robot_table_rope_split_mujoco_semiimplicit.md)
- [native_robot_table_penetration_probe.md](./native_robot_table_penetration_probe.md)
- [../../decisions/2026-04-09_robot_ps_interaction_retirement.md](../../decisions/2026-04-09_robot_ps_interaction_retirement.md)
