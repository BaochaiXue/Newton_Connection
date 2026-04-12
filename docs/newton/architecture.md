# Newton Architecture For This Project

## Purpose

Give a stable mental model of Newton without trying to re-document the entire
upstream simulator.

## Main Layers

### Public/User-Facing Layer

Examples:

- `newton.Model`
- `newton.ModelBuilder`
- `newton.solvers.*`
- `newton.viewer.*`

This is the layer most bridge demos use directly.

### Internal Runtime Layer

Examples:

- collision pipeline
- geometry queries
- semi-implicit kernels
- MPM solver internals
- viewer kernels / rendering utils

This is the layer we often read to understand behavior, but do not modify in
this workspace.

### Example Layer

Examples under:

- `Newton/newton/newton/examples/`

Project reading aid:

- `docs/newton/robot_example_patterns.md`

These are useful as reference patterns for supported native workflows.

## Newton Concepts Most Relevant To This Project

- `body`
  - stores rigid-body dynamical state such as mass/inertia and motion state
- `shape`
  - stores collision geometry attached to bodies or the world
- `solver`
  - advances model state in time
- `contacts`
  - generated contact data consumed during a solver step
- `viewer`
  - runtime visualization / offline frame capture support

## Important Boundary

The bridge project should distinguish carefully between:

- what Newton natively supports
- what the bridge reconstructs or overrides
- what is only used for analysis/diagnostics

That distinction is especially important when discussing contact, self-collision,
and performance.
