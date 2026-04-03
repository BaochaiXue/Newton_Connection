# Spec: robot_rope_true_size_recalibration

## Goal

Recalibrate the tabletop hero after switching the rope to a smaller true
physical size so the rope laydown looks natural and the visible Franka finger
clearly reaches and pushes it again.

## Non-Goals

- Modifying `Newton/newton/`
- Reverting to hidden helpers or proxy-only contact claims
- Using render-only thickness tricks as the primary fix
- Declaring final two-way coupling success

## Inputs

- current accepted tabletop hero chain:
  `docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
- current wrapper:
  `scripts/run_robot_rope_franka_tabletop_hero.sh`
- current demo:
  `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- current diagnostics:
  `scripts/diagnose_robot_rope_remote_interaction.py`

## Outputs

- bounded physical-radius sweep videos
- diagnosis board for laydown, contact height, and waypoint regression
- updated candidate bundles for true-size rope recalibration
- doc/status updates if a new candidate becomes authoritative

## Constraints

- keep the robot native to Newton
- keep the table native to Newton
- keep the rope on the PhysTwin -> Newton bridge
- no hidden helper
- no edits under `Newton/newton/`

## Done When

- the true-size rope starts in a natural tabletop shape
- the visible finger clearly reaches and pushes it
- no miss / near-miss / remote-interaction impression remains
- validator + diagnostics + truthful manual review pass
