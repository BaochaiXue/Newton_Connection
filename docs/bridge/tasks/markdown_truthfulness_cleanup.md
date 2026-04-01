# Task: Markdown Truthfulness Cleanup

## Question

How do we turn the repo's Markdown control plane into a fail-closed truth
system so future agents are not misled by stale, conflicting, or
historical-but-live-sounding surfaces?

## Why It Matters

This repo now depends on Markdown as part of the harness control system.
If a file sounds authoritative but is stale, duplicated, or only locally true,
future agents will route work through the wrong surface and drift will return
even if the code is correct.

## Current Status

- In progress
- Audit-first cleanup pass for Markdown truth surfaces is underway
- This task specifically targets:
  - stale or conflicting Markdown control-plane surfaces
  - deprecated/historical files that still sound live
  - run-meaning drift between status pages and `results_meta/`
  - mechanical detection of future Markdown drift

## Code Entry Points

- Canonical control plane:
  - `AGENTS.md`
  - `docs/README.md`
  - `docs/bridge/current_status.md`
  - `docs/bridge/tasks/README.md`
  - `tasks/AGENTS.md`
  - `docs/bridge/tasks/AGENTS.md`
- Generated audit surfaces:
  - `docs/generated/harness_audit.md`
  - `docs/generated/harness_deprecations.md`
- Canonical results registry:
  - `results_meta/README.md`
  - `results_meta/INDEX.md`
  - `results_meta/LATEST.md`
  - `results_meta/tasks/*.json`
- Mechanical checks:
  - `scripts/lint_harness_consistency.py`

## Canonical Commands

```bash
python scripts/lint_harness_consistency.py
rg --files -g '*.md' .
rg -n 'authoritative|current|latest|promoted|best run|final' . -g '*.md'
```

## Required Artifacts

- `docs/generated/md_inventory.md`
- `docs/generated/md_inventory.json`
- `docs/generated/md_cleanup_report.md`
- `docs/generated/md_orphans.md`
- `docs/generated/md_deprecation_matrix.md`
- `docs/runbooks/doc_gardening.md`

## Success Criteria

- every live-looking Markdown control-plane surface is either canonical,
  deprecated, historical, generated, or deleted
- root singleton docs are absent or explicit stubs only
- canonical run meaning agrees with `results_meta/`
- no canonical Markdown surface uses machine-local absolute paths
- deprecated and historical files are explicitly marked
- Markdown drift becomes mechanically lint-detectable

## Open Questions

- Which historical files should remain in place as stubs versus move under an
  explicit archive subtree?
- How much of the Markdown inventory should be enforced directly in lint versus
  refreshed by a maintenance workflow?

## Related Pages

- [harness_engineering_upgrade.md](./harness_engineering_upgrade.md)
- [slide_deck_overhaul.md](./slide_deck_overhaul.md)
