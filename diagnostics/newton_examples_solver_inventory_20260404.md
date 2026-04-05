# Newton Examples Solver Inventory

Last updated: 2026-04-04

I scanned the current `Newton/newton/newton/examples` tree to answer one
practical question for the robot+rope work:

> Which native Newton example families already use which solver families, so we
> can reuse existing Newton patterns instead of inventing custom mechanisms?

## High-Level Count

- total example python files scanned: `66`

## Relevant Findings

- Native SemiImplicit deformable examples are already present in Newton:
  - `cloth/example_cloth_hanging.py`
  - `diffsim/example_diffsim_ball.py`
  - `diffsim/example_diffsim_bear.py`
  - `diffsim/example_diffsim_cloth.py`
  - `diffsim/example_diffsim_soft_body.py`
  - `diffsim/example_diffsim_spring_cage.py`
- Native robot examples exist, but most robot-manipulation examples use
  MuJoCo rather than SemiImplicit:
  - `contacts/example_brick_stacking.py`
  - `robot/example_robot_panda_hydro.py`
  - `robot/example_robot_ur10.py`
  - `robot/example_robot_g1.py`
- Native deformable+robot examples also exist, but the main public cloth/soft
  robot examples are VBD / Featherstone heavy rather than SemiImplicit:
  - `cloth/example_cloth_franka.py`
  - `softbody/example_softbody_franka.py`
- There is no obvious off-the-shelf Newton example that already matches our
  exact claim:
  - native Franka
  - native tabletop
  - bridged PhysTwin rope
  - one-way robot -> rope acceptable
  - deformable interaction under SemiImplicit

## Engineering Implication

- Reusing the current bridge-side `demo_robot_rope_franka.py` remains the
  lowest-risk path.
- For this task, it is more native to Newton to:
  - keep the rope interaction on `SolverSemiImplicit`
  - keep the robot and table native
  - reuse existing viewer / validator / rollout-history patterns
- It is less justified to:
  - invent custom collision machinery
  - invent a new solver-side robot/deformable coupling scheme
  - revive the blocked physical-blocking goal in this task

## Conclusion

The Newton examples support the current scope decision:

- `SolverSemiImplicit` is a native Newton deformable path we can legitimately
  build on
- robot manipulation examples in Newton do not provide a ready-made stronger
  physical-blocking recipe we should chase here
- the simplest honest path is still the conservative one-way
  `robot -> rope` baseline
