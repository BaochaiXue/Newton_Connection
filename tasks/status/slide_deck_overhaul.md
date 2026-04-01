# Status: slide_deck_overhaul

## Current State

Tracked as an active task with a backfilled authoritative chain and an active
PPTX size-budget gate on the 2026-04-01 deck builder.

## Last Completed Step

Redesigned the 2026-04-01 meeting deck to match the current review standard:

- replaced bridge-local wrapper citations on the performance source-proof page
  with upstream Newton core + PhysTwin source
- removed performance data-chart slides in favor of short conclusion slides
- removed the bunny mechanism code-citation slide so that bunny evidence is now
  carried by videos instead of our own diagnostic implementation details
- replaced the static self-collision campaign/image block with:
  - one hypothesis page
  - one upstream PhysTwin source-proof page
  - one controlled cloth+box decision video grid
  - one hero/parity progress video page
- kept the VSCode-like synthetic code renderer as the reusable code-panel path
- regenerated the full deck, transcript, and a fresh review build under
  `tmp_vis/redeck_20260401/`

## Next Step

Do a final pass on wording density and GIF sizing if another meeting-review
iteration changes the claim boundaries.

## Blocking Issues

- None recorded for the performance-section pass

## Artifact Paths

- `formal_slide/meeting_2026_03_25/`
- `formal_slide/meeting_2026_04_01/`
- `formal_slide/meeting_2026_04_01/performance_section_audit.md`
- `formal_slide/meeting_2026_04_01/code_render_style_audit.md`
- `tmp_vis/performance_analysis_20260401/`
- `tmp_vis/redeck_20260401/`
