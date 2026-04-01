# Plan: robot_rope_franka_tabletop_push_hero

## Goal

Turn the native Franka rope demo into a slow tabletop-push hero result with
clean candidate management and explicit visual validation.

## Constraints

- no edits under `Newton/newton/`
- use `demo_robot_rope_franka.py` as the main path
- final result root must live under `Newton/phystwin_bridge/results/robot_rope_franka/`

## Milestones

1. scaffold docs, status, and canonical result tree
2. implement tabletop-push task/result/validation path
3. iterate candidates until one passes all hard gates and is promoted

Status:

- Milestones 1-3 completed on `2026-04-01`
- accepted run:
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260401_081639_fixeddt_c08_gatepass/`

## Validation

- ffprobe and keyframe artifacts exist for every serious candidate
- validation answers explicit YES/NO questions
- local `BEST_RUN/` docs explain why the winner beat the other candidates
