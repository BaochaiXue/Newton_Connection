# Implement Runbook: Robot + Deformable Demo Tuning

## Preconditions

- Repository root is the current git worktree root
- `Newton/newton/` stays read-only
- The existing best run has been reviewed as the comparison point

## Canonical Commands

- tuned canonical run:
  `scripts/run_robot_rope_franka.sh`
- optional direct script invocation:
  `python Newton/phystwin_bridge/demos/demo_robot_rope_franka.py --help`

## Step Sequence

1. Run the canonical wrapper with the tuned defaults
2. Inspect the summary for contact duration, displacement, and speed spikes
3. Check the rendered QA bundle for rope/table overlap and abrupt motion

## Validation

- wrapper exits cleanly
- summary JSON is populated
- `qa/verdict.md` reports PASS
- the video remains readable in both MP4 and GIF form

## Output Paths

- `results/robot_deformable_demo/runs/<run_id>/summary.json`
- `results/robot_deformable_demo/runs/<run_id>/media/final.mp4`
- `results/robot_deformable_demo/runs/<run_id>/media/preview.gif`
- `results/robot_deformable_demo/runs/<run_id>/qa/`
