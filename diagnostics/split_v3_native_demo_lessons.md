# Split V3 Native Demo Lessons

Date: 2026-04-08

Studied:

- [example_robot_panda_hydro.py](/home/xinjie/Newton_Connection/Newton/newton/newton/examples/robot/example_robot_panda_hydro.py)
- [example_ik_franka.py](/home/xinjie/Newton_Connection/Newton/newton/newton/examples/ik/example_ik_franka.py)
- [example_robot_policy.py](/home/xinjie/Newton_Connection/Newton/newton/newton/examples/robot/example_robot_policy.py)
- [example_cloth_franka.py](/home/xinjie/Newton_Connection/Newton/newton/newton/examples/cloth/example_cloth_franka.py)
- [example_softbody_franka.py](/home/xinjie/Newton_Connection/Newton/newton/newton/examples/softbody/example_softbody_franka.py)
- [examples/__init__.py](/home/xinjie/Newton_Connection/Newton/newton/newton/examples/__init__.py)

## Key lessons

### 1. Official robot demos are robot-first

`robot_panda_hydro` and `robot_policy` treat the robot as the primary system:

- articulated builder/model setup is centralized
- controller outputs joint targets or policy actions
- the sim loop is explicit and solver-owned

### 2. Official IK is online target generation, not replay truth

`ik_franka` and `robot_panda_hydro` use IK to compute a working joint target
for the current step.
They do not treat a precomputed joint path as physical truth.

### 3. Official robot + deformable examples are split

`cloth_franka` and `softbody_franka` do not force articulated robot execution
and deformable execution through one monolithic solver semantics.
They coordinate multiple subsystems explicitly.

### 4. Launcher / Example structure matters

`examples/__init__.py` reinforces:

- small Example class
- explicit parser/init/run lifecycle
- clear separation between controller `step()` and renderer `render()`

### 5. What split-v3 should reuse

- explicit Example-style lifecycle
- online target generation
- solver-owned state progression
- split robot/deformable coordination

### 6. What split-v3 should avoid

- giant monolithic demos with mixed semantics
- overwrite/replay truth
- using deformable-side convenience as the reason to keep robot-side semantics
  on a weak articulation path
