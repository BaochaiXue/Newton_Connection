> status: historical
> canonical_replacement: `../../../docs/bridge/tasks/robot_rope_franka_physical_blocking.md`
> owner_surface: `robot_rope_franka_split_v3`
> last_reviewed: `2026-04-09`
> notes: Historical exploratory spec archived out of `tasks/spec/`.

# Spec: robot_rope_franka_split_v3

## Goal

Build a new split-architecture robot/table/rope demo that uses a robot-first
native Newton pattern for robot-table truth and keeps the rope on the
deformable bridge path.

## Scope

- create a new split-v3 task chain
- study native Newton robot/deformable examples
- produce Stage-0 robot-table proof in the new architecture
- then add rope back in Stage-1 under the same visible finger truth surface

## Non-Goals

- continuing to salvage v2 as the final route
- modifying `Newton/newton/`
- promoting stronger authority before a real pass exists

## Constraints

- direct finger remains the visible and physical contactor
- table blocking must be real
- rope remains geometry-honest
- multimodal review is primary pass/fail

## Done When

- Stage-0 passes under split-v3
- Stage-1 also passes
- all three user requirements hold together
