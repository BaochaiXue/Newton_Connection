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
