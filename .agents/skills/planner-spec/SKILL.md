---
name: planner-spec
description: Expand a short task request into a bounded repo-native task spec with clear scope, constraints, and done conditions.
---

# Planner Spec

Use this skill when a task prompt is too short or ambiguous to execute safely
without a tighter task spec.

## Goal

Turn a loose task request into one bounded `tasks/spec/<task>.md` artifact.

## Required Outputs

- clarified goal
- non-goals
- inputs
- outputs
- constraints
- done criteria

## Rule

Prefer tightening scope before implementation instead of compensating with chat
memory later.
