# Plan: robot_visible_rigid_tool_baseline

## Goal

Create a conservative, visually honest rigid-tool intermediary baseline for the
tabletop rope demo.

## Milestones

1. Create the new task chain and diagnosis board.
2. Choose the visible rigid tool geometry and honest attachment strategy.
3. Implement the tool as both a physical contactor and a matching visible
   render object.
4. Re-tune scene/layout/camera so the visible tool clearly touches and moves the
   rope.
5. Run full validation and promote only after a fail-closed video pass.

## Validation

- standard hero video validator
- tool-truth diagnostics
- full-video multimodal review
- truthful manual YES/NO review

## Notes

- This task must not silently overwrite the older tabletop baseline or the
  blocked physical-blocking follow-on task.
