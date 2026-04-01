# PhysTwin -> Newton Bridge: TODO Index

> Updated: 2026-03-31  
> This file is now a task index. The detailed source of truth lives under `docs/bridge/tasks/`.

## How To Use This File

- Use this page to see the active task set at a glance.
- Do not expand detailed implementation notes here.
- Put detailed context, commands, success criteria, and open questions into the linked task pages.

Primary task index:
- [docs/bridge/tasks/README.md](./docs/bridge/tasks/README.md)

Operational ledgers:
- [docs/bridge/current_status.md](./docs/bridge/current_status.md)
- [docs/bridge/open_questions.md](./docs/bridge/open_questions.md)
- [docs/bridge/experiment_index.md](./docs/bridge/experiment_index.md)

## High Priority

### 1. Slide Deck Overhaul
- Task page: [slide_deck_overhaul.md](./docs/bridge/tasks/slide_deck_overhaul.md)
- Current goal: make each slide defensible in 15-20 seconds and keep the story hypothesis-driven.

### 2. Bunny Penetration Force Diagnostic
- Task page: [bunny_penetration_force_diagnostic.md](./docs/bridge/tasks/bunny_penetration_force_diagnostic.md)
- Current goal: explain bunny failure in terms of direction, magnitude, internal force, and geometry with parity-checked diagnostics.

### 3. Video Presentation Quality
- Task page: [video_presentation_quality.md](./docs/bridge/tasks/video_presentation_quality.md)
- Current goal: make all demos readable as evidence, not just visually acceptable.

### 4. Robot + Deformable Demo
- Task page: [robot_deformable_demo.md](./docs/bridge/tasks/robot_deformable_demo.md)
- Current goal: turn robot + deformable into a defendable claim with native Newton robot assets, layered deliverables, and measurable acceptance.

### 5. Native Robot Rope Drop/Release Sanity Baseline
- Task page: [native_robot_rope_drop_release.md](./docs/bridge/tasks/native_robot_rope_drop_release.md)
- Current goal: isolate the stage-0 native Franka rope release/drop baseline before any stronger two-way-coupling claim.

## Medium Priority

### 6. Interactive Playground Profiling
- Task page: [interactive_playground_profiling.md](./docs/bridge/tasks/interactive_playground_profiling.md)
- Current goal: maintain a no-render, data-backed explanation of realtime performance.

### 6b. Rope Perf Apples-To-Apples
- Task page: [rope_perf_apples_to_apples.md](./docs/bridge/tasks/rope_perf_apples_to_apples.md)
- Current goal: establish the same-case Newton-vs-PhysTwin rope replay benchmark before discussing optimization.

### 7. Self-Collision Transfer
- Task page: [self_collision_transfer.md](./docs/bridge/tasks/self_collision_transfer.md)
- Current goal: turn self-collision into a controlled decision task and choose the minimum bridge-side scheme that is stable enough for demos.

### 8. Data Collection Protocol
- Task page: [data_collection_protocol.md](./docs/bridge/tasks/data_collection_protocol.md)
- Current goal: define a stable capture procedure for new data.

## Lower Priority

### 9. Fast-FoundationStereo Evaluation
- Task page: [fast_foundation_stereo.md](./docs/bridge/tasks/fast_foundation_stereo.md)
- Current goal: determine whether it is worth adopting in the current pipeline.

## Adjacent Work

These are still important, but not yet promoted into dedicated bridge task pages here:

- Multi-view 3D reconstruction / LBS tracking on the PhysTwin side
- MPM direction exploration
- Meeting-summary discipline
- Code naming / slide explanation hygiene

If one of these becomes an active bridge workstream, create a new page from:
- [docs/bridge/tasks/_task_template.md](./docs/bridge/tasks/_task_template.md)

## Confirmed / Already Established

- PhysTwin -> Newton bridge baseline exists for recall demos.
- Particle-mesh contact is already bidirectional at the source-code level.
- Weight scaling is not a single-mass knob; bridge logic couples mass and spring/contact semantics.
- Rope + bunny interaction is demonstrated.
- Multi-deformable interaction works in current bridge demos.
- Force diagnostic infrastructure now exists on the cloth+bunny path.
