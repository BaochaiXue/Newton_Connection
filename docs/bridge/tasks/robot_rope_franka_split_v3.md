# Task: robot_rope_franka_split_v3

## Question

Can the project satisfy all three final requirements together with a
split-architecture design:

- robot starts stable
- table truly blocks the finger
- finger truthfully pushes the rope

while staying grounded in official native Newton patterns?

## Why It Matters

The v2 rewrite has already shown that removing overwrite semantics is not
enough. The remaining blocker is now architectural, not cosmetic. This task is
the first explicit split-architecture workstream.

## Current Status

- In progress
- v2 is now treated as a completed limit-proof path, not the final answer

## Code Entry Points

- New split-v3 entrypoint: pending
- Current diagnosis references:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka_native_v2.py`
  - `diagnostics/split_v3_native_demo_lessons.md`
  - `diagnostics/split_v3_architecture_decision.md`

## Canonical Commands

- To be filled in when the first split-v3 wrapper lands.

## Required Artifacts

- Stage-0 bundle:
  - robot + table only
- Stage-1 bundle:
  - robot + table + rope
- same-history:
  - `hero_presentation.mp4`
  - `hero_debug.mp4`
  - `validation_camera.mp4`
- multimodal review surfaces

## Success Criteria

- No startup sag
- Real table blocking
- Visible direct-finger rope push
- No hidden helper or fake geometry
- Multimodal skeptical review passes

## Open Questions

- Which robot-first solver pattern is the best fit for Stage-0:
  `SolverMuJoCo` or `SolverFeatherstone`?
- What is the minimum honest coupling path that keeps the rope on the
  deformable side without reintroducing fake robot semantics?

## Related Pages

- `docs/bridge/tasks/robot_rope_franka_native_v2.md`
- `docs/bridge/tasks/robot_rope_franka_physical_blocking.md`
