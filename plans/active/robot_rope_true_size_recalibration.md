# Plan: robot_rope_true_size_recalibration

## Goal

Recover a meeting-defensible tabletop finger-push demo after the rope physical
radius was changed toward a truer size.

## Constraints

- no edits under `Newton/newton/`
- no hidden helper or fake contact proof
- keep actual finger-box contact as the proof surface
- use bounded sweeps, not blind brute force

## Milestones

1. Create the task scaffold and diagnosis board.
2. Compare accepted c12 against true-size candidates and isolate the coupled regression.
3. Run a bounded physical-radius sweep to understand the shape/contact tradeoff.
4. Recalibrate laydown, settle, contact height, and XY waypoints together.
5. Promote only if the true-size rope hero is again visually defensible.

## Validation

- strict validator pass
- `diagnose_robot_rope_remote_interaction.py` supports the contact story
- full-video review of hero/debug/validation
- docs/results_meta updated only after a real pass

## Notes

- c12 remains authoritative unless a new true-size candidate clearly beats it.
