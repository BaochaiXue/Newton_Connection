> status: active
> canonical_replacement: none
> owner_surface: `robot_table_rope_split_mujoco_semiimplicit`
> last_reviewed: `2026-04-28`
> review_interval: `14d`
> update_rule: `Update when the milestone boundary, coupling mode, artifact contract, or recommended implementation path changes.`
> notes: Active task for a split robot/table/rope demo that uses MuJoCo on the native robot/table side and SemiImplicit on the bridged rope side, with direct-finger contact and physical rope rendering.

# Task: Robot Table Rope Split MuJoCo SemiImplicit

## Question

How should the repo implement a truthful direct-finger Panda + native rigid
table + PhysTwin rope demo when:

- robot/table are driven by a native rigid-body path
- rope remains a SemiImplicit deformable object
- rope must visibly rest on the table/ground and render at its real physical
  thickness
- the implementation must follow official Newton example patterns rather than
  retired local robot demo practices?

## Why It Matters

This is the current best path to a meeting-facing direct-finger rope demo
without reviving the old monolithic bridge robot stack:

- `robot_panda_hydro` already demonstrates the right rigid manipulation shape
- the new native robot/table probe already shows that MuJoCo robot + native
  table blocking is stable in this repo
- the remaining work is honest split coupling to the SemiImplicit rope path

## Current Status

- Active
- Opened on `2026-04-13`
- Initial implementation target is `one_way`; `two_way` is explicitly the next
  milestone, not a hidden assumption for first acceptance
- Code and wrapper now exist
- Rope default total object mass is now `0.1kg` through the shared bridge
  `weight_scale` path
- Rope default physical radius is now `0.2x` of the previous value through the
  shared bridge `particle_radius_scale` path
- Recording now starts from post-settle state by default
- The demo now tracks support penetration proxies and no longer treats
  support-contact counts alone as success
- Default support parameters now satisfy the non-burying gate without any
  support override flags
- A separate presentation pick-place path now exists for meeting-facing video:
  - starts from a visible opening
  - targets a table-edge-accessible rope segment
  - controls the gripper center between the two pads
  - closes, lifts, transfers, lowers, releases, and retracts over a full render
    cycle
  - now disallows `grasp_assist` by default for the meeting-facing route
  - now defaults to true native Panda finger geometry via
    `--presentation-gripper-geometry panda_fingers`
  - rejects `panda_pads` and `rope_cradle` for final strict acceptance when
    `--strict-require-native-panda-fingers` is enabled
  - reports strict contact-only gate fields in `summary.json`
- Current best native-Panda-finger-only diagnostic artifact:
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
  - validator passes the artifact contract, but the result is not accepted
    because true Panda fingers contact the rope without forming a visible carry
- Earlier one-way fine-step support artifact:
  - keeps `rope_table_contact` and `rope_ground_contact` true in the same run
  - keeps `rope_render_matches_physics = true`
  - keeps `robot_table_contact_frames = 0`
  - is now superseded for meeting-video purposes by the strict contact-only
    presentation artifact

## Code Entry Points

- Native rigid-side probe:
  - `Newton/phystwin_bridge/demos/demo_native_robot_table_penetration_probe.py`
