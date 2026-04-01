# Implement: Native Robot + Native Table + PhysTwin Rope Hero Demo

## Preconditions

- read `AGENTS.md`
- read `docs/bridge/tasks/robot_rope_franka_tabletop_push.md`
- read `docs/bridge/tasks/video_presentation_quality.md`
- confirm the current robot demo entry point and output paths

## Canonical Commands

```bash
python Newton/phystwin_bridge/demos/demo_robot_rope_franka.py --help
scripts/run_robot_rope_franka.sh
```

## Step Sequence

1. Add or tune a tabletop-push hero preset in `demo_robot_rope_franka.py`
2. Produce candidate hero runs with explicit debug, presentation, and validation cameras
3. Validate readability, contact visibility, and artifact completeness
4. Promote one best run under the canonical result tree

## Output Paths

- `Newton/phystwin_bridge/results/robot_rope_franka/`
- `Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/`
- `Newton/phystwin_bridge/results/robot_rope_franka/candidates/`
