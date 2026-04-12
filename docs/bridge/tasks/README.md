> status: canonical
> canonical_replacement: none
> owner_surface: `task_index`
> last_reviewed: `2026-04-11`
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

- [bridge_code_structure_cleanup.md](./bridge_code_structure_cleanup.md)
- [markdown_harness_maintenance_upgrade.md](./markdown_harness_maintenance_upgrade.md)
- [newton_robot_examples_kb_update.md](./newton_robot_examples_kb_update.md)
- [native_robot_table_penetration_probe.md](./native_robot_table_penetration_probe.md)
- [slide_deck_overhaul.md](./slide_deck_overhaul.md)
- [meeting_20260408_recall_part.md](./meeting_20260408_recall_part.md)
- [bunny_penetration_force_diagnostic.md](./bunny_penetration_force_diagnostic.md)
- [video_presentation_quality.md](./video_presentation_quality.md)
- [interactive_playground_profiling.md](./interactive_playground_profiling.md)
- [rope_perf_apples_to_apples.md](./rope_perf_apples_to_apples.md)
- [self_collision_transfer.md](./self_collision_transfer.md)
- [data_collection_protocol.md](./data_collection_protocol.md)
- [fast_foundation_stereo.md](./fast_foundation_stereo.md)

## Historical / Archive Routing

- [docs/archive/tasks/README.md](../../archive/tasks/README.md)
- [docs/archive/README.md](../../archive/README.md)
- [2026-04-09_robot_ps_interaction_retirement.md](../../decisions/2026-04-09_robot_ps_interaction_retirement.md)

Do not enumerate archived task pages inline here. Active entrypoints should map
current work first and route historical browsing through the archive hub.

Task template:

- [_task_template.md](./_task_template.md)

## Usage Rule

When Codex starts work on one of these tasks, it should treat the corresponding
page as the first source of truth after `AGENTS.md`.
