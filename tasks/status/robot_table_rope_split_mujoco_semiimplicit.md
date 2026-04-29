> status: active
> canonical_replacement: none
> owner_surface: `robot_table_rope_split_mujoco_semiimplicit`
> last_reviewed: `2026-04-28`
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
- The default support parameter set now passes the full
  `no fly-away + no burying` gate
- A separate presentation-oriented video path now exists for meeting-facing
  rendering:
  - visible opening instead of hidden preroll
  - full-cycle render length derived from motion phases
  - dedicated presentation camera framing
  - gripper-center-targeted IK instrumentation
- A new presentation pick-place candidate now shows a complete table-edge
  grasp, lift, transfer, and release sequence without contact-buffer overflow
- `grasp_assist` is now disallowed for the meeting-facing path:
  - the presentation wrapper passes `--no-presentation-grasp-assist`
  - parser default is now `presentation_grasp_assist = false`
  - strict contact-only gate fields are emitted in `summary.json`
- The meeting-facing default has now been reset to true native Panda fingers:
  - wrapper default is `--presentation-gripper-geometry panda_fingers`
  - auxiliary green `manipulation_objects/pad` meshes are only added for the
    explicit diagnostic value `--presentation-gripper-geometry panda_pads`
  - the visible teal `rope_cradle` helper is no longer eligible for final
    strict acceptance
  - `--strict-require-native-panda-fingers` defaults to true
- The strict gate now also exposes `strict_max_rope_height_m` and fails clips
  where light-rope tuning makes the rope fly away.
- The previous `strict_contact_only_pass_20260426` artifact has been demoted
  after visual review: it could pass the old local-segment gate while still
  reading as rope self-drop.
- The self-drop-fixed artifact was later demoted after visual review: it still
  read like a single side wall/hook was lifting the rope.
- The previous `rope_cradle` strict contact-only physics-contact artifact is
  preserved only as demoted evidence:
  - `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427`
  - `strict_contact_only_pass = true`
  - `grasp_assist_enabled = false`
  - `first_grasp_assist_frame = null`
  - skeptical video audit verdict is `PASS`
  - it is not accepted as the final meeting-facing video after user visual
    review because the visible teal `rope_cradle` helper is not native Panda
    finger geometry
- The current native-only diagnostic is:
  - `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428`
  - `presentation_gripper_geometry = panda_fingers`
  - `presentation_aux_panda_pad_geometry_enabled = false`
  - `strict_require_native_panda_fingers = true`
  - `strict_contact_only_pass = false`
  - `grasp_assist_enabled = false`
  - `first_finger_rope_contact_frame = 6`
  - `rope_motion_after_contact = true`
  - `lift_window_contact_balance_ratio = 0.337578`
  - `lift_window_unilateral_finger_rope_contact_frames = 0`
  - `lift_window_both_finger_rope_contact_frames = 7`
  - `rope_lift_height_m = 0.0`
  - `grasp_particle_lift_during_lift_transfer_m = 0.010288`
  - `nonfinger_table_contact_frames = 7`
  - `max_support_penetration_m = 0.000327`
  - `rope_render_matches_physics = true`
  - artifact contract validation is `OK`, but this is a failing diagnostic

## Latest Native Panda Finger Reset

- changed the split demo and presentation wrapper so the default meeting route
  uses only the real Panda finger meshes:
  - no `grasp_assist`
  - no `rope_cradle`
  - no auxiliary green `panda_pads`
  - no hidden helper geometry accepted by the strict gate
- filled pad/contact instrumentation from the native Panda finger local target
  when no auxiliary pad shapes are created, so the existing controller metrics
  still report the intended contactor.
- ran native-finger probes:
  - baseline native fingers: contact and rope response, but no lift
  - outside/tight native fingers: best current native-only diagnostic with
    balanced lift-window contact but still no carry
  - high-z/slow native fingers: worse one-sided contact
  - hanging-tail native fingers: pre-contact drop and no carry
  - light-rope native fingers: unacceptable fly-away
- validated current best native-only diagnostic:
  - `python scripts/validate_experiment_artifacts.py tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428 --require-video --require-gif --summary-field strict_contact_only_pass --summary-field grasp_assist_enabled --summary-field presentation_gripper_geometry --summary-field presentation_aux_panda_pad_geometry_enabled --summary-field strict_require_native_panda_fingers --summary-field lift_window_contact_balance_ratio --summary-field lift_window_unilateral_finger_rope_contact_frames --summary-field rope_lift_height_m --summary-field rope_render_matches_physics`
  - validator output: `/tmp/validate_native_panda_fingers_outside_tight_20260428.out`
