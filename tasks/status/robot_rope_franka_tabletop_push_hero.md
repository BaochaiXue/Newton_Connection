> status: active
> canonical_replacement: none
> owner_surface: `robot_rope_franka_tabletop_push_hero`
> last_reviewed: `2026-04-01`
> review_interval: `14d`
> update_rule: `Update when the promoted run, task blocker, or registry-backed claim boundary changes.`
> notes: Live status page for the tabletop-push hero task. Committed authority lives in `results_meta/`; local result trees are secondary.

# Task Status: robot_rope_franka_tabletop_push_hero

## State

- Status: accepted
- Last updated: 2026-04-01

## Canonical Authority

- Task page:
  - `docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
- Registry entry:
  - `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
- Registry indexes:
  - `results_meta/INDEX.md`
  - `results_meta/LATEST.md`
- Current committed run id:
  - `20260401_203416_remotefix_truthcam_c12`

## Local Navigation Surfaces

- Main demo:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Local bundle root:
  - `Newton/phystwin_bridge/results/robot_rope_franka/`
- Local subtree status stub:
  - `Newton/phystwin_bridge/STATUS.md`

## Current Focus

- preserve the truth-fixed tabletop hero bundle and its rerun path
- keep `ee_contact_radius` explicitly downgraded to diagnostic-only semantics
  so proxy radii cannot drift back into the task's proof surface

## Latest Findings

- Accepted run:
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260401_203416_remotefix_truthcam_c12/`
- Local convenience mirror:
  - `Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/`
- Winning implementation details:
  - fixed timestep preserved: `sim_dt = 5e-5`, `substeps = 667`
  - native Newton Franka + native Newton table + PhysTwin rope remain intact
  - tabletop hero switched from unreliable tabletop IK to a tabletop-only
    native joint-space waypoint controller
  - remote-interaction root cause was diagnosed as a visual-truth mismatch plus
    proxy/camera ambiguity, not a hidden helper or Newton-core bug
  - rope render radius is now aligned with the physical rope collision radius
  - hero/debug contact reporting is now grounded in actual finger-box contact
    instead of `finger_span` as the primary proof surface
  - hero presentation still hides the oversized pedestal while validation view
    keeps the full geometry honest
- Accepted run evidence:
  - `hero_presentation.mp4`, `hero_debug.mp4`, `validation_camera.mp4`
  - `duration_s = 6.2`
  - `contact_started = true`
  - `first_contact_phase = approach`
  - `first_contact_time_s = 1.6675`
  - `actual_finger_box_first_contact_time_s = 1.6675`
  - `contact_duration_s = 2.96815`
  - `contact_peak_proxy = right_tip_box`
  - `min_clearance_min_m = -0.0128063839`
  - `preroll_settle_pass = true`
  - strict validator `overall_pass = true`
  - truthful manual review `all YES`
  - canonical rerun wrapper:
    - `scripts/run_robot_rope_franka_tabletop_hero.sh`
  - remote-interaction review:
    - full-video review now says the visible Franka finger itself is clearly the
      contactor and the earlier stand-off impression is gone

## Current Blocker

- No open blocker for the accepted tabletop-push hero milestone.

## Proof-Surface Guardrail

- `ee_contact_radius` is `diagnostic only`.
- It may still affect proxy overlays and offline proxy-clearance reports for:
  - `gripper_center`
  - `left_finger`
  - `right_finger`
  - `finger_span`
- It does **not** change the real finger collider geometry.
- It is **not** valid as final contact proof.
- It is **not** allowed as a final acceptance surface for this task.
- Accepted tabletop contact claims must remain grounded in actual finger-box
  contact evidence.
