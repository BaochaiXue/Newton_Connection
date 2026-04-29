# PhysTwin Data Process Flow

## Purpose

This page explains what the local PhysTwin data-process stage does before any
Newton bridge import happens.

The short version:

1. raw multi-camera RGB-D capture enters `PhysTwin/data/different_types/<case>/`
2. PhysTwin segments the object and hand, tracks motion, lifts depth into 3D,
   filters masks/tracks, optionally aligns a shape prior, and samples final
   inverse-physics input data
3. later PhysTwin stages optimize/train/infer a deformable model
4. the bridge exports the useful physical products into a stricter Newton-facing
   package

## Input Contract

Each raw case is expected to start with:

- `color/<camera>/<frame>.png`
- `depth/<camera>/<frame>.npy`
- `calibrate.pkl`
- `metadata.json`

Case selection is controlled by a CSV config with at least three columns:

- `case_name`
- `category`
- `shape_prior`

The batch entry point is:

- `PhysTwin/script_process_data.py`

That script loads the config, intersects it with cases present under the input
root, and calls:

- `PhysTwin/process_data.py --case_name <case> --category <category>`

When `shape_prior` is `true`, it also passes `--shape_prior`.

## Per-Case Stage Chain

`PhysTwin/process_data.py` runs the following logical stages.

1. Video segmentation

   Uses GroundedSAM-style segmentation to label the manipulated object and the
   hand/controller. The text prompt is formed as `<category>.hand`.

   Main output family:

   - `mask/`
   - `mask/mask_info_<camera>.json`

2. Optional shape-prior generation

   Runs only when `shape_prior=true`. The first-frame object mask is used to
   create a high-resolution masked image, then a shape-prior model generates a
   mesh or point representation.

   Main output family:

   - `shape/high_resolution.png`
   - `shape/masked_image.png`
   - `shape/`

3. Dense tracking

   Tracks object motion through the video with CoTracker-style dense tracking.

   Main output family:

   - `cotracker/`

4. Lift to 3D

   Combines depth, calibration, and images into per-frame world-coordinate point
   clouds.

   Main output family:

   - `pcd/<frame>.npz`

5. Mask post-processing

   Cleans and filters object/controller masks so downstream point and track
   extraction does not treat raw segmentation as final truth.

   Main output family:

   - `mask/processed_masks.pkl`

6. Track post-processing

   Converts dense image-space tracks into processed data aligned with the 3D
   observations.

   Main output family:

   - `track_process_data.pkl`

7. Optional shape-prior alignment

   Runs only when `shape_prior=true`. Aligns the shape prior to the partial
   observation and controller/object masks.

   Main output family:

   - `shape/matching/`

8. Final data generation

   Samples and packages the final point-cloud representation used by inverse
   physics. The script also records a train/test split based on the number of
   generated point-cloud frames.

   Main output family:

   - `final_data.pkl`
   - `split.json`

## Full PhysTwin Pipeline Context

The full local PhysTwin pipeline extends the data-process stage in this order:

1. `script_process_data`
2. `export_video_human_mask`
3. `dynamic_export_gs_data`
4. `script_optimize`
5. `script_train`
6. `script_inference`
7. `dynamic_fast_gs`
8. `final_eval`

The important distinction is that `script_process_data` prepares the observed
case data. The later stages estimate parameters, train/infer the PhysTwin model,
train/render Gaussian appearance, and archive evaluation outputs.

## Bridge-Relevant Products

The Newton bridge does not need every file that PhysTwin creates. It mainly
cares about products that can become a native Newton deformable model:

- initial particle positions and velocities
- mass-related fields
- collision/contact radius fields
- spring topology and rest lengths
- spring stiffness/damping fields
- controller indices and trajectories when the demo preserves control

Those bridge-facing products are documented at:

- `docs/phystwin/artifacts.md`
- `docs/bridge/ir_and_import.md`

## Canonical Local Commands

Use the repo wrapper first:

```bash
scripts/run_phystwin_local_pipeline.sh \
  --mode data-process \
  --config-path PhysTwin/configs/data_config_four_new_cases.csv \
  --task-name phystwin_four_cases_reprocess_20260427
```

For a full local PhysTwin run:

```bash
scripts/run_phystwin_local_pipeline.sh \
  --mode full \
  --config-path PhysTwin/configs/data_config_four_new_cases.csv \
  --task-name phystwin_four_cases_full_20260427
```

The wrapper writes:

- `command.sh`
- `run.log`
- `summary.json`
- full-pipeline stage logs under `stage_logs/`

For full mode, the PhysTwin archive is expected at:

- `PhysTwin/archive_result/<task_name>/`

## Common Failure Modes

- The config includes a case that is not present under the input root.
- `calibrate.pkl` camera order does not match `color/<camera>/` and
  `depth/<camera>/`.
- Segmentation produces multiple non-hand object masks in the first frame.
- Dense tracks leave the valid image/depth bounds.
- Shape-prior mode is enabled for a case that has no usable `shape/` inputs or
  cannot generate a stable prior.
- A resumed full pipeline starts after an earlier stage whose outputs are stale.

When reprocessing a raw case, clean generated per-case outputs first with:

```bash
python scripts/clean_phystwin_case_outputs.py --case <case_name>
```

If a camera-order diagnosis shows the shared `cam1`/`cam2` swap seen in the four
new sloth cases, repair the local capture copy with:

```bash
python scripts/fix_phystwin_calibrate_order.py --case <case_name> --order 0,2,1
```
