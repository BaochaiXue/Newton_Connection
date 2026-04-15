# Implement: phystwin_upstream_sync_review

## Preconditions

- `PhysTwin` remote `upstream` is configured
- Local uncommitted work is left untouched
- The task pages exist before detailed comparison begins

## Canonical Commands

- Refresh upstream state:
  - `git -C PhysTwin fetch upstream main`
- Confirm ahead/behind counts:
  - `git -C PhysTwin rev-list --left-right --count main...upstream/main`
- Show missing commits:
  - `git -C PhysTwin log --reverse --decorate --oneline main..upstream/main`
- Show impacted files:
  - `git -C PhysTwin diff --stat main..upstream/main`
- Inspect representative commit diffs:
  - `git -C PhysTwin show --stat <commit>`
  - `git -C PhysTwin show <commit> -- <path>`

## Step Sequence

1. Fetch `upstream/main`
2. Verify the exact divergence against local `main`
3. Inspect the missing commits in chronological order
4. Group related commits into adoption themes
5. Record the recommendation and any conflict risk in the status page

## Validation

- The missing commit list matches the verified behind count
- The recommendation references concrete files or commit hashes
- The status page captures the recommended adoption path

## Output Paths

- `docs/bridge/tasks/phystwin_upstream_sync_review.md`
- `plans/active/phystwin_upstream_sync_review.md`
- `tasks/status/phystwin_upstream_sync_review.md`
