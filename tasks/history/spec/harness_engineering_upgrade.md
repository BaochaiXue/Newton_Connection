# Spec: harness_engineering_upgrade

## Goal

Implement a durable repo-native harness upgrade covering source-of-truth
discipline, results governance, skeptical video evaluation, handoff/contracts,
and mechanical consistency checks.

## Non-Goals

- Editing `Newton/newton/`
- Rewriting historical accepted evidence bundles in place
- Converting every legacy local experiment into a fully mirrored metadata entry
  in one pass

## Inputs

- `AGENTS.md`
- `docs/README.md`
- `docs/PROJECT_MAP.md`
- `docs/STYLE_GUIDE.md`
- `docs/bridge/current_status.md`
- `.codex/config.toml`
- `.codex/hooks.json`
- `.codex/hooks/`
- `.agents/skills/`
- `scripts/validate_*.py`

## Outputs

- harness audit doc
- canonical task-chain coverage for all active tasks
- results metadata mirror
- skeptical video evaluator docs/templates and supporting script paths
- harness lint and stronger hook behavior

## Constraints

- Keep `Newton/newton/` read-only
- Prefer explicit deprecation + migration over silent replacement
- Keep heavy binaries local; mirror authoritative meaning in committed metadata

## Done When

- the harness audit exists and is actionable
- the active task set has canonical execution artifacts
- the new lint passes
- the new evaluator/handoff/results-governance docs cross-link correctly
