# Spec: phystwin_upstream_sync_review

## Goal

Review the commits on `upstream/main` that are missing from local
`PhysTwin/main` and decide which changes are worth adopting for this workspace.

## Non-Goals

- Automatically merging upstream into local `PhysTwin/main`
- Editing `Newton/newton/`
- Rewriting local PhysTwin work to match upstream when the value is unclear

## Inputs

- local `PhysTwin/main`
- `PhysTwin` upstream remote `upstream/main`
- affected PhysTwin source/config files
- current bridge-task priorities in `docs/bridge/`

## Outputs

- a categorized recommendation for the behind commits
- updated task docs under `docs/`, `plans/`, and `tasks/`
- identified candidate files/commits for future adoption work

## Constraints

- Treat `Newton/newton/` as read-only
- Do not discard or overwrite existing local PhysTwin changes
- Prefer cherry-pickable or manually transplantable improvements over broad
  history sync
- Base recommendations on concrete diff inspection, not commit titles alone

## Done When

- The local-vs-upstream behind count is verified
- The behind commits are reviewed with file-level context
- Worth-adopting changes are called out explicitly
- The task status page records the recommended next action
