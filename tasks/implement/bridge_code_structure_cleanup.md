> status: active
> owner_surface: `bridge_code_structure_cleanup`
> last_reviewed: `2026-04-11`
> review_interval: `7d`
> update_rule: `Update when the canonical commands, smoke coverage, or follow-on extraction order changes.`

# Implement: bridge_code_structure_cleanup

## Preconditions

- the cloth+bunny task page, spec, plan, contract, and handoff all exist
- `Newton/newton/` remains untouched
- the current worktree may be dirty, so only cloth+bunny package/shim/doc surfaces are modified

## Canonical Commands

```bash
python -m py_compile \
  Newton/phystwin_bridge/demos/cloth_bunny/*.py \
  Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py \
  Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py \
  Newton/phystwin_bridge/demos/cloth_bunny_common.py \
  Newton/phystwin_bridge/demos/cloth_bunny_force_viz.py \
  Newton/phystwin_bridge/demos/cloth_bunny_outputs.py \
  scripts/run_bunny_force_case.py \
  scripts/render_bunny_force_artifacts.py \
  scripts/build_bunny_collision_force_bundle.py

python Newton/phystwin_bridge/demos/cloth_bunny/offline.py --help
python Newton/phystwin_bridge/demos/cloth_bunny/example.py --help
python Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py --help
python Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py --help

python Newton/phystwin_bridge/demos/cloth_bunny/example.py \
  --viewer null \
  --num-frames 2 \
  --mode off \
  --out-dir tmp/cloth_bunny_example_smoke

python Newton/phystwin_bridge/demos/cloth_bunny/offline.py \
  --out-dir tmp/cloth_bunny_offline_smoke \
  --frames 2 \
  --skip-render
```

## Step Sequence

1. move canonical cloth+bunny implementation into `demos/cloth_bunny/`
2. add config/runtime/diagnostic wrapper modules and keep public names package-first
3. turn old top-level cloth+bunny files into transition shims
4. migrate cloth+bunny wrapper scripts off private underscore calls
5. validate canonical and legacy entrypoints
6. sync task/docs/current-status and regenerate required workflow metadata

## Output Paths

- `Newton/phystwin_bridge/demos/cloth_bunny/`
- `tmp/cloth_bunny_example_smoke/`
- `tmp/cloth_bunny_offline_smoke/`
- `tmp/cloth_bunny_script_smoke/`
- `tmp/cloth_bunny_force_bundle_build_case/`
- `tmp/cloth_bunny_force_artifacts_smoke/`
- `tmp/cloth_bunny_collision_bundle_smoke/`
