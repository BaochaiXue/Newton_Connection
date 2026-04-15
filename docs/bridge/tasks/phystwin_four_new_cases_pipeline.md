# Task: PhysTwin Four New Cases Pipeline

## Question

Can we ingest the four newly provided PhysTwin motion cases into the canonical
`PhysTwin/data/different_types/` tree and run the full PhysTwin pipeline on
only those four cases without disturbing the existing case set?

## Why It Matters

These cases are new raw captures. Until they are placed correctly and passed
through the standard pipeline, they cannot be used for reconstruction,
optimization, inference, or render evaluation.

## Current Status

- In progress
- The new archive is present as `PhysTwin/data_different_types_only.zip`
- The four case names are:
  - `sloth_base_motion_ffs`
  - `sloth_base_motion_native`
  - `sloth_set_2_motion_ffs`
  - `sloth_set_2_motion_native`
- Archive inspection shows raw capture inputs only:
  - `color/`
  - `depth/`
  - `calibrate.pkl`
  - `metadata.json`
- The cases do not include `shape/`, so the allowlist metadata should use
  category `sloth` with `shape_prior=False`

## Code Entry Points

- Main pipeline:
  - `PhysTwin/pipeline_commnad.py`
- Stage scripts:
  - `PhysTwin/script_process_data.py`
  - `PhysTwin/export_video_human_mask.py`
  - `PhysTwin/dynamic_export_gs_data.py`
  - `PhysTwin/script_optimize.py`
  - `PhysTwin/script_train.py`
  - `PhysTwin/script_inference.py`
  - `PhysTwin/dynamic_fast_gs.py`
  - `PhysTwin/final_eval.py`
- Relevant docs:
  - `docs/runbooks/pipeline_run.md`

## Canonical Commands

- Unpack into the canonical data root:
  - `unzip PhysTwin/data_different_types_only.zip -d PhysTwin`
- Run the pipeline with a 4-case allowlist config and a unique archive task:
  - `conda run -n phystwin python PhysTwin/pipeline_commnad.py --config-path PhysTwin/configs/data_config_four_new_cases.csv --task-name phystwin_four_new_cases_20260415 --logs-dir PhysTwin/logs/phystwin_four_new_cases_20260415`

## Required Artifacts

- summary:
  - pipeline success/failure summary by stage and case
- scene / rollout:
  - `PhysTwin/experiments/<case>/`
  - `PhysTwin/experiments_optimization/<case>/`
  - `PhysTwin/gaussian_output/<case>/`
- video / gif:
  - archived render outputs under `PhysTwin/archive_result/<task_name>/`
- diagnostic outputs if applicable:
  - `PhysTwin/logs/<run_name>/`

## Success Criteria

- The four new case folders exist under `PhysTwin/data/different_types/`
- The zip file is removed after extraction
- The full PhysTwin pipeline runs against only the four new cases
- Logs and archived outputs are preserved under a unique run name
- The task status page records the outcome and artifact paths

## Open Questions

- Which conda environment is the correct end-to-end runtime on this machine if
  `phystwin` and `ps` differ in installed dependencies?
- Do any later stages require extra case metadata beyond `sloth,False`?

## Related Pages

- `tasks/spec/phystwin_four_new_cases_pipeline.md`
- `plans/active/phystwin_four_new_cases_pipeline.md`
- `tasks/implement/phystwin_four_new_cases_pipeline.md`
- `tasks/status/phystwin_four_new_cases_pipeline.md`
