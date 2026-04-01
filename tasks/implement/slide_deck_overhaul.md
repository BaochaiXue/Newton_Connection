# Implement: slide_deck_overhaul

## Preconditions

- read the relevant meeting bundle builder and transcript
- confirm which result bundles are currently authoritative

## Canonical Commands

```bash
sed -n '1,260p' formal_slide/meeting_2026_04_01/build_meeting_20260401.py
sed -n '1,260p' formal_slide/meeting_2026_04_01/transcript.md
```

## Step Sequence

1. map each current slide to one hypothesis, result, or appendix role
2. identify story drift between build script, transcript, and validated artifacts
3. update slide/transcript outputs only after the story boundary is explicit

## Validation

- the resulting deck uses validated evidence
- transcript wording matches slide structure

## Output Paths

- `formal_slide/meeting_2026_03_25/`
- `formal_slide/meeting_2026_04_01/`
