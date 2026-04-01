# Task: Harness Engineering Upgrade

## Question

How do we upgrade this repo from a useful first-layer Codex harness into a
durable long-running multi-agent harness with tighter source-of-truth
discipline, better result governance, more skeptical video acceptance, and
cleaner session handoff?

## Why It Matters

The project now depends on Codex for multi-step physics, video, and
presentation work. Without stronger harness engineering, agents will keep
drifting across duplicate docs, optimistic video validators, ignored heavy
artifacts, and incomplete handoff state.

## Current Status

- In progress
- Existing harness baseline already includes:
  - root + subtree `AGENTS.md`
  - `docs/`, `plans/`, `tasks/` control-plane structure
  - `.codex/` hooks/config
  - first-wave validators and wrapper scripts
- Known gaps before implementation:
  - no committed authoritative results registry
  - no skeptical multimodal video evaluator layer
  - hooks mostly remind rather than enforce
  - no first-class contracts / handoffs
  - no harness lint for duplicate truth surfaces and portability drift

## Code Entry Points

- Harness rules:
  - `AGENTS.md`
  - `docs/README.md`
  - `docs/PROJECT_MAP.md`
  - `docs/bridge/current_status.md`
  - `docs/bridge/open_questions.md`
- Control plane:
  - `.codex/config.toml`
  - `.codex/hooks.json`
  - `.codex/hooks/`
  - `.agents/skills/`
- Execution/evaluation:
  - `plans/`
  - `tasks/`
  - `scripts/`
  - `docs/evals/`

## Canonical Commands

Audit and consistency checks should start from:

```bash
rg --files -g '*.md'
find .codex/hooks -maxdepth 2 -type f | sort
rg --files scripts | rg 'validate|lint|check'
```

Final validation for this task must include:

```bash
python scripts/lint_harness_consistency.py
```

## Required Artifacts

- `docs/generated/harness_audit.md`
- authoritative task/spec/plan/implement/status chain for this upgrade task
- committed results-metadata mirror for authoritative local runs
- skeptical video evaluator docs/prompts and supporting scripts/templates
- harness lint/check script plus any useful hook upgrades
- contract/handoff templates and any local `AGENTS.md` additions

## Success Criteria

- active tasks have one clear authoritative chain
- duplicate truth surfaces are removed or explicitly deprecated
- authoritative run meaning no longer lives only in ignored local artifacts
- video tasks have a skeptical evaluator layer that fails closed
- handoff/contract artifacts exist for long-running work
- harness lint detects drift mechanically

## Open Questions

- How much enforcement should happen in hooks versus lint-only checks?
- Which metadata mirror location is best:
  `docs/generated/results_registry/`, `results_meta/`, or another explicit tree?

## Related Pages

- [README.md](./README.md)
- [delivery_and_profiling_review_20260401.md](./delivery_and_profiling_review_20260401.md)
- [harness_markdown_cleanup_20260401.md](./harness_markdown_cleanup_20260401.md)
