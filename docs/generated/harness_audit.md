# Harness Audit

Updated: 2026-04-01

This audit records the repo-harness issues that materially hurt long-running
Codex work. It is intentionally implementation-oriented: each issue includes
severity, evidence, why it hurts agents, and the exact remediation.

## Audit Scope

Reviewed surfaces:

- root + subtree `AGENTS.md`
- `docs/`, `plans/`, `tasks/`
- `.codex/config.toml`
- `.codex/hooks.json`
- `.codex/hooks/`
- `.agents/skills/`
- current validators under `scripts/`
- local authoritative-result surfaces under `results/` and
  `Newton/phystwin_bridge/results/`

## Findings

### 1. Active task set does not have a complete authoritative chain

- Severity: `critical`
- Evidence:
  - `docs/bridge/tasks/README.md` lists 10 active tasks.
  - The following active tasks were missing one or more of `spec -> plan -> implement -> status`:
    - `slide_deck_overhaul`
    - `video_presentation_quality`
    - `interactive_playground_profiling`
    - `self_collision_transfer`
    - `data_collection_protocol`
    - `fast_foundation_stereo`
- Affected paths:
  - `docs/bridge/tasks/README.md`
  - `tasks/spec/`
  - `plans/active/`
  - `tasks/implement/`
  - `tasks/status/`
- Why it hurts agents:
  - agents cannot tell whether a task is active-but-lightweight or simply missing its execution scaffolding
  - planning and handoff drift into chat because there is no durable chain to update
- Exact remediation:
  - create missing `spec`, `plan`, `implement`, and `status` files for every active task
  - add a harness lint that fails if an active task is missing any link in the chain

### 2. Authoritative meaning lives in ignored local result bundles

- Severity: `critical`
- Evidence:
  - root `.gitignore` ignores `results/` entirely
  - `git ls-files results 'Newton/phystwin_bridge/results/*'` returns nothing
  - major local result bundles expose important truth only in ignored paths:
    - `results/robot_deformable_demo/`
    - `results/native_robot_rope_drop_release/`
    - `results/bunny_force_visualization/`
    - `results/rope_perf_apples_to_apples/`
- Affected paths:
  - `.gitignore`
  - `results/`
  - task status pages that point into ignored results roots
- Why it hurts agents:
  - a fresh agent reading only committed repo state cannot reconstruct why one run is authoritative and another is rejected
  - ignored result-bundle metadata can silently drift from tracked docs
- Exact remediation:
  - create a committed metadata mirror outside ignored local result roots
  - define required per-run metadata fields
  - add a sync workflow and lint that verifies authoritative local runs have committed mirrors

### 3. Conflicting authoritative pointers already exist

- Severity: `high`
- Evidence:
  - `results/bunny_force_visualization/README.md` still says the current validated run is `20260330_183245_final_matrix`
  - `docs/bridge/current_status.md` and the bunny task docs point to
    `20260331_231500_fullprocess_sync_matrix_manual_v2`
  - several local result-bundle files use absolute canonical paths while task status pages use repo-relative paths
- Affected paths:
  - `results/bunny_force_visualization/README.md`
  - `docs/bridge/current_status.md`
  - `docs/bridge/tasks/bunny_penetration_force_diagnostic.md`
  - `tasks/status/bunny_penetration_force_diagnostic.md`
- Why it hurts agents:
  - agents can pick different “best runs” depending on which surface they read first
  - stale bundle-local metadata creates false confidence because it looks authoritative
- Exact remediation:
  - move repo-authoritative meaning into a single committed results registry
  - keep local bundle pointers as convenience surfaces only
  - lint bundle/task pointer mismatches against the registry

### 4. Portable-path discipline is inconsistent

- Severity: `high`
- Evidence:
  - durable docs still contain machine-specific paths, for example:
    - `tasks/implement/robot_deformable_demo.md`
    - `tasks/implement/native_robot_rope_drop_release.md`
  - local campaign readmes under generated/result areas contain many `/home/xinjie/...` paths
- Affected paths:
  - `tasks/implement/robot_deformable_demo.md`
  - `tasks/implement/native_robot_rope_drop_release.md`
  - several generated artifact readmes under `formal_slide/` and local result roots
- Why it hurts agents:
  - local absolute paths reduce portability and make repo docs less reusable across machines or fresh worktrees
  - agents cannot easily tell which docs are durable versus machine-local notes
- Exact remediation:
  - remove machine-local paths from durable docs/status pages
  - keep absolute paths only inside local run notes or generated outputs
  - lint durable docs for absolute-path patterns

### 5. Video evaluation is optimistic and generator-coupled

- Severity: `critical`
- Evidence:
  - `docs/evals/` contains only a generic evaluator rubric; there is no skeptical video acceptance rubric or evaluator prompt
  - video validators exist, but they mostly stop at automatic gates plus a written verdict file
  - current validators are implemented in the same repo layer as the generators they validate
- Affected paths:
  - `docs/evals/README.md`
  - `docs/evals/evaluator_rubric.md`
  - `scripts/validate_bridge_video_qc.py`
  - `scripts/validate_bunny_force_visualization.py`
  - `scripts/validate_robot_deformable_video.py`
  - `scripts/validate_native_robot_rope_drop_release_video.py`
