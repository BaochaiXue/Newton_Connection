> status: canonical
> canonical_replacement: none
> owner_surface: `docs_archive`
> last_reviewed: `2026-04-09`
> review_interval: `30d`
> update_rule: `Update when historical bridge task pages are moved into or out of this subtree.`
> notes: Singular archive neighborhood for historical bridge task pages that should not remain beside active task pages.

# Archived Bridge Task Pages

This subtree holds historical bridge task pages that still matter for audit or
traceability but should no longer live inside `docs/bridge/tasks/`.

Use the live task map for current work:

- `docs/bridge/tasks/README.md`
- `docs/bridge/tasks/markdown_harness_maintenance_upgrade.md`
- `docs/decisions/2026-04-09_robot_ps_interaction_retirement.md` for the retired robot + deformable line

Rules:

- keep historical metadata blocks intact
- point `canonical_replacement` directly at the current live surface when one
  exists
- do not move active task pages here
