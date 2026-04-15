# Plan: phystwin_four_new_cases_pipeline

## Goal

Run the canonical PhysTwin processing/training/evaluation stack on the four new
motion cases without broadening the run to unrelated cases.

## Constraints

- No edits under `Newton/newton/`
- Preserve existing PhysTwin archives and outputs
- Use a four-case allowlist instead of the global default config

## Milestones

1. Create task scaffolding and inspect the incoming zip layout
2. Place the four raw cases into `PhysTwin/data/different_types/` and remove the zip
3. Prepare a four-case pipeline config and ensure the driver can use it
4. Run the full PhysTwin pipeline and inspect stage logs/output paths
5. Update status with completion or failure details

## Validation

- `unzip -l` confirms the expected four cases before extraction
- The extracted case folders contain `color/`, `depth/`, `calibrate.pkl`, and `metadata.json`
- The pipeline logs directory contains per-stage stdout/stderr files
- Archive output exists under a unique `PhysTwin/archive_result/<task_name>/`

## Notes

- The existing `PhysTwin/pipeline_commnad.py` archive step is acceptable for
  this run because the live `results/` and `gaussian_output_dynamic*` roots are
  currently absent; existing historical runs already live under `archive_result/`
