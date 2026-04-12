> status: active
> canonical_replacement: none
> owner_surface: `bridge_code_structure_cleanup`
> last_reviewed: `2026-04-11`
> review_interval: `7d`
> update_rule: `Update after each meaningful refactor milestone and after validation.`
> notes: Live status log for cloth+bunny package-first cleanup.

# Status: bridge_code_structure_cleanup

## Current State

In progress.

The cloth+bunny path now has a canonical family package under
`Newton/phystwin_bridge/demos/cloth_bunny/`, while the old top-level demo and
helper files have been demoted to transition shims.

## What Changed This Pass

- moved the canonical cloth+bunny implementation into:
  - `Newton/phystwin_bridge/demos/cloth_bunny/offline.py`
  - `Newton/phystwin_bridge/demos/cloth_bunny/example.py`
  - `Newton/phystwin_bridge/demos/cloth_bunny/profiling.py`
  - `Newton/phystwin_bridge/demos/cloth_bunny/scene.py`
  - `Newton/phystwin_bridge/demos/cloth_bunny/render.py`
  - `Newton/phystwin_bridge/demos/cloth_bunny/outputs.py`
- added package-facing support modules:
  - `Newton/phystwin_bridge/demos/cloth_bunny/config.py`
  - `Newton/phystwin_bridge/demos/cloth_bunny/runtime.py`
  - `Newton/phystwin_bridge/demos/cloth_bunny/diagnostics.py`
- replaced the old top-level cloth+bunny files with thin compatibility shims
- updated `scripts/run_bunny_force_case.py`,
  `scripts/render_bunny_force_artifacts.py`, and
  `scripts/build_bunny_collision_force_bundle.py` to call package APIs instead
  of private demo-module helpers
- fixed two wrapper-script compatibility bugs discovered during smoke validation:
  - `render_bunny_force_artifacts.py` no longer dereferences an undefined
    `inferred` path
  - `build_bunny_collision_force_bundle.py` now falls back to all sim frames
    when `render_output_frame_indices` is absent in a skip-render bundle
- moved realtime-playground profiling helpers out of
  `cloth_bunny/example.py` into `Newton/phystwin_bridge/demos/cloth_bunny/profiling.py`
- expanded `Newton/phystwin_bridge/demos/cloth_bunny/runtime.py` from a thin
  forwarder into the owner of realtime playground path normalization, mode
  normalization, and model / solver setup
- moved force bundle / subprocess render bundle ownership into
  `Newton/phystwin_bridge/demos/cloth_bunny/diagnostics.py` for:
  - `resolve_force_dump_dir(...)`
  - `write_force_render_bundle(...)`
  - `render_force_artifacts_subprocess(...)`
- made `ClothBunnyExample.create_parser()` a real class entrypoint so the
  canonical realtime viewer reads more like a Newton example and less like a
  utility script with an embedded example class

## Problem Solved

- the cloth+bunny line is no longer organized around one giant top-level entry
  file plus several flat helper modules
- the repo now has a clear canonical package path and a separate compatibility
  layer, which matches Newton's example-family organization much more closely
- downstream scripts no longer need to reach into underscore-prefixed helper
  names to drive cloth+bunny workflows
- the canonical realtime playground entrypoint is less monolithic because setup
  and profiling/reporting logic now live in package support modules
- `runtime.py` and `diagnostics.py` are now real owners instead of symbolic
  wrappers

## Findings / Conclusions

- the package-first layout is already much easier to navigate even though some
  heavy force-diagnostic logic still lives in `cloth_bunny/offline.py`
- keeping a one-pass shim layer was necessary because the realtime viewer and
  multiple scripts still expect the old file paths
- wrapper-script smoke testing found real compatibility issues that static
  import checking would not catch
- ownership cleanup inside the canonical package matters almost as much as the
  original file move into `cloth_bunny/`
