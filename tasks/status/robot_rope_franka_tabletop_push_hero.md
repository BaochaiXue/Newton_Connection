# Task Status: robot_rope_franka_tabletop_push_hero

## State

- Status: accepted
- Last updated: 2026-04-01

## Authoritative Paths

- Task page:
  - `docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
- Main demo:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Local status:
  - `Newton/phystwin_bridge/STATUS.md`
- Result root:
  - `Newton/phystwin_bridge/results/robot_rope_franka/`

## Current Focus

- preserve the accepted fixed-timestep tabletop hero bundle and its rerun path

## Latest Findings

- Accepted run:
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260401_081639_fixeddt_c08_gatepass/`
- Promoted mirror:
  - `Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/`
- Winning implementation details:
  - fixed timestep preserved: `sim_dt = 5e-5`, `substeps = 667`
  - native Newton Franka + native Newton table + PhysTwin rope remain intact
  - tabletop hero switched from unreliable tabletop IK to a tabletop-only
    native joint-space waypoint controller
  - table raised to a readable workbench height so the contact line is legible
  - hero presentation hides the oversized visual pedestal while validation view
    keeps the full geometry honest
- Accepted run evidence:
  - `hero_presentation.mp4`, `hero_debug.mp4`, `validation_camera.mp4`
  - `duration_s = 6.2`
  - `contact_started = true`
  - `first_contact_phase = push`
  - `contact_duration_s = 1.8676`
  - `preroll_settle_pass = true`
  - strict validator `overall_pass = true`

## Current Blocker

- No open blocker for the accepted tabletop-push hero milestone.
