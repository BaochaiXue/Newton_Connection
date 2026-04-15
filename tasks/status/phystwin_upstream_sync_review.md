# Status: PhysTwin Upstream Sync Review

## Current State

- Review complete
- Verified divergence after `git -C PhysTwin fetch upstream main`:
  - local `main` is `34` commits ahead of `upstream/main`
  - local `main` is `19` commits behind `upstream/main`
- The true `behind 19` set is README-only:
  - `README.md`
  - `assets/gradio_support.png`
  - `assets/RL_game.gif`
- No upstream-only changes were found in the current missing commit set for:
  - `pipeline_commnad.py`
  - `script_process_data.py`
  - `script_optimize.py`
  - `script_train.py`
  - `script_inference.py`
  - `final_eval.py`
  - `qqtt/`
- Recommendation:
  - do not perform a broad history sync just to absorb these `19` commits
  - if README parity matters, manually transplant the specific useful hunks
    instead of cherry-picking the full sequence

## Recommendation Summary

- Worth adopting manually:
  - `7bbb37d`
    - swaps README data/result download links from Google Drive to Hugging Face
    - this is the only clearly practical improvement for day-to-day users
      because the local README still points at the older Google Drive URLs
  - `37e3376`, `e787f2d`
    - add README guidance and image support for headless-server / Gradio usage
    - adopt only if this repo still wants to advertise remote interactive
      playground setup
  - `3c20c5f`, `6b65587`, `7343513`, `6288507`, `44f17cc`
    - public-facing README refresh: newer release notes, RL-game teaser, and
      related-project links
    - useful for external presentation, but not operationally important for the
      local Newton-bridge workflow
- Not worth adopting on their own:
  - `ab18627`, `bdcfc6e`, `cc3a0cb`, `da10a2f`, `87c852a`, `4dc2314`,
    `43ae01d`, `a38daa5`, `b1a8cb0`, `a899d2b`, `50aa54a`
  - these are incremental README wording/positioning edits whose value is too
    small to justify a sync action by themselves

## Why This Matters For The Workspace

- The current behind set does **not** hide upstream fixes to PhysTwin pipeline,
  training, inference, or simulation code
- This means the local branch is not missing a likely bug fix in the core
  PhysTwin execution path just because GitHub shows `19` commits behind
- If we decide to sync anything, it should be treated as README curation rather
  than code synchronization

## Last Completed Step

- Loaded the workspace harness and PhysTwin subtree rules
- Confirmed that `PhysTwin` is a nested git repository with local `main` and
  upstream remote configured
- Created the task/spec/plan/runbook/status chain for the sync review
- Fetched `upstream/main` and validated the divergence count with:
  - `git -C PhysTwin rev-list --left-right --count main...upstream/main`
- Inspected the missing commit list with:
  - `git -C PhysTwin log --reverse --decorate --date=short --pretty=format:'%h %ad %an %s' main..upstream/main`
- Confirmed the upstream-only file impact with:
  - `git -C PhysTwin diff --stat main...upstream/main`

## Next Step

- if desired, manually copy the Hugging Face download-link update into
  `PhysTwin/README.md`
- optionally port the Gradio / RL teaser / related-project README sections
  without changing local code or branch history

## Blocking Issues

- none

## Artifact Paths

- task page:
  - `docs/bridge/tasks/phystwin_upstream_sync_review.md`
