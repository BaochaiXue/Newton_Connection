> status: active
> canonical_replacement: none
> owner_surface: `meeting_20260408_recall_part`
> last_reviewed: `2026-04-05`
> review_interval: `7d`
> update_rule: `Update after each meaningful bootstrap/build milestone for the 2026-04-08 meeting bundle.`
> notes: Live status log for the 2026-04-08 meeting bundle, which started as recall-only and now includes appended weekly sections.

# Status: meeting_20260408_recall_part

## Current State

- Active
- Current meeting bundle now includes:
  - recall block
  - stable self-collision mechanism section
  - conservative robot SemiImplicit section
- current story shape:
  - `12` slides
  - tightened for `~30 min`
  - lower text density with detailed analysis moved to transcript

## Last Completed Step

- Reworked the deck story to be clearer and shorter:
  - explicit agenda / claim-boundary slide
  - compressed recall to two slides
  - kept self-collision to one evidence slide + one conclusion slide
  - kept robot to one scope slide + two result slides + one close slide
- Preserved the existing stable self-collision update
- Kept the robot section sourced from current promoted authorities:
  - `robot_visible_rigid_tool_baseline`
  - `robot_rope_franka_semiimplicit_oneway`
- Added same-rollout hero+validation composite GIF generation for both robot baselines
- Added slide-ready three-view exports for both promoted robot baselines:
  - `formal_slide/meeting_2026_04_08/robot_visible_tool_three_views/`
  - `formal_slide/meeting_2026_04_08/robot_direct_finger_three_views/`
- Fixed and replaced the robot slide media after removing a presentation-render
  collision-geometry leak:
  - `hero_presentation.mp4` / `validation_camera.mp4` for both robot exports
    were re-rendered from saved rollout histories
  - the deck-local robot GIFs were rebuilt from the cleaned videos
- Rebuilt the meeting artifacts:
  - `formal_slide/meeting_2026_04_08/bridge_meeting_20260408_recall_initial.pptx`
  - `formal_slide/meeting_2026_04_08/transcript.md`
  - `formal_slide/meeting_2026_04_08/transcript.pdf`
- New robot media artifacts:
  - `formal_slide/meeting_2026_04_08/gif/robot_visible_rigid_tool_baseline_hero_validation_deck.gif`
  - `formal_slide/meeting_2026_04_08/gif/robot_rope_franka_semiimplicit_oneway_hero_validation_deck.gif`
  - `formal_slide/meeting_2026_04_08/robot_visible_tool_three_views/hero_presentation.mp4`
  - `formal_slide/meeting_2026_04_08/robot_visible_tool_three_views/hero_presentation.gif`
  - `formal_slide/meeting_2026_04_08/robot_visible_tool_three_views/hero_debug.mp4`
  - `formal_slide/meeting_2026_04_08/robot_visible_tool_three_views/hero_debug.gif`
  - `formal_slide/meeting_2026_04_08/robot_visible_tool_three_views/validation_camera.mp4`
  - `formal_slide/meeting_2026_04_08/robot_visible_tool_three_views/validation_camera.gif`
  - `formal_slide/meeting_2026_04_08/robot_direct_finger_three_views/hero_presentation.mp4`
  - `formal_slide/meeting_2026_04_08/robot_direct_finger_three_views/hero_presentation.gif`
  - `formal_slide/meeting_2026_04_08/robot_direct_finger_three_views/hero_debug.mp4`
  - `formal_slide/meeting_2026_04_08/robot_direct_finger_three_views/hero_debug.gif`
  - `formal_slide/meeting_2026_04_08/robot_direct_finger_three_views/validation_camera.mp4`
  - `formal_slide/meeting_2026_04_08/robot_direct_finger_three_views/validation_camera.gif`
- Current draft size/state:
  - `12` slides
  - `25 MB` PPTX
  - bundle-local `gif/` and `images/` assets generated successfully

## Next Step

- Decide whether additional weekly sections beyond self-collision + robot should be appended.
- If the Wednesday narrative is shortened further, keep the visible-tool robot slide as the primary visual and the direct-finger slide as the authority backup.

## Blocking Issues

- none

## Validation

- `python -m py_compile formal_slide/meeting_2026_04_08/build_meeting_20260408.py`
- `python formal_slide/meeting_2026_04_08/build_meeting_20260408.py`
- `scripts/export_robot_slide_views.sh`
- `python scripts/validate_experiment_artifacts.py formal_slide/meeting_2026_04_08/robot_visible_tool_three_views --require-video --require-gif`
- `python scripts/validate_experiment_artifacts.py formal_slide/meeting_2026_04_08/robot_direct_finger_three_views --require-video --require-gif`
- current result:
  - pass
- optional harness check run after task-page/index updates:
  - `python scripts/generate_md_inventory.py`
  - `python scripts/lint_harness_consistency.py`
  - current result: fails on pre-existing unrelated surfaces:
    - rerun after the current markdown-harness maintenance pass regenerates the
      ledgers and clears the old residual failures
