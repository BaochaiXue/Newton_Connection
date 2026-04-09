> status: historical
> canonical_replacement: `../../docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`
> owner_surface: `robot_rope_franka_native_v2`
> last_reviewed: `2026-04-09`
> notes: Historical exploratory plan archived out of `plans/active/`.

# Plan: robot_rope_franka_native_v2

## Goal

Replace the old stronger-task monolith with a native-style v2 demo path that
uses Cartesian waypoints + IK + joint targets and keeps direct-finger table and
rope interaction truthful.

## Milestones

1. Create a fresh v2 task chain and preserve old authority routing.
2. Implement a small Example-style v2 demo:
   - scene builder
   - native-style controller
   - simulation loop
   - history/render/summary
3. Add a canonical wrapper with same-history hero/debug/validation.
4. Run three v2 candidates:
   - safe-start baseline
   - shallower-push baseline
   - clearer-rope-motion baseline
5. Validate numerically and visually; only then update status docs.

## Validation

- `py_compile` on the new demo and wrapper-adjacent Python
- artifact validator pass
- physical-blocking validator pass
- skeptical early-frame / full-video review on hero and validation

## Notes

- Keep solver route bridge-side for round one
- Do not touch `Newton/newton/`
- Do not promote stronger authority in this round
