# Implement: robot_rope_franka_tabletop_push_hero

## Preconditions

- Read `AGENTS.md`, `docs/README.md`, `TODO.md`
- Read `docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
- Confirm no writes under `Newton/newton/`

## Canonical Entry Points

```bash
python Newton/phystwin_bridge/demos/demo_robot_rope_franka.py --help
sed -n '1,260p' scripts/run_robot_rope_franka_tabletop_hero.sh
```

## Step Sequence

1. Add or tune a dedicated tabletop-push hero path in `demo_robot_rope_franka.py`
2. Write candidate outputs into `Newton/phystwin_bridge/results/robot_rope_franka/candidates/`
3. Validate every candidate with ffprobe, keyframes, contact sheet, and YES/NO QA
4. Promote the local winner into `BEST_RUN/`, then update status/docs and
   `results_meta/` if the task gains a committed promoted result

## Required Outputs

- `hero_presentation.mp4`
- `hero_debug.mp4`
- `validation_camera.mp4`
- `metrics.json`
- `validation.md`
- `contact_sheet.png`
- `keyframes/`
