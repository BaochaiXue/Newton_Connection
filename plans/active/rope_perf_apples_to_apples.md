# Plan: rope_perf_apples_to_apples

## Goal

Turn rope performance discussion from scattered Newton-only profiling into a
clean same-case Newton-vs-PhysTwin benchmark with an evidence-based bottleneck
explanation and slide-ready artifacts.

## Constraints

- No edits under `Newton/newton/`
- Same rope case, same trajectory, same `dt`, same substeps, same GPU
- Primary comparison must be no-render / headless
- No optimization claims before throughput + attribution are complete

## Milestones

1. Create canonical task/results scaffold and verify both benchmark entry points
2. Run Newton A0/A1 throughput and A2/A3 attribution into organized stage dirs
3. Build or promote a fair PhysTwin B0 headless replay harness and run it
4. Add PhysTwin B1 attribution if practical
5. Summarize the gap, write conclusions, and update slide assets

## Validation

- Stage dirs each contain `manifest.json`, `command.txt`, `git_rev.txt`,
  `stdout.log`, `stderr.log`, `summary.json`, `verdict.md`
- Benchmark table reports `ms_per_substep`, `RTF`, repeated-run mean/std/CV
- Conclusions explicitly separate bridge tax from remaining cost

## Notes

- Existing Newton rope raw outputs under `tmp/` are useful references, but they
  are not canonical evidence
- PhysTwin `interactive_playground.py` is not the final benchmark path because
  it includes visualization/UI
