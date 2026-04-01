# Harness Audit

> status: generated
> canonical_replacement: `python scripts/lint_harness_consistency.py` plus the repo control-plane files it checks
> owner_surface: `harness_engineering_upgrade`
> last_reviewed: `2026-04-01`
> notes: Machine-maintained audit ledger. Update this file only when the harness audit itself changes.

Updated: 2026-04-01

This audit records the harness issues that materially affected long-running
Codex work in this repo and the exact remediation chosen in the current
upgrade.

For each issue, this file records:

- severity
- evidence
- affected paths
- why it hurt agents
- exact remediation
- current status

## Scope

Reviewed surfaces:

- root and subtree `AGENTS.md`
- `docs/`, `plans/`, `tasks/`
- `.codex/config.toml`
- `.codex/hooks.json`
- `.codex/hooks/`
- `.agents/skills/`
- validators and wrappers under `scripts/`
- local authoritative result surfaces under `results/` and
  `Newton/phystwin_bridge/results/`
- committed results metadata under `results_meta/`

## Findings

### 1. Active Task Chains Drifted Or Were Missing

- Severity: `critical`
- Evidence:
  - active tasks are indexed in `docs/bridge/tasks/README.md`
  - long-running work depends on `task page -> spec -> plan -> implement -> status`
  - prior audits found missing chains and slug mismatches, especially on the
    self-collision family
- Affected paths:
  - `docs/bridge/tasks/README.md`
  - `tasks/spec/`
  - `plans/active/`
  - `tasks/implement/`
  - `tasks/status/`
- Why it hurt agents:
  - agents could not tell whether a task was truly active or just partially
    scaffolded
  - planning and handoff state drifted into chat memory
- Exact remediation:
  - backfill missing task-chain artifacts for active tasks
  - normalize the active self-collision slug to `self_collision_transfer`
  - add `docs/bridge/tasks/AGENTS.md` and `tasks/AGENTS.md` guidance
  - add `scripts/lint_harness_consistency.py` to fail on missing chain links
- Current status: `resolved for the current active task set`

### 2. Root-Level Shadow Docs Competed With Task-Scoped Truth

- Severity: `high`
- Evidence:
  - root singleton docs such as `Plan.md`, `Status.md`, `Prompt.md`, and
    `DecisionLog.md` previously acted like one-task control-plane files
  - they did not scale to multiple simultaneous workstreams
- Affected paths:
  - root control-plane docs
  - `AGENTS.md`
  - `docs/generated/harness_deprecations.md`
- Why it hurt agents:
  - multiple places could sound authoritative at once
  - future agents could update the wrong surface
- Exact remediation:
  - retire the root singleton docs
  - route future work through task-scoped surfaces
  - record the deprecation in `docs/generated/harness_deprecations.md`
- Current status: `resolved`

### 3. Authoritative Meaning Lived Only In Ignored Local Result Bundles

- Severity: `critical`
- Evidence:
  - `.gitignore` ignores `results/`
  - authoritative result meaning was previously scattered across local-only
    files such as `BEST_RUN.md`, `LATEST_SUCCESS.txt`, and bundle-local
    `INDEX.md`
- Affected paths:
  - `.gitignore`
  - `results/`
  - `Newton/phystwin_bridge/results/`
  - task status pages that pointed into ignored results roots
- Why it hurt agents:
  - a fresh agent reading committed repo state alone could not reconstruct the
    current authoritative run or why it passed
- Exact remediation:
  - create committed metadata mirrors under `results_meta/`
  - add per-task registry JSON entries
  - generate `results_meta/INDEX.md` and `results_meta/LATEST.md`
  - treat local bundle pointers as secondary/local-only surfaces
- Current status: `resolved for major task families; future promotions must keep the registry updated`

### 4. Authoritative Pointers Used Inconsistent Formats And Machine-Local Paths

- Severity: `high`
- Evidence:
  - bundle-local pointers used a mix of `BEST_RUN.md`, `LATEST_SUCCESS.txt`,
    `LATEST_ATTEMPT.txt`, and `INDEX.md`
  - some tracked docs and scripts embedded machine-local absolute paths
- Affected paths:
  - `tasks/implement/robot_deformable_demo.md`
  - `tasks/implement/native_robot_rope_drop_release.md`
  - `run_phystwin_newton_pipeline.sh`
  - local bundle pointer files under `results/`
- Why it hurt agents:
  - path portability was poor
  - pointer parsing was inconsistent
- Exact remediation:
  - remove machine-local paths from durable docs and scripts where practical
  - move committed authoritative meaning to `results_meta/`
  - lint durable docs for machine-local absolute-path patterns
- Current status: `partially resolved; durable docs and the main shell pipeline were fixed, but local ignored bundle files may still contain absolute paths`

