> status: active
> canonical_replacement: none
> owner_surface: `pure_semiimplicit_robot_loaded_object`
> last_reviewed: `2026-05-11`
> review_interval: `7d`
> update_rule: `Update after each implementation checkpoint or experiment run.`
> notes: Live status log for the reopened pure SemiImplicit robot + PhysTwin-loaded object repair diagnostic.

# Status: pure_semiimplicit_robot_loaded_object

## Current State

- Reopened on `2026-05-11`.
- Scope is a clean diagnostic repair, not a replacement for the current split
  MuJoCo/SemiImplicit meeting-video route.
- A new single-`SolverSemiImplicit` diagnostic exists with Panda, table,
  ground, and an object-only PhysTwin rope IR.
- The demo now drives Panda through `IK -> control.joint_target_pos ->
  solver-owned state`; it does not overwrite robot state after solver steps.
- Motion targets now advance on integrated `sim_time`, not video frame index,
  so fine SemiImplicit timesteps no longer create a fake high-speed control
  trajectory.
- A simplified dynamic proxy robot pusher now provides the required positive
  two-way coupling demo with the PhysTwin-like rope IR. This is intentionally
  not a full Panda claim.

## Latest Run

### Positive Two-Way Proxy Robot

- Artifact:
  `tmp/proxy_robot_rope_two_way_soft_20260511`
- Main video:
  `tmp/proxy_robot_rope_two_way_soft_20260511/hero.mp4`
- Summary:
  `tmp/proxy_robot_rope_two_way_soft_20260511/summary.json`
- Command:
  `bash scripts/run_proxy_robot_rope_two_way_demo.sh tmp/proxy_robot_rope_two_way_soft_20260511 --num-frames 360 --video-fps 60 --sim-substeps 20 --sim-dt 5.0e-5 --settle-seconds 0.02 --push-seconds 0.22 --hold-seconds 0.10 --robot-mass 0.5 --robot-drive-kp 70 --robot-drive-kd 8 --robot-drive-force-cap 5 --robot-shape-ke 450 --robot-shape-kd 8 --robot-shape-kf 8 --soft-contact-ke 450 --soft-contact-kd 8 --soft-contact-kf 8 --width 640 --height 360`

Key summary fields:

- `two_way_coupling_signal = true`
- `numerics_finite = true`
- `pure_semiimplicit = true`
- `solver_owned_robot_state = true`
- `post_step_robot_state_overwrite = false`
- `robot_model = dynamic_proxy_pusher`
- `full_panda_dynamic = false`
- `uses_phystwin_ir = true`
- `robot_rope_contact_frames = 117`
- `first_robot_rope_contact_frame = 127`
- `first_rope_motion_after_robot_contact_frame = 147`
- `rope_motion_after_robot_contact = true`
- `robot_reaction_signal = true`
- `max_rope_com_delta_m = 0.43288829922676086`

### Full Panda Negative Diagnostic

- Artifact:
  `tmp/pure_semiimplicit_robot_loaded_object_timing_fixed_smoke_20260511`
- Main video:
  `tmp/pure_semiimplicit_robot_loaded_object_timing_fixed_smoke_20260511/hero.mp4`
- Summary:
  `tmp/pure_semiimplicit_robot_loaded_object_timing_fixed_smoke_20260511/summary.json`
- Command:
  `bash scripts/run_pure_semiimplicit_robot_loaded_object_demo.sh tmp/pure_semiimplicit_robot_loaded_object_timing_fixed_smoke_20260511 --num-frames 60 --video-fps 1000 --sim-substeps 100 --sim-dt 1.0e-5 --settle-seconds 0.004 --approach-seconds 0.010 --push-seconds 0.030 --table-probe-seconds 0.010 --retract-seconds 0.006 --push-distance 0.06 --width 640 --height 360`

Key summary fields:

- `pure_semiimplicit = true`
- `solver_owned_robot_state = true`
- `uses_mujoco = false`
- `post_step_robot_state_overwrite = false`
- `motion_time_source = sim_time`
- `video_frame_dt_s = 0.001`
- `integrated_dt_per_render_frame_s = 0.001`
- `numerics_finite = false`
- `ik_fallback_frames = 0`
- `finger_object_contact_frames = 0`
- `rope_motion_after_contact = false`
- `table_object_contact_frames = 60`
- `max_rope_com_delta_m = 0.011118516325950623`

## Validation

- `python -m py_compile Newton/phystwin_bridge/demos/demo_proxy_robot_rope_two_way.py Newton/phystwin_bridge/demos/demo_pure_semiimplicit_robot_loaded_object.py`
  passed.
- `bash -n scripts/run_proxy_robot_rope_two_way_demo.sh scripts/run_pure_semiimplicit_robot_loaded_object_demo.sh`
  passed.
- `python scripts/validate_experiment_artifacts.py tmp/proxy_robot_rope_two_way_soft_20260511 --require-video --require-gif --summary-field pure_semiimplicit --summary-field solver_owned_robot_state --summary-field two_way_coupling_signal --summary-field robot_rope_contact_frames --summary-field rope_motion_after_robot_contact --summary-field robot_reaction_signal --summary-field numerics_finite`
  passed as an artifact-contract check.
- `python -m py_compile Newton/phystwin_bridge/demos/demo_pure_semiimplicit_robot_loaded_object.py`
  passed.
- `bash -n scripts/run_pure_semiimplicit_robot_loaded_object_demo.sh` passed.
- `python scripts/validate_experiment_artifacts.py tmp/pure_semiimplicit_robot_loaded_object_timing_fixed_smoke_20260511 --require-video --require-gif --summary-field pure_semiimplicit --summary-field solver_owned_robot_state --summary-field rope_motion_after_contact --summary-field table_blocking_attempted --summary-field numerics_finite --summary-field ik_fallback_frames --summary-field motion_time_source`
  passed as an artifact-contract check.
- `python scripts/generate_md_inventory.py` refreshed generated Markdown
  inventory surfaces after adding the new task chain.
- `python scripts/lint_harness_consistency.py` still fails on unrelated
  stale/missing review metadata for existing task pages
  (`phystwin_four_new_cases_pipeline`,
  `phystwin_upstream_sync_review`, older due review stamps, and
  `markdown_harness_maintenance_upgrade` surfaces). The pure-SemiImplicit
  task chain is no longer the reported stale-inventory cause.
- After adding the proxy two-way demo, `python scripts/generate_md_inventory.py`
  was rerun. `python scripts/lint_harness_consistency.py` still reports only
  the same unrelated stale/missing metadata surfaces.

## Conclusion

The full Panda physical claim remains negative, but the requested two-way
coupling demo now exists through the proxy robot route. The positive artifact
uses only `SolverSemiImplicit`, keeps robot state solver-owned, imports the
PhysTwin-like rope IR, records robot-rope contact, records rope motion after
robot contact, and records a robot-side reaction signal in one finite run.

## Next Step

Choose the claim boundary:

- If the next target is a meeting-facing robot claim, upgrade the proxy pusher
  to a simplified two-finger dynamic gripper while preserving the same summary
  gates.
- Do not claim full-Panda pure-SemiImplicit success until `numerics_finite`,
  finger-object contact, and object motion after contact all pass in the same
  full-Panda artifact.
