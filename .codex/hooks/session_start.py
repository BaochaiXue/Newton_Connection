#!/usr/bin/env python3
from __future__ import annotations

import json
import sys


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    additional = (
        "Load the repo harness before editing: read AGENTS.md, docs/README.md, "
        "TODO.md, then the relevant docs/bridge/tasks page. Use scripts/ wrappers "
        "when they exist. Update task/status docs for non-trivial work. For high-risk "
        "or multi-session tasks, use tasks/contracts and tasks/handoffs selectively "
        "instead of leaving the workflow implicit. If a run becomes authoritative, "
        "update results_meta before claiming completion. If you rename, deprecate, "
        "archive, or supersede a Markdown surface, update docs/generated/md_inventory.*, "
        "md_staleness_report.md, task_surface_matrix.md, the deprecation ledger, and run scripts/lint_harness_consistency.py before ending. "
        "Historical bridge task pages belong in docs/archive/tasks/, not docs/bridge/tasks/. "
        "Treat tracked `results/*` pointer docs and `Newton/phystwin_bridge/STATUS.md` as "
        "secondary surfaces only; if they change, keep them aligned with results_meta and the inventory. "
        "When reporting back to the user, lead with what changed, what problem was solved, "
        "what conclusion now holds, what GIF/video/artifact is worth checking, and the next step. "
        "Do not foreground pass labels, tool/subagent usage, deleted-file inventories, or internal workflow narration unless the user explicitly asks."
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": additional,
        }
    }
    json.dump(out, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
