# Split V3 Architecture Decision

Date: 2026-04-08

## Decision

Choose a split architecture:

- robot/table: robot-first native pattern
- rope: deformable bridge path
- coupling: direct-finger geometry truth

## Why

The completed v2 rewrite already proved:

- removing overwrite semantics is necessary
- but not sufficient
- the remaining failure is structural

## Candidate ranking

1. Split architecture
   - best match to official Newton patterns
   - highest chance of satisfying startup stability + real blocking + rope push
2. Keep tuning v2
   - low yield
   - already negative-result-proven

## Immediate implication

Stage-0 for split-v3 should be:

- robot + table only
- no rope
- no support box
- no visible tool

Only after this passes should rope return in Stage-1.