- profiling output code and runtime setup code were low-risk extractions that
  improved readability without changing cloth+bunny behavior

## Artifact Paths To Review

- realtime headless smoke log: `tmp/cloth_bunny_example_smoke/`
- offline skip-render smoke log: `tmp/cloth_bunny_offline_smoke/`
- realtime headless smoke log (refactor pass): `tmp/cloth_bunny_example_smoke_refactor/`
- offline skip-render smoke log (refactor pass): `tmp/cloth_bunny_offline_smoke_refactor/`
- diagnostics bundle smoke output: `tmp/cloth_bunny_diag_bundle_smoke/`
- wrapper smoke outputs:
  - `tmp/cloth_bunny_script_smoke/`
  - `tmp/cloth_bunny_force_bundle_build_case/`
  - `tmp/cloth_bunny_force_artifacts_smoke/`
  - `tmp/cloth_bunny_collision_bundle_smoke/`

## Next Step

- shrink `Newton/phystwin_bridge/demos/cloth_bunny/example.py` further by
  extracting manual substep and viewer-UI bookkeeping so the file looks even
  closer to a Newton official example
- shrink `Newton/phystwin_bridge/demos/cloth_bunny/offline.py` further by
  moving force-diagnostic mechanics into a real runtime/diagnostics split
- once that settles, decide whether rope/box families should adopt the same
  package template

## Blocking Issues

- `scripts/build_bunny_collision_force_bundle.py` is slower than the other
  wrapper smokes because it reconstructs explicit per-frame force states
- `python scripts/lint_harness_consistency.py` still reports one unrelated
  pre-existing issue: `tasks/status/rope_perf_apples_to_apples.md` contains a
  machine-local absolute path

## Validation

- `python -m py_compile Newton/phystwin_bridge/demos/cloth_bunny/*.py Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py Newton/phystwin_bridge/demos/cloth_bunny_common.py Newton/phystwin_bridge/demos/cloth_bunny_force_viz.py Newton/phystwin_bridge/demos/cloth_bunny_outputs.py scripts/run_bunny_force_case.py scripts/render_bunny_force_artifacts.py scripts/build_bunny_collision_force_bundle.py`
- `python Newton/phystwin_bridge/demos/cloth_bunny/offline.py --help`
- `python Newton/phystwin_bridge/demos/cloth_bunny/example.py --help`
- `python Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py --help`
- `python Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py --help`
- `python Newton/phystwin_bridge/demos/cloth_bunny/example.py --viewer null --num-frames 2 --mode off --out-dir tmp/cloth_bunny_example_smoke`
- `python Newton/phystwin_bridge/demos/cloth_bunny/offline.py --out-dir tmp/cloth_bunny_offline_smoke --frames 2 --skip-render`
- `python Newton/phystwin_bridge/demos/cloth_bunny/example.py --viewer null --num-frames 2 --mode off --out-dir tmp/cloth_bunny_example_smoke_refactor`
- `python Newton/phystwin_bridge/demos/cloth_bunny/offline.py --out-dir tmp/cloth_bunny_offline_smoke_refactor --frames 2 --skip-render`
- `python - <<'PY' ... diagnostics.write_force_render_bundle(...) ... PY`
- `python scripts/run_bunny_force_case.py --out-dir tmp/cloth_bunny_script_smoke --frames 2 --substeps 1 --skip-render`
- `python scripts/render_bunny_force_artifacts.py --bundle tmp/cloth_bunny_force_bundle_build_case/force_diagnostic/force_render_bundle.pkl --force-dump-dir tmp/cloth_bunny_force_artifacts_smoke`
- `python scripts/build_bunny_collision_force_bundle.py --bundle tmp/cloth_bunny_force_bundle_build_case/force_diagnostic/force_render_bundle.pkl --out-dir tmp/cloth_bunny_collision_bundle_smoke`
- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py` -> fails only on unrelated `tasks/status/rope_perf_apples_to_apples.md` machine-local path
