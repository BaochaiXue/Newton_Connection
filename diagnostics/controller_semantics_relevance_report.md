# Controller Semantics Relevance Report

- current direct-finger tabletop path remains `joint_trajectory` and effectively controller-driven rather than fully physically blocked.
- that limitation matters for the stronger physical-blocking task, but it is secondary for explaining the sphere question.

## Interpretation

For the sphere-inflation question, controller semantics are not the primary error term. The main issue is geometric truth: where the command reference is, where the real finger boxes are, and whether the actual finger path reaches the settled rope laydown.
Sphere inflation cannot solve the blocked-physics limitation; at best it papers over geometry miss in a controller-driven rollout.
