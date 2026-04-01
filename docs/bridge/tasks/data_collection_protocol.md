> status: active
> canonical_replacement: none
> owner_surface: `data_collection_protocol`
> last_reviewed: `2026-04-01`
> review_interval: `21d`
> update_rule: `Update when capture steps, required artifacts, or default collection policy changes.`
> notes: Active canonical task page for the bridge-side data collection procedure.

# Task: Data Collection Protocol

## Question

What should new data collection look like so it supports both PhysTwin
reconstruction and downstream bridge use?

## Why It Matters

Weak or inconsistent capture ruins everything downstream.

## Current Requirements

- front half of sequence should show the full object clearly
- back half should contain the manipulation/motion phase
- hand motion should be slower and steadier
- hand and object should move as a rigidly connected unit during the action
- capture should remain continuous

## Downstream Consumers

- PhysTwin reconstruction
- bridge export/import
- possible Fast-FoundationStereo evaluation

## Success Criteria

- protocol is short enough that new captures actually follow it
- protocol explicitly lists what to save
- protocol can be handed to a student without additional oral explanation
