> status: active
> canonical_replacement: none
> owner_surface: `meeting_20260408_recall_part`
> last_reviewed: `2026-04-08`
> review_interval: `14d`
> update_rule: `Update when milestones or validation steps for the 2026-04-08 recall bootstrap change.`
> notes: Active plan for maintaining the current 2026-04-08 meeting bundle after recall, performance, self-collision, and robot sections were combined.

# Plan: meeting_20260408_recall_part

## Goal

Maintain a reusable `2026-04-08` meeting bundle with recall, rope performance,
self-collision, and conservative robot sections plus a matching transcript.

## Constraints

- no edits under `Newton/newton/`
- reuse existing validated recall media where possible
- keep the main claims conservative and separable

## Milestones

1. keep the shared `2026-04-01` helper dependency healthy
2. keep section order explicit inside the `2026-04-08` bundle
3. rebuild the meeting-local PPTX and transcript whenever promoted sources or story order change
4. keep the task/status surfaces truthful about current slide count and scope

## Validation

- `python formal_slide/meeting_2026_04_08/build_meeting_20260408.py`

## Notes

- current local deck now includes recall + performance + self-collision + robot
