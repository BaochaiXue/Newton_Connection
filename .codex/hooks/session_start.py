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
        "when they exist. Update task/status docs for non-trivial work."
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
