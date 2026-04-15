# Task: PhysTwin Upstream Sync Review

## Question

Among the commits present on `Jianghanxiao/PhysTwin:main` but missing from the
local `PhysTwin/main`, which changes are worth adopting into this workspace?

## Why It Matters

The local bridge work depends on PhysTwin-side pipeline, data-processing,
training, and evaluation behavior. If we stay behind useful upstream fixes, we
risk debugging already-solved issues or carrying avoidable local patches.

## Current Status

- Review complete
- `PhysTwin` is a nested git repository with:
  - local branch: `main`
  - local remote: `origin`
  - upstream remote: `Jianghanxiao/PhysTwin.git`
- Verified locally after fetching `upstream/main`:
  - ahead by `34`
  - behind by `19`
- The `behind 19` set only changes:
  - `README.md`
  - `assets/gradio_support.png`
  - `assets/RL_game.gif`
- No missing upstream commits were found in the current behind set for the live
  PhysTwin pipeline / training / inference code paths
- The task goal is to classify the behind commits as:
  - worth adopting directly
  - worth partially/manual adoption
  - not currently worth adopting

## Code Entry Points

- Git history / diff surface:
  - `PhysTwin/.git`
- Likely affected PhysTwin paths:
  - `PhysTwin/pipeline_commnad.py`
  - `PhysTwin/script_process_data.py`
  - `PhysTwin/script_optimize.py`
  - `PhysTwin/script_train.py`
  - `PhysTwin/script_inference.py`
  - `PhysTwin/final_eval.py`
  - `PhysTwin/configs/`
- Relevant docs:
  - `docs/phystwin/README.md`
  - `tasks/spec/phystwin_upstream_sync_review.md`
  - `tasks/status/phystwin_upstream_sync_review.md`

## Canonical Commands

- Refresh upstream refs:
  - `git -C PhysTwin fetch upstream main`
- Confirm divergence:
  - `git -C PhysTwin rev-list --left-right --count main...upstream/main`
- List behind commits:
  - `git -C PhysTwin log --reverse --oneline main..upstream/main`
- Inspect file-level impact:
  - `git -C PhysTwin diff --stat main..upstream/main`

## Required Artifacts

- summary:
  - a ranked recommendation for which upstream commits or themes should be
    adopted
- diagnostic outputs if applicable:
  - commit list, affected file summary, and task status notes

## Success Criteria

- The exact behind-commit set is confirmed locally
- Each behind commit is categorized by adoption value for this workspace
- The recommendation explains why a change matters or does not matter
- The status page records the conclusion and next step

## Open Questions

- Are any upstream commits blocked by conflicting local changes on the same
  files?
- Should adoption happen via `cherry-pick`, selective patching, or by manually
  reimplementing the useful parts?

## Related Pages

- `tasks/spec/phystwin_upstream_sync_review.md`
- `plans/active/phystwin_upstream_sync_review.md`
- `tasks/implement/phystwin_upstream_sync_review.md`
- `tasks/status/phystwin_upstream_sync_review.md`
