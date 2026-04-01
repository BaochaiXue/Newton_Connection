# Active Plan: Bunny Penetration Force Diagnostic

## Milestones

1. Audit the current baseline outputs and wrapper paths
2. Fix the full-process render/packaging path for `bunny_baseline`
3. Render and validate baseline until it passes strict gates
4. Propagate the accepted pipeline to the other three cases
5. Refresh canonical result pointers and summary board

## Canonical Commands

- baseline run:
  `scripts/run_bunny_force_case.py ... --force-diagnostic --defer-force-artifacts`
- force helper:
  `scripts/render_bunny_force_artifacts.py --bundle ... --force-dump-dir ...`
- QA:
  `scripts/validate_bunny_force_visualization.py --run-dir <case_root>`

## Stop-And-Fix Rule

If any of these fail, do not advance to the matrix:

- phenomenon duration < 3.0s
- force duration < 4.0s
- force video loses full cloth context
- local panel is unreadable
- QA or contact sheet still indicates slideshow/static behavior
