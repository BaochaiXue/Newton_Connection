# Meeting 20260325 Bundle

This folder is the local bundle for the `2026-03-25` formal slide deck.

## Structure

- `build_meeting_20260325.py`
  - Folder-local Python entry point for generating the slides and transcript.
- `bridge_meeting_20260325.pptx`
  - Latest generated slide deck.
- `transcript.md`
  - Latest generated transcript source.
- `transcript.pdf`
  - Latest rendered transcript PDF.
- `templates/`
  - Local PPTX template directory.
  - Current generator depends only on `My Adjust.pptx`.
- `slides_assets/gif/`
  - Direct GIF assets used by the meeting deck.
- `gif/`
  - Generated GIF assets used by the meeting deck.
- `images/`
  - Generated PNG/code/diagram assets used by the meeting deck.
- `exp_*/`
  - Local experiment folders already copied into this meeting bundle.

## Goal

The intent is that the meeting-specific generator code and its direct media/template
dependencies live inside this meeting folder instead of being spread across `~/下载`
and the repo root.
