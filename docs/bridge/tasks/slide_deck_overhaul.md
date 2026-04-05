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
- each slide remains readable within roughly `15-20 s`
- detailed explanation lives in the transcript, not as on-slide text walls
- slides stay English; transcript stays Chinese with English terminology
- full deck is scoped for a `~30 min` talk rather than a dump of every artifact
- visuals dominate over text where possible
- transcript is explanatory, not redundant filler
- deck order matches the intended story
- the shipped full-deck PPTX stays below `100 MB` without manual post-build cleanup

## Current Formatting Policy

- keep slide text minimal:
  - a short title
  - at most a few short bullets or one short note line
- if code appears on slides:
  - Python syntax highlighting
  - monospace font
  - no more than `20` visible lines per excerpt
  - highlight no more than `5` key lines
  - on-slide analysis limited to `1-2` short sentences
- push detailed mechanism explanation into transcript paragraphs

## Open Questions

- Which results should remain in the main deck vs appendix?
- Which code pages are strong enough to keep?
