# Task Spec: Robot + Deformable Demo Tuning

## Goal

Make the native Franka rope demo more physically defensible by reducing rope-through-table behavior and smoothing the controller response while keeping:

- native Newton Franka assets
- semi-implicit integration
- bridge-side implementation only

## Non-Goals

- Modifying `Newton/newton/`
- Replacing the native Franka path with the old proxy robot demo
- Turning this into a cloth or bunny task
- Chasing exact realism beyond what the current bridge can support

## Inputs

- task page:
  `docs/bridge/tasks/robot_deformable_demo.md`
- main demo:
  `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- canonical wrapper:
  `scripts/run_robot_rope_franka.sh`
- best-run reference:
  `results/robot_deformable_demo/BEST_RUN.md`

## Outputs

- updated native Franka controller/task tuning
- canonical run directory under `results/robot_deformable_demo/runs/`
- summary JSON with the tuned parameters recorded
- validated MP4/GIF/QA bundle
- updated task status notes

## Constraints

- Do not modify `Newton/newton/`
- Keep the mainline demo on native Franka + semi-implicit
- Prefer conservative bridge-side changes over large structural rewrites
- Preserve reproducibility through the wrapper script

## Done When

- the tuned run completes without crash or NaN
- rope motion is visually less prone to table intersection / odd sweeps
- summary metrics still show a meaningful interaction
- the run is validated and promoted as the current best tuning candidate
