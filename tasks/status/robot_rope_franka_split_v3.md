# Status: robot_rope_franka_split_v3

## Current State

- Active
- New architecture workstream
- v2 is now treated as a completed limit-proof, not the final path
- split_v3 Stage-0 now has a passing robot-first candidate bundle

## Last Completed Step

- Implemented the first real split_v3 Stage-0 code path:
  - [demo_robot_rope_franka_split_v3_stage0.py](../../Newton/phystwin_bridge/demos/demo_robot_rope_franka_split_v3_stage0.py)
  - [run_robot_rope_franka_split_v3_stage0.sh](../../scripts/run_robot_rope_franka_split_v3_stage0.sh)
- Implemented a Stage-0-specific multimodal review surface:
  - [review_robot_rope_franka_split_v3_stage0.py](../../scripts/review_robot_rope_franka_split_v3_stage0.py)
- Produced the first passing Stage-0 candidate:
  - [20260408_152739_c04_nobanner](../../Newton/phystwin_bridge/results/robot_rope_franka_split_v3_stage0/candidates/20260408_152739_c04_nobanner)
  - current verdict surfaces:
    - `blocking_metrics.json`: PASS
    - `multimodal_review.md`: PASS
    - `diagnostics/review_bundle_hero/skeptical_audit.md`: PASS

## Latest Findings

- Robot-first Stage-0 on the native solver path removes the old startup-sag
  failure that blocked the v2 route.
- The table truly blocks the finger under solver-owned motion:
  - `robot_table_first_contact_phase = contact`
  - `robot_table_penetration_min_m = -4.46e-4`
  - `ee_target_to_actual_error_during_block_mean_m = 7.82e-2`
- Non-finger table loading remains absent:
  - `nonfinger_table_contact_duration_s = 0.0`
- Final Stage-0 presentation uses no support box, no visible tool, and no rope.
- The local generic VQA helper remained noisy on startup frames, so the final
  skeptical review is grounded in same-history frame sheets plus exact solved
  geometry rather than trusting generic VQA over known physical clearance.

## Next Step

- Freeze Stage-0 as a local pass.
- Start split_v3 Stage-1 only:
  - keep the same visible finger truth surface
  - add rope back under the deformable path
  - preserve same-history hero/debug/validation
