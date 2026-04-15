# Status: PhysTwin Four New Cases Pipeline

## Current State

- Completed
- Requested scope is limited to four new cases:
  - `sloth_base_motion_ffs`
  - `sloth_base_motion_native`
  - `sloth_set_2_motion_ffs`
  - `sloth_set_2_motion_native`
- Archive inspection is complete:
  - each case contains raw `color/` + `depth/` captures with
    `calibrate.pkl` and `metadata.json`
  - no `shape/` directory was found in the incoming archive
- Planned allowlist metadata:
  - category `sloth`
  - `shape_prior=False`
- Pipeline run status:
  - front-end calibration ordering issue diagnosed and fixed
  - `script_process_data` was rerun successfully to usable completion for all
    four cases after calibration repair plus a tracking bug fix
  - resumed pipeline completed through:
    - `export_video_human_mask`
    - `dynamic_export_gs_data`
    - `script_optimize`
    - `script_train`
    - `script_inference`
    - `dynamic_fast_gs`
    - `final_eval`
  - final archived output root:
    - `PhysTwin/archive_result/phystwin_four_new_cases_20260415/`
  - do not trust downstream artifacts from the pre-fix interrupted run

## Last Completed Step

- Loaded the repo harness and identified the canonical PhysTwin stage order
- Verified that the incoming zip is already rooted at `data/different_types/`
- Confirmed the live PhysTwin render/eval output roots are currently absent, so
  a task-scoped archive run will not sweep unrelated live results
- Extracted the four new cases into `PhysTwin/data/different_types/`
- Deleted `PhysTwin/data_different_types_only.zip`
- Added:
  - `PhysTwin/configs/data_config_four_new_cases.csv`
  - `scripts/build_phystwin_color_videos.py`
- Built the missing `color/0.mp4`, `color/1.mp4`, and `color/2.mp4` files for
  all four new cases so `process_data.py` could start
- Ran the pipeline into `script_process_data` and diagnosed the first
  case-level failure mode:
  - case: `sloth_base_motion_ffs`
  - symptom: the merged raw point cloud looked split / duplicated across views
  - evidence:
    - raw debug outputs exist under
      `PhysTwin/data/different_types/sloth_base_motion_ffs/pcd_debug/`
    - object-only cross-view alignment with current calibration order
      `(0,1,2)` gives mean symmetric nearest-neighbor distance `~0.242 m`
    - swapping the last two extrinsics to `(0,2,1)` drops the same metric to
      `~0.025 m`
  - current conclusion:
    - this is much more consistent with a camera-order mismatch in
      `calibrate.pkl` than with generic mask noise
- Stopped the in-flight pipeline after the diagnosis so it would not keep
  producing bad downstream artifacts
- Extended the same permutation diagnosis to all four cases using first-frame
  single-image object masks under `/tmp/phystwin_calib_diag/`
- Result: all four cases prefer the same camera-order permutation `(0,2,1)`
  over the identity `(0,1,2)`
  - `sloth_base_motion_ffs`
    - best `(0,2,1)`: `~0.0260 m`
    - identity `(0,1,2)`: `~0.2471 m`
  - `sloth_base_motion_native`
    - best `(0,2,1)`: `~0.0279 m`
    - identity `(0,1,2)`: `~0.2885 m`
  - `sloth_set_2_motion_ffs`
    - best `(0,2,1)`: `~0.0261 m`
    - identity `(0,1,2)`: `~0.1548 m`
  - `sloth_set_2_motion_native`
    - best `(0,2,1)`: `~0.0281 m`
    - identity `(0,1,2)`: `~0.1541 m`
- Strong current conclusion:
  - these four new cases are internally consistent with a shared camera-order
    mismatch where `cam1` and `cam2` should be swapped relative to the current
    `calibrate.pkl` ordering
- Implemented fixes:
  - added `scripts/fix_phystwin_calibrate_order.py`
  - added `scripts/clean_phystwin_case_outputs.py`
  - patched `PhysTwin/data_process/data_process_track.py` to invalidate
    out-of-bounds track indices before indexing into point/depth grids
  - patched `PhysTwin/process_data.py` to fail fast on substep errors instead
    of silently continuing after non-zero `os.system(...)` returns
- After the code fixes:
  - manually repaired the missing `track_process_data.pkl` / `final_data.pkl`
    for:
    - `sloth_set_2_motion_ffs`
    - `sloth_set_2_motion_native`
  - verified all four cases now have:
    - `final_data.pkl`
    - `split.json`
- Final resumed run:
  - command:
    - `env MPLCONFIGDIR=/tmp/matplotlib conda run -n phystwin python PhysTwin/pipeline_commnad.py --config-path PhysTwin/configs/data_config_four_new_cases.csv --task-name phystwin_four_new_cases_20260415 --logs-dir PhysTwin/logs/phystwin_four_new_cases_20260415_resume_after_trackfix --start-stage export_video_human_mask`
  - current logs:
    - `PhysTwin/logs/phystwin_four_new_cases_20260415_resume_after_trackfix/`
  - stage logs present for:
    - `export_video_human_mask`
    - `dynamic_export_gs_data`
    - `script_optimize`
    - `script_train`
    - `script_inference`
    - `dynamic_fast_gs`
    - `final_eval`

## Next Step

- optional: prepare a compact delivery manifest for the four cases with the
  most useful `.pkl`, `.pth`, `.mp4`, and metrics-table paths
- optional: spot-check the archived qualitative videos and compare them against
  `results/final_results.csv`

## Blocking Issues

- No active blocker for the completed four-case pipeline run
- Residual note:
  - `results/final_track.csv` currently contains only the header row, so the
    main populated quantitative table is `results/final_results.csv`

## Artifact Paths

- Logs:
  - `PhysTwin/logs/phystwin_four_new_cases_20260415/`
  - `PhysTwin/logs/phystwin_four_new_cases_20260415_camfix_rerun/`
  - `PhysTwin/logs/phystwin_four_new_cases_20260415_resume_after_trackfix/`
- Final archive:
  - `PhysTwin/archive_result/phystwin_four_new_cases_20260415/`
- Final metrics:
  - `PhysTwin/archive_result/phystwin_four_new_cases_20260415/results/final_results.csv`
  - `PhysTwin/archive_result/phystwin_four_new_cases_20260415/results/final_track.csv`
- Comparison boards:
  - `PhysTwin/archive_result/phystwin_four_new_cases_20260415/comparison_boards/base_motion_native_vs_ffs_overlay_2x3_labeled.mp4`
  - `PhysTwin/archive_result/phystwin_four_new_cases_20260415/comparison_boards/base_motion_native_vs_ffs_overlay_2x3_labeled.gif`
  - `PhysTwin/archive_result/phystwin_four_new_cases_20260415/comparison_boards/set2_motion_native_vs_ffs_overlay_2x3_labeled.mp4`
  - `PhysTwin/archive_result/phystwin_four_new_cases_20260415/comparison_boards/set2_motion_native_vs_ffs_overlay_2x3_labeled.gif`
- First diagnosed raw-point-cloud debug bundle:
  - `PhysTwin/data/different_types/sloth_base_motion_ffs/pcd_debug/`
- First-frame diagnostic masks:
  - `/tmp/phystwin_calib_diag/`