- static checks passed:
  - `python -m py_compile Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
  - `bash -n scripts/run_robot_table_rope_split_presentation_video.sh`
- harness lint remains blocked on unrelated control-plane maintenance issues:
  - `/tmp/lint_harness_consistency_native_panda_20260428.out`
  - current-status dashboard length and missing/stale metadata on other task
    pages; no new native-Panda-finger artifact contract issue remains
- conclusion:
  - visual helper-geometry issue is fixed by default routing, but final
    meeting-video acceptance is still blocked
  - current hard blocker is physical native Panda finger carry: the fingers
    reach and touch the rope, but the rope slips/drops instead of being
    visibly pinched, lifted, moved, and released

## Latest Visual Review

- user review on `2026-04-27` flagged the current `hero.mp4` as visually weird:
  - the green/teal gripper part is the presentation `rope_cradle` helper, not
    a natural Panda finger surface
  - the rope is rendered at the real solver particle radius, so close-up frames
    read as bead-like clumps instead of a continuous rope
  - the contact metrics are improved, but the clip still does not read as
    realistic physical Panda two-finger rope manipulation
- current conclusion:
  - `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427`
    remains useful physics-contact evidence
  - it is demoted from final meeting-video acceptance
  - the current default route has now removed the helper geometry; the next
    blocker is physical native Panda finger carry, not `grasp_assist`, support
    penetration, side-suction metrics, or wrapper recording semantics
- next implementation direction:
  - make the native Panda pads themselves form the lift geometry
  - add a continuous physical-radius rope render path so truthful thickness no
    longer appears as a pile of beads in close view, after physical carry works

## Latest Side-Suction Fix

- fixed the side-suction false positive by adding strict lift/transfer contact
  balance gates:
  - `lift_window_contact_balance_ratio`
  - `strict_min_lift_contact_balance_ratio`
  - `lift_window_unilateral_finger_rope_contact_frames`
  - `strict_max_unilateral_lift_contact_frames`
- changed the presentation default target away from the outside hanging tail:
  - `presentation_edge_grasp_outset_y = 0.000`
  - `presentation_grasp_x_offset_m = 0.030`
  - this places the target at the table-edge line instead of `25mm` outside it
- reduced the side-wall hook geometry and compensated support stiffness:
  - `presentation_cradle_lip_depth_m = 0.035`
  - `presentation_cradle_wall_height_m = 0.015`
  - `presentation_cradle_grasp_z_clearance_m = 0.018`
  - `presentation_table_shape_contact_scale = 8.0`
- ran the replacement meeting-video artifact:
  - `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427`
  - `strict_contact_only_pass = true`
  - `strict_contact_only_fail_reasons = []`
  - `grasp_assist_enabled = false`
  - `first_grasp_assist_frame = null`
  - `first_finger_rope_contact_frame = 5`
  - `first_rope_motion_frame = 6`
  - `rope_motion_after_contact = true`
  - `lift_window_contact_balance_ratio = 0.310864`
  - `strict_min_lift_contact_balance_ratio = 0.2`
  - `lift_window_unilateral_finger_rope_contact_frames = 0`
  - `strict_max_unilateral_lift_contact_frames = 0`
  - `lift_window_both_finger_rope_contact_frames = 32`
  - `final_finger_rope_contact_frames = 0`
  - `rope_lift_height_m = 0.135920`
  - `grasp_particle_lift_during_lift_transfer_m = 0.153220`
  - `rope_ground_contact_frames_final_30 = 28`
  - `max_support_penetration_m = 0.001068`
  - `finger_table_contact_frames = 40`
  - `nonfinger_table_contact_frames = 0`
  - `rope_render_matches_physics = true`
- validated the artifact with `scripts/validate_experiment_artifacts.py`
- static checks passed:
  - `python -m py_compile Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
  - `bash -n scripts/run_robot_table_rope_split_presentation_video.sh`
- prepared and ran the skeptical video audit:
  - review bundle:
    `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/review_bundle`
  - skeptical verdict is `PASS`
  - hard-fail reasons are empty
