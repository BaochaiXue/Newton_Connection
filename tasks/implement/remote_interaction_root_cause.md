# Implement: remote_interaction_root_cause

## Preconditions

- Read `AGENTS.md`, `docs/README.md`, `TODO.md`
- Read tabletop hero task/status/current-status pages
- Re-audit the current promoted run bundle before changing behavior

## Canonical Commands

- `bash scripts/run_robot_rope_franka_tabletop_hero.sh --tag <tag>`
- `python scripts/validate_robot_rope_franka_hero.py <RUN_DIR> --manual-review-json <RUN_DIR>/manual_review.json`

## Step Sequence

1. Build the hypothesis board and record all candidate causes before editing.
2. Instrument the current run to compare visible finger geometry, real URDF
   colliders, control targets, proxies, and rope collision thickness.
3. Write the ranked root-cause report in `diagnostics/root_cause_ranked_report.md`.
4. Implement the smallest truthful fix aimed at the primary cause.
5. Generate a new full candidate bundle and perform strict validator plus
   multimodal full-video review.
6. Update task/docs/results surfaces only after the claim is defensible.

## Validation

- `scripts/validate_robot_rope_franka_hero.py`
- explicit visual YES/NO review
- diagnostic artifact bundle under `diagnostics/`

## Output Paths

- `diagnostics/`
- `Newton/phystwin_bridge/results/robot_rope_franka/candidates/<RUN_ID>/`
- `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json` if promoted
