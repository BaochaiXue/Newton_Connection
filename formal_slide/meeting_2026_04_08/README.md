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
- `robot_visible_tool_three_views/`
  - slide-ready `mp4 + gif` export of the promoted visible-tool robot baseline
- `robot_direct_finger_three_views/`
  - slide-ready `mp4 + gif` export of the promoted direct-finger conservative robot baseline

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

Additional slide-ready three-view exports:

- `robot_visible_tool_three_views/`
  - `hero_presentation.mp4/.gif`
  - `hero_debug.mp4/.gif`
  - `validation_camera.mp4/.gif`
- `robot_direct_finger_three_views/`
  - `hero_presentation.mp4/.gif`
  - `hero_debug.mp4/.gif`
  - `validation_camera.mp4/.gif`

## Common Build Command

```bash
python formal_slide/meeting_2026_04_08/build_meeting_20260408.py
```