- refreshed generated markdown inventory and results registry
- `scripts/lint_harness_consistency.py` still fails only on pre-existing
  dashboard/stale-metadata issues outside this robot split artifact

## Latest Self-Drop Fix

- fixed the self-drop false positive by adding strict visible-carry gates:
  - `strict_rope_lift_height_m`
  - `strict_rope_max_z_lift_height_m`
  - the old artifact has `rope_lift_height_m = 0.0`, so it is no longer an
    eligible pass under the current gate
- changed the release/retract path so the gripper retreats from the placement
  pose instead of from the high carry pose; this avoids turning release into a
  second hidden lift
- updated the presentation wrapper defaults to the current stable contact-only
  edge-pick setup:
  - `presentation_cradle_grasp_z_clearance_m = 0.016`
  - `presentation_grasp_closed_opening_m = 0.004`
  - `finger_shape_contact_scale = 1.3`
  - `finger_shape_friction_multiplier = 10.0`
  - `presentation_retract_y_offset_m = 0.240`
- split table-contact diagnostics into:
  - `finger_table_contact_frames`
  - `nonfinger_table_contact_frames`
  - strict acceptance now fails non-finger robot-body table contact, while
    finger/cradle table-edge contact remains reported for review because the
    edge scoop physically touches the support
- ran the replacement meeting-video artifact:
  - `tmp/robot_table_rope_split_selfdrop_fix_contact_only_20260426`
  - `strict_contact_only_pass = true`
  - `strict_contact_only_fail_reasons = []`
  - `grasp_assist_enabled = false`
  - `first_grasp_assist_frame = null`
  - `first_finger_rope_contact_frame = 4`
  - `first_rope_motion_frame = 5`
  - `rope_motion_after_contact = true`
  - `lift_window_both_finger_rope_contact_frames = 10`
  - `final_finger_rope_contact_frames = 0`
  - `rope_lift_height_m = 0.116019`
  - `rope_max_z_lift_height_m = 0.124933`
  - `grasp_particle_lift_during_lift_transfer_m = 0.116898`
  - `pre_contact_ground_contact_frames = 0`
  - `rope_ground_contact_frames_final_30 = 28`
  - `max_support_penetration_m = 0.001581`
  - `final_support_penetration_p99_m = 0.0`
  - `robot_table_contact_frames = 41`
  - `finger_table_contact_frames = 41`
  - `nonfinger_table_contact_frames = 0`
  - `rope_render_matches_physics = true`
- validated the artifact with `scripts/validate_experiment_artifacts.py`
- prepared and ran the skeptical video audit:
  - review bundle:
    `tmp/robot_table_rope_split_selfdrop_fix_contact_only_20260426/review_bundle`
  - skeptical verdict is `PASS`
  - hard-fail reasons are empty

## Previous Strict Pass Context

- implemented the real pure-contact grasp geometry/control route requested by
  user review:
  - `presentation_gripper_geometry = "rope_cradle"`
  - `gripper_yaw_rad = 2.89159265359`
  - `presentation_grasp_closed_opening_m = 0.008`
  - `finger_shape_contact_scale = 1.6`
  - `finger_shape_friction_multiplier = 50.0`
  - the closing axis now crosses the rope cross-section instead of closing
    mostly along the rope length
- tightened the strict gate so release/retract bounce cannot fake success:
  - added `grasp_particle_lift_during_lift_transfer_m`
  - `strict_contact_only_pass` now requires local grasp-segment lift during
    the closed lift/transfer window
- updated the presentation wrapper defaults to the accepted strict-contact
  setup while keeping `--no-presentation-grasp-assist`
- ran the accepted strict contact-only artifact:
  - `tmp/robot_table_rope_split_strict_contact_only_pass_20260426`
  - `strict_contact_only_pass = true`
  - `strict_contact_only_fail_reasons = []`
  - `grasp_assist_enabled = false`
  - `first_grasp_assist_frame = null`
  - `grasp_assist_frames = 0`
  - `first_finger_rope_contact_frame = 9`
  - `first_rope_motion_frame = 15`
  - `rope_motion_after_contact = true`
  - `grasp_particle_lift_during_lift_transfer_m = 0.031469`
  - `lift_window_both_finger_rope_contact_frames = 7`
  - `robot_table_contact_frames = 0`
  - `max_support_penetration_m = 0.001443`
  - `final_support_penetration_p99_m = 0.0`
  - `rope_ground_contact_frames_final_30 = 30`
  - `rope_render_matches_physics = true`
