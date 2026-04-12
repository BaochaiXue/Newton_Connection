> status: active
> canonical_replacement: none
> owner_surface: `bridge_code_structure_cleanup`
> last_reviewed: `2026-04-11`
> review_interval: `14d`
> update_rule: `Update when the execution steps or canonical commands for the bounded refactor change.`
> notes: Runbook for bridge-layer structure cleanup.

# Implement: bridge_code_structure_cleanup

## Preconditions

- inspect the largest bridge-layer Python files
- identify one extraction boundary that is mostly pure helper logic
- confirm the target stays outside `Newton/newton/`

## Canonical Commands

```bash
find Newton/phystwin_bridge -type f -name '*.py' -print0 | xargs -0 wc -l | sort -nr | sed -n '1,40p'
python -m py_compile \
  Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py \
  Newton/phystwin_bridge/demos/cloth_bunny_force_viz.py
```

## Step Sequence

1. isolate a helper cluster inside the target monolith
2. move it to a new helper module with a narrow responsibility
3. update imports/call sites
4. run targeted validation
5. document the outcome and next candidate module

## Validation

- target scripts compile cleanly
- the new helper module name matches its actual responsibility

## Output Paths

- `Newton/phystwin_bridge/demos/`
- `tasks/status/bridge_code_structure_cleanup.md`
