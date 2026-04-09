> status: active
> canonical_replacement: none
> owner_surface: `robot_visible_rigid_tool_baseline`
> last_reviewed: `2026-04-04`
> review_interval: `14d`
> update_rule: `Update when the visible-tool claim boundary, tool geometry, or promoted result meaning changes.`
> notes: New intermediary baseline between the readable tabletop finger-push hero and the blocked physical-contact task.

# Task: Visible Rigid Tool Tabletop Rope Baseline

## Question

Can the bridge deliver a visually honest tabletop robot demo where a native
Newton Franka carries a visible rigid tool, and that same visible rigid tool is
the real physical contactor that pushes the bridged PhysTwin rope across the
native Newton tabletop?

## Why It Matters

This is a conservative, meeting-safe intermediary step:

- stronger than bare “robot nearby” motion
- weaker than the blocked physical-contact claim
- explicitly tool-mediated
- useful even if the stronger SemiImplicit articulation-blocking path remains
  blocked

## Claim Boundary

This task only claims:

- native Newton Franka
- native Newton tabletop
- PhysTwin -> Newton rope
- a **visible rigid robot-mounted tool** is the actual physical contactor
- rope deformation and motion begin after the visible tool touches it

It does **not** claim:

- robot-table physical blocking
- full two-way coupling
- direct finger contact

## Current State

- Opened on `2026-04-04`.
- Existing baseline preserved:
  - `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
- Existing stronger blocked follow-on preserved:
  - `docs/bridge/tasks/robot_rope_franka_physical_blocking.md`
- Promoted visible-tool baseline:
  - `results_meta/tasks/robot_visible_rigid_tool_baseline.json`
  - authoritative run: `20260404_145031_c08_samehistory`
- Existing entry point reused:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`

## Current Best Meaning

- The promoted run mounts a visible red crossbar-style capsule tool on `fr3_link7`.
- That visible tool is the real physical contactor in hero/debug/validation views.
- Tool contact begins before visible rope lateral motion and deformation.
- The authoritative rerender now keeps hero/debug/validation on one saved rollout history, so all three views agree on tool-first contact ordering.
- The promoted bundle now includes separate skeptical video audits over the prepared hero and validation review bundles.
- The result is meeting-safe as a **tool-mediated** contact baseline only.
- The promoted candidate now also has:
  - passing standard hero validation
  - passing fail-closed skeptical review bundles for hero/debug/validation
  - a passing repo-native artifact-contract check after adding candidate-local
    `README.md` and `command.txt`

## Expected Artifacts

- candidate bundle under a dedicated result root
- `tool_geometry_report.md`
- `tool_vs_collider_report.md`
- `rope_visual_vs_physical_thickness_report.md`
- `multimodal_review.md`
- `hero_presentation.mp4`
- `hero_debug.mp4`
- `validation_camera.mp4`
- `contact_sheet.png`
- `event_sheet.png`

## Related Pages

- [robot_rope_franka_tabletop_push_hero.md](./robot_rope_franka_tabletop_push_hero.md)
- [robot_rope_franka_physical_blocking.md](./robot_rope_franka_physical_blocking.md)
- [remote_interaction_root_cause.md](./remote_interaction_root_cause.md)
