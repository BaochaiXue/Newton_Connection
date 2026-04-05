# Meeting 20260408 Bundle

This folder is the local bundle for the current `2026-04-08` meeting draft.

## Structure

- `build_meeting_20260408.py`
  - folder-local Python entry point for generating the recall + self-collision + robot slides and transcript
- `bridge_meeting_20260408_recall_initial.pptx`
  - latest generated PPTX
- `transcript.md`
  - latest generated transcript source
- `transcript.pdf`
  - latest rendered transcript PDF
- `gif/`
  - deck-sized GIF copies used by this meeting bundle
- `images/`
  - generated static analysis boards used by this meeting bundle

## Current Scope

This bundle currently includes:

- opening
- recall block
- stable self-collision / ground-contact mechanism update
- conservative robot SemiImplicit section:
  - visible-tool meeting visual
  - direct-finger promoted authority

## Dependency Note

To avoid cloning another giant builder, this bundle currently reuses:

- the shared PPTX template from `formal_slide/meeting_2026_04_01/templates/`
- the established recall media sources already used in the `2026-04-01` bundle
- the stable self-collision results under `Newton/phystwin_bridge/results/`
- the promoted robot result bundles under:
  - `results_meta/tasks/robot_visible_rigid_tool_baseline.json`
  - `results_meta/tasks/robot_rope_franka_semiimplicit_oneway.json`

The generated GIF copies still live locally in this folder under `gif/`, including:

- `robot_visible_rigid_tool_baseline_hero_validation_deck.gif`
- `robot_rope_franka_semiimplicit_oneway_hero_validation_deck.gif`

## Common Build Command

```bash
python formal_slide/meeting_2026_04_08/build_meeting_20260408.py
```
