# Meeting 20260408 Recall Bundle

This folder is the local bundle for the initial `2026-04-08` recall-only
meeting draft.

## Structure

- `build_meeting_20260408.py`
  - folder-local Python entry point for generating the recall-only slides and transcript
- `bridge_meeting_20260408_recall_initial.pptx`
  - latest generated recall-only PPTX
- `transcript.md`
  - latest generated recall transcript source
- `transcript.pdf`
  - latest rendered transcript PDF
- `gif/`
  - deck-sized GIF copies used by this meeting bundle

## Current Scope

This is intentionally only the opening + recall block for the `2026-04-08`
meeting.

It is the initial scaffold, not the final full meeting deck.

## Dependency Note

To avoid cloning another giant builder, this bundle currently reuses:

- the shared PPTX template from `formal_slide/meeting_2026_04_01/templates/`
- the established recall media sources already used in the `2026-04-01` bundle

The generated GIF copies still live locally in this folder under `gif/`.

## Common Build Command

```bash
python formal_slide/meeting_2026_04_08/build_meeting_20260408.py
```
