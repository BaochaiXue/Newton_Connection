# Implement: harness_engineering_upgrade

## Preconditions

- Read the repo control-plane docs, hooks, skills, task/task-status structure, and validators
- Integrate the required audit perspectives before implementing migrations

## Canonical Commands

```bash
rg --files -g '*.md'
find .codex/hooks -maxdepth 2 -type f | sort
rg --files scripts | rg 'validate|lint|check'
python scripts/lint_harness_consistency.py
```

## Step Sequence

1. Bootstrap this task and write the integrated harness audit
2. Fix source-of-truth drift and slug ambiguity
3. Add committed results metadata mirror and migration docs
4. Add contracts, handoffs, skeptical video evaluator docs/prompts, and any needed scripts
5. Add harness lint and stronger hook enforcement
6. Update status docs and validate the upgraded harness

## Validation

- active tasks resolve to one authoritative chain
- authoritative results are discoverable from repo-only metadata
- skeptical video evaluation is distinct from generation and fails closed
- lint catches the intended drift classes

## Output Paths

- `docs/generated/harness_audit.md`
- `docs/evals/`
- `tasks/contracts/`
- `tasks/handoffs/`
- results metadata mirror subtree
- `scripts/lint_harness_consistency.py`
