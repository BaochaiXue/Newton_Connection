> status: active
> canonical_replacement: none
> owner_surface: `fast_foundation_stereo`
> last_reviewed: `2026-04-01`
> review_interval: `21d`
> update_rule: `Update when evaluation scope, decision criteria, or adoption recommendation changes.`
> notes: Active canonical task page for the Fast-FoundationStereo decision.

# Task: Fast-FoundationStereo Evaluation

## Question

Can Fast-FoundationStereo replace or improve the current RealSense depth path on
the cases this project actually uses?

## Why It Matters

If it works, it may be a relatively cheap improvement to the reconstruction side.

## Evaluation Focus

- does it run on the available data/modalities?
- does it produce usable disparity/depth for the pipeline?
- is its coordinate convention easy to integrate?
- is the gain worth the engineering cost?

## Evidence We Need

- at least one successful case
- at least one failure mode if it does not work
- comparison against current depth path

## Success Criteria

- conclude one of:
  - worth adopting
  - worth further study
  - not worth project time right now
