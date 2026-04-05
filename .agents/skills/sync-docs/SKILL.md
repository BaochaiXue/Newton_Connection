---
name: sync-docs
description: Update the repo-native documentation after meaningful code, workflow, or artifact-contract changes. Use when implementation changed semantics, commands, or output structures.
---

# Sync Docs

## Goal

Keep repo knowledge in files, not in chat memory.

## Minimum Update Set

Depending on the change, update one or more of:

- `docs/PROJECT_MAP.md`
- `docs/bridge/current_status.md`
- `docs/bridge/open_questions.md`
- `docs/bridge/experiment_index.md`
- the relevant `docs/bridge/tasks/*.md`
- the matching `tasks/status/*.md`

## Trigger Conditions

- command-line interface changed
- artifact layout changed
- task status changed
- a conclusion became stronger or weaker
- a canonical wrapper script was added or changed

## Do Not

- do not rewrite stable docs just to match phrasing
- do not leave changed workflows undocumented
- do not report the change back as process choreography; summarize the user-facing change, solved problem, conclusion, artifact path, and next step
