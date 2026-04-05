> status: active
> canonical_replacement: none
> owner_surface: `robot_rope_true_size_recalibration`
> last_reviewed: `2026-04-05`
> review_interval: `14d`
> update_rule: `Update when the true-size recovery hypothesis, bounded sweep plan, or honest promotion rule changes.`
> notes: Active repair task for the true-size tabletop rope regression after shrinking the physical rope radius.

# Task: Robot Rope True-Size Recalibration

## Question

After switching the tabletop rope to a smaller truer physical radius, what is
the smallest honest recalibration that restores a readable finger-push demo
without falling back to fake contact stories?

## Why It Matters

The accepted `c12` tabletop baseline is still the committed authority, but the
current repo defaults have drifted toward a thinner physical rope. That means
the project needs a separate recovery task before it can claim a truthful
true-size direct-finger baseline.

## Scope

- keep the robot native to Newton
- keep the table native to Newton
- keep the rope on the PhysTwin -> Newton bridge
- use bounded physical/layout/controller sweeps
- keep actual finger contact as the proof surface
- do not change `Newton/newton/`

## Open Question

Which coupled term is dominant in the current regression:

- rope laydown
- rope contact height
- robot base / waypoint XY reach
- controller timing after the thinner physical radius change

## Success Surface

- one truthful candidate bundle with:
  - readable hero/debug/validation video
  - actual finger contact still visible and physically consistent
  - rope render thickness aligned with physical rope thickness
- only then consider any authority update

## Related Pages

- [robot_rope_franka_tabletop_push_hero.md](./robot_rope_franka_tabletop_push_hero.md)
- [remote_interaction_root_cause.md](./remote_interaction_root_cause.md)
- [robot_rope_franka_physical_blocking.md](./robot_rope_franka_physical_blocking.md)
