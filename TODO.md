> status: active
> canonical_replacement: none
> owner_surface: `task_index`
> last_reviewed: `2026-04-11`
> review_interval: `30d`
> update_rule: `Update when the meeting-level TODO list, active task routing, or archive-routing rule changes.`
> notes: Short meeting map only. Route active detail into the task pages and route history through the archive hub instead of inline historical lists.

# TODO List (Meeting 2026-04-01)

Detailed task truth lives under `docs/bridge/tasks/` and the execution chain.

Primary task index:
- [docs/bridge/tasks/README.md](./docs/bridge/tasks/README.md)

Archive hub for historical task pages:
- [docs/archive/tasks/README.md](./docs/archive/tasks/README.md)

Retired this cycle:
- robot + deformable PS-object demo line
  - retrospective: [2026-04-09_robot_ps_interaction_retirement.md](./docs/decisions/2026-04-09_robot_ps_interaction_retirement.md)

## 1. Continue Newton Interactive Playground — Performance Profiling

- Task pages:
  - [interactive_playground_profiling.md](./docs/bridge/tasks/interactive_playground_profiling.md)
  - [rope_perf_apples_to_apples.md](./docs/bridge/tasks/rope_perf_apples_to_apples.md)
- Current focus:
  - disable rendering
  - run profiler
  - identify the actual bottleneck

## 2. Continue Self-Collision Investigation

- Task page:
  - [self_collision_transfer.md](./docs/bridge/tasks/self_collision_transfer.md)
- Current focus:
  - explore whether PhysTwin's collision kernel can be ported directly into Newton
  - run the ground-contact experiment

## 3. Fast-FoundationStereo Testing

- Task page:
  - [fast_foundation_stereo.md](./docs/bridge/tasks/fast_foundation_stereo.md)
- Current focus:
  - test whether Fast-FoundationStereo can replace RealSense depth
  - evaluate near-infrared stereo support

## 4. Bridge Code Structure Cleanup

- Task page:
  - [bridge_code_structure_cleanup.md](./docs/bridge/tasks/bridge_code_structure_cleanup.md)
- Current focus:
  - reduce bridge-layer monolith size
  - extract pure helper logic from the cloth+bunny demo into clearer modules
