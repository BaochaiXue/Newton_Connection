#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys


DENY_PATTERNS: list[tuple[str, str]] = [
    (
        r"^\s*(?:(?:python|python3|bash|sh)\b.*\bsend_pdf_via_yahoo\.py\b|(?:\./|scripts/)?send_pdf_via_yahoo\.py\b)",
        "External send is release-gated; do not send email without explicit human approval.",
    ),
    (r"\bgit\s+push\s+--force\b", "Force-push is blocked by repo policy."),
    (r"\brm\s+-rf\b", "Recursive deletion is blocked by repo policy."),
    (
        r"\brm\b.*\b(formal_slide|result_for_slides)\b",
        "Do not bulk-delete generated deliverables without an explicit cleanup task.",
    ),
    (
        r"\bfind\b.*\b(formal_slide|result_for_slides)\b.*-delete\b",
        "Do not bulk-delete generated deliverables without an explicit cleanup task.",
    ),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    command = str(payload.get("tool_input", {}).get("command", ""))
    for pattern, reason in DENY_PATTERNS:
        if re.search(pattern, command):
            out = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                },
                "systemMessage": reason,
            }
            json.dump(out, sys.stdout)
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
