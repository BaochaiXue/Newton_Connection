> status: active
> canonical_replacement: none
> owner_surface: `docs_archive`
> last_reviewed: `2026-04-01`
> review_interval: `30d`
> update_rule: `Update when archive policy or archive sub-indexes change.`
> notes: Canonical policy surface for documentation archives. Archived files must not remain in live-looking neighborhoods.

> status: canonical
> canonical_replacement: none
> owner_surface: `docs_archive`
> last_reviewed: `2026-04-01`
> review_interval: `30d`
> update_rule: `Update when archive layout, archive routing, or live-vs-historical placement rules change.`
> notes: Canonical policy for historical documentation that must stop living in active-looking neighborhoods.

# Docs Archive Policy

This subtree is reserved for documentation that still has historical value but
is no longer part of the live control plane.

## Rule

Archived files must not compete with current instructions.

They should:

- preserve historical context,
- carry explicit historical/deprecated metadata,
- and point readers back to the canonical live surface when one exists.

## When To Move A File Here

Move a file here when:

- it is historically useful,
- its original path makes it look active or canonical,
- and an in-place deprecated pointer stub is no longer enough.

## Archive Subtrees

- `docs/archive/tasks/`
  - historical bridge task pages that should no longer live under
    `docs/bridge/tasks/`

Archive indexes:

- [tasks/README.md](./tasks/README.md)
