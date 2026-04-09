> status: canonical
> canonical_replacement: none
> owner_surface: `bridge_control_plane`
> last_reviewed: `2026-04-09`
> review_interval: `30d`
> update_rule: `Update when the experiment directory contract, index policy, or canonical validation path changes.`
> notes: Canonical experiment-contract surface for bridge work; keep this as the durable index rather than a run ledger.

# Experiment Index

Last updated: 2026-04-09

This page explains how experiment outputs should be organized and indexed.

## Purpose

Bridge experiments currently live mostly under `tmp/`. That is acceptable for
active research, but only if each experiment directory has a predictable shape
and a human-readable index.

## Canonical Experiment Directory Contract

Each serious experiment directory should contain:

- `README.md`
- `command.sh` or `command.txt`
- `summary.json`
- `scene.npz` or equivalent rollout artifact
- `*.mp4` render output when relevant
- `*.gif` presentation output when relevant

Canonical template surface:

- [templates/experiment_README_template.md](./templates/experiment_README_template.md)

If the experiment is diagnostic, also include:

- `force_diag_trigger_substep.npz`
- `force_diag_trigger_summary.json`
- `force_diag_trigger_snapshot.png`

## Validation Rule

The artifact contract is not only a writing guideline. It is meant to be
checkable by:

- `scripts/validate_experiment_artifacts.py`
- `scripts/validate_bunny_force_visualization.py` for bunny force-visualization
  runs that need sampled-frame QA, black-screen checks, motion checks, and
  contact sheets

Typical validation dimensions:

- `README.md` present
- `command.sh` or `command.txt` present
- summary present
- scene / rollout artifact present
- diagnostic bundle present when required

If validation fails, the experiment should not be treated as a clean reusable
artifact yet.

Specialized bunny visual QA bundles should also expose the workflow under
`results/bunny_force_visualization/`, including a verdict template for manual
review.

For the reopened meeting-facing bunny board task, the canonical promoted local
bundle is now:

- `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5`

and the bundle-level latest pointers under `results/bunny_force_visualization/`
should be treated only as the fast local entrypoint, not as the canonical
committed source of truth.

## Legacy vs Canonical

Not every existing directory under `tmp/` already satisfies the contract.
Until backfilled, think in two buckets:

- canonical
  - has README, command trace, summary, and expected artifacts
  - safe for Codex to consume as a reusable reference
- legacy
  - may contain valuable outputs
  - but still requires manual interpretation or backfill before reuse

The validator should be the default tool for distinguishing these two states.

Canonical committed meaning for promoted local bundles now lives under:

- `results_meta/tasks/*.json`
- `results_meta/INDEX.md`
- `results_meta/LATEST.md`

For promoted result bundles that should stay easy to navigate, prefer a
dedicated folder under `results/<bundle_name>/` with:

- `README.md`
- `README.template.md` when templating is useful
- `manifest.template.json` when the bundle uses manifests
- `INDEX.md` and/or `index.csv` depending on the bundle
- `LATEST_ATTEMPT.txt` and `LATEST_SUCCESS.txt` as secondary local-only
  convenience pointers when the bundle promotes runs by pointer
- a `runs/<run_id>/` subtree for the actual artifacts

Current and preserved bundles intentionally vary slightly:

- `results/bunny_force_visualization/` uses `INDEX.md` plus local-only pointer files
- `results/robot_deformable_demo/` uses `index.csv` plus local-only `BEST_RUN.md`
- `results/native_robot_rope_drop_release/` uses `index.csv` plus local-only pointer files

These local surfaces are now secondary/local-only. The committed registry under
`results_meta/` is the canonical cross-task surface.

## Experiment Categories

### Contact / Penetration

Examples:

- cloth vs bunny
- cloth vs box
- rope vs bunny

### Multi-Deformable

Examples:

- two ropes
- rope + sloth
- ropes on rigid support

### Robot + Deformable

Status:

- retired on `2026-04-09`
- canonical retrospective:
  - `docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`
- keep the preserved robot bundles as historical evidence only, not as current promoted work

Historical local result roots:

- `results/robot_deformable_demo/`
  - local-only `BEST_RUN.md`
  - `index.csv`
  - `runs/<run_id>/`
- `rejected/<run_id>/`

Historical preserved robot + deformable run:

- `results/robot_deformable_demo/runs/20260331_030148_native_franka_lift_release_presentation`

Historical registry record for that run lives in:

- `results_meta/tasks/robot_deformable_demo.json`

Its required review artifacts are:

- `media/final.mp4`
- `summary.json`
- `qa/ffprobe.json`
- `qa/contact_sheet.png`
- `qa/event_sheet.png`
- `qa/validation.json`
- `qa/verdict.md`

Separate historical stage-0 sanity baseline bundle:

- `results/native_robot_rope_drop_release/`
  - local-only `BEST_RUN.md`
  - `index.csv`
  - `README.template.md`
  - `manifest.template.json`
  - `SLIDE_READY.md`
  - `drag_ab_compare.json`

This bundle is reserved for the simpler native robot + semi-implicit
rope release/drop sanity baseline and should not be mixed into the older
lift-release evidence chain.

Historical preserved stage-0 run:

- `results/native_robot_rope_drop_release/runs/20260331_232106_native_franka_recoilfix_drag_off_w5`
  - `final_presentation.mp4`
  - `final_debug.mp4`
  - `summary.json`
  - `physics_validation.json`
  - `qa/contact_sheet.png`
  - `qa/event_sheet.png`
  - `qa/verdict.md`

Matched drag-ON comparison:

- `results/native_robot_rope_drop_release/runs/20260331_232459_native_franka_recoilfix_drag_on_w5`
  - `final_presentation.mp4`
  - `summary.json`
  - `physics_validation.json`

The historical robot bundle still keeps local helpers so archived runs remain
auditable without rediscovering the layout:

- `results/robot_deformable_demo/README.template.md`
- `results/robot_deformable_demo/manifest.template.json`
- `results/robot_deformable_demo/SLIDE_READY.md`
- a run-local `README.md` in each promoted `runs/<run_id>/` directory

Historical registry record for the stage-0 baseline lives in:

- `results_meta/tasks/native_robot_rope_drop_release.json`

### Profiling

Examples:

- realtime viewer no-render profiles
- rope control profile runs

## Documentation Rule

When a new experiment becomes important to meetings or long-term reasoning,
document it either:

- as a dedicated task page under `tasks/`, or
- as a short section on the relevant topic page with links to the artifact path

## Minimal Promotion Workflow

To promote an experiment from a raw `tmp/` run into a reusable project artifact:

1. ensure the directory follows the canonical contract
2. run the validator
3. link it from the relevant task page or topic page
4. record its status in `current_status.md` if it changes a real project claim

## Related Pages

- [tasks/README.md](./tasks/README.md)
- [../STYLE_GUIDE.md](../STYLE_GUIDE.md)
