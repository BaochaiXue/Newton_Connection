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
```

## Step Sequence

1. map each current slide to one hypothesis, result, or appendix role
2. identify story drift between build script, transcript, and validated artifacts
3. update slide/transcript outputs only after the story boundary is explicit
4. regenerate deck-sized GIF assets before shipping the PPTX
5. fail closed if the built PPTX exceeds `100 MB`

## Validation

- the resulting deck uses validated evidence
- transcript wording matches slide structure
- the default deck build passes the `100 MB` size gate

## Output Paths

- `formal_slide/meeting_2026_03_25/`
- `formal_slide/meeting_2026_04_01/`
