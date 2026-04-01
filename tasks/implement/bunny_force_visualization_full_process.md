# Implement Runbook: Bunny Force Visualization Full Process

## Canonical Baseline Workflow

1. run `scripts/run_bunny_force_case.py` into a fresh `phenomenon/` directory
2. render force artifacts from the generated `force_render_bundle.pkl` into a
   separate `force_mechanism/` directory
3. validate the case root with `scripts/validate_bunny_force_visualization.py`
4. inspect sampled frames and contact sheets before promoting the run

## Expected Case Layout

- `artifacts/<case>/phenomenon/`
- `artifacts/<case>/force_mechanism/self_off/force_diagnostic/`
- `artifacts/<case>/qa/`

## Reporting Rule

If duration, temporal density, or subject visibility fails, do not promote the
run. Update `tasks/status/bunny_force_visualization_full_process.md` first.
