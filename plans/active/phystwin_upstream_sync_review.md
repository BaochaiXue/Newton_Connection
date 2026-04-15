# Plan: phystwin_upstream_sync_review

## Goal

Produce a concrete recommendation for which missing upstream PhysTwin changes
should be adopted locally.

## Constraints

- No edits under `Newton/newton/`
- Preserve existing local PhysTwin work and uncommitted files
- Evaluate adoption value against current workspace needs, not abstract code
  cleanliness alone

## Milestones

1. Bootstrap the task chain and confirm local/upstream branch state
2. Enumerate the exact commits missing from local `PhysTwin/main`
3. Inspect the impacted files and summarize each commit theme
4. Classify the missing work as direct-adopt / partial-adopt / skip-for-now
5. Write the recommendation and next step into task status

## Validation

- `git -C PhysTwin rev-list --left-right --count main...upstream/main`
- `git -C PhysTwin log --reverse --oneline main..upstream/main`
- `git -C PhysTwin diff --stat main..upstream/main`

## Notes

- If several upstream commits form one coherent feature, recommendation may be
  given at feature-cluster level rather than one-commit-at-a-time
