# Active Plan: Bunny Force Visualization Full Process

## Milestones

1. audit the current baseline and identify the real blockers
2. fix the baseline pipeline so it uses the same object-only OFF semantics as
   the working demo path
3. render and validate one accepted `bunny_baseline` bundle
4. propagate the accepted pipeline to the remaining three cases
5. rebuild the summary board and canonical results pointers

## Validation

- `python -m py_compile ...`
- `python scripts/render_bunny_force_artifacts.py ...`
- `python scripts/validate_bunny_force_visualization.py --run-dir ... --sample-count 12`
- manual frame/contact-sheet inspection

## Current Focus

Fix the split baseline workflow so the force video is full-process, not
trigger-centric, and the trigger summary still matches the object-only OFF path.
