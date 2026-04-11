> status: active
> canonical_replacement: none
> owner_surface: `slide_deck_overhaul`
> last_reviewed: `2026-04-11`
> review_interval: `21d`
> update_rule: `Update when the canonical deck-build commands, size gates, or review-artifact workflow changes.`
> notes: Active execution runbook for meeting-slide maintenance. Keep commands readable and size gates explicit.

# Implement: slide_deck_overhaul

## Preconditions

- read the relevant meeting bundle builder and transcript
- confirm which result bundles are currently authoritative

## Canonical Commands

```bash
sed -n '1,260p' formal_slide/meeting_2026_04_01/build_meeting_20260401.py
sed -n '1,260p' formal_slide/meeting_2026_04_01/transcript.md
python formal_slide/meeting_2026_04_01/build_meeting_20260401.py --max-pptx-mb 100
du -h formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx
python scripts/build_slide_transcript_review_pdf.py \
  --pptx formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx \
  --transcript-md formal_slide/meeting_2026_04_01/transcript.md \
  --out-pdf formal_slide/meeting_2026_04_01/bridge_meeting_20260401_review.pdf \
  --work-dir tmp_vis/review_pdf_20260401 \
  --deck-title "PhysTwin -> Newton Bridge 2026-04-01 Review"
pdfinfo formal_slide/meeting_2026_04_01/bridge_meeting_20260401_review.pdf
```

## Step Sequence

1. map each current slide to one hypothesis, result, or appendix role
2. identify story drift between build script, transcript, and validated artifacts
3. update slide/transcript outputs only after the story boundary is explicit
4. regenerate deck-sized GIF assets before shipping the PPTX
5. fail closed if the built PPTX exceeds `100 MB`
6. when a review artifact is requested, render one slide plus the matching transcript onto each review page
7. validate the review PDF page count before release

## Validation

- the resulting deck uses validated evidence
- transcript wording matches slide structure
- the default deck build passes the `100 MB` size gate
- the review PDF page count matches the slide / transcript count

## Output Paths

- `formal_slide/meeting_2026_03_25/`
- `formal_slide/meeting_2026_04_01/`
