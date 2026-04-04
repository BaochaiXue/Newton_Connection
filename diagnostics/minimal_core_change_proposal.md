# Minimal Core Change Proposal

Last updated: 2026-04-03

## Goal

Enable a native Newton articulated robot in `SolverSemiImplicit` to move under
an explicit control input in a way that allows contact-generated tracking error
to persist, so the bridge layer can build a truthful physical-blocking tabletop
rope demo.

## Smallest Useful Capability

One of the following must be verified and exposed for SemiImplicit articulated
robots:

1. A working joint-target actuation path where dynamic updates to:
   - `control.joint_target_pos`
   - `control.joint_target_vel`
   together with
   - `model.joint_target_ke`
   - `model.joint_target_kd`
   actually move articulated joints during `solver.step(...)`.

2. A working feedforward torque path where updates to:
   - `control.joint_f`
   actually move articulated joints during `solver.step(...)`.

3. If neither of the above is intended to work in the current API, expose a
   documented articulation-motor control surface for `SolverSemiImplicit`.

## Why This Is Needed

The bridge layer already proved:

- the old tabletop path is a kinematic override
- removing the overwrite is not enough by itself
- the currently accessible target/force surfaces do not produce joint motion on
  this path

So the missing piece is no longer “better task tuning”. It is a verified
articulation actuation capability.

## Acceptance For The Core/API Fix

After the minimal fix, the bridge layer should be able to demonstrate all of
the following:

- commanded robot motion comes from an actuation surface, not direct state
  overwrite
- table contact can create persistent target-vs-actual error
- robot-table penetration stays near zero or below a tiny documented tolerance
- the same visible finger still pushes the rope

## What The Bridge Layer Can Do Immediately Afterward

Once a verified articulated actuation path exists, the current stronger-task
tooling is already in place:

- [run_robot_rope_franka_physical_blocking.sh](/home/xinjie/Newton_Connection/scripts/run_robot_rope_franka_physical_blocking.sh)
- [diagnose_robot_rope_physical_blocking.py](/home/xinjie/Newton_Connection/scripts/diagnose_robot_rope_physical_blocking.py)
- [validate_robot_rope_franka_physical_blocking.py](/home/xinjie/Newton_Connection/scripts/validate_robot_rope_franka_physical_blocking.py)

The remaining work would then reduce to bounded gain/base-pose/contact retuning
to recover readable rope push under truthful physical blocking.
