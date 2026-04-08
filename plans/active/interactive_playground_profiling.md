# Plan: interactive_playground_profiling

## Goal

Keep interactive-playground profiling as a clean no-render attribution task.

## Constraints

- distinguish clean replay from weak-contact scenes
- do not let GUI/render timing contaminate the main conclusion

## Milestones

1. capture no-render profiling outputs
2. separate collision, solver-path, structural overhead, and render cost
3. document what still remains open after the first attribution split
4. keep same-case controller-replay comparison separate from the committed rope benchmark truth

## Validation

- profiling outputs are reproducible
- the written interpretation avoids overclaiming

## Notes

- Backfilled during the harness upgrade so the active task set has a full chain.
- Latest completed exploratory milestone:
  - rope latest:
    `results/interactive_playground_profiling/runs/20260408_090500_rope_interactive_one_to_one_v1`
  - cloth counterexample:
    `results/interactive_playground_profiling/runs/20260408_075949_blue_cloth_interactive_one_to_one_v1`
  - render OFF on both sides
  - Newton baseline/precomputed throughput plus Newton/PhysTwin op attribution
