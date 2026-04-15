# Implement: phystwin_four_new_cases_pipeline

## Preconditions

- `PhysTwin/data_different_types_only.zip` exists
- A runnable PhysTwin conda environment is available
- The four-case allowlist config exists before launching the pipeline

## Canonical Commands

- Inspect the archive:
  - `unzip -l PhysTwin/data_different_types_only.zip`
- Extract the raw cases:
  - `unzip PhysTwin/data_different_types_only.zip -d PhysTwin`
- Remove the source archive:
  - `rm PhysTwin/data_different_types_only.zip`
- Run the full pipeline:
  - `conda run -n phystwin python PhysTwin/pipeline_commnad.py --config-path PhysTwin/configs/data_config_four_new_cases.csv --task-name phystwin_four_new_cases_20260415 --logs-dir PhysTwin/logs/phystwin_four_new_cases_20260415`

## Step Sequence

1. Verify the case names and expected raw-capture structure in the zip
2. Extract into `PhysTwin/` so the cases land in `PhysTwin/data/different_types/`
3. Delete the source zip
4. Run the pipeline against the four-case allowlist
5. Inspect logs and archived outputs, then write status

## Validation

- Confirm the four extracted case directories exist
- Confirm the zip path no longer exists
- Confirm the pipeline logs directory exists and contains all stage logs
- Confirm the archive output directory exists for the run task name

## Output Paths

- `PhysTwin/data/different_types/<case>/`
- `PhysTwin/logs/phystwin_four_new_cases_20260415/`
- `PhysTwin/archive_result/phystwin_four_new_cases_20260415/`
