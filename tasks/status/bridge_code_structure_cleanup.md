> status: active
> canonical_replacement: none
> owner_surface: `bridge_code_structure_cleanup`
> last_reviewed: `2026-04-11`
> review_interval: `7d`
> update_rule: `Update after each meaningful refactor milestone and after validation.`
> notes: Live status log for bounded bridge-layer structure cleanup.

# Status: bridge_code_structure_cleanup

## Current State

Started.

This pass is scoped to a behavior-preserving structural extraction inside the
cloth+bunny bridge demo.

## What Changed This Pass

- bootstrapped the active task/spec/plan/implement/status chain
- selected the first cleanup target: force-visualization / camera / process-story
  helpers inside `demo_cloth_bunny_drop_without_self_contact.py`

## Problem Solved

- the repo now has a bounded, resumable structure-cleanup workstream instead of
  an unbounded “clean the whole codebase” request

## Findings / Conclusions

- the largest bridge hotspot is still
  `Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py`
- a safe first extraction boundary exists around pure force-visualization and
  projection helpers

## GIF / Artifact Paths To Review

- none yet; this pass is code-structure-first

## Next Step

- extract the cloth+bunny force-visualization helper cluster into a dedicated
  demo-local module and validate imports

## Blocking Issues

- none yet

## Validation

- task chain bootstrapped; code refactor validation pending
