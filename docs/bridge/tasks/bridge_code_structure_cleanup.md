> status: active
> canonical_replacement: none
> owner_surface: `bridge_code_structure_cleanup`
> last_reviewed: `2026-04-11`
> review_interval: `14d`
> update_rule: `Update when the bounded refactor scope, target modules, or next structural extraction milestone changes.`
> notes: Active code-structure cleanup task. Keep scope bounded to bridge-layer structure improvement rather than broad behavior rewrites.

# Task: Bridge Code Structure Cleanup

## Question

How do we make the bridge-layer codebase easier to navigate and extend without
rewriting Newton core or destabilizing active experiment logic?

## Why It Matters

The repo's biggest code-quality risk is not only buggy logic; it is oversized,
mixed-responsibility bridge files that force future Codex runs to re-derive
module boundaries from scratch.

## Current Status

- In progress
- Scope for this pass is intentionally narrow:
  - start with the cloth+bunny force-visualization path
  - separate orchestration from pure visualization helpers
  - leave physics semantics unchanged

## Code Entry Points

- Main script:
  - `Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py`
- Shared helpers:
  - `Newton/phystwin_bridge/demos/cloth_bunny_common.py`
  - `Newton/phystwin_bridge/demos/bridge_shared.py`
  - `Newton/phystwin_bridge/demos/bridge_deformable_common.py`
- Supporting docs:
  - `docs/bridge/tasks/bridge_code_structure_cleanup.md`

## Canonical Commands

```bash
python -m py_compile \
  Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py \
  Newton/phystwin_bridge/demos/cloth_bunny_force_viz.py
```

## Required Artifacts

- clearer helper-module boundaries in `Newton/phystwin_bridge/demos/`
- unchanged runtime behavior for the refactored path
- updated task status documenting the extraction boundary and next step

## Success Criteria

- the targeted monolithic bridge file shrinks materially
- pure helper logic moves into a named module with a coherent responsibility
- imports/readability improve without changing experiment semantics
- targeted validation passes

## Open Questions

- which large bridge file should be the second extraction target after the
  cloth+bunny demo?
- when should helper modules be promoted from demo-local to tool/core-level?

## Related Pages

- [bunny_penetration_force_diagnostic.md](./bunny_penetration_force_diagnostic.md)
- [slide_deck_overhaul.md](./slide_deck_overhaul.md)
