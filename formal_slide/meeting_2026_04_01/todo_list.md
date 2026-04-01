# Meeting TODO Status — 2026-04-01

## Current Status

- `Todo 2: Newton Interactive Playground 性能 Profiling`
  - `Status: Completed`
  - `Todo 2 已完成（scope: rope replay case）`
  - `What is finished:`
    - fair rope replay throughput benchmark
    - Newton A0/A1 throughput comparison
    - Newton A2/A3 attribution breakdown
    - PhysTwin B0/B1 headless replay benchmark
    - Nsight A1/B0 launch-structure evidence
  - `Current conclusion:`
    - fair rope replay benchmark is complete
    - Newton A1 remains about `3.295x` slower than PhysTwin B0 on the clean rope replay baseline
    - controller bridge tax explains part of the gap (`A0 -> A1` gives about `1.874x` speedup)
    - the residual gap points to execution structure / graph launch, not collision
    - optimization discussion should come only after the fair benchmark and bottleneck explanation are established
  - `What remains outside Todo 2:`
    - optimize Newton replay only after this benchmark conclusion
    - keep weak-contact rope profiling as a separate workstream
    - extend the same methodology to other playground cases if needed
