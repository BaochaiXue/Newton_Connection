> status: active
> canonical_replacement: none
> owner_surface: `harness_engineering`
> last_reviewed: `2026-05-21`
> review_interval: `30d`
> update_rule: `Update when agent workflow roles, task-control artifacts, validation gates, or garbage-collection policy change.`
> notes: Canonical repo-level runbook for managing this project as an agent-readable engineering harness.

# Harness Engineering Runbook

Use this runbook when a task is bigger than a direct code edit, produces
research artifacts, changes shared structure, or needs to survive a context
reset.

## Core Rule

The repository is the control system. Durable task state, acceptance criteria,
validation evidence, and handoff state must live in versioned repo files rather
than hidden chat context.

Do not create a parallel harness. Strengthen the existing surfaces:

- `AGENTS.md`
- `docs/`
- `docs/bridge/tasks/`
- `tasks/spec/`
- `plans/active/`
- `tasks/implement/`
- `tasks/status/`
- `tasks/contracts/`
- `tasks/handoffs/`
- `results_meta/`
- `scripts/lint_harness_consistency.py`

## Control Loop

1. Map
   - Start from `AGENTS.md`, `docs/README.md`, and the relevant task page.
   - Prefer short entrypoint maps over large inline manuals.
2. Plan
   - For non-trivial work, create or refresh the task/spec/plan/status chain.
   - Keep plans concrete enough for another agent to resume.
3. Contract
   - Before risky or result-bearing milestones, write a contract with hard-fail
     conditions and evaluator evidence.
   - Use `tasks/contracts/<task>.md` for required-workflow tasks.
4. Execute
   - Make scoped changes through normal repo tools and wrappers.
   - Prefer reproducible scripts over one-off terminal recipes.
5. Evaluate
   - Run the smallest meaningful validator first, then broader checks.
   - Treat failures as harness feedback: missing tool, missing doc, missing
     invariant, or missing artifact contract.
6. Record
   - Update the status page with outcomes, conclusions, artifacts, blockers,
     and validation.
   - Put durable result meaning in `results_meta/`, not only local bundles.
7. Handoff
   - For long or interruptible work, write the exact next command and current
     blocker in `tasks/handoffs/<task>.md`.
8. Garbage Collect
   - Archive historical task pages.
   - Keep active entrypoints map-like.
   - Run the markdown inventory and harness lint after control-plane changes.

## Agent Roles

Use these roles as a design pattern, not as mandatory process overhead:

- Planner: expands a vague request into scope, risks, milestones, and acceptance
  criteria.
- Builder: implements one coherent slice at a time and leaves reproducible
  evidence.
- Evaluator: skeptically checks behavior against the contract, using validators,
  artifacts, logs, screenshots, videos, or source inspection as appropriate.

For small changes, one agent can perform all roles locally. For complex or
high-risk work, separate the evaluator mindset from the builder mindset even if
the same Codex session performs both passes.

## Task Classes

Small direct edit:

- No new task chain required.
- Run the local test or syntax check that covers the changed surface.

Non-trivial implementation:

- Requires task page, spec, active plan, implement page, and status page.
- Update status after each meaningful checkpoint.

Result-bearing experiment:

- Requires artifact directory with command provenance and summary metadata.
- Validate with `scripts/validate_experiment_artifacts.py` when applicable.
- Mirror committed result meaning in `results_meta/`.

Long-running or multi-session work:

- Requires a contract before major milestones.
- Requires a handoff before pausing, context reset, or final partial closeout.

Harness/control-plane work:

- Update this runbook or `docs/runbooks/doc_gardening.md` if the rule itself
  changes.
- Regenerate generated markdown inventory surfaces.
- Run harness lint before claiming the control plane is healthy.

## Required Evidence

For any substantial closeout, the status page should answer:

- what changed
- what problem was solved or clarified
- what conclusion now holds
- which artifact, GIF, MP4, PDF, or result bundle matters
- what validation ran
- what the exact next step is

User-facing reports should follow `docs/runbooks/agent_reporting.md`.

## Mechanical Checks

Canonical harness checks:

```bash
python scripts/generate_md_inventory.py
python scripts/lint_harness_consistency.py
```

When result registry JSON changes:

```bash
python scripts/sync_results_registry.py
```

When an experiment directory is produced:

```bash
python scripts/validate_experiment_artifacts.py <run_dir>
```

## Anti-Patterns

- stuffing all project knowledge into `AGENTS.md`
- relying on chat-only decisions for future agent behavior
- treating local result bundle notes as committed truth
- leaving completed tasks in active task directories
- adding root-level scripts or configs that are not true repo entry surfaces
- accepting a visual or experiment result without artifact evidence
- reporting process mechanics instead of outcomes
