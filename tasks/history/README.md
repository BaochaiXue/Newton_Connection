> status: canonical
> canonical_replacement: none
> owner_surface: `task_history`
> last_reviewed: `2026-04-05`
> review_interval: `30d`
> update_rule: `Update when execution-layer historical files are moved into or out of this subtree.`
> notes: Archive neighborhood for completed, superseded, or alias task-chain artifacts that should not live beside active execution files.

# Task History

This subtree stores historical execution-layer artifacts that no longer belong
in `tasks/spec/`, `tasks/implement/`, or `tasks/status/`.

Use it for:

- completed one-off reviews
- superseded cleanup passes
- historical campaign records
- deprecated alias task chains

Do not put active task state here.