- prepared and ran the skeptical review bundle for the accepted artifact:
  - review bundle:
    `tmp/robot_table_rope_split_strict_contact_only_pass_20260426/review_bundle`
  - skeptical verdict is `PASS`
  - hard-fail reasons are empty
  - missing-or-ambiguous evidence is empty
- validated the accepted strict contact-only artifact with
  `scripts/validate_experiment_artifacts.py`
- promoted the accepted strict contact-only artifact in `results_meta` as the
  current meeting-video surface; the support-default artifact remains
  supporting evidence for the non-burying support calibration
- retired `grasp_assist` from the default presentation path after user review:
  - `scripts/run_robot_table_rope_split_presentation_video.sh` now explicitly
    uses `--no-presentation-grasp-assist`
  - `--presentation-grasp-assist` remains available only as an explicit
    diagnostic override, not as the meeting-video route
- added strict contact-only summary gate fields:
  - `strict_contact_only_pass`
  - `strict_contact_only_fail_reasons`
  - `lift_window_left_finger_rope_contact_frames`
  - `lift_window_right_finger_rope_contact_frames`
  - `lift_window_both_finger_rope_contact_frames`
  - `grasp_metric_particle_count`
- added bridge-layer tuning knobs for strict contact-only experiments:
  - `--presentation-grasp-x-offset`
  - `--presentation-grasp-y-offset`
  - `--presentation-grasp-z-offset`
  - `--finger-shape-friction-multiplier`
- ran the previous strict contact-only failure artifact:
  - `tmp/robot_table_rope_split_strict_contact_default_20260426`
  - `grasp_assist_enabled = false`
  - `first_grasp_assist_frame = null`
  - `grasp_assist_frames = 0`
  - `first_finger_rope_contact_frame = 12`
  - `first_rope_motion_frame = 18`
  - `rope_motion_after_contact = true`
  - `robot_table_contact_frames = 0`
  - `max_support_penetration_m = 0.002243`
  - `rope_render_matches_physics = true`
  - `strict_contact_only_pass = false`
  - strict fail reasons:
    - `both fingers did not maintain contact during the lift/transfer window`
    - `local grasp segment did not lift enough`
- validated the strict contact-only artifact with
  `scripts/validate_experiment_artifacts.py`
- prepared and ran the fail-closed skeptical audit for the strict artifact:
  - review bundle:
    `tmp/robot_table_rope_split_strict_contact_default_20260426/review_bundle`
  - automatic QC has no black/static-frame hard fail
  - skeptical verdict was `FAIL`
- ran additional strict contact-only tuning probes:
  - `tmp/robot_table_rope_split_pick_place_strict_contact_baseline_20260426`
  - `tmp/robot_table_rope_split_pick_place_strict_contact_tight_v1_20260426`
  - `tmp/robot_table_rope_split_pick_place_strict_contact_xoffset_v2_20260426`
  - `tmp/robot_table_rope_split_pick_place_strict_contact_yaw_v3_20260426`
  - `tmp/robot_table_rope_split_pick_place_strict_contact_friction_v4_20260426`
  - `tmp/robot_table_rope_split_pick_place_strict_contact_scoop_v5_20260426`
  - `tmp/robot_table_rope_split_pick_place_strict_contact_endgrab_v6_20260426`
  - `tmp/robot_table_rope_split_pick_place_strict_contact_endgrab_v7_20260426`
- diagnosis from those failed probes:
  - the old gripper yaw was mostly aligned with the rope length, so it touched
    or dragged the rope instead of clamping the rope cross-section
  - yaw rotation had to be combined with a real visible rope-cradle contactor,
    a tighter closed opening, higher finger contact/friction, farther ground
    placement, and a negative-y retract
  - the active blocker was strict contact-only grasp geometry/contact
    modeling, not recording, support penetration, or buffer capacity
- reworked the presentation strategy from side-pad pushing to staged
  pick-and-place:
  - target the gripper center between the two pads instead of only the wrist/EE
  - choose a table-edge rope segment so the lower jaw has access and does not
    have to close through the table
  - open, approach, lower, close, lift, transfer, lower to ground, release, and
    retract over a full visible cycle
