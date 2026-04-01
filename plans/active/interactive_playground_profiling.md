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

## Validation

- profiling outputs are reproducible
- the written interpretation avoids overclaiming

## Notes

- Backfilled during the harness upgrade so the active task set has a full chain.
