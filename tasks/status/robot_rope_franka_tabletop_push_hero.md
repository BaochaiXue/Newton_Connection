# Task Status: robot_rope_franka_tabletop_push_hero

## State

- Status: scaffolded, audit completed, implementation in progress
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

- determine whether a slow tabletop push can be achieved through bridge-layer
  scene/motion/camera changes alone
- add canonical candidate and best-run structure under `phystwin_bridge/results`
- build a stricter hero-demo validation path before accepting any run

## Latest Findings

- `demo_robot_rope_franka.py` now contains a dedicated `tabletop_push_hero`
  path with:
  - tabletop-specific camera presets
  - tabletop reshape / preroll settle logic
  - local summary + physics-validation sidecars
- A canonical local wrapper now exists:
  - `scripts/run_robot_rope_franka_hero.sh`
- A strict local validator now exists:
  - `scripts/validate_robot_rope_franka_hero.py`
- Stable short-smoke runs now show:
  - the rope can preroll-settle on the tabletop without immediate explosion
  - result packaging is no longer the main blocker
  - the remaining blocker is still robot-rope contact
- Best stable short-smoke so far:
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260401_hero_quick_eeoffset_v1/`
  - `preroll_settle_pass = true`
  - `min_clearance_min_m ~= 0.1986`
  - `contact_started = false`

## Current Blocker

- The remaining blocker is no longer generic scene readability or result
  organization.
- The blocker is the tabletop contact geometry itself:
  - robot base placement, IK control body, and near-table target path still do
    not bring the finger/span into credible contact with the rope under the
    stable timestep.
