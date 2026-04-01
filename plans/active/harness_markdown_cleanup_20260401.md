# Plan: harness_markdown_cleanup_20260401

## Goal

Bring the repo's harness markdown back to one coherent workflow.

## Constraints

- No edits under `Newton/newton/`
- Do not keep duplicate docs merely for history if they are unreferenced and contradictory
- Keep changes focused on harness / engineering markdown

## Milestones

1. Identify stale and duplicate harness markdown
2. Remove orphaned root singleton docs and duplicate bunny scaffold docs
3. Update authoritative harness pages so future agents are routed correctly

## Validation

- removed files are unreferenced
- retained docs point to existing paths and current bundle structure
- current status / project map / AGENTS all agree on the control-plane workflow

## Notes

- Third-party markdown outside the project harness is out of scope for this cleanup.
