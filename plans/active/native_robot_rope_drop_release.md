# Plan: Native Robot Rope Drop/Release Sanity Baseline

## Goal

Establish a stage-0 baseline for the robot + rope workstream: native Franka,
semi-implicit rope dynamics, explicit release, real ground contact, and a
1:1-time presentation render.

## Constraints

- Do not touch `Newton/newton/`
- Keep this separate from the previous lift-release presentation baseline
- Treat drag as an experimental variable, not an assumption

## Milestones

1. Create the dedicated task/result scaffolding for the new milestone slug
2. Record the baseline evidence contract for release, impact, and gravity-like free fall
3. Promote the first credible accepted run into the new bundle

## Validation

- physics validation artifacts capture drag on/off A/B comparisons
- video validation artifacts reject black, unreadable, or wrong-camera outputs
- the promoted run is indexed in the new bundle, not mixed into the older lift-release bundle

## Notes

- The old `results/robot_deformable_demo/` bundle remains the historical
  lift-release evidence chain.
- This milestone should stay narrow until the drop/release baseline is visibly
  credible.
