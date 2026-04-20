> status: active
> canonical_replacement: none
> owner_surface: `robot_table_rope_split_mujoco_semiimplicit`
> last_reviewed: `2026-04-16`
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
  - pad-center-targeted IK instrumentation
- `finger first contact` is still not achieved, so milestone 1 is not yet
  accepted

## What Changed In The Latest Pass

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
- current best presentation-facing artifact is still not acceptable:
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
- but the presentation control path is still short of acceptance:
  - pad-center targeting is now active, so the remaining miss is no longer just
    “EE tracking the wrong surrogate”
  - the best presentation run still bottoms out at
    `min_leading_pad_to_rope_distance_m = 0.05427`
  - `first_finger_rope_contact_frame` and `first_rope_motion_frame` both remain
    `null`
- current blocker is geometric, not architectural:
  - the split stack, render truth, and support contacts are now aligned under
  the default parameter set
  - support-proof and presentation rendering are now separate, which is the
    right product split
  - the remaining blocker is presentation contact targeting under the current
    one-way controller path

## Artifact Paths To Review

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
- keep the new presentation mode and wrapper as the meeting-video path
- continue presentation contact targeting on top of the current v10 framing:
  - do not re-open support sweep unless the authoritative support artifact regresses
  - do not promote a presentation artifact until skeptical review can defend
    visible finger-rope contact and rope response

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
- `python scripts/sync_results_registry.py`
- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
  - still `FAIL`, but only for pre-existing unrelated metadata problems on
    `phystwin_four_new_cases_pipeline` / `phystwin_upstream_sync_review`