- added presentation-only finite-force grasp assist in the earlier candidate:
  - implemented as bounded spring-damper forces on the selected local rope
    segment
  - reported explicitly in `summary.json` via `first_grasp_assist_frame`,
    `grasp_assist_enabled`, `grasp_assist_frames`, and lift metrics
  - now disallowed for the default meeting-facing route
- added presentation-specific contact-buffer controls and enabled them in
  `scripts/run_robot_table_rope_split_presentation_video.sh`:
  - `--rope-rigid-contact-max 8192`
  - `--rope-soft-contact-max 8192`
  - this removed the repeated `Contact buffer overflowed 1002 > 1000`
    warnings from the latest presentation run
- ran the current presentation candidate:
  - `tmp/robot_table_rope_split_pick_place_contactbuf_20260425_2`
  - `video_mode = "presentation_pick_place"`
  - `motion_pattern = "grasp_lift_place"`
  - `render_frame_count = 135`
  - `first_finger_rope_contact_frame = 11`
  - `first_rope_motion_frame = 11`
  - `rope_motion_after_contact = true`
  - `first_grasp_assist_frame = 11`
  - `robot_table_contact_frames = 0`
  - `max_support_penetration_m = 0.002359`
  - `final_support_penetration_p99_m = 0.0`
  - `grasp_particle_lift_height_m = 0.057232`
  - `rope_max_z_lift_height_m = 0.042504`
  - `rope_ground_contact_frames_final_30 = 30`
  - `rope_render_matches_physics = true`
- prepared the skeptical review bundle for the assisted presentation candidate:
  - `tmp/robot_table_rope_split_pick_place_contactbuf_20260425_2/review_bundle`
  - automatic QC has no black/static-frame hard fail
  - fail-closed skeptical verdict was `FAIL` because no separate
    `manual_review.json` PASS has been supplied
- validated the assisted presentation candidate with
  `scripts/validate_experiment_artifacts.py`
- fast-forwarded `Newton/newton` to the latest official upstream `origin/main`
  commit:
  - `b6a879957cd321e37ca0f3bf15a1f6ea8a55112b`
- ran a post-core-update split-demo smoke artifact to confirm the bridge path
  still imports, builds, simulates, and renders without any bridge-side API
  patch:
  - `tmp/robot_table_rope_split_post_core_update_smoke_20260415`
- validated the post-core-update smoke artifact with
  `scripts/validate_experiment_artifacts.py`
- confirmed that no bridge interface updates were required for the active split
  demo path after the core refresh
- refactored the rigid-side Panda/table builder to match the newer upstream
  `example_robot_panda_hydro.py` configuration style:
  - base `ShapeConfig`
  - explicit hydroelastic mesh config
  - explicit hydroelastic primitive config
- ran a post-refactor smoke artifact and validated it:
  - `tmp/robot_table_rope_split_post_builder_refactor_smoke_20260415`
- prepared skeptical review bundles for the latest rendered smoke video and the
  current default-support authoritative video:
  - `tmp/review_bundle_post_builder_refactor_smoke_20260415`
  - `tmp/review_bundle_support_default_authoritative_20260415`
- conservative video verdict for both bundles is `FAIL`:
  - the latest rendered smoke video is only `5` frames (`0.1667s`) and does
    not show a complete process window
  - the current default-support video is stable and readable, but it still does
    not show a defensible finger-rope contact or visible manipulation outcome
- added a dedicated presentation wrapper:
  - `scripts/run_robot_table_rope_split_presentation_video.sh`
- implemented a presentation-only video mode in the split demo:
  - `video_mode = "presentation_lifted"`
  - `record_start_mode = "visible_opening"`
  - `rope_preroll_seconds = 0.0`
  - `render_frame_count = rigid.total_frames + presentation_tail_frames`
- presentation mode now also uses:
  - presentation-specific rope placement
  - presentation-specific camera framing
  - runtime pad-distance instrumentation
  - pad-center-targeted IK instead of only EE-indirect targeting
- ran a series of presentation smokes to iterate on geometry, camera, and
  control targeting:
  - `tmp/robot_table_rope_split_presentation_smoke_v6_20260416`
  - `tmp/robot_table_rope_split_presentation_smoke_v8_20260416`
  - `tmp/robot_table_rope_split_presentation_smoke_v10_20260416`
  - `tmp/robot_table_rope_split_presentation_smoke_v11_20260416`
