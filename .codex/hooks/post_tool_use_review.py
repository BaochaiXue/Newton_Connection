#!/usr/bin/env python3
from __future__ import annotations

import json
import sys


WATCH_TERMS = (
    "run_bunny_force_diag.sh",
    "run_realtime_profile.sh",
    "run_robot_rope_franka.sh",
    "render_answer_pdf.py",
    "render_gif.sh",
    "validate_experiment_artifacts.py",
    "formal_slide",
    "result_for_slides",
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    command = str(payload.get("tool_input", {}).get("command", ""))
    if any(term in command for term in WATCH_TERMS):
        out = {
            "decision": "block",
            "reason": (
                "This command likely changed or validated artifacts. Before moving on, review the output, "
                "record artifact paths, and update the relevant task/status docs."
            ),
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    "If this command produced deliverables, run scripts/validate_experiment_artifacts.py when relevant "
                    "and write the result into tasks/status and docs/bridge/current_status.md."
                ),
            },
        }
        json.dump(out, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
