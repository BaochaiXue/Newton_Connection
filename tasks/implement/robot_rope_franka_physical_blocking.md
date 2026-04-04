# Implement: robot_rope_franka_physical_blocking

## Canonical Commands

- Control-plane audit inputs:
  - `docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
  - `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
  - `scripts/run_robot_rope_franka_tabletop_hero.sh`
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Existing bundle roots:
  - `Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/`
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/`

## Required Diagnostics

- control update-order report
- robot-table signed-distance / penetration timeseries
- end-effector target-vs-actual report around blocking
- contact-filter and hidden-helper audit
- pre-fix and post-fix full-video review

## Expected Stronger-Task Run Shape

- a new wrapper under `scripts/` if the old tabletop wrapper no longer matches
  the stronger claim
- a new blocking validator under `scripts/`
- run-local diagnostics placed under the candidate directory

## Guardrails

- Do not edit `Newton/newton/`
- Do not destroy the old accepted tabletop baseline
- Do not accept a camera-only or path-only workaround
