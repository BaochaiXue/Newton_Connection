# Meeting TODO Status — 2026-04-01

## Current Status

- `Todo 2: Newton Interactive Playground 性能 Profiling`
  - `Status: Completed`
  - `Todo 2 已完成（scope: rope replay case）`
  - `What is finished:`
    - Newton E1 real-viewer end-to-end benchmark
    - fair rope replay throughput benchmark
    - Newton A0/A1 throughput comparison
    - Newton A2/A3 attribution breakdown
    - PhysTwin B0/B1 headless replay benchmark
    - Nsight A1/B0 runtime-organization evidence
  - `Current conclusion:`
    - the rope viewer itself is now measured directly through E1
    - on this rope case, render ON is only about `1.11x` slower than the same replay with render OFF
    - Newton A1 still remains about `3.295x` slower than PhysTwin B0 on the same no-render rope replay benchmark
    - controller replay overhead explains part of the gap (`A0 -> A1` gives about `1.874x` speedup), but not the whole gap
    - within this controlled rope benchmark, the residual gap is more consistent with runtime organization than with replay overhead alone
    - slide/source proof now cites Newton core + PhysTwin core directly, and wrapper code is kept as methodology only
    - optimization discussion starts only after the viewer-facing benchmark and the apples-to-apples benchmark are both established
  - `What remains outside Todo 2:`
    - optimize Newton replay only after this benchmark conclusion
    - keep weak-contact rope profiling as a separate workstream
    - extend the same methodology to other playground cases if needed