- New split demo:
  - `Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
- New wrapper:
  - `scripts/run_robot_table_rope_split_demo.sh`
  - `scripts/run_robot_table_rope_split_support_sweep.sh`
  - `scripts/run_robot_table_rope_split_presentation_video.sh`
- Relevant bridge helpers:
  - `Newton/phystwin_bridge/demos/bridge_deformable_common.py`
  - `Newton/phystwin_bridge/demos/bridge_shared.py`
  - `Newton/phystwin_bridge/demos/rope/common.py`
  - `Newton/phystwin_bridge/demos/rope_demo_common.py`
  - `Newton/phystwin_bridge/tools/core/newton_import_ir.py`
- Official references:
  - `Newton/newton/newton/examples/robot/example_robot_panda_hydro.py`
  - `Newton/newton/newton/examples/ik/example_ik_franka.py`
  - `Newton/newton/newton/examples/cloth/example_cloth_hanging.py`
  - `Newton/newton/newton/examples/diffsim/example_diffsim_cloth.py`
  - `Newton/newton/newton/examples/mpm/example_mpm_twoway_coupling.py`

## Workflow Surfaces

- Contract:
  - [../../../tasks/contracts/robot_table_rope_split_mujoco_semiimplicit.md](../../../tasks/contracts/robot_table_rope_split_mujoco_semiimplicit.md)
- Handoff:
  - [../../../tasks/handoffs/robot_table_rope_split_mujoco_semiimplicit.md](../../../tasks/handoffs/robot_table_rope_split_mujoco_semiimplicit.md)

## Canonical Commands

```bash
bash scripts/run_robot_table_rope_split_demo.sh
bash scripts/run_robot_table_rope_split_support_sweep.sh <out_dir>
bash scripts/run_robot_table_rope_split_presentation_video.sh <out_dir> --width 960 --height 540
python scripts/validate_experiment_artifacts.py <out_dir> --require-video --require-gif --summary-field strict_contact_only_pass --summary-field grasp_assist_enabled --summary-field lift_window_contact_balance_ratio --summary-field lift_window_unilateral_finger_rope_contact_frames --summary-field rope_render_matches_physics
python scripts/validate_experiment_artifacts.py <out_dir> --require-video --require-gif --summary-field strict_contact_only_pass --summary-field grasp_assist_enabled --summary-field presentation_gripper_geometry --summary-field presentation_aux_panda_pad_geometry_enabled --summary-field strict_require_native_panda_fingers --summary-field rope_lift_height_m --summary-field rope_render_matches_physics
python scripts/lint_harness_consistency.py
```

Mass-control flags now supported by the split demo:

- `--auto-set-weight` (default `0.1`)
- `--mass-spring-scale`
- `--object-mass`
- `--particle-radius-scale` (default `0.2`)
- `--rope-rigid-contact-max`
- `--rope-soft-contact-max`
- `--presentation-grasp-x-offset`
- `--presentation-grasp-y-offset`
- `--presentation-grasp-z-offset`
- `--presentation-gripper-geometry`
- `--presentation-panda-finger-grasp-local-x`
- `--presentation-panda-finger-grasp-local-y`
- `--presentation-panda-finger-grasp-local-z`
- `--presentation-grasp-closed-opening`
- `--gripper-yaw`
- `--finger-shape-friction-multiplier`
- `--presentation-edge-grasp-outset-y`
- `--presentation-table-shape-contact-scale`
- `--strict-min-lift-contact-balance-ratio`
- `--strict-max-unilateral-lift-contact-frames`
- `--strict-require-native-panda-fingers`
- `--strict-max-rope-height`

## Required Artifacts

- experiment directory with:
  - `README.md`
  - `command.sh`
  - `run.log`
  - `summary.json`
  - `scene.npz`
  - `timeseries.csv`
  - `hero.mp4`
  - `hero.gif`
  - `contact_sheet.jpg`
- optional stage-1/two-way additions:
  - `reaction_timeseries.csv`
  - `two_way_ablation.json`

## Success Criteria

- one-way split demo runs end-to-end from a wrapper
- rope settles into a table-edge drape and visibly contacts both table and ground
- finger first contact is detectable before rope motion
- rope render radius equals the physical radius used by the solver
- task status records the artifact path and current milestone conclusion

## Latest Artifact

- Best-known one-way run:
  - `/tmp/robot_table_rope_split_one_way_fine_v5/summary.json`
  - `/tmp/robot_table_rope_split_one_way_fine_v5/hero.mp4`
  - `/tmp/robot_table_rope_split_one_way_fine_v5/contact_sheet.jpg`
- Default-mass validation run:
  - `/tmp/robot_table_rope_split_weight_0p1_default/summary.json`
  - `/tmp/robot_table_rope_split_weight_0p1_default/hero.mp4`
  - `/tmp/robot_table_rope_split_weight_0p1_default/contact_sheet.jpg`
- Default-radius validation run:
  - `/tmp/robot_table_rope_split_radius_0p2_default/summary.json`
  - `/tmp/robot_table_rope_split_radius_0p2_default/hero.mp4`
  - `/tmp/robot_table_rope_split_radius_0p2_default/contact_sheet.jpg`
- Calibrated light-rope run:
  - `/tmp/robot_table_rope_split_candidate_c/summary.json`
  - `/tmp/robot_table_rope_split_candidate_c/hero.mp4`
  - `/tmp/robot_table_rope_split_candidate_c/first_30_frames_sheet.jpg`
- Penetration-gate default run:
  - `/tmp/robot_table_rope_split_penetration_gate_default/summary.json`
  - `/tmp/robot_table_rope_split_penetration_gate_default/hero.mp4`
  - `/tmp/robot_table_rope_split_penetration_gate_default/first_30_frames_sheet.jpg`
- Support-default authoritative run:
  - `tmp/robot_table_rope_split_support_default_authoritative_20260415/summary.json`
  - `tmp/robot_table_rope_split_support_default_authoritative_20260415/hero.mp4`
  - `tmp/robot_table_rope_split_support_default_authoritative_20260415/first_30_frames_sheet.jpg`
- Presentation pick-place candidate:
  - `tmp/robot_table_rope_split_pick_place_contactbuf_20260425_2/summary.json`
  - `tmp/robot_table_rope_split_pick_place_contactbuf_20260425_2/hero.mp4`
  - `tmp/robot_table_rope_split_pick_place_contactbuf_20260425_2/hero.gif`
  - `tmp/robot_table_rope_split_pick_place_contactbuf_20260425_2/review_bundle/contact_sheet.png`
  - `tmp/robot_table_rope_split_pick_place_contactbuf_20260425_2/review_bundle/skeptical_audit.json`
- Demoted `rope_cradle` physics-contact artifact:
  - `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/summary.json`
  - `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/hero.mp4`
  - `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/hero.gif`
  - `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/contact_sheet.jpg`
  - `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/review_bundle/contact_sheet.png`
  - `tmp/robot_table_rope_split_side_suction_fix_edge_balanced_20260427/review_bundle/skeptical_audit.json`
  - old verdict: metrics pass, but user visual review rejects the visible teal
    `rope_cradle` as helper hardware, so it is no longer eligible for final
    meeting-video acceptance
- Current native-Panda-finger-only diagnostic, not accepted:
  - `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428/summary.json`
  - `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428/hero.mp4`
  - `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428/hero.gif`
  - `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428/contact_sheet.jpg`
  - `tmp/robot_table_rope_split_native_panda_fingers_outside_tight_20260428/review_bundle/contact_sheet.png`
  - current verdict: true native Panda fingers and no assist/helper geometry,
    but strict carry fails because the rope does not lift
- Current physical blocker:
  - the hard native Panda finger meshes can touch the rope and sometimes create
    balanced two-sided contact, but they do not yet form a stable pinch/support
    that carries the rope off the table
  - lowering rope mass alone is not acceptable: the light-rope probe flew away,
    so strict acceptance now also exposes a `strict_max_rope_height_m` guard
  - the rope render still preserves physical radius; later visual work may add
    a continuous physical-radius strand renderer, but that is secondary until
    true native finger carry works
- Demoted side-suction false-positive artifact:
  - `tmp/robot_table_rope_split_selfdrop_fix_contact_only_20260426/summary.json`
  - `tmp/robot_table_rope_split_selfdrop_fix_contact_only_20260426/hero.mp4`
  - `tmp/robot_table_rope_split_selfdrop_fix_contact_only_20260426/hero.gif`
  - `tmp/robot_table_rope_split_selfdrop_fix_contact_only_20260426/contact_sheet.jpg`
  - `tmp/robot_table_rope_split_selfdrop_fix_contact_only_20260426/review_bundle/contact_sheet.png`
  - `tmp/robot_table_rope_split_selfdrop_fix_contact_only_20260426/review_bundle/skeptical_audit.json`
  - old `strict_contact_only_pass = true` is no longer accepted because the
    old gate did not reject lift/transfer dominated by one side wall/hook
- Demoted self-drop false-positive artifact:
  - `tmp/robot_table_rope_split_strict_contact_only_pass_20260426/summary.json`
  - old `strict_contact_only_pass = true` is no longer accepted because the
    old gate did not require whole-rope visible lift
- Previous strict contact-only failed default artifact:
  - `tmp/robot_table_rope_split_strict_contact_default_20260426/summary.json`
  - `tmp/robot_table_rope_split_strict_contact_default_20260426/hero.mp4`
  - `tmp/robot_table_rope_split_strict_contact_default_20260426/hero.gif`
  - `tmp/robot_table_rope_split_strict_contact_default_20260426/review_bundle/contact_sheet.png`
  - `tmp/robot_table_rope_split_strict_contact_default_20260426/review_bundle/skeptical_audit.json`
- Current conclusion:
  - the split solver architecture is viable at the fine rope timestep
  - the default support parameter set now passes the non-burying support gate
    while keeping `rope_table_contact_frames_first_30 = 30` and
    `rope_ground_contact_frames_first_30 = 30`
  - `candidate_c` remains a failed support-calibration example, because it
    keeps contact by burying into the support geometry
  - the old side-push presentation path failed because it targeted the wrong
    geometry and never entered a defensible rope contact window
  - the earlier assisted pick-place presentation path showed the intended
    process, but `grasp_assist` is now disallowed for the final meeting video
  - the `rope_cradle` route remains useful historical physics-contact evidence,
    but final acceptance now requires `presentation_gripper_geometry =
    panda_fingers` with no `rope_cradle`, no auxiliary `panda_pads`, and no
    `grasp_assist`
  - the current native-only route proves the controller can reach the rope and
    generate rope response, but it does not yet satisfy physical carry:
    `rope_lift_height_m = 0.0` and
    `grasp_particle_lift_during_lift_transfer_m = 0.010288`
  - final meeting-video acceptance remains blocked on a real Panda finger
    pinch/support geometry that can lift and place the rope without helper
    fixtures or numerical fly-away
  - two-way robot-rope reaction feedback remains outside this accepted one-way
    presentation claim

## Open Questions

- Does the first direct-finger layout already yield a clean single-leading-pad
  contact window, or does that require a follow-up orientation tweak?
- Is the SemiImplicit body-force output sufficiently clean for the planned
  two-way wrench feedback, or will that stage need additional filtering?

## Related Pages

- [../../newton/robot_example_patterns.md](../../newton/robot_example_patterns.md)
- [native_robot_table_penetration_probe.md](./native_robot_table_penetration_probe.md)
- [../../decisions/2026-04-09_robot_ps_interaction_retirement.md](../../decisions/2026-04-09_robot_ps_interaction_retirement.md)
