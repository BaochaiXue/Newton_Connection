> status: active
> canonical_replacement: none
> owner_surface: `robot_rope_franka_physical_blocking`
> last_reviewed: `2026-04-03`
> review_interval: `14d`
> update_rule: `Update when the stronger physical-blocking claim boundary, diagnostics, or authoritative result meaning changes.`
> notes: New stronger task that must not silently overwrite the existing tabletop-push baseline claim.

# Task: Native Newton Franka Table-Blocking + Rope Push

## Question

Can the bridge deliver a stronger tabletop robot demo where the native Newton
Franka is physically actuated so table contact can block the hand, while the
same visible finger still pushes the bridged PhysTwin rope?

## Why It Matters

The accepted tabletop hero is a readable contact baseline, but it does not yet
prove that robot motion is physically blocked by support contact. This task is
the next claim step:

- native Newton robot remains the contactor
- native Newton table remains the blocking support
- PhysTwin rope remains the deformable object being pushed
- robot-table contact must be able to stop or deflect motion instead of being
  overwritten by the controller

## Claim Boundary

This task is stronger than `robot_rope_franka_tabletop_push_hero`.

It only passes if:

- the robot is physically actuated rather than effectively kinematic
- table contact can create tracking error and block motion
- the visible finger still pushes the rope in a readable way

It does **not** allow:

- hidden helpers
- direct post-solve robot pose overwrite as the primary mechanism
- trajectory-only or camera-only “fixes”
- silent relabeling of the older accepted baseline

## Current State

- Newly opened on `2026-04-03`.
- Existing baseline to preserve:
  - `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
- Existing local bundle root:
  - `Newton/phystwin_bridge/results/robot_rope_franka/`
- Existing entry point under audit:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`

## Expected Artifacts

- diagnostics/control_update_order_report.md
- diagnostics/control_timeline.md
- diagnostics/suspected_kinematic_override.md
- diagnostics/robot_table_clearance_timeseries.csv
- diagnostics/robot_table_contact_report.json
- diagnostics/robot_table_contact_sheet.png
- diagnostics/robot_table_penetration_plot.png
- diagnostics/ee_target_vs_actual_timeseries.csv
- diagnostics/ee_target_vs_actual_plot.png
- diagnostics/blocking_event_report.md
- diagnostics/root_cause_ranked_report.md
- a new stronger candidate bundle plus:
  - `hero_presentation.mp4`
  - `hero_debug.mp4`
  - `validation_camera.mp4`
  - `summary.json`
  - `metrics.json`
  - `validation.md`
  - `manual_review.json`
  - `physics_validation.json`

## Related Pages

- [robot_rope_franka_tabletop_push_hero.md](./robot_rope_franka_tabletop_push_hero.md)
- [robot_deformable_demo.md](./robot_deformable_demo.md)
- [video_presentation_quality.md](./video_presentation_quality.md)
