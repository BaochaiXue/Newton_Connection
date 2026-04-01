> status: active
> canonical_replacement: none
> owner_surface: `meeting_20260408_recall_part`
> last_reviewed: `2026-04-01`
> review_interval: `14d`
> update_rule: `Update when scope, outputs, or constraints for the 2026-04-08 recall bootstrap change.`
> notes: Bounded execution spec for the 2026-04-08 recall-only meeting bundle.

# Spec: meeting_20260408_recall_part

## Goal

Create the first repo-native `2026-04-08` meeting bundle with an opening slide,
recall-only content, and a matching transcript.

## Non-Goals

- building the full `2026-04-08` meeting deck
- rerunning experiments only to fill this initial recall draft
- modifying `Newton/newton/`

## Inputs

- `formal_slide/meeting_2026_04_01/`
- `formal_slide/meeting_2026_03_25/`
- `docs/bridge/tasks/meeting_20260408_recall_part.md`

## Outputs

- new `formal_slide/meeting_2026_04_08/` bundle
- `build_meeting_20260408.py`
- generated recall-only `pptx + transcript`

## Constraints

- slides in English
- transcript in Chinese with English terminology preserved
- start with recall only; do not pretend the rest of the meeting already exists

## Done When

- the `2026-04-08` bundle builds locally
- the recall deck is readable and reusable as the initial meeting scaffold
