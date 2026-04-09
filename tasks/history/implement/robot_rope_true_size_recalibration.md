> status: active
> canonical_replacement: none
> owner_surface: `robot_rope_true_size_recalibration`
> last_reviewed: `2026-04-05`
> review_interval: `14d`
> update_rule: `Update when the bounded repair workflow or validation path changes.`
> notes: Execution runbook for recovering a truthful true-size tabletop rope baseline.

# Implement: robot_rope_true_size_recalibration

## Canonical Inputs

- `docs/bridge/tasks/robot_rope_true_size_recalibration.md`
- `tasks/spec/robot_rope_true_size_recalibration.md`
- `tasks/status/robot_rope_true_size_recalibration.md`
- `docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
- `docs/bridge/tasks/remote_interaction_root_cause.md`
- `scripts/run_robot_rope_franka_tabletop_hero.sh`
- `scripts/diagnose_robot_rope_remote_interaction.py`
- `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`

## Working Order

1. Reconfirm the accepted `c12` control/geometry path before changing anything.
2. Compare current true-size defaults against the accepted baseline.
3. Run bounded sweeps over laydown, settle, contact height, and XY base/waypoint terms.
4. Keep actual finger contact as the proof surface; reject proxy-only or render-only fixes.
5. Promote only if a new candidate is honest on full video plus diagnostics.

## Validation

- `validate_robot_rope_franka_hero.py`
- `diagnose_robot_rope_remote_interaction.py`
- full-video review on hero/debug/validation
- no authority update unless a new candidate clearly beats `c12`
