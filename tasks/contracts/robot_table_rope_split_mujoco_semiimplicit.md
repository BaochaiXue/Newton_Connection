# Contract: robot_table_rope_split_mujoco_semiimplicit / one_way_direct_finger

## Goal

Land a truthful one-way direct-finger Panda + table + rope split demo using
MuJoCo on the rigid side and SemiImplicit on the rope side.

## Scope Boundary

- In scope:
  - native Panda + native rigid table on the rigid side
  - PhysTwin rope on the SemiImplicit side
  - table-edge drape scene
  - side-finger push motion
  - physical-only rope render thickness
  - one-way robot -> rope coupling
- Out of scope:
  - full two-way robot-rope coupling as a first-pass acceptance gate
  - Newton core changes
  - any return to state overwrite semantics
  - treating the presentation grasp-assist video as a pure contact-only
    contract pass
  - using `grasp_assist` for the final meeting-facing pick-place video
  - using visible helper gripper geometry such as `rope_cradle` or auxiliary
    `panda_pads` as the final meeting-facing route
  - accepting one-sided lift/transfer contact that reads as side suction, side
    pickup, or hidden hook support

## Required Inputs

- `docs/newton/robot_example_patterns.md`
- `Newton/phystwin_bridge/demos/demo_native_robot_table_penetration_probe.py`
- `Newton/newton/newton/examples/robot/example_robot_panda_hydro.py`
- `Newton/newton/newton/examples/ik/example_ik_franka.py`
- `Newton/newton/newton/examples/cloth/example_cloth_hanging.py`

## Required Outputs

- new split demo and wrapper
- one validated experiment directory
- task status entry with artifact path and conclusion

## Hard-Fail Conditions

- robot motion reverts to direct state overwrite
- rope render thickness differs from the physical rope radius in the accepted run
- rope motion begins before any detectable finger-rope contact
- accepted run lacks either rope-table or rope-ground contact
- accepted presentation video uses `grasp_assist`
- accepted final meeting video uses anything other than
  `presentation_gripper_geometry = "panda_fingers"`
- accepted final meeting video relies on auxiliary green pad meshes,
  `rope_cradle`, or any other helper contactor that is not the native Panda
  finger mesh
- accepted final meeting video makes the rope fly away or exceed the strict
  max rope height guard
- accepted presentation video lifts primarily through one visible side wall,
  hook, or unilateral finger/cradle contact
- accepted final meeting video depends on visually obvious helper hardware that
  does not read as part of the Panda gripper
- accepted final meeting video shows the rope as particle clumps rather than a
  continuous rope-like object at truthful physical radius

## Acceptance Criteria

- wrapper runs end-to-end and emits the required artifact bundle
- `summary.json` includes:
  - `first_finger_rope_contact_frame`
  - `first_rope_motion_frame`
  - `rope_motion_after_contact`
  - `rope_table_contact_frames`
  - `rope_ground_contact_frames`
  - `rope_render_matches_physics`
  - `coupling_mode`
- `rope_motion_after_contact == true`
- `rope_render_matches_physics == true`
- `rope_table_contact_frames > 0`
- `rope_ground_contact_frames > 0`
- `coupling_mode == "one_way"`

## Evaluator Evidence Required

- validator command(s):
  - `python -m py_compile Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
  - `bash scripts/run_robot_table_rope_split_demo.sh`
  - `python scripts/validate_experiment_artifacts.py <out_dir> --require-video --require-gif --summary-field rope_motion_after_contact --summary-field rope_render_matches_physics`
- artifact paths:
  - experiment `summary.json`
  - `hero.mp4`
  - `hero.gif`
  - `contact_sheet.jpg`
- skeptical review required: no

## Next Command After Acceptance

```bash
python scripts/lint_harness_consistency.py
```

## Presentation Addendum

The meeting-facing `presentation_pick_place` path is a separate video artifact
track. It must run without `grasp_assist` for final acceptance. Diagnostic runs
may still enable assist explicitly, but assisted artifacts are not eligible for
final meeting-video PASS.

Strict presentation acceptance additionally requires:

- `grasp_assist_enabled == false`
- `first_grasp_assist_frame == null`
- `grasp_assist_frames == 0`
- `presentation_gripper_geometry == "panda_fingers"`
- `presentation_aux_panda_pad_geometry_enabled == false`
- `strict_require_native_panda_fingers == true`
- `strict_contact_only_pass == true`
- nonzero sustained two-finger contact during the lift/transfer window
- `lift_window_contact_balance_ratio >= strict_min_lift_contact_balance_ratio`
- `lift_window_unilateral_finger_rope_contact_frames <=
  strict_max_unilateral_lift_contact_frames`
- measurable local grasp-segment lift during the closed lift/transfer window
- measurable whole-rope visible lift, so a local contact/release bounce cannot
  pass as a pick
- zero final finger/cradle-rope contact after release
- zero non-finger robot-body table contact; finger/cradle edge contact may be
  reported separately for the physical edge-scoop path
- skeptical video review must be able to defend the interaction as a physical
  two-sided grasp/lift rather than side suction or side hooking
- final meeting-facing acceptance additionally requires visual naturalness:
  the contactor must read as the robot gripper rather than a colored helper
  fixture, and rope rendering must preserve physical thickness while reading as
  a continuous strand instead of a bead cluster
