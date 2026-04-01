# Task Spec: Bunny Force Visualization Full Process

## Goal

Upgrade the bunny penetration visualization package from a short trigger-centric
diagnostic into a meeting-ready full-process package that preserves both:

- the global cloth process
- the local force mechanism

## Scope

- `Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py`
- `scripts/run_bunny_force_case.py`
- `scripts/render_bunny_force_artifacts.py`
- `scripts/validate_bunny_force_visualization.py`
- `scripts/run_bunny_force_visualization_matrix.sh`
- `results/bunny_force_visualization/`

## Constraints

- `Newton/newton/` is read-only
- do not claim success from file existence alone
- bunny baseline must pass before the other three cases are rerun

## Done When

1. `bunny_baseline` has:
   - a phenomenon video `>= 3.0s` and target `3.5s+`
   - a force mechanism video `>= 4.0s` and target `4.5s+`
   - force video preserves full cloth in the global panel
   - force video has a readable local patch
   - stricter QA passes
2. the same pipeline is propagated to:
   - `box_control`
   - `bunny_low_inertia`
   - `bunny_larger_scale`
3. `results/bunny_force_visualization/INDEX.md` and latest pointers describe the
   current valid run accurately
