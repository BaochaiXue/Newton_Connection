> status: active
> canonical_replacement: none
> owner_surface: `meeting_20260408_recall_part`
> last_reviewed: `2026-04-01`
> review_interval: `14d`
> update_rule: `Update when milestones or validation steps for the 2026-04-08 recall bootstrap change.`
> notes: Active plan for creating the initial 2026-04-08 recall-only meeting bundle.

# Plan: meeting_20260408_recall_part

## Goal

Bootstrap a reusable `2026-04-08` meeting bundle with opening + recall slides
and a matching transcript.

## Constraints

- no edits under `Newton/newton/`
- reuse existing validated recall media where possible
- keep the first pass intentionally narrow

## Milestones

1. create the task chain and the new meeting bundle directory
2. build a lightweight `2026-04-08` builder by reusing the `2026-04-01` recall infrastructure
3. write the initial opening + recall slide content and transcript
4. generate the first recall-only PPTX and transcript PDF

## Validation

- `python formal_slide/meeting_2026_04_08/build_meeting_20260408.py`

## Notes

- this is the first-pass recall scaffold, not the final full meeting deck
