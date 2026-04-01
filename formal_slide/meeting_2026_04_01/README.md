# Meeting 20260401 Bundle

This folder is the local bundle for the `2026-04-01` formal slide deck.

## Structure

- `build_meeting_20260401.py`
  - Folder-local Python entry point for generating the slides and transcript.
- `bridge_meeting_20260401.pptx`
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

## Common Build Commands

- Full deck + transcript:
  - `python formal_slide/meeting_2026_04_01/build_meeting_20260401.py`
- Performance-only slice (`slides 8-12`) for external review:
  - `python formal_slide/meeting_2026_04_01/build_meeting_20260401.py --out-dir tmp_vis/performance_analysis_20260401 --out-pptx tmp_vis/performance_analysis_20260401/bridge_meeting_20260401_performance_only_slides_8_12.pptx --slide-range 8-12`
