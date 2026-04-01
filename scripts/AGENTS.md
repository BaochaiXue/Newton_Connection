# Scripts Subtree Rules

This subtree contains canonical wrappers and utility scripts.

## Goal

Make repeatable workflows easier for Codex and humans.

## Script Expectations

Prefer wrappers that:

- create explicit output directories
- write `command.sh`
- write `run.log`
- print artifact locations

## Rule

If a command will likely be run repeatedly, prefer adding or updating a wrapper
script instead of retyping the long command in chat.
