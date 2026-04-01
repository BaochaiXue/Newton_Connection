# Spec: Native Robot + Native Table + PhysTwin Rope Hero Demo

## Goal

Produce a meeting-ready hero demo where a native Newton Franka pushes a
PhysTwin-loaded rope across a native Newton table with clear, legible contact.

## Non-Goals

- Newton core / solver rewrites
- bunny, cloth, or self-collision workstreams
- a ballistic or drop-style rope demo
- a hidden-contact or composited-only result

## Inputs

- task page:
  `docs/bridge/tasks/robot_rope_franka_tabletop_push.md`
- main demo path:
  `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- bridge helpers:
  `Newton/phystwin_bridge/demos/rope_demo_common.py`
  `Newton/phystwin_bridge/demos/bridge_deformable_common.py`

## Outputs

- canonical result tree under `Newton/phystwin_bridge/results/robot_rope_franka/`
- candidate run folders with videos, metrics, QA, and keyframes
- updated bridge status and result metadata

## Constraints

- keep the robot native
- keep the rope on the PhysTwin -> Newton bridge path
- keep the table native
- keep the clip quasi-static and visually readable
- prefer bridge-side changes over Newton core changes

## Done When

- a candidate hero demo clearly shows robot, table, rope, and contact
- the final selected run is documented in `BEST_RUN`
- result metadata and task/status docs are aligned