- old presentation-facing artifact was not acceptable:
  - `tmp/robot_table_rope_split_presentation_smoke_v10_20260416`
  - it now shows a complete visible process window with rope kept in frame
  - but `first_finger_rope_contact_frame` remains `null`
  - and `min_leading_pad_to_rope_distance_m = 0.05427`, so there is still no
    conservative visual proof of finger-rope contact
- validated the current best presentation artifact with
  `scripts/validate_experiment_artifacts.py`
- prepared a skeptical review bundle for the current best presentation artifact:
  - `tmp/review_bundle_presentation_smoke_v10_20260416`
- slower or lower presentation follow-ups did not rescue contact and started to
  trigger repeated rope-side contact-buffer overflow warnings:
  - `tmp/robot_table_rope_split_presentation_smoke_v11_20260416`
  - `tmp/robot_table_rope_split_presentation_smoke_v12_20260416`
- added a support-only sweep wrapper:
  - `scripts/run_robot_table_rope_split_support_sweep.sh`
- promoted a support-passing default parameter set into the demo parser:
  - `ground_shape_contact_scale = 1e-3`
  - `ground_shape_contact_damping_multiplier = 64.0`
  - `table_shape_contact_scale = 1e-3`
  - `table_shape_contact_damping_multiplier = 64.0`
  - `finger_shape_contact_scale = 0.1`
  - `finger_shape_contact_damping_multiplier = 1.5`
  - `table_edge_inset_y = 0.17`
  - `overhang_drop_factor = 0.02`
- ran no-render truth probes to select the first candidate that satisfies the
  support gate at the fine rope timestep
- ran a new canonical default artifact with no support override flags:
  - `tmp/robot_table_rope_split_support_default_authoritative_20260415`
- validated the new default-support artifact with
  `scripts/validate_experiment_artifacts.py`
- promoted the new default-support artifact as the current authoritative partial
  surface in `results_meta/tasks/robot_table_rope_split_mujoco_semiimplicit.json`
- `candidate_c` remains a failed support-calibration example and is no longer
  treated as a default or near-pass surface

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
- the new default parameter set is now acceptable under the support gate:
  - `tmp/robot_table_rope_split_support_default_authoritative_20260415`
  - `rope_table_contact_frames_first_30 = 30`
  - `rope_ground_contact_frames_first_30 = 30`
  - `max_support_penetration_m = 0.000639`
  - `final_support_penetration_p99_m = 0.0`
  - `rope_render_matches_physics = true`
- the active split bridge path still works after the core update to
  `b6a87995`:
  - `tmp/robot_table_rope_split_post_core_update_smoke_20260415`
  - `rope_table_contact_frames = 5`
  - `rope_ground_contact_frames = 5`
  - `max_support_penetration_m = 0.000608`
  - `rope_render_matches_physics = true`
- the rigid-side builder refactor also preserved current split behavior:
  - `tmp/robot_table_rope_split_post_builder_refactor_smoke_20260415`
  - `rope_table_contact_frames = 5`
  - `rope_ground_contact_frames = 5`
  - `max_support_penetration_m = 0.000666`
  - `rope_render_matches_physics = true`
- but video acceptance still fails under a skeptical review:
  - latest rendered smoke bundle:
    `tmp/review_bundle_post_builder_refactor_smoke_20260415/skeptical_audit.json`
  - default-support bundle:
    `tmp/review_bundle_support_default_authoritative_20260415/skeptical_audit.json`
  - neither video currently provides conservative visual proof of purposeful
    finger-rope interaction
- the new presentation path fixes the previous artifact-type mismatch:
  - recording begins from a visible lifted opening state
  - the rope now stays on-screen through the early window
  - camera framing is finally good enough for meeting-facing review
- the old presentation control path was short of acceptance:
  - pad-center targeting alone still missed the rope in
    `tmp/robot_table_rope_split_presentation_smoke_v10_20260416`
  - that run bottomed out at `min_leading_pad_to_rope_distance_m = 0.05427`
  - `first_finger_rope_contact_frame` and `first_rope_motion_frame` were both
    `null`
- the new pick-place presentation path fixes the core geometry error:
  - the grasp target is an edge-accessible rope segment, not a fully
    table-backed segment
  - the controlled point is the gripper center between the pads
  - the assisted run recorded non-null first finger contact and rope motion at
    frame `11`
  - the first strict run recorded non-null first finger contact and rope
    motion, but did not lift the local grasp segment
  - the accepted strict run adds rope-cradle geometry and yawed closing across
    the rope section, then lifts the local grasp segment during the closed
    lift/transfer window
  - support penetration remains low enough for review-scale presentation
  - contact-buffer overflow warnings are gone
