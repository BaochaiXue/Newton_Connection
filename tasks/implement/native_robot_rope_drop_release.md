# Implement Runbook: Native Robot Rope Drop/Release Sanity Baseline

## Preconditions

- Repository root is the current git worktree root
- `Newton/newton/` stays read-only
- The previous robot + deformable lift-release bundle is preserved as history

## Canonical Commands

- eventual demo invocation:
  `python Newton/phystwin_bridge/demos/demo_robot_rope_franka.py --task drop_release_baseline`
- physics validator:
  `scripts/validate_robot_rope_drop_release_physics.py <run_dir>`

## Step Sequence

1. Create or update the dedicated result bundle files
2. Record the milestone-specific claim boundary in the task page and docs
3. Promote the first credible run into `results/native_robot_rope_drop_release/runs/`
4. Keep drag on/off evidence together with the run-local physics report

## Validation

- run metadata is self-describing
- release and impact timing are explicit in `summary.json`
- any promoted current baseline is recorded in
  `results_meta/tasks/native_robot_rope_drop_release.json`

## Output Paths

- `results/native_robot_rope_drop_release/README.md`
- `results_meta/tasks/native_robot_rope_drop_release.json`
- `results/native_robot_rope_drop_release/BEST_RUN.md` as a secondary local-only pointer
- `results/native_robot_rope_drop_release/index.csv`
- `results/native_robot_rope_drop_release/runs/<run_id>/`
