> status: historical
> canonical_replacement: `../../decisions/2026-04-09_robot_ps_interaction_retirement.md`
> owner_surface: `robot_rope_franka_physical_blocking`
> last_reviewed: `2026-04-09`
> review_interval: `90d`
> update_rule: `Historical evidence only. Do not record new active state here.`
> notes: Archived stronger direct-finger blocking branch after the 2026-04-09 retirement decision.

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

Current diagnostic lean:

- the old readable tabletop path remains non-physical because it overwrites
  joint state directly
- the repaired bridge-layer `joint_target_drive` path now keeps solver body
  truth and explicit reduced-state resync instead of stale post-step FK
  overwrite
- Stage-0 rigid-only direct-finger blocking has already passed locally on that
  repaired bridge-layer path
- the current canonical stronger-task wrapper now defaults to the first verified
  no-support-box / short-settle mitigation:
  - `tabletop_support_box_mode = none`
  - `tabletop_settle_seconds = 0.05`
  - `tabletop_robot_base_offset = (-0.56, -0.22, 0.10)`
  - local pass surface:
    `Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260408_092911_rope_integrated_auto_fix_20260408`
- this is a real bridge-layer improvement, but not the final physics-side cure:
  - the default stronger demo no longer starts from the obviously collapsed
    long-settle/support-box path
  - however the deeper robot-side gravity-support problem on the current
    `SolverSemiImplicit` articulation path is still not fully removed
- the new official-style source path is now also integrated locally:
  - `demo_robot_rope_franka_native_v2.py` can run with `SolverMuJoCo` and
    Franka gravcomp enabled
  - a replayed rope composite from that source is now reproducible
  - but there is still no meeting-grade clip that honestly and clearly shows
    all three requirements at once; the remaining problem is trajectory /
    presentation readability, not merely “make the old bridge path less bad”
- a Newton core change is still not justified at this boundary

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
