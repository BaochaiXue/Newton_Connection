# Video Acceptance Rubric

This rubric is for the skeptical evaluator layer, not the generator.

The evaluator must fail closed.
Ambiguous evidence is not a pass.

## Required Inputs

Every video acceptance attempt must include:

- the target claim boundary
- the video file
- evenly sampled frames across the entire video
- several consecutive-frame windows
- a contact sheet
- an event sheet
- timestamps and frame indices
- structured written evidence for pass/fail

## Hard-Fail Criteria

Fail immediately if any of the following is true:

1. black, blank, invisible, or decode-corrupt output
2. effectively static output
3. misleading camera motion over frozen or unreadable physics
4. force/contact visualization too faint, too small, off-screen, low-contrast, or occluded
5. missing process visibility
6. physics visibly contradicts the stated claim
7. evidence bundle is incomplete
8. the evaluator cannot defend PASS conservatively

## Evidence Requirements

The skeptical evaluator must cite:

- timestamps
- frame indices
- frame paths
- at least one full-video sheet
- at least one event/process sheet

## Verdict Rules

- `PASS`:
  - no hard fail triggered
  - evidence bundle is complete
  - skeptical reviewer explicitly explains why the claim is visible
- `FAIL`:
  - any hard fail triggered
  - or evidence remains incomplete / ambiguous

## Separation Of Roles

- generator:
  - render the video
  - run automatic QC
  - prepare the review bundle
- evaluator:
  - review the claim against the bundle
  - fail closed when evidence is weak

Automatic QC alone does not count as final acceptance.
