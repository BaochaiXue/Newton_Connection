# Workspace Agent Rules

This file is the repo entrypoint for all Codex agents and sub-agents.
Treat it as a short routing layer, not as the full project encyclopedia.

## Hard Boundary

- `Newton/newton/` is strictly read-only.
- Do not modify any file under `Newton/newton/`.
- If a task truly requires a Newton core change, stop and report that it
  conflicts with the workspace rule.

## Allowed Write Scope

Agents may edit files outside `Newton/newton/`, especially:

- `Newton/phystwin_bridge/`
- `docs/`
- `plans/`
- `tasks/`
- `scripts/`
- slide / report / transcript generation code

## Where To Start

For any non-trivial task, read in this order:

1. this `AGENTS.md`
2. [docs/README.md](./docs/README.md)
3. [TODO.md](./TODO.md)
4. the relevant task page under `docs/bridge/tasks/`
5. the relevant status/open-question page under `docs/bridge/`

Do not dump all project knowledge into this file. Put durable explanations in
`docs/`.

## Repo-Native Harness

This repo is organized so Codex can work as an engineering agent, not only a
chat window.

### Knowledge Layer

- `docs/` is the system of record for durable project knowledge.
- `docs/bridge/tasks/` contains task-specific working pages.
- `docs/bridge/current_status.md` is the short operational summary.
- `docs/bridge/open_questions.md` records unresolved technical questions.

### Execution Layer

- `plans/active/` contains active execution plans.
- `plans/completed/` contains finished plans.
- `tasks/spec/` stores task specs.
- `tasks/implement/` stores execution runbooks.
- `tasks/status/` stores task-local progress logs.

### Tooling Layer

- `scripts/` contains canonical wrapper scripts for common workflows.
- Prefer wrapper scripts over ad hoc shell commands when a wrapper exists.
- If no wrapper exists and the task will likely repeat, create one.

### Evaluation Layer

- `docs/evals/` contains evaluator rubrics and validation conventions.
- Use the artifact validator in `scripts/validate_experiment_artifacts.py` for
  experiment directories when relevant.

## Standard Agent Loop

For any long-running or multi-step task:

1. Find or create the task page.
2. Find or create:
   - `tasks/spec/<task>.md`
   - `plans/active/<task>.md`
   - `tasks/status/<task>.md`
3. Execute one milestone at a time.
4. Run validation before claiming success.
5. Update status docs after each meaningful checkpoint.
6. Prefer committing only after the task state is documented.

## Artifact Contract

Serious experiments should not live only as loose files in `tmp/`.

Each experiment directory should contain, when applicable:

- `README.md`
- `command.sh` or `command.txt`
- `summary.json`
- scene / rollout artifact such as `scene.npz`
- `*.mp4`
- `*.gif`
- diagnostic artifacts if the task is diagnostic

If a task produces an experiment directory, validate it before calling the task
done.

## Completion Definition

Do not say a task is done unless:

- the main code/doc changes are present
- the expected artifacts exist
- the relevant validator/test/check command has been run
- the status page reflects the new state

## Preferred Biases

- Prefer bridge-layer fixes and documentation over core modifications.
- Prefer reproducible scripts over one-off commands.
- Prefer explicit task/status artifacts over hidden conversational state.
- If the same confusion happens twice, improve the harness rather than restating
  the answer in chat.

## Retired Root Docs

The root-level singleton task files below are retired and should not be
recreated:

- `Plan.md`
- `Status.md`
- `Prompt.md`
- `DecisionLog.md`

Use `docs/bridge/tasks/` plus `tasks/spec/`, `plans/active/`,
`tasks/implement/`, and `tasks/status/` instead.
