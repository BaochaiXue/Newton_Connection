---
name: doc-gardener
description: Scan and repair stale pointers, duplicate truth surfaces, deprecated-but-unmarked docs, and portability drift.
---

# Doc Gardener

Use this skill when docs, task artifacts, and status surfaces risk drifting out
of sync.

## Required Outputs

- stale pointer list
- duplicate truth-surface list
- explicit deprecation/migration edits

## Rule

If the same ambiguity appears twice, encode the fix into the harness rather
than restating it in chat.