- Why it hurts agents:
  - automatic PASS can become a false positive when the actual claim is visually ambiguous
  - there is no durable evaluator persona that fails closed on weak process visibility or misleading camera/view motion
- Exact remediation:
  - add a skeptical multimodal video acceptance rubric and evaluator prompt
  - separate generator and evaluator roles explicitly
  - add a script path that prepares evenly sampled frames, consecutive windows, and a structured audit bundle for multimodal review

### 6. Hooks remind, but they do not enforce harness invariants strongly enough

- Severity: `high`
- Evidence:
  - `session_start.py` only injects general context
  - `post_tool_use_review.py` blocks after some artifact-producing commands, but it does not require results-registry or skeptical-video evidence updates
  - `stop_continue.py` only checks for generic validation words, not explicit verdict or lint evidence
- Affected paths:
  - `.codex/hooks/session_start.py`
  - `.codex/hooks/post_tool_use_review.py`
  - `.codex/hooks/stop_continue.py`
- Why it hurts agents:
  - agents can still claim completion after optimistic validation or without durable metadata updates
  - artifact-producing work is not coupled to handoff/registry updates
- Exact remediation:
  - strengthen stop-hook completion checks to require explicit pass/verdict/lint language
  - expand artifact-producing watches to include results-registry updates and skeptical video audit expectations
  - add a dedicated harness lint and mention it in completion enforcement

### 7. Contracts and handoffs are missing as first-class artifacts

- Severity: `high`
- Evidence:
  - there is no `tasks/contracts/`
  - there is no `tasks/handoffs/`
  - no repo-local templates exist for milestone contract or fresh-session handoff
- Affected paths:
  - `tasks/`
- Why it hurts agents:
  - long-running tasks accumulate informal next-step state in status logs or chat
  - a fresh agent cannot quickly see what not to redo, what evidence is still missing, or whether reset is recommended
- Exact remediation:
  - add `tasks/contracts/README.md` and `_contract_template.md`
  - add `tasks/handoffs/README.md` and `_handoff_template.md`
  - add repo-local skills for planner-spec, milestone-contract, and handoff-resume

### 8. Local AGENTS layering is too coarse for task/results-heavy work

- Severity: `medium`
- Evidence:
  - local `AGENTS.md` files currently exist only for root, `docs/`, `scripts/`, `PhysTwin/`, and `Newton/phystwin_bridge/`
  - there is no task-local guidance in:
    - `docs/bridge/tasks/`
    - `tasks/`
    - any committed results-metadata subtree
    - `Newton/phystwin_bridge/demos/`
- Affected paths:
  - `docs/bridge/tasks/`
  - `tasks/`
  - `Newton/phystwin_bridge/demos/`
  - future results registry subtree
- Why it hurts agents:
  - recurring local rules remain implicit
  - agents need to reconstruct the difference between stable task pages, execution artifacts, and local-only run notes
- Exact remediation:
  - add short local `AGENTS.md` files for the above subtrees
  - keep them specific: canonical chain, path discipline, deprecation behavior, and evaluation expectations

### 9. Results governance is fragmented by bundle-specific conventions

- Severity: `medium`
- Evidence:
  - `results/bunny_force_visualization/` uses `INDEX.md` plus pointer files
  - `results/robot_deformable_demo/` uses `index.csv` plus `BEST_RUN.md`
  - `results/native_robot_rope_drop_release/` uses `index.csv` plus pointer files
  - `results/rope_perf_apples_to_apples/` uses a methodology-style README plus `BEST_EVIDENCE.md`
- Affected paths:
  - `results/*`
  - `docs/bridge/experiment_index.md`
- Why it hurts agents:
  - bundle-specific local conventions are manageable for humans but too inconsistent for durable machine-assisted reasoning
  - registry sync and lint become harder when there is no normalized metadata shape
- Exact remediation:
  - add one committed results-registry schema that can mirror these bundle styles without rewriting them in place
  - define a minimal normalized field set per authoritative run/bundle

### 10. Harness drift is not checked mechanically

- Severity: `critical`
- Evidence:
  - there is no `scripts/lint_harness_consistency.py`
  - duplicate truth surfaces, missing chain links, and absolute paths were discovered via ad hoc audit rather than routine checks
- Affected paths:
  - `scripts/`
  - all control-plane docs
- Why it hurts agents:
  - every new session must rediscover the same ambiguity manually
  - fixes remain social conventions instead of encoded repo behavior
- Exact remediation:
  - add a dedicated harness lint that checks:
    - active task chain completeness
    - duplicate/near-duplicate slugs
    - absolute paths in durable docs
    - results-registry coverage for authoritative runs
    - deprecated-surface hygiene

## Implementation Priorities

1. Add the committed results registry and harness lint.
2. Add skeptical video evaluator docs/prompts and a review-bundle prep script.
3. Add contracts/handoffs and local `AGENTS.md` layering.
4. Backfill missing task chains for every active task.
5. Strengthen hooks to require explicit verdict/lint language on completion.
