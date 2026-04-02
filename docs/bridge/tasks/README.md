> status: canonical
> canonical_replacement: none
> owner_surface: `task_index`
> last_reviewed: `2026-04-01`
> review_interval: `14d`
> update_rule: `Update when the active task set, historical task section, or task-index policy changes.`
> notes: Canonical bridge-task index. Keep active tasks separate from predecessor or one-off historical records.

# Bridge Task Pages

These pages are the working layer between `TODO.md` and implementation.

Each task page should answer:

1. What question are we trying to answer?
2. Why does it matter?
3. Which code paths are involved?
4. What experiment or artifact counts as success?
5. What remains open?

## Active Task Set

- [markdown_harness_maintenance_upgrade.md](./markdown_harness_maintenance_upgrade.md)
- [slide_deck_overhaul.md](./slide_deck_overhaul.md)
- [meeting_20260408_recall_part.md](./meeting_20260408_recall_part.md)
- [bunny_penetration_force_diagnostic.md](./bunny_penetration_force_diagnostic.md)
- [video_presentation_quality.md](./video_presentation_quality.md)
- [robot_deformable_demo.md](./robot_deformable_demo.md)
- [robot_rope_franka_tabletop_push_hero.md](./robot_rope_franka_tabletop_push_hero.md)
- [remote_interaction_root_cause.md](./remote_interaction_root_cause.md)
- [native_robot_rope_drop_release.md](./native_robot_rope_drop_release.md)
- [interactive_playground_profiling.md](./interactive_playground_profiling.md)
- [rope_perf_apples_to_apples.md](./rope_perf_apples_to_apples.md)
- [self_collision_transfer.md](./self_collision_transfer.md)
- [data_collection_protocol.md](./data_collection_protocol.md)
- [fast_foundation_stereo.md](./fast_foundation_stereo.md)

## One-Off / Historical Task Records

- [docs/archive/tasks/README.md](../../archive/tasks/README.md)
- [harness_engineering_upgrade.md](../../archive/tasks/harness_engineering_upgrade.md)
- [markdown_truthfulness_cleanup.md](../../archive/tasks/markdown_truthfulness_cleanup.md)
- [delivery_and_profiling_review_20260401.md](../../archive/tasks/delivery_and_profiling_review_20260401.md)
- [harness_markdown_cleanup_20260401.md](../../archive/tasks/harness_markdown_cleanup_20260401.md)
- [meeting_20260401_rope_profiling_rebuild.md](../../archive/tasks/meeting_20260401_rope_profiling_rebuild.md)

Task template:

- [_task_template.md](./_task_template.md)

## Usage Rule

When Codex starts work on one of these tasks, it should treat the corresponding
page as the first source of truth after `AGENTS.md`.
