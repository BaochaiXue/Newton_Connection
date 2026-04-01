# Spec: harness_engineering_upgrade

## Goal

Implement a durable repo-native harness upgrade that improves single-source of
truth, results governance, skeptical video evaluation, structured handoff, and
mechanical consistency enforcement.

## Non-Goals

- Modifying `Newton/newton/`
- Rewriting historical accepted evidence bundles in place
- Replacing existing validators when they can be layered instead
- Auditing third-party or vendored markdown outside the project harness

## Inputs

- `docs/bridge/tasks/harness_engineering_upgrade.md`
- `AGENTS.md`
- `docs/README.md`
- `docs/PROJECT_MAP.md`
- `docs/bridge/current_status.md`
- `docs/bridge/open_questions.md`
- `.codex/config.toml`
- `.codex/hooks.json`
- `.codex/hooks/`
- `.agents/skills/`
- `plans/`
- `tasks/`
- validators under `scripts/`

## Outputs

- `docs/generated/harness_audit.md`
- results metadata mirror subtree
- contract/handoff templates
- skeptical video evaluator docs/prompts
- harness lint/check script
- updated hooks / AGENTS / status docs / local guidance files

## Constraints

- Do not modify `Newton/newton/`
- Deprecate old surfaces explicitly; do not silently leave conflicting truth
- Heavy binaries may remain ignored, but authoritative meaning may not
- Keep migrations incremental and repo-readable

## Done When

- audit exists and is reflected in implementation
- active tasks have clean authoritative chains
- fresh agents can identify current best runs from repo-only metadata
- video tasks have a skeptical evaluator layer
- lint/hook validation runs cleanly enough to defend the harness upgrade
