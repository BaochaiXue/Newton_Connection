# Implement: interactive_playground_profiling

## Preconditions

- confirm the exact scene and whether it is clean replay or weak-contact
- confirm render is disabled in the main throughput path

## Canonical Commands

```bash
python Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py --help
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
