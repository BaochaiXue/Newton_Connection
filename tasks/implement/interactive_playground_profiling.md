# Implement: interactive_playground_profiling

## Preconditions

- confirm the exact scene and whether it is clean replay or weak-contact
- confirm render is disabled in the main throughput path

## Canonical Commands

```bash
python Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py --help
```

Same-case one-to-one controller-replay bundle:

```bash
bash scripts/run_interactive_playground_apples_to_apples.sh \
  20260408_075949_blue_cloth_interactive_one_to_one_v1
```

Rope interactive playground one-to-one bundle:

```bash
bash scripts/run_interactive_playground_apples_to_apples.sh \
  20260408_090500_rope_interactive_one_to_one_v1 \
  --case-name rope_double_hand \
  --phystwin-env phystwin
```

## Step Sequence

1. run or inspect no-render profiling output first
2. attribute collision, solver-path, structural overhead, and render separately
3. document what remains unknown after the first split

## Validation

- mean/std or equivalent summary exists
- interpretation stays within the measured scope

## Output Paths

- profiling result bundles
- related meeting or task summary docs
- current same-case exploratory bundle:
  - rope:
    `results/interactive_playground_profiling/runs/20260408_090500_rope_interactive_one_to_one_v1`
  - cloth counterexample:
    `results/interactive_playground_profiling/runs/20260408_075949_blue_cloth_interactive_one_to_one_v1`
