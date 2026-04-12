# Handoff: slide_deck_overhaul

## Current Milestone

Stable source-of-truth maintenance for the active meeting deck workflow.

## What Changed

- the task now has an explicit contract/handoff pair because it is a
  meeting-facing, multi-session workflow
- the execution runbook already wraps the canonical build and review-PDF
  commands

## Current Conclusion

This task is not blocked by story structure right now; it is a governed
maintenance path. Any future deck change should rebuild from source, not
from old exports.

## Exact Next Command

```bash
python formal_slide/meeting_2026_04_01/build_meeting_20260401.py --max-pptx-mb 100
```

## Current Blocker

No blocker recorded for the current workflow.

## Last Failed Acceptance Criterion

The task previously lacked an explicit contract/handoff even though it is a
high-risk meeting-release workflow.

## Key GIF / Artifact Paths

- `formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx`
- `formal_slide/meeting_2026_04_01/bridge_meeting_20260401_review.pdf`
- `tasks/status/slide_deck_overhaul.md`

## What Not To Redo

- do not treat resend history as current state
- do not patch PPTX binaries as the main workflow
- do not widen the deck claim boundary beyond validated evidence

## Missing Evidence

- none for the current workflow baseline

## Context Reset Recommendation

- recommended: yes
- reason:
  - this task survives context resets well if the agent resumes from the task
    page, status page, and source bundle
