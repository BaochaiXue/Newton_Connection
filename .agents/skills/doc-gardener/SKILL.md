---
name: doc-gardener
description: Repair stale pointers, duplicate truth surfaces, deprecated-but-not-marked files, and portability drift in the repo docs/control plane.
---

# Doc Gardener

Use this skill when documentation drift or duplicate truth surfaces are slowing
agents down.

## Goal

Keep one canonical surface per concept and make deprecations explicit.

## Check For

- stale run pointers
- duplicate task slugs
- missing spec/plan/implement/status links
- absolute machine-local paths in durable docs
- deprecated files without migration notes

## Rule

If the same ambiguity appears twice, encode the fix into docs, lint, or hooks.
