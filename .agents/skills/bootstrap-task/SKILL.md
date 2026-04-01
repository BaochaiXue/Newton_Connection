---
name: bootstrap-task
description: "Create the execution scaffolding for a non-trivial repo task: task page linkage, task spec, active plan, implement runbook, and status log. Use when work should span more than a quick one-shot edit."
---

# Bootstrap Task

Use this skill when a task is large enough that it should not live only in chat.

## Goal

Create the minimum repo-native task scaffold so later Codex agents can resume
work without reconstructing context from memory.

## Required Outputs

- one task page under `docs/bridge/tasks/` or a link to an existing one
- one spec in `tasks/spec/`
- one active plan in `plans/active/`
- one runbook in `tasks/implement/`
- one status file in `tasks/status/`

## Workflow

1. Read `AGENTS.md`, `docs/README.md`, and `TODO.md`.
2. Map the work to an existing task page under `docs/bridge/tasks/`, or create a
   new page from `_task_template.md`.
3. Create matching files in:
   - `tasks/spec/`
   - `plans/active/`
   - `tasks/implement/`
   - `tasks/status/`
4. Keep titles and slugs aligned across all files.
5. Record:
   - goal
   - constraints
   - canonical commands
   - artifact expectations
   - next step

## Do Not

- do not start implementing major code changes before the scaffold exists
- do not duplicate a task page if one already exists
