# TODO 2 Audit Report — 2026-04-01

## What Was Already Good

- The TODO 2 section already followed the correct research order:
  comparison -> attribution -> Nsight -> optimization.
- The section was already framed as a rope-case story rather than a robot-case
  story.
- The deck already separated throughput claims from attribution claims, which is
  scientifically important.

## What Was Too Text-Heavy

- Slide 9 still carried parity-check detail on the main slide.
- Slide 10 had a useful source-proof role, but the title, common settings, and
  left/right labels were longer than needed for quick reading.
- Slide 12 carried too many exact split numbers directly on the slide body.
- Slide 13 carried more detail than needed for a 15-second slide read.

## What Was Moved Into The Transcript

- Slide 9 parity-check detail now stays in the transcript rather than the slide
  body.
- Slide 11 keeps benchmark metadata as a note and transcript context, not as
  the visual focus.
- Slide 12 keeps exact Newton / PhysTwin attribution split numbers in the
  transcript.
- Slide 13 keeps exact API percentages and kernel-name detail in the
  transcript.

## What Was Corrected For Consistency

- TODO 2 slide titles were shortened and made more conclusion-oriented.
- Slide 10 was tightened so it stays a source-proof slide instead of becoming a
  second explanation slide.
- `todo_list.md` was aligned with the current rope profiling result:
  - fair rope replay benchmark complete
  - Newton A1 still slower than PhysTwin B0
  - bridge tax explains part of the gap
  - residual gap points to execution structure / graph launch, not collision

## README Status

- `README.md` did not need content changes for this audit because the bundle
  structure remained valid.
