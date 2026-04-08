# Status: robot_rope_franka_split_v3

## Current State

- Active
- New architecture workstream
- v2 is now treated as a completed limit-proof, not the final path

## Last Completed Step

- Re-studied official native Newton robot / IK / robot-policy / cloth examples
- Wrote the first split-v3 diagnosis surfaces:
  - `diagnostics/split_v3_native_demo_lessons.md`
  - `diagnostics/split_v3_architecture_decision.md`
  - `diagnostics/split_v3_final_causal_account.md`
- Confirmed the current conclusion:
  - continuing to micro-tune the v2 bridge-side articulated route is low-yield
  - the next honest move is a robot-first / deformable split architecture

## Next Step

- implement the split-v3 Stage-0 robot-table entrypoint
- choose the first robot-first solver pattern
- keep the rope out until Stage-0 passes
