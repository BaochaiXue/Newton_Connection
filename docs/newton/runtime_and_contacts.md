# Newton Runtime And Contacts

## Purpose

Document the Newton runtime concepts that repeatedly matter in current research
questions.

## Runtime Topics That Matter Most

### Semi-Implicit Solver

This is the main Newton solver family currently used by the bridge demos for
spring-mass / cloth / rope interaction experiments.

### Viewer / Rendering

The project uses both:

- interactive viewers
- offline MP4 rendering via ViewerGL frame capture

These should always be distinguished from no-render physics profiling.

### Particle-Shape Contact

This is central to:

- cloth vs bunny
- rope vs bunny
- robot proxy vs rope

### Particle-Particle Contact / Self-Collision

This matters for:

- Newton-native self-collision
- cross-object filtering experiments
- comparisons against PhysTwin contact behavior

### Native Robot / Deformable Example Caveat

The upstream examples most relevant to this project do not all make the same
claim.

- `robot_panda_hydro` is the closest robot-side manipulation template
- `cloth_franka` and `softbody_franka` are most useful for split scheduling and
  coupling order

That distinction matters because the bridge should not over-claim a staged
robot/deformable example as if it already proved strict local direct-finger
robot-table-deformable truth. See `docs/newton/robot_example_patterns.md`.

### MPM Contact / Coupling

This matters for:

- one-way sand demos
- two-way coupling investigations

## Current Project Questions

When the project asks about Newton runtime behavior, it usually means one of:

- is the issue in geometry/contact generation?
- is the issue in force resolution?
- is the issue in solver choice/path?
- is the issue in viewer/rendering rather than physics?

## Code Entry Points Worth Reading

- `Newton/newton/newton/solvers.py`
- `Newton/newton/newton/viewer.py`
- `Newton/newton/newton/_src/geometry/`
- `Newton/newton/newton/_src/solvers/semi_implicit/`

## Bridge-Side Readers Of Newton

- `Newton/phystwin_bridge/tools/core/newton_import_ir.py`
- `Newton/phystwin_bridge/demos/semiimplicit_bridge_kernels.py`
- `Newton/phystwin_bridge/demos/self_contact_bridge_kernels.py`
- `Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py`