- strict physical grasping is now solved for the one-way meeting-video claim:
  - the split stack, render truth, and support contacts are now aligned under
    the default parameter set
  - support-proof and presentation rendering are now separate, which is the
    right product split
  - the remaining future physics milestone is two-way robot-rope reaction,
    not re-enabling or hiding `grasp_assist`

## Artifact Paths To Review

- accepted strict contact-only meeting-video artifact:
  - `tmp/robot_table_rope_split_strict_contact_only_pass_20260426/summary.json`
  - `tmp/robot_table_rope_split_strict_contact_only_pass_20260426/hero.mp4`
  - `tmp/robot_table_rope_split_strict_contact_only_pass_20260426/hero.gif`
  - `tmp/robot_table_rope_split_strict_contact_only_pass_20260426/contact_sheet.jpg`
  - `tmp/robot_table_rope_split_strict_contact_only_pass_20260426/review_bundle/contact_sheet.png`
  - `tmp/robot_table_rope_split_strict_contact_only_pass_20260426/review_bundle/event_sheet.png`
  - `tmp/robot_table_rope_split_strict_contact_only_pass_20260426/review_bundle/skeptical_audit.json`
- assisted presentation pick-place candidate:
  - `tmp/robot_table_rope_split_pick_place_contactbuf_20260425_2/summary.json`
  - `tmp/robot_table_rope_split_pick_place_contactbuf_20260425_2/hero.mp4`
  - `tmp/robot_table_rope_split_pick_place_contactbuf_20260425_2/hero.gif`
  - `tmp/robot_table_rope_split_pick_place_contactbuf_20260425_2/review_bundle/contact_sheet.png`
  - `tmp/robot_table_rope_split_pick_place_contactbuf_20260425_2/review_bundle/event_sheet.png`
  - `tmp/robot_table_rope_split_pick_place_contactbuf_20260425_2/review_bundle/skeptical_audit.json`
- previous strict contact-only failed artifact:
  - `tmp/robot_table_rope_split_strict_contact_default_20260426/summary.json`
  - `tmp/robot_table_rope_split_strict_contact_default_20260426/hero.mp4`
  - `tmp/robot_table_rope_split_strict_contact_default_20260426/hero.gif`
  - `tmp/robot_table_rope_split_strict_contact_default_20260426/review_bundle/contact_sheet.png`
  - `tmp/robot_table_rope_split_strict_contact_default_20260426/review_bundle/skeptical_audit.json`
- authoritative default-support artifact:
  - `tmp/robot_table_rope_split_support_default_authoritative_20260415/summary.json`
  - `tmp/robot_table_rope_split_support_default_authoritative_20260415/hero.mp4`
  - `tmp/robot_table_rope_split_support_default_authoritative_20260415/hero.gif`
  - `tmp/robot_table_rope_split_support_default_authoritative_20260415/contact_sheet.jpg`
  - `tmp/robot_table_rope_split_support_default_authoritative_20260415/first_30_frames_sheet.jpg`
- post-core-update smoke artifact:
  - `tmp/robot_table_rope_split_post_core_update_smoke_20260415/summary.json`
  - `tmp/robot_table_rope_split_post_core_update_smoke_20260415/hero.mp4`
  - `tmp/robot_table_rope_split_post_core_update_smoke_20260415/hero.gif`
- post-builder-refactor smoke artifact:
  - `tmp/robot_table_rope_split_post_builder_refactor_smoke_20260415/summary.json`
  - `tmp/robot_table_rope_split_post_builder_refactor_smoke_20260415/hero.mp4`
  - `tmp/robot_table_rope_split_post_builder_refactor_smoke_20260415/hero.gif`
- skeptical review bundles:
  - `tmp/review_bundle_post_builder_refactor_smoke_20260415/contact_sheet.png`
  - `tmp/review_bundle_post_builder_refactor_smoke_20260415/event_sheet.png`
  - `tmp/review_bundle_support_default_authoritative_20260415/contact_sheet.png`
  - `tmp/review_bundle_support_default_authoritative_20260415/event_sheet.png`
