---
name: skeptical-video-audit
description: Run the fail-closed skeptical evaluator workflow for meeting-facing videos using review bundles, rubrics, and a separate verdict surface.
---

# Skeptical Video Audit

Use this skill for any video task where the final claim depends on what is
visible in the rendered artifact.

## Goal

Separate generator success from evaluator acceptance.

## Required Surfaces

- `docs/evals/video_acceptance_rubric.md`
- `docs/evals/video_evaluator_prompt.md`
- `scripts/prepare_video_review_bundle.py`
- `scripts/run_skeptical_video_audit.py`

## Rule

Automatic QC may prepare evidence, but it does not equal final acceptance.
If the skeptical evaluator cannot defend PASS conservatively, the verdict is
FAIL.
