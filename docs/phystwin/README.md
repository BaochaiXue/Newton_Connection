# PhysTwin Section

This section explains what PhysTwin contributes to the current project.

In this repository, PhysTwin is not just an upstream dependency. It is the
source of the deformable-object state, learned/estimated parameters, topology,
and object-specific data products that the bridge later maps into Newton.

## What This Section Covers

- What PhysTwin produces that the bridge actually consumes
- Which PhysTwin outputs are stable enough to treat as contracts
- Where the current project touches PhysTwin directly
- Which parts are upstream PhysTwin concerns vs bridge concerns

## Start Here

- [architecture.md](./architecture.md)
- [artifacts.md](./artifacts.md)
- [data_process_flow.md](./data_process_flow.md)

## Key Repo Roots

- `PhysTwin/README.md`
- `PhysTwin/export_topology.py`
- `PhysTwin/qqtt/`
- `PhysTwin/configs/`
- `PhysTwin/pipeline_commnad.py`
- `PhysTwin/script_process_data.py`
- `PhysTwin/process_data.py`
- `PhysTwin/experiments/`
- `PhysTwin/experiments_optimization/`
- `PhysTwin/gaussian_output/`
- `scripts/run_phystwin_local_pipeline.sh`

## Relationship To The Bridge

PhysTwin does not directly run the Newton experiments. Instead:

1. PhysTwin reconstructs / optimizes object state and parameters.
2. The bridge exports a strict IR-like package.
3. Newton-side demos rebuild a native simulation from that package.

That means PhysTwin pages should focus on what is exported and why it matters,
not on Newton-side rendering or diagnostics.

## Open Questions

- Which PhysTwin outputs are semantically stable enough to document as a hard contract?
- Which fields are artifacts of the current pipeline and should not be treated as universal?
- Where should "interactive playground" behavior be documented: PhysTwin or bridge?

## Related Pages

- [../bridge/README.md](../bridge/README.md)
- [../bridge/ir_and_import.md](../bridge/ir_and_import.md)
