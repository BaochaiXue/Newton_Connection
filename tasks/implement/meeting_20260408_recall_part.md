> status: active
> canonical_replacement: none
> owner_surface: `meeting_20260408_recall_part`
> last_reviewed: `2026-04-08`
> review_interval: `14d`
> update_rule: `Update when the execution steps or canonical commands for the 2026-04-08 recall bootstrap change.`
> notes: Runbook for building the current 2026-04-08 meeting bundle after recall, performance, self-collision, and robot sections were merged into one deck.

# Implement: meeting_20260408_recall_part

## Preconditions

- read `formal_slide/meeting_2026_04_01/README.md`
- inspect the `2026-04-01` shared slide builder because the 2026-04-08 bundle reuses its helper surface
- confirm the current promoted robot authorities still resolve locally

## Canonical Commands

```bash
python formal_slide/meeting_2026_04_08/build_meeting_20260408.py
```

## Step Sequence

1. create the `formal_slide/meeting_2026_04_08/` bundle
2. reuse the `2026-04-01` shared helper pipeline instead of cloning a giant builder
3. keep the current section order explicit:
   - recall
   - rope performance profiling
   - stable self-collision
   - conservative robot baseline
4. generate transcript markdown and transcript PDF from the same slide source
5. validate that the bundle builds end to end

## Validation

- the PPTX is generated
- the transcript markdown is generated
- the transcript PDF is generated

## Output Paths

- `formal_slide/meeting_2026_04_08/`
