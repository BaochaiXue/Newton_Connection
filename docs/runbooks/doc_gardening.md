> status: active
> canonical_replacement: none
> owner_surface: `doc_gardening`
> last_reviewed: `2026-04-11`
> review_interval: `30d`
> update_rule: `Update when markdown closeout policy, inventory generation, or review-age expectations change.`
> notes: Canonical runbook for markdown truthfulness maintenance, progressive disclosure, root hygiene, and stale-doc garbage collection.

# Markdown Maintenance Runbook

Use this runbook whenever a Markdown control-plane surface is renamed,
deprecated, archived, promoted, or superseded.

## Core Rule

Markdown truthfulness is part of the harness. When the filesystem and the docs
disagree, make them converge immediately.

Progressive disclosure is also part of the harness. Active entrypoints should
map current work first and route historical context through archive hubs rather
than enumerating long historical file lists inline.

When reporting the cleanup to the user, follow
[`agent_reporting.md`](./agent_reporting.md): lead with the change, the problem
it fixes, the resulting conclusion, and the next step instead of narrating the
maintenance process.

## User-Facing Closeout Rule

When a maintenance pass is reported back to the user, the summary must stay
outcome-first:

1. what changed
2. what ambiguity or stale surface was removed
3. what conclusion or new truth rule now holds
4. which artifact/GIF/video surfaces are worth checking, when relevant
5. what the next step is

Do not lead with inventory regeneration, lint commands, hook edits, or task
scaffolding. Those belong in a short trailing validation note, not the main
headline.

## Closeout Flow

1. Update the task status file.
2. Update the canonical replacement surface.
3. Add or refresh the deprecated/historical banner if the old file remains.
4. If a bridge task page becomes historical, move it to `docs/archive/tasks/`
   instead of leaving it under `docs/bridge/tasks/`.
5. If a workstream ends in a negative result or failed final claim, write a
   single decision/retrospective surface under `docs/decisions/` and point the
   archived task chain at that retirement record.
6. If root-level tracked files are not stable repo entry surfaces or core
   top-level configuration, move them under `scripts/` or convert them into
   ignored local-only state.
7. Do not mass-move deep bundle trees when approved entry-surface quarantine is
   enough. Keep only a small approved set of local bundle entry Markdown
   surfaces indexed into the harness.
8. Narrow hooks so mutation/publish/archive/generation flows remain guarded,
   but plain read-only inspection of watched paths does not get blocked.
9. For tasks in the repo's required-workflow class, create or refresh:
   - `tasks/contracts/<task>.md`
   - `tasks/handoffs/<task>.md`
   before treating the task as fully maintained.
10. Refresh `docs/generated/md_deprecation_matrix.md` and `docs/generated/md_cleanup_report.md` when the deprecation set changes.
11. Update `results_meta/` if run meaning changed.
12. Run `python scripts/sync_results_registry.py` when registry JSON changed.
13. Run `python scripts/generate_md_inventory.py`.
14. Review `docs/generated/md_staleness_report.md` and `docs/generated/task_surface_matrix.md`.
15. Run `python scripts/lint_harness_consistency.py`.
16. Refresh local bundle pointers only if they still add local convenience.
17. Do not recreate retired generated ledgers once their role has been absorbed by the `md_*` report set.
18. When reporting the pass, follow `docs/runbooks/agent_reporting.md`: lead
    with changes, solved problems, conclusions, artifacts, and next steps, not
    bookkeeping.

## Required Metadata For Deprecated / Historical Files

At the top of the file, expose:

- `status`
- `canonical_replacement`
- `owner_surface`
- `last_reviewed`
- `notes`

## Metadata Convention For Control-Plane Markdown

For non-trivial control-plane Markdown, prefer the same top-of-file metadata
block across active, local-only, deprecated, historical, and generated
surfaces:

- `status`
- `canonical_replacement`
- `owner_surface`
- `last_reviewed`
- `review_interval`
- `update_rule`
- `notes`

Recommended status values:

- `active`
- `local_only_secondary`
- `deprecated`
- `historical`
- `generated`

Rules:

- canonical files may use `canonical_replacement: none`
- local-only files must say they are not the committed authority surface
- deprecated/historical files must point at the canonical live replacement when
  one exists
- generated files must name their regeneration command and whether hand edits
  are allowed

## Delete vs Stub vs Archive

- Delete:
  - only when the file is redundant, reproducible, unreferenced, and not historically useful
- Stub:
  - when the old path still matters for discoverability
- Archive:
  - when the file remains historically useful but should stop living in a live-looking location
  - bridge task pages should archive into `docs/archive/tasks/`

## Quarantine Deep Bundles

- Do not treat every `README.md` under `results/` or
  `Newton/phystwin_bridge/results/` as a harness entrypoint.
- Keep only a small approved set of family-level or pointer-level Markdown
  surfaces indexed into the harness.
- Deeper run-local `README.md` files are for local browsing only unless they
  are explicitly promoted into the approved entry set.
- Under `results/`, prefer keeping one family-root `README.md` and demoting
  deeper local notes, verdicts, and run summaries to `.txt`.
- Use `python scripts/demote_results_markdown.py --dry-run` before a broad
  `results/` demotion pass so the rename scope stays auditable.

## Root Allowlist

- Root-level tracked files should be limited to true repo entry surfaces such as
  `AGENTS.md`, `TODO.md`, and stable top-level config files.
- Reusable scripts, report renderers, and example configs belong in `scripts/`.
- Runtime-local files such as viewer layout state should stay ignored or
  explicitly local-only instead of being tracked at root.

## Review-Age Policy

- `docs/bridge/current_status.md`
  - review every `7d`
- active task pages and the current markdown-harness maintenance chain
  - review every `14-21d`
- task indexes, registry README surfaces, generated-docs README, and runbooks
  - review every `30d`
- broader encyclopedia or historical archives
  - longer intervals are acceptable if they remain clearly scoped
