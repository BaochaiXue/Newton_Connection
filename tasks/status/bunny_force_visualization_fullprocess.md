# Status: Bunny Force Visualization Full-Process Closure

## 2026-03-30

- Reopened the bunny visualization task under stricter full-process criteria.
- Confirmed the prior short bundle is no longer acceptable:
  - phenomenon too short
  - force clip too short and too trigger-centric
- Identified two concrete issues:
  - longer full-rollout phenomenon can go blank because the camera auto-fit
    includes later absurd body motion
  - the force helper was not yet closing the stable base-video overlay path as
    the canonical full-process mechanism render
- Current implementation work:
  - store actual phenomenon render camera in `sim_data`
  - route force finalization through the base-video overlay path
  - converge on a passing `bunny_baseline` before re-rendering the other cases

## 2026-03-31

- The stricter full-process package is now closed under:
  - `results/bunny_force_visualization/runs/20260331_031500_fullprocess_force_matrix_manual_v1`
- The canonical package now contains all four required cases:
  - `bunny_baseline`
  - `box_control`
  - `bunny_low_inertia`
  - `bunny_larger_scale`
- Every case now has:
  - full-process phenomenon video
  - full-process force mechanism video
  - QA contact sheets
  - QA verdict
  - case README
- The stable final rendering path is:
  - phenomenon render as the global truth
  - base-video force composition with projected 2D glyphs and zoom panel
- The validator now uses geometry-aware cloth visibility for phenomenon clips,
  which removed the previous false-negative on landed cloth visibility.
- Result-folder pointers now resolve to the canonical successful 4-case run:
  - `results/bunny_force_visualization/LATEST_SUCCESS.txt`
  - `results/bunny_force_visualization/LATEST_ATTEMPT.txt`
