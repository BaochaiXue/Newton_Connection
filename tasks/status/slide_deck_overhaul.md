> status: active
> canonical_replacement: none
> owner_surface: `slide_deck_overhaul`
> last_reviewed: `2026-04-01`
> review_interval: `14d`
> update_rule: `Update when the active 0401 deck story, shipped bundle workflow, or paired review-PDF process changes materially.`
> notes: Live status page for the deck-overhaul task. Keep this page current-state-first; do not accumulate a resend/rebuild changelog that produces multiple conflicting “current” claims.

# Status: slide_deck_overhaul

## Current State

Tracked as an active task with a stable `0401` bundle workflow:

- `formal_slide/meeting_2026_04_01/build_meeting_20260401.py` is the canonical
  deck/transcript builder
- the builder enforces a PPTX size gate
- `scripts/build_slide_transcript_review_pdf.py` generates the paired
  slide-plus-transcript review PDF
- release sends are expected to use the latest regenerated review PDF, not a
  stale export
- current active style constraint for new decks:
  - one claim per slide
  - `15-20 s` reading density
  - English slides + Chinese transcript
  - detailed analysis moved off-slide

## Last Completed Step

Stabilized the April 1 release path around the current source of truth:

- rebuild the latest PPTX/transcript from source
- regenerate the paired review PDF from that same source
- verify slide-page / transcript-section count alignment
- keep the review build manifest under `tmp_vis/review_pdf_20260401/`

Historical resend note:

- this task saw several same-day refreshes while the `0401` deck was still
  changing
- those events are routine release churn, not separate competing current
  states

## Next Step

If the `0401` deck changes again:

- keep the wording density under control
- rebuild both the PPTX and the paired review PDF from source
- preserve the PPTX size gate
- avoid turning this page into a resend ledger

If the `0408` deck continues to evolve:

- keep the Wednesday deck near a `30 min` story length
- preserve the short-slide policy
- avoid adding long code dumps unless they satisfy the code-slide constraints

## Blocking Issues

- None recorded for the current deck workflow

## Artifact Paths

- `formal_slide/meeting_2026_03_25/`
- `formal_slide/meeting_2026_04_01/`
- `formal_slide/meeting_2026_04_01/bridge_meeting_20260401_review.pdf`
- `formal_slide/meeting_2026_04_01/performance_section_audit.md`
- `formal_slide/meeting_2026_04_01/code_render_style_audit.md`
- `tmp_vis/performance_analysis_20260401/`
- `tmp_vis/redeck_20260401/`
- `tmp_vis/review_pdf_20260401/`
