# Status: markdown_truthfulness_cleanup

## Current State

In progress. The control-plane Markdown layer is being audited and normalized
so only canonical files sound authoritative.

## Last Completed Step

Bootstrapped the repo-native task chain and started the multi-surface Markdown
audit.

## Next Step

Implement the cleanup: generate the inventory, convert stale surfaces into
explicit deprecated/historical states, align `results_meta` references, and run
lint.

## Blocking Issues

- None recorded yet

## Artifact Paths

- `docs/generated/`
- `docs/runbooks/doc_gardening.md`
- `results_meta/`
