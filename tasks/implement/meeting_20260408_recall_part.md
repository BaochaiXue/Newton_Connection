> status: active
> canonical_replacement: none
> owner_surface: `meeting_20260408_recall_part`
> last_reviewed: `2026-04-01`
> review_interval: `14d`
> update_rule: `Update when the execution steps or canonical commands for the 2026-04-08 recall bootstrap change.`
> notes: Runbook for creating the first 2026-04-08 recall-only meeting bundle.

# Implement: meeting_20260408_recall_part

## Preconditions

- read `formal_slide/meeting_2026_04_01/README.md`
- inspect the `2026-04-01` recall slide source
- confirm the new bundle is recall-only for now

## Canonical Commands

```bash
python formal_slide/meeting_2026_04_08/build_meeting_20260408.py
```

## Step Sequence

1. create the `formal_slide/meeting_2026_04_08/` bundle
2. reuse the `2026-04-01` recall helper pipeline instead of cloning a giant builder
3. write the initial opening + recall slide list
4. generate transcript markdown and transcript PDF from the same slide source
5. validate that the bundle builds end to end

## Validation

- the PPTX is generated
- the transcript markdown is generated
- the transcript PDF is generated

## Output Paths

- `formal_slide/meeting_2026_04_08/`
