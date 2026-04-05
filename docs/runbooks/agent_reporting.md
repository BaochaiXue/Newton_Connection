> status: active
> canonical_replacement: none
> owner_surface: `agent_reporting`
> last_reviewed: `2026-04-05`
> review_interval: `30d`
> update_rule: `Update when user-facing report expectations or hook enforcement changes.`
> notes: Canonical runbook for user-facing Codex reporting style in this repo.

# Agent Reporting Runbook

Use this runbook for progress updates and final closeout messages.

## Core Rule

The report is not a diary of what the agent read, planned, or orchestrated.
The report is a short engineering update about outcomes.

## Required Focus

Default order:

1. what changed
2. what problem was solved, reduced, or clarified
3. what findings or conclusions now hold
4. which artifacts are worth opening:
   - `GIF`
   - `MP4`
   - `PPTX`
   - `PDF`
   - result bundle path
5. the next step

## Do Not Emphasize

Do not spend user-facing report space on:

- files read
- tools or skills used
- subagent orchestration
- prompt strategy
- task-chain bookkeeping
- inventory/lint/registry chores
- page-purpose narration

These may appear only when the user explicitly asks for process detail or when
they are themselves the change being made.

## Good Reporting Shapes

### Short task

- one short paragraph for change + solved problem + conclusion
- one short artifact line if a `GIF`/`MP4`/deck exists
- one short next-step line if follow-up remains

### Larger task

Use at most these sections:

- `Changed`
- `Solved`
- `Findings`
- `Artifacts`
- `Next step`

Each section should stay short and concrete.

## Artifact Rule

If the task produced meeting-facing visuals, name the best `GIF`/`MP4` to open.

If no new visual artifact exists, say so plainly:

- `No new GIF/MP4 in this pass.`

## Validation Rule

Validation may be reported, but only after the outcome.

Good:

- `Updated the slide builder so source-proof snippets use the real solver path. This removes the misleading example-based citation.`
- `Conclusion: the performance gap is still real, but the root-cause claim remains weaker than the throughput claim.`
- `GIF to inspect: .../rope_release_anchor.gif`
- `Validation: build_meeting_20260401.py ran successfully.`

Bad:

- `I first read AGENTS.md and then inspected several files.`
- `I used two skills and three subagents.`
- `I updated the task chain, status doc, and inventory before continuing.`
- `This page shows what the page is doing.`
