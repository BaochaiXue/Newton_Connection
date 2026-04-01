# Implement: rope_perf_apples_to_apples

## Preconditions

- GPU available on `cuda:0`
- Rope strict IR present
- PhysTwin rope case data and trained checkpoint present
- Rendering excluded from the primary benchmark commands

## Canonical Commands

- Newton throughput / attribution:
  - `python Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py ...`
- PhysTwin headless throughput / attribution:
  - `python scripts/benchmark_phystwin_rope_headless.py ...`
- Summary/material generation:
  - `python scripts/summarize_rope_perf_apples_to_apples.py ...`

## Step Sequence

1. Create the canonical results tree under `results/rope_perf_apples_to_apples/`
2. Run Newton A0/A1/A2/A3 with `--viewer null --profile-only`
3. Run PhysTwin B0 headless replay without GUI/render timing
4. Run PhysTwin B1 attribution if practical
5. Generate `index.csv`, methodology, conclusions, and slide assets

## Validation

- Check stage manifests and summaries exist
- Check repeated-run metrics are present
- Check the main comparison excludes rendering
- Check final conclusions do not overclaim unsupported causes

## Output Paths

- `results/rope_perf_apples_to_apples/`
- `formal_slide/meeting_2026_04_01/`
