> status: active
> canonical_replacement: none
> owner_surface: `meeting_20260408_recall_part`
> last_reviewed: `2026-04-08`
> review_interval: `14d`
> update_rule: `Update when the 2026-04-08 meeting scope, source slides, or generated artifacts change.`
> notes: Meeting-specific task for the 2026-04-08 bundle; started as recall-only, then expanded with later weekly sections.

# Task: Meeting 2026-04-08 Recall Part

## Question

What is the minimum defensible `2026-04-08` meeting bundle, and can we keep it
structured so recall remains stable while new weekly result sections are added
without overclaiming?

## Why It Matters

The next formal meeting needs a clean starting point, but the deck also has to
carry the current weekly result sections once their claim boundaries are ready.

## Current Status

- Active bootstrap for the `2026-04-08` meeting bundle
- Current included sections:
  - opening page
  - recall block
  - stable self-collision update
  - conservative robot section
- current presentation policy for this bundle:
  - one claim per slide
  - readable within `15-20 s`
  - English on-slide, Chinese in transcript
  - detailed mechanism reasoning pushed into transcript
- current generated bundle state:
  - `13` slides
  - rebuilt against the current promoted robot authorities on `2026-04-08`

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
- deck-local media derived from current promoted robot authorities:
  - `formal_slide/meeting_2026_04_08/gif/robot_visible_rigid_tool_baseline_hero_validation_deck.gif`
  - `formal_slide/meeting_2026_04_08/gif/robot_rope_franka_semiimplicit_oneway_hero_validation_deck.gif`
- slide-ready three-view robot exports:
  - `formal_slide/meeting_2026_04_08/robot_visible_tool_three_views/`
  - `formal_slide/meeting_2026_04_08/robot_direct_finger_three_views/`

## Success Criteria

- a meeting-local builder exists for `2026-04-08`
- the default build generates the current meeting PPTX and transcript
- the recall part is in English on-slide and Chinese in transcript
- later weekly sections can be appended without rebuilding the harness from scratch
- the current deck remains understandable on first pass, not only after reading the transcript
- the robot section stays conservative:
  - direct-finger slide as the main deck robot visual
  - visible-tool slide demoted to backup-only explanation

## Open Questions

- how much additional weekly material beyond self-collision + robot should still be appended before Wednesday?
- should Slide 10 or Slide 11 be the default stop point for the robot discussion?

## Related Pages

- [slide_deck_overhaul.md](./slide_deck_overhaul.md)
