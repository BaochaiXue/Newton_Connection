# Implement Runbook: Bunny Force Visualization Full-Process Closure

## Canonical Loop

1. Run one baseline-only case.
2. Render phenomenon.
3. Build the full-process force video from the same phenomenon render.
4. Validate.
5. Inspect sampled frames/contact sheets.
6. Iterate until baseline passes.
7. Only then propagate to the other three cases.

## Preferred Command Pattern

Use `scripts/run_bunny_force_case.py` to generate:

- scene NPZ
- phenomenon MP4
- summary JSON
- force render bundle

Then use `scripts/render_bunny_force_artifacts.py` to finalize:

- force snapshot PNG/MP4
- full-process force mechanism MP4

Finally run:

- `scripts/validate_bunny_force_visualization.py`

## Notes

- Keep the phenomenon render as the global truth.
- Use projected 2D overlays for force glyphs when possible.
- Avoid second-viewer-only force rendering as the canonical path.
