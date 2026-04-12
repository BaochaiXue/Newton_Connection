# Newton Official Robot Example Patterns

## Purpose

Capture the reusable upstream patterns from official Newton robot examples that
matter to this project.

This page is a durable reference for future bridge work. It is not a claim that
the current bridge-side robot + deformable line is active or already solved.

For robot-driving questions, prefer this page over archived bridge robot demo
surfaces.

## Repo Boundary

As of `2026-04-11`, the local repo still treats the old bridge-side robot +
deformable demo line as retired active work:

- `docs/bridge/current_status.md`
- `docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`

That means the examples below should be used as:

- upstream mechanism references
- implementation templates for any future reopening
- source-grounded explanations of what Newton natively tends to do

They should not be cited as proof that the local bridge task already satisfies
the old combined robot-table-deformable claim.

## How Native Demos Currently Drive Robots

Current Newton native examples fall into three main robot-driving families.

### 1. IK-only reference generation

Representative example:

- `ik_franka`

Driving pattern:

- set end-effector targets
- solve IK directly with `IKSolver`
- update joint coordinates for the current frame

Interpretation:

- this is a kinematic reference-generation pattern
- it is useful for online target generation
- it is not the same thing as contact-rich rigid-body execution

### 2. Rigid-body execution through joint targets

Representative examples:

- `robot_panda_hydro`
- `robot_ur10`
- `robot_policy`

Driving pattern:

- compute or update a desired joint target
- write the target into `control.joint_target_pos`
- let the rigid-body solver advance the robot state

Interpretation:

- this is the main current native pattern for robot-side execution
- when robot/table/contact truth matters, this is the family to study first

### 3. Split robot/deformable staged coupling

Representative examples:

- `cloth_franka`
- `softbody_franka`

Driving pattern:

- compute a robot-side reference from IK or task-space control
- stage the robot update through a dedicated rigid-body path
- then advance the deformable subsystem separately

Interpretation:

- this is the current native pattern for robot + deformable coordination
- it is useful for scheduling and subsystem boundaries
- it should not be over-read as proof that any local strict robot-table-
  deformable claim is already solved

## Outdated Local Practices

The following local bridge-side robot practices are now historical and should
not be used as reference templates.

### Direct state overwrite around the solver

Non-reference-worthy pattern:

- write desired values into `state_in.joint_q/joint_qd`
- step the solver
- write the target back into `state_out.joint_q/joint_qd`

Why it is outdated:

- it suppresses the very tracking error and contact response that the robot
  execution path is supposed to reveal

Use instead:

- solver-owned state progression with targets written into `control`

### Treating the old bridge-side SemiImplicit Franka path as the baseline robot template

Non-reference-worthy pattern:

- start robot design discussions from the archived bridge-side
  `SolverSemiImplicit` Franka actuation experiments

Why it is outdated:

- those experiments are useful as failure analysis
- they are not the current native reference for how Newton examples drive
  articulated robots

Use instead:

- `robot_panda_hydro` for rigid manipulation semantics
- `ik_franka` for online target generation
- `cloth_franka` / `softbody_franka` for split deformable scheduling

### Treating retired bridge robot demos as positive design priors

Non-reference-worthy pattern:

- inheriting controller assumptions from retired local robot demos because they
  are already in-repo

Why it is outdated:

- those surfaces remain valuable as archived evidence and negative results
- they are no longer recommended starting points for implementation decisions

## Recommended Reading Order

### 1. `robot_panda_hydro`

Use first when the question is:

- how should robot-side manipulation be organized?
- which contact geometry deserves the highest fidelity?
- how should the table exist in the same native scene as the robot?

Why it matters:

- the robot is solver-driven, not state-overwritten
- IK generates targets; it is not the physics truth surface
- finger / hand contact geometry is treated as special
- non-critical robot geometry is downgraded to cheaper approximations
- the table is a native world shape, not a late debug prop

Project lesson:

- if robot-side blocking or finger-first contact matters, start here before
  reading deformable examples

### 2. `ik_franka`

Use when the question is:

- how should online Cartesian intent become joint references?

Why it matters:

- it shows `IKObjectivePosition`, `IKObjectiveRotation`, and joint-limit-aware
  solving in the smallest Franka example
- the control pattern is per-step target refresh, not offline replay treated as
  truth

Project lesson:

- treat IK as a reference generator that feeds the execution path; do not treat
  it as a substitute for contact-rich robot simulation

### 3. `cloth_franka`

Use when the question is:

- how does Newton stage robot + deformable coordination?
- how are rigid and cloth subsystems split?

