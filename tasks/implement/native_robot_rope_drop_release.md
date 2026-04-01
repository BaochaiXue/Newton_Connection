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
- the bundle-level status files distinguish this baseline from the older lift-release run

## Output Paths

- `results/native_robot_rope_drop_release/README.md`
- `results/native_robot_rope_drop_release/BEST_RUN.md`
- `results/native_robot_rope_drop_release/index.csv`
- `results/native_robot_rope_drop_release/runs/<run_id>/`
