# Plan: slide_deck_overhaul

## Goal

Maintain a meeting deck whose order, claims, and transcript stay synchronized.

## Constraints

- use validated artifacts only
- keep appendix spillover separate from main-deck claims
- keep the shipped PPTX below `100 MB`

## Milestones

1. audit current deck structure against the intended meeting story
2. identify which slides belong in the main deck versus appendix
3. update build/transcript assets when the selected story changes
4. keep generated media and the final PPTX inside the deck-size budget

## Validation

- build script and transcript agree on section structure
- each slide can be defended in 15-20 seconds
- the full-deck build stays below `100 MB`

## Notes

- Backfilled during the harness upgrade so the active task set has a full chain.