Why it matters:

- the example uses separate rigid and cloth solver paths
- cloth runs through `SolverVBD`
- the robot path is staged explicitly before deformable stepping

Project caution:

- this is a split-coupling reference, not a proof of honest fully dynamic
  direct-finger manipulation
- the robot side is driven in a staged way that is useful architecturally, but
  it should not be over-claimed as the final answer to a strict bridge-side
  physical-blocking requirement

### 4. `softbody_franka`

Use when the question is:

- what does the same split idea look like for soft bodies in meter scale?

Why it matters:

- it makes the coupling pattern even clearer than `cloth_franka`
- IK solves a target pose
- the result is converted into joint-space motion for the robot side
- the soft body then advances through `SolverVBD`

Project caution:

- this example is extremely useful for staged robot/deformable coupling
- it still represents a guided robot-side execution path rather than a
  meeting-grade proof of honest direct-finger bridge dynamics

### 5. `robot_ur10`

Use when the question is:

- what should a clean target-update loop look like?

Why it matters:

- it isolates the pattern:
  - update target trajectory
  - write `joint_target_pos`
  - step the solver

Project lesson:

- this is the best compact template for bridge-side control plumbing when the
  issue is target update order rather than contact semantics

### 6. `robot_policy`

Use when the question is:

- how should a reusable robot control scaffold be structured?
- how should observations, actions, reset, and graph capture fit together?

Why it matters:

- it provides a strong deployment scaffold
- it shows a clean pattern for `control.joint_target_pos`, reset, and graph
  capture

Project lesson:

- borrow scaffolding from here
- do not mistake it for a contact-rich manipulation template

### 7. Lower-priority sanity references

- `robot_cartpole`
- `robot_g1`
- `robot_h1`
- `robot_anymal_d`

Use these for:

- articulation sanity
- startup stability intuition
- minimal solver-owned robot examples

They are lower priority for this project because they are farther from
finger-table-deformable interaction.

## Reusable Patterns

### Robot-side control ownership

The strongest upstream robot examples let the solver own state progression.

Preferred pattern:

- compute or update a target
- write target data into `control`
- let the solver advance the state

Avoid:

- writing desired state directly into `state_in` / `state_out` and then calling
  that physical execution

### Contact geometry stratification

The most relevant manipulation example does not give every robot surface the
same contact treatment.

Preferred pattern:

- keep fingers / hand as the highest-fidelity contact geometry
- simplify non-critical robot geometry when possible
- keep visual geometry and physical geometry conceptually separate even when
  they share the same asset source

### Native table / world geometry

The table should be part of the physical scene from the start.

Preferred pattern:

- add it as native world geometry
- validate it through solver-owned contact, not by presentation-only props

### IK as online reference generation

Upstream IK examples solve for the current step's desired robot configuration.

Preferred pattern:

- use IK to produce a current reference
- feed that reference into the robot execution layer

Avoid:

- treating a precomputed joint path as if it were automatically physically
  truthful

### Split robot / deformable coordination

The official deformable examples are useful, but they carry an important scope
boundary.

What they teach well:

- subsystem separation
- explicit scheduling
- coupling order
- collision-pipeline placement

What they do not automatically prove:

- that a strict local bridge claim about honest direct-finger blocking and
  deformable interaction has been solved

## What Not To Copy Blindly

- A giant monolithic bridge demo that mixes robot control semantics,
  deformable stepping, diagnostics, and presentation logic in one path.
- State overwrite used as a hidden truth surface.
- Archived local bridge robot demos used as positive control templates.
- The assumption that any split robot/deformable upstream example is already a
  match for the local bridge claim boundary.

## How To Use This Page In Future Work

If robot-side work is reopened later:

- Stage-0 robot/table blocking should begin from `robot_panda_hydro` plus
  `ik_franka`
- control-loop cleanup should use `robot_ur10`
- any Stage-1 deformable reintegration should read `cloth_franka` and
  `softbody_franka` with an explicit written claim boundary
- broader robot deployment scaffolding can borrow from `robot_policy`
- archived bridge robot demos should be consulted only for failure analysis, not
  as primary implementation templates

## Related Pages

- [README.md](./README.md)
- [architecture.md](./architecture.md)
- [runtime_and_contacts.md](./runtime_and_contacts.md)
- [../decisions/2026-04-09_robot_ps_interaction_retirement.md](../decisions/2026-04-09_robot_ps_interaction_retirement.md)
- [../../diagnostics/split_v3_native_demo_lessons.md](../../diagnostics/split_v3_native_demo_lessons.md)
