# Contract: slide_deck_overhaul / source-of-truth deck maintenance

## Goal

Keep the active meeting deck workflow source-grounded, size-bounded, and
reviewable without turning the task into resend churn.

## Scope Boundary

- In scope:
  - source-of-truth deck/transcript updates
  - paired review-PDF workflow
  - PPTX size gate enforcement
  - keeping claim density and media usage inside the current deck policy
- Out of scope:
  - rerunning experiments only to decorate slides
  - reviving archived robot demo claims
  - ad hoc binary PPTX patching

## Required Inputs

- `docs/bridge/tasks/slide_deck_overhaul.md`
- `tasks/status/slide_deck_overhaul.md`
- active meeting bundle builders and transcripts under `formal_slide/`
- validated media / result bundles

## Required Outputs

- updated source build inputs when the story changes
- rebuilt PPTX/transcript/review PDF when applicable
- current status page aligned to the latest source-of-truth bundle

## Hard-Fail Conditions

- the deck grows past the `100 MB` PPTX gate
- slide claims drift away from validated evidence
- review PDF no longer matches the source PPTX/transcript pair

## Acceptance Criteria

- source builder remains the only deck truth surface
- the current deck stays readable at one-claim-per-slide density
- paired review PDF stays aligned to the current source bundle
- task status reflects the current workflow without resend-log drift

## Evaluator Evidence Required

- validator command(s):
  - `python formal_slide/meeting_2026_04_01/build_meeting_20260401.py --max-pptx-mb 100`
  - `python scripts/build_slide_transcript_review_pdf.py ...`
- artifact paths:
  - `formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx`
  - `formal_slide/meeting_2026_04_01/bridge_meeting_20260401_review.pdf`
- skeptical review required: yes

## Next Command After Acceptance

```bash
python formal_slide/meeting_2026_04_01/build_meeting_20260401.py --max-pptx-mb 100
```
