# Implement: harness_engineering_upgrade

## Preconditions

- Read `AGENTS.md`, `docs/README.md`, `docs/PROJECT_MAP.md`, and `TODO.md`
- Read `.codex/config.toml`, `.codex/hooks.json`, and current validators under `scripts/`

## Canonical Commands

```bash
python scripts/lint_harness_consistency.py
rg -n '/home/|Plan.md|Status.md|Prompt.md|DecisionLog.md' AGENTS.md docs plans tasks results
```

## Step Sequence

1. Record the harness audit
2. Normalize active task chains and deprecate ambiguous surfaces
3. Add committed results metadata mirrors
4. Add skeptical video evaluator docs/prompts and supporting scripts/templates
5. Add contracts/handoffs/templates and local AGENTS guidance
6. Strengthen lint and hooks, then validate

## Validation

- lint passes
- active task chain is complete for every active task
- results metadata mirrors identify current authoritative runs
- skeptical video evaluator layer is documented and discoverable

## Output Paths

- `docs/generated/harness_audit.md`
- `results_meta/`
- `docs/evals/`
- `tasks/contracts/`
- `tasks/handoffs/`
