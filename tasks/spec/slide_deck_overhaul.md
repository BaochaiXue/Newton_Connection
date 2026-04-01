# Spec: slide_deck_overhaul

## Goal

Turn the meeting deck into a sequence of bounded, one-claim slides with a
matching transcript and defensible evidence selection.

## Non-Goals

- Re-running experiments only to fill visual space
- Turning every appendix artifact into a main-deck slide

## Inputs

- `docs/bridge/tasks/slide_deck_overhaul.md`
- `formal_slide/meeting_2026_03_25/`
- `formal_slide/meeting_2026_04_01/`
- validated result bundles and selected media

## Outputs

- bounded slide-story decisions
- matching build/transcript updates
- task-local status for what remains main-deck versus appendix
- a default full-deck build that stays below `100 MB`

## Constraints

- keep slide claims aligned with validated evidence
- prefer one claim per slide
- keep transcript explanatory rather than duplicative
- keep the shipped PPTX below `100 MB`

## Done When

- the deck order matches the intended story
- each slide has a clear claim boundary
- transcript and slide structure agree
- the default deck build passes the `100 MB` size gate
