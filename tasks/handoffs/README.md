# Task Handoffs

This directory stores structured state transfers for long-running work.

Use a handoff when a task is likely to span sessions, agents, or context
resets.

Each handoff should let a fresh agent resume without reconstructing hidden chat
state.

Use:

- [_handoff_template.md](./_handoff_template.md)
