# Scope Note: robot_rope_franka_semiimplicit_oneway

Last updated: 2026-04-04

This task deliberately uses the weaker, safer claim:

- deformable rope interaction must run under `SolverSemiImplicit`
- one-way `robot -> rope` is acceptable
- articulated robot-table physical blocking is out of scope
- full two-way coupling is out of scope
- self-collision parity is out of scope
- direct finger is preferred
- visible rigid tool is fallback only if direct finger cannot stay visually
  honest
