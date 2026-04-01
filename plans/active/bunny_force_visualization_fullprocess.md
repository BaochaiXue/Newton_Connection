# Active Plan: Bunny Force Visualization Full-Process Closure

## Milestones

1. Audit the current baseline and identify why the existing “accepted” bundle is
   invalid under the stricter duration/full-process gates.
2. Patch the rendering pipeline so the force video uses the stable phenomenon
   frames as the global panel, with projected force overlays and a zoom panel.
3. Produce one passing `bunny_baseline` run with:
   - phenomenon duration >= 3.5s
   - force duration >= 4.5s
   - readable global cloth
   - readable local force panel
4. Run QA and visual inspection on the baseline.
5. Propagate the stable pipeline to:
   - `box_control`
   - `bunny_low_inertia`
   - `bunny_larger_scale`
6. Refresh the canonical result index and only then update slides/transcript.

## Validation Commands

- `python -m py_compile ...`
- `python scripts/render_bunny_force_artifacts.py ...`
- `python scripts/validate_bunny_force_visualization.py --run-dir ...`

## Fail-Closed Rule

Do not mark the task done if:

- the phenomenon or force video is still too short,
- the global cloth disappears,
- the force clip is still trigger-centric,
- the latest pointers still point to an invalid short-run bundle.
