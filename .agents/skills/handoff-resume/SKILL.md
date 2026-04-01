---
name: handoff-resume
description: Create a structured handoff that lets a fresh agent resume without hidden chat state.
---

# Handoff Resume

Use this skill when work is likely to span sessions or agents.

## Required Outputs

- one handoff under `tasks/handoffs/`
- exact next command
- blocker
- missing evidence
- what not to redo

## Rule

Prefer one explicit handoff over a long ambiguous status log.
