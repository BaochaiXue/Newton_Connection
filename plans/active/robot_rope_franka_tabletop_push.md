# Plan: Native Robot + Native Table + PhysTwin Rope Hero Demo

## Goal

Turn the current native Franka rope path into a slow tabletop-push hero demo
that is visually readable and meeting-ready.

## Constraints

- no Newton core changes unless explicitly justified
- keep the deformable object on the PhysTwin bridge path
- do not turn the hero demo into a drop test
- keep the final run short enough to read, but long enough to defend

## Milestones

1. Scaffold the task and result tree
2. Add or tune a tabletop-push task preset and readable camera path
3. Validate candidate runs and promote one best run

## Validation

- explicit video QA with yes/no checks
- ffprobe metrics and keyframes for each candidate
- clean result-folder organization with one promoted best run
