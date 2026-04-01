> status: active
> canonical_replacement: none
> owner_surface: `meeting_20260408_recall_part`
> last_reviewed: `2026-04-01`
> review_interval: `14d`
> update_rule: `Update when the 2026-04-08 meeting recall scope, source slides, or generated artifacts change.`
> notes: Meeting-specific task for bootstrapping the 2026-04-08 recall-only slide/transcript bundle.

# Task: Meeting 2026-04-08 Recall Part

## Question

What is the minimum defensible recall block for the `2026-04-08` meeting, and
can we package it as a meeting-local slide/transcript bundle that is ready for
later extension?

## Why It Matters

The next formal meeting needs a clean starting point. A recall-only draft keeps
the baseline story stable before the new weekly results are inserted.

## Current Status

- Active bootstrap for the `2026-04-08` meeting bundle
- Scope is intentionally narrow:
  - opening page
  - recall block only
  - no new performance / penetration / self-collision / robot sections yet

## Code Entry Points

- `formal_slide/meeting_2026_04_08/build_meeting_20260408.py`
- `formal_slide/meeting_2026_04_08/transcript.md`
- `formal_slide/meeting_2026_04_01/build_meeting_20260401.py`

## Canonical Commands

```bash
python formal_slide/meeting_2026_04_08/build_meeting_20260408.py
```

## Required Artifacts

- `formal_slide/meeting_2026_04_08/bridge_meeting_20260408_recall_initial.pptx`
- `formal_slide/meeting_2026_04_08/transcript.md`
- `formal_slide/meeting_2026_04_08/transcript.pdf`

## Success Criteria

- a meeting-local builder exists for `2026-04-08`
- the default build generates a recall-only initial PPTX and transcript
- the recall part is in English on-slide and Chinese in transcript
- the bundle is structured so later sections can be appended without rebuilding the harness from scratch

## Open Questions

- how much of the `2026-04-01` recall block should survive unchanged?
- which new weekly results will be inserted after recall once the rest of the meeting story is ready?

## Related Pages

- [slide_deck_overhaul.md](./slide_deck_overhaul.md)
