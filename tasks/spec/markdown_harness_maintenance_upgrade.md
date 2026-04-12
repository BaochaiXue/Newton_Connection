> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-11`
> review_interval: `14d`
> update_rule: `Update when scope, constraints, or done criteria for the current harness-maintenance pass change.`
> notes: Bounded spec for the current harness-maintenance upgrade; includes progressive disclosure, root hygiene, hook semantics, and truthful user-facing reporting as part of harness enforcement.

# Spec: markdown_harness_maintenance_upgrade

## Goal

Upgrade the repo's existing markdown/control-plane harness so stale or
historical surfaces cannot plausibly masquerade as current truth, root-level
clutter no longer competes with entry surfaces, read-only inspection is not
blocked by overly broad hooks, and future Codex updates report outcomes instead
of bookkeeping.

## Non-Goals

- Editing `Newton/newton/`
- Creating a second results registry outside `results_meta/`
- Rewriting deep local result bundles purely for archival aesthetics
- Mass-relocating historical bundle trees when entry-surface quarantine is sufficient

## Inputs

- `AGENTS.md`
- `TODO.md`
- `docs/bridge/tasks/README.md`
- `docs/archive/tasks/README.md`
- `docs/bridge/current_status.md`
- `docs/generated/md_inventory.*`
- `docs/generated/md_cleanup_report.md`
- `results_meta/`
- `.codex/hooks/`
- `scripts/generate_md_inventory.py`
- `scripts/lint_harness_consistency.py`

## Outputs

- canonical markdown-maintenance task chain
- cleaned dashboard/index/task taxonomy surfaces
- archive-hub routing for historical bridge task pages
- root-level allowlist policy for tracked files
- narrowed hook policy: write-strict, read-loose
- approved bundle-entry policy for `results/` and `Newton/phystwin_bridge/results/`
- family-root-only Markdown policy for `results/`, with deeper local notes
  demoted to `.txt`
- refreshed generated markdown ledgers
- stronger lint/hook policy for markdown drift
- explicit outcome-first reporting policy for user-facing agent summaries
- outcome-first reporting contract encoded in durable repo instructions

## Constraints

- Keep `Newton/newton/` read-only
- Preserve historical value, but not in live-looking neighborhoods
- Treat `results_meta/` as the only committed authority for result meaning
- Prefer routing and quarantine over physically moving deep historical bundles

## Done When

- active and historical task artifacts are separated intentionally
- active entrypoints use progressive disclosure instead of inline historical enumerations
- tracked root clutter is moved into `scripts/` or converted into local-only ignored state
- deep bundle markdown is indexed only when explicitly approved as an entry surface
- `results/` family roots keep one local-browsing `README.md` each while deeper
  local notes/verdicts stop using Markdown
- current-status, task status pages, and `results_meta/` agree on authority
- generator/lint docs name one public inventory entrypoint
- active canonical task pages expose review metadata
- markdown maintenance becomes part of normal closeout instead of one-off cleanup
- hooks keep guarding risky mutation/publish flows without blocking plain read-only inspection
- future agent reports are steered toward outcomes instead of housekeeping
- user-facing Codex summaries are mechanically steered toward changes, resolved problems, findings, artifact pointers, and next step
