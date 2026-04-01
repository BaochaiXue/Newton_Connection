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
  - `20260401_081639_fixeddt_c08_gatepass`

## Local Navigation Surfaces

- Main demo:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Local bundle root:
  - `Newton/phystwin_bridge/results/robot_rope_franka/`
- Local subtree status stub:
  - `Newton/phystwin_bridge/STATUS.md`

## Current Focus

- preserve the accepted fixed-timestep tabletop hero bundle and its rerun path

## Latest Findings

- Accepted run:
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260401_081639_fixeddt_c08_gatepass/`
- Local convenience mirror:
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
  - `first_contact_time_s = 2.56795`
  - `contact_duration_s = 2.6013`
  - `min_clearance_min_m = -0.0113213938`
  - `preroll_settle_pass = true`
  - strict validator `overall_pass = true`
  - canonical rerun wrapper:
    - `scripts/run_robot_rope_franka_tabletop_hero.sh`
  - note on current drift:
    - the accepted run command history still contains a duplicated `--tabletop-control-mode`
      flag, but the canonical current wrapper is `scripts/run_robot_rope_franka_tabletop_hero.sh`
      and the promoted top-level `summary.json` is the presentation summary

## Current Blocker

- No open blocker for the accepted tabletop-push hero milestone.
