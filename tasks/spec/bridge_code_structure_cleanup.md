> status: active
> canonical_replacement: none
> owner_surface: `bridge_code_structure_cleanup`
> last_reviewed: `2026-04-11`
> review_interval: `14d`
> update_rule: `Update when the bounded refactor scope, target module set, or done criteria change.`
> notes: Bounded spec for bridge-layer structure cleanup. This task is about code organization, not broad behavior changes.

# Spec: bridge_code_structure_cleanup

## Goal

Reduce bridge-layer monoliths by extracting coherent helper modules that make
future refactors and debugging easier.

## Non-Goals

- Editing `Newton/newton/`
- Rewriting physics semantics during the same pass
- Renaming the whole bridge layer or inventing a second helper hierarchy

## Inputs

- `docs/bridge/tasks/bridge_code_structure_cleanup.md`
- `Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py`
- existing helper modules under `Newton/phystwin_bridge/demos/`

## Outputs

- one new helper module with a narrow, readable responsibility
- reduced size and mixed-responsibility pressure in the target demo
- task-local status documenting what moved and what remains

## Constraints

- behavior-preserving refactor only
- prefer demo-local helper extraction before broader package re-layout
- keep imports and naming explicit

## Done When

- the selected target file is materially smaller
- extracted helpers have a coherent responsibility boundary
- targeted validation passes
- the next extraction target is documented
