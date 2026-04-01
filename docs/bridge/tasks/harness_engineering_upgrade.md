# Task: Harness Engineering Upgrade

## Question

How do we upgrade this repo from a good first-layer Codex harness into a
durable long-running multi-agent harness with stronger source-of-truth
discipline, skeptical evaluator layers, cleaner handoff, and results
governance that survives local-only heavy artifacts?

## Why It Matters

Future agents should spend their time solving bridge, physics, video, and
presentation problems rather than rediscovering task state, arguing over stale
docs, or over-trusting optimistic validators.

## Current Status

- Implemented for the current upgrade pass
- This task owns the current harness hardening pass
- Landed upgrade areas:
  - single-source-of-truth discipline
  - planner / builder / evaluator / handoff orchestration
  - skeptical multimodal video acceptance
  - committed metadata mirrors for authoritative local results
  - mechanical harness linting and stronger hooks
- Remaining tradeoffs:
  - local ignored result-bundle pointer files still exist as secondary
    convenience surfaces
  - skeptical video acceptance is intentionally fail-closed and still requires
    a separate reviewer payload to produce a final PASS

## Code Entry Points

- Harness rules:
  - `AGENTS.md`
  - `docs/PROJECT_MAP.md`
  - `.codex/config.toml`
  - `.codex/hooks.json`
  - `.codex/hooks/`
- Task-control surfaces:
  - `docs/bridge/tasks/`
  - `plans/active/`
  - `tasks/spec/`
  - `tasks/implement/`
  - `tasks/status/`
- Evaluation and validators:
  - `docs/evals/`
  - `scripts/validate_*.py`
- Results governance:
  - `results/`
  - `results_meta/`

## Canonical Commands

```bash
python scripts/lint_harness_consistency.py
python scripts/validate_experiment_artifacts.py <run_dir>
```

Audit-first commands:

```bash
rg --files -g '*.md'
rg -n 'Plan.md|Status.md|Prompt.md|DecisionLog.md' AGENTS.md docs plans tasks
```

## Required Artifacts

- `docs/generated/harness_audit.md`
- authoritative harness task chain for this upgrade
- committed results metadata mirror for authoritative runs
- skeptical video evaluator docs/templates
- harness lint/check script

## Success Criteria

- every active task has a clear authoritative task/spec/plan/implement/status chain
- duplicate or ambiguous task slugs are normalized or explicitly deprecated
- authoritative run meaning no longer lives only in ignored local bundles
- video tasks have a fail-closed skeptical evaluator layer
- handoff/contracts templates exist for long sessions
- hooks and lint catch harness drift mechanically

## Open Questions

- Which parts of the results-metadata workflow should be enforced by hooks
  versus lint versus human review?
- Which low-signal legacy experiment trees should stay historical exceptions
  instead of being fully mirrored?

## Related Pages

- [README.md](./README.md)
- [video_presentation_quality.md](./video_presentation_quality.md)
- [interactive_playground_profiling.md](./interactive_playground_profiling.md)
