> status: active
> canonical_replacement: none
> owner_surface: `slide_deck_overhaul`
> last_reviewed: `2026-04-01`
> review_interval: `21d`
> update_rule: `Update when the deck story structure, review artifacts, or slide-build policy changes.`
> notes: Active canonical task page for slide/transcript structure and review-deliverable upkeep.

# Task: Slide Deck Overhaul

## Question

How do we convert current bridge results into a meeting-ready slide deck where
each slide has one claim and can be understood in 15-20 seconds?

## Why It Matters

Poor slide structure hides real progress. The advisor feedback was explicit:

- every slide needs a clear point
- long text walls should become diagrams or visuals
- code slides need short analysis on-slide and fuller explanation in transcript

## Code Entry Points

- `formal_slide/meeting_2026_03_25/build_meeting_20260325.py`
- `formal_slide/meeting_2026_04_01/build_meeting_20260401.py`

## Inputs

- meeting transcript
- validated experiment artifacts
- selected GIF/MP4 outputs
- code excerpts with short highlighted snippets

## Success Criteria

- each slide supports one hypothesis or one conclusion
- visuals dominate over text where possible
- transcript is explanatory, not redundant filler
- deck order matches the intended story
- the shipped full-deck PPTX stays below `100 MB` without manual post-build cleanup

## Open Questions

- Which results should remain in the main deck vs appendix?
- Which code pages are strong enough to keep?
