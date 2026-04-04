# Control Update Order Report

Last updated: 2026-04-03

## Verdict

The current tabletop path is effectively kinematic for the robot articulation.
The solver does not get a meaningful chance to let table contact push the robot
off the commanded path because the demo writes robot joint state directly before
the solve and writes the commanded joint state back again after the solve.

## Key Evidence

- Current tabletop baseline uses `tabletop_control_mode = joint_trajectory`.
  See [demo_robot_rope_franka.py:224](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py#L224).
- The model builder configures joint targets and gains:
  - [demo_robot_rope_franka.py:1551](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py#L1551)
  - [demo_robot_rope_franka.py:1552](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py#L1552)
  - [demo_robot_rope_franka.py:1553](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py#L1553)
- But runtime tabletop control bypasses those drives:
  - pre-step direct write to `state_in.joint_q/joint_qd`:
    [demo_robot_rope_franka.py:2256](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py#L2256)
    [demo_robot_rope_franka.py:2257](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py#L2257)
  - immediate FK recompute from the imposed joint state:
    [demo_robot_rope_franka.py:2258](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py#L2258)
  - post-solve direct write back to the commanded joint state:
    [demo_robot_rope_franka.py:2286](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py#L2286)
    [demo_robot_rope_franka.py:2287](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py#L2287)
    [demo_robot_rope_franka.py:2288](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py#L2288)

## Interpretation

- Desired motion is produced by `_joint_phase_state(...)`.
- The desired joint path is then imposed as state, not as a soft reference.
- Any contact-generated deviation can only exist inside the solver step and is
  overwritten before the next substep.
- As a result, near-zero target-tracking error during deep robot-table
  penetration is expected and is evidence of kinematic override, not physical
  blocking.

## Current Root-Cause Lean

- H1: YES
- H2: YES
- H5: YES
- H6: likely YES