### 5. Video Acceptance Was Optimistic And Generator-Coupled

- Severity: `critical`
- Evidence:
  - `docs/evals/` previously exposed only a generic evaluator rubric
  - existing validators mostly stopped at automatic QC or bundle-specific PASS
    files
- Affected paths:
  - `docs/evals/README.md`
  - `docs/evals/evaluator_rubric.md`
  - `scripts/validate_bridge_video_qc.py`
  - `scripts/validate_bunny_force_visualization.py`
  - `scripts/validate_robot_deformable_demo.py`
  - `scripts/validate_native_robot_rope_drop_release_video.py`
- Why it hurt agents:
  - automatic PASS could be mistaken for evidentiary acceptance
  - there was no fail-closed skeptical reviewer surface
- Exact remediation:
  - add `docs/evals/video_acceptance_rubric.md`
  - add `docs/evals/video_evaluator_prompt.md`
  - add `scripts/prepare_video_review_bundle.py`
  - add `scripts/run_skeptical_video_audit.py`
  - require a separate skeptical verdict to defend final acceptance
- Current status: `resolved at the harness layer; existing generators can now feed a fail-closed skeptical audit`

### 6. Planner / Builder / Evaluator / Handoff Artifacts Were Not First-Class

- Severity: `high`
- Evidence:
  - long-running tasks needed more than spec/plan/status
  - milestone acceptance and session-resume state were too easy to leave in chat
- Affected paths:
  - `tasks/contracts/`
  - `tasks/handoffs/`
  - `.agents/skills/`
- Why it hurt agents:
  - agents re-did work
  - fresh sessions had weak resume state
- Exact remediation:
  - maintain `tasks/contracts/` and `tasks/handoffs/`
  - add repo-local skills:
    - `planner-spec`
    - `milestone-contract`
    - `handoff-resume`
    - `skeptical-video-audit`
    - `doc-gardener`
- Current status: `resolved`

### 7. Hooks Mostly Reminded But Did Not Enforce Enough

- Severity: `high`
- Evidence:
  - stop hooks previously looked only for generic “done without validation”
  - artifact-producing commands were not tied to results metadata or skeptical
    video review updates
- Affected paths:
  - `.codex/hooks/session_start.py`
  - `.codex/hooks/post_tool_use_review.py`
  - `.codex/hooks/stop_continue.py`
- Why it hurt agents:
  - completion claims could still land without the strongest evidence surfaces
  - artifact-producing workflows did not mechanically remind agents to update
    the results registry
- Exact remediation:
  - teach session start about contracts/handoffs/results registry
  - make post-tool review mention results metadata and skeptical video audit
  - make stop-hook checks stricter for video and authoritative/promotion claims
- Current status: `resolved for the local hook layer`

### 8. There Was No Mechanical Harness Consistency Lint

- Severity: `critical`
- Evidence:
  - previous drift was discovered only by manual audit
- Affected paths:
  - `scripts/`
  - control-plane docs and task/status surfaces
- Why it hurt agents:
  - the same ambiguities reappeared because nothing checked them mechanically
- Exact remediation:
  - add `scripts/lint_harness_consistency.py`
  - check:
    - active task chain completeness
    - deprecated-surface markers
    - required results registry entries
    - absolute machine-local paths in durable docs
    - local pointer mismatch against registry run ids
- Current status: `resolved`

### 9. Local AGENTS Layering Was Too Coarse

- Severity: `medium`
- Evidence:
  - recurring local rules for generated docs, demos, and results metadata were
    not encoded in the relevant subtree
- Affected paths:
  - `docs/generated/`
  - `results_meta/`
  - `Newton/phystwin_bridge/demos/`
- Why it hurt agents:
  - local conventions had to be reconstructed from memory
- Exact remediation:
  - add or improve local `AGENTS.md` in the high-drift subtrees
- Current status: `resolved`

### 10. Historical / Deprecated Surfaces Were Not Centralized

- Severity: `medium`
- Evidence:
  - slug aliases such as `self_collision_transfer_decision` and historical task
    families such as `final_self_collision_campaign` were easy to rediscover as
    if they were still primary
- Affected paths:
  - self-collision task scaffolds
  - `docs/generated/harness_deprecations.md`
- Why it hurt agents:
  - agents could keep two competing truth surfaces alive
- Exact remediation:
  - add a central deprecation ledger
  - mark deprecated/historical files in place with migration notes
- Current status: `resolved`

## Remaining Tradeoffs

- Some ignored local result-bundle files still use machine-local or stale
  wording; they are now secondary surfaces, but local cleanup can continue.
- The skeptical video layer is fail-closed by design, so it requires an
  explicit separate reviewer payload to produce `PASS`.
- `results_meta/` is now the committed registry, but local bundle pointers are
  still useful convenience surfaces and must be kept aligned by workflow.
