---
name: skeptical-video-audit
description: Run a fail-closed evaluator pass for video tasks using review bundles, skeptical verdicts, and explicit evidence.
---

# Skeptical Video Audit

Use this skill when a task claims success based on video evidence.

## Required Inputs

- video path
- contact sheet
- event sheet when relevant
- sampled-frame bundle
- current claim boundary

## Required Outputs

- structured pass/fail verdict
- frame/timestamp evidence
- explicit reasons to reject optimistic passes

## Rule

Do not accept “probably okay” for video tasks.