- best current presentation artifact:
  - `tmp/robot_table_rope_split_presentation_smoke_v10_20260416/summary.json`
  - `tmp/robot_table_rope_split_presentation_smoke_v10_20260416/hero.mp4`
  - `tmp/robot_table_rope_split_presentation_smoke_v10_20260416/hero.gif`
  - `tmp/robot_table_rope_split_presentation_smoke_v10_20260416/contact_sheet.jpg`
  - `tmp/robot_table_rope_split_presentation_smoke_v10_20260416/first_30_frames_sheet.jpg`
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

- keep the current solver split and support defaults unchanged
- use `tmp/robot_table_rope_split_strict_contact_only_pass_20260426` as the
  current meeting-video artifact to inspect
- keep `grasp_assist` disabled; assisted artifacts remain diagnostic-only
- next engineering milestone is robustness/visual-margin improvement or
  two-way robot-rope reaction feedback, not another hidden assist path

## Validation

- `python -m py_compile Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
- `python -m py_compile Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py Newton/phystwin_bridge/tools/core/newton_import_ir.py Newton/phystwin_bridge/demos/demo_native_robot_table_penetration_probe.py`
- `bash scripts/run_robot_table_rope_split_demo.sh tmp/robot_table_rope_split_post_core_update_smoke_20260415 --num-frames 5 --coupling-mode one_way --width 320 --height 180`
- `python scripts/validate_experiment_artifacts.py tmp/robot_table_rope_split_post_core_update_smoke_20260415 --require-video --require-gif --summary-field max_support_penetration_m --summary-field rope_render_matches_physics`
- `bash scripts/run_robot_table_rope_split_demo.sh tmp/robot_table_rope_split_post_builder_refactor_smoke_20260415 --num-frames 5 --coupling-mode one_way --width 320 --height 180`
- `python scripts/validate_experiment_artifacts.py tmp/robot_table_rope_split_post_builder_refactor_smoke_20260415 --require-video --require-gif --summary-field max_support_penetration_m --summary-field rope_render_matches_physics`
- `bash scripts/run_robot_table_rope_split_demo.sh tmp/robot_table_rope_split_support_default_authoritative_20260415 --num-frames 30 --coupling-mode one_way`
- `python scripts/validate_experiment_artifacts.py tmp/robot_table_rope_split_support_default_authoritative_20260415 --require-video --require-gif --summary-field max_support_penetration_m --summary-field final_support_penetration_p99_m --summary-field rope_render_matches_physics`
- `bash scripts/run_robot_table_rope_split_demo.sh tmp/robot_table_rope_split_presentation_smoke_v10_20260416 --num-frames 5 --coupling-mode one_way --video-mode presentation_lifted --width 320 --height 180`
- `python scripts/prepare_video_review_bundle.py --video tmp/robot_table_rope_split_presentation_smoke_v10_20260416/hero.mp4 --out-dir tmp/review_bundle_presentation_smoke_v10_20260416`
- `python scripts/validate_experiment_artifacts.py tmp/robot_table_rope_split_presentation_smoke_v10_20260416 --require-video --require-gif --summary-field video_mode --summary-field record_start_mode --summary-field min_leading_pad_to_rope_distance_m --summary-field rope_render_matches_physics`
- `python -m py_compile Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
- `bash -n scripts/run_robot_table_rope_split_presentation_video.sh`
- `python scripts/validate_experiment_artifacts.py tmp/robot_table_rope_split_strict_contact_only_pass_20260426 --require-video --require-gif --summary-field strict_contact_only_pass --summary-field strict_contact_only_fail_reasons --summary-field grasp_assist_enabled --summary-field first_grasp_assist_frame --summary-field grasp_particle_lift_during_lift_transfer_m --summary-field lift_window_both_finger_rope_contact_frames --summary-field robot_table_contact_frames --summary-field max_support_penetration_m --summary-field rope_ground_contact_frames_final_30 --summary-field rope_render_matches_physics`
  - latest captured output:
    `/tmp/robot_table_rope_split_validate_latest.out`
- `python scripts/run_skeptical_video_audit.py --bundle tmp/robot_table_rope_split_strict_contact_only_pass_20260426/review_bundle`
  - verdict: `PASS`
- `python scripts/sync_results_registry.py`
- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
  - still `FAIL`, but only for unrelated dashboard/metadata staleness outside
    this robot split artifact; the new artifact-local README banner issue was
    fixed
