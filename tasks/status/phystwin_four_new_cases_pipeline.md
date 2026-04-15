# Status: PhysTwin Four New Cases Pipeline

## Current State

- In progress
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

## Last Completed Step

- Loaded the repo harness and identified the canonical PhysTwin stage order
- Verified that the incoming zip is already rooted at `data/different_types/`
- Confirmed the live PhysTwin render/eval output roots are currently absent, so
  a task-scoped archive run will not sweep unrelated live results

## Next Step

- Extract the four cases into `PhysTwin/data/different_types/`
- Prepare the four-case allowlist config
- Launch the full pipeline and capture logs

## Blocking Issues

- None yet

## Artifact Paths

- Incoming archive:
  - `PhysTwin/data_different_types_only.zip`
