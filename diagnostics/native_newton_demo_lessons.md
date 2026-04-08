# Native Newton Demo Lessons

Date: 2026-04-08

Studied sources:

- [example_robot_panda_hydro.py](/home/xinjie/Newton_Connection/Newton/newton/newton/examples/robot/example_robot_panda_hydro.py)
- [example_ik_franka.py](/home/xinjie/Newton_Connection/Newton/newton/newton/examples/ik/example_ik_franka.py)
- [example_cloth_franka.py](/home/xinjie/Newton_Connection/Newton/newton/newton/examples/cloth/example_cloth_franka.py)
- [example_robot_policy.py](/home/xinjie/Newton_Connection/Newton/newton/newton/examples/robot/example_robot_policy.py)
- [examples/__init__.py](/home/xinjie/Newton_Connection/Newton/newton/newton/examples/__init__.py)
- [demo_robot_rope_franka.py](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py)

## 1. How official Newton demos represent robot control

Official Newton demos do not use direct post-step state overwrite as their main
control semantics.

The dominant patterns are:

- `joint_target_pos` servo control on the model/control surface
- IK solving into a working joint buffer, then copying that result into
  `control.joint_target_pos`
- a single explicit simulation loop:
  - `state_0.clear_forces()`
  - `collision_pipeline.collide(state_0, contacts)`
  - `solver.step(state_0, state_1, control, contacts, dt)`
  - swap `state_0`, `state_1`

Evidence:

- `robot_panda_hydro` writes targets into `self.control.joint_target_pos`, then
  calls `collision_pipeline.collide(...)` and `solver.step(...)`. It does not
  overwrite `state_1.body_q` after the solver.
- `robot_policy` configures joint target modes and stiffness/damping directly on
  the builder/model side rather than replaying a full joint trajectory as body
  truth.

## 2. What the official IK usage pattern looks like

Official IK usage is online and target-driven:

- build one or more IK objectives
- keep a working joint vector (`joint_q_ik`)
- every frame:
  - update target position / rotation
  - run IK
  - copy solved joints into `control.joint_target_pos`

Important lesson:

- `ik_franka` is not a full physics demo; it directly solves kinematics each
  frame.
- `robot_panda_hydro` is the more relevant control shape for this task:
  IK is used to generate joint targets, but physics execution still happens in
  the solver loop.

## 3. How official robot + deformable coupling is organized

Official robot + deformable examples are **split-architecture**, not one
monolithic single-solver articulation/deformable rewrite.

Evidence:

- `cloth_franka` uses:
  - `SolverFeatherstone` for the robot
  - `SolverVBD` for the cloth
- the robot and deformable system are stepped in a coordinated but distinct
  pipeline
- the robot side gets a controller appropriate for articulated dynamics
- the deformable side gets the solver specialized for cloth/soft contacts

This is the strongest native lesson from the official examples:

**Newton’s native examples do not force articulated robot control and
deformables through the same solver path just to keep the code simple.**

## 4. What should be reused directly

Reusable from official patterns:

- Example-style class structure:
  - scene build
  - controller update
  - `simulate()`
  - `step()`
  - `render()`
- explicit `state_0` / `state_1` double buffering
- explicit collision pipeline object instead of implicit hidden collision calls
- IK as an online target generator, not a one-shot preprocessing step
- `control.joint_target_pos` as the main robot control surface
- `examples/__init__.py` launcher discipline:
  - `create_parser()`
  - `init()`
  - `run()`

Reusable from the bridge side only after re-certification:

- rope IR loading
- object-only rope bridge path
- same-history render/export utilities
- direct-finger diagnostics and proof surface

## 5. What should be avoided from our current broken path

Banned design habits from the legacy bridge demo:

- mixing multiple robot semantics in one file:
  - IK overwrite
  - joint trajectory overwrite
  - joint target drive
  - replay
- using post-step reduced-state logic to overwrite solved body truth
- carrying readable-baseline geometry assumptions into truthful physical runs
- using support props to mask a robot startup instability that already exists
  without the support prop
- relying on old numeric contact metrics as primary pass/fail instead of
  multimodal visual inspection

## 6. Concrete design takeaway

The most important native Newton lesson is not “copy Panda Hydro literally”.
It is:

**copy the control structure, but also respect Newton’s solver specialization.**

For this task, that means:

- the bridge should stop using overwrite/replay semantics
- the robot side should follow the native online-target pattern
- the final architecture should strongly consider a split robot/deformable
  structure rather than forcing everything into one SemiImplicit articulation
  path just because the rope already works there
