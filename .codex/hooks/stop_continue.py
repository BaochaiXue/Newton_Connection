#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys


DONE_WORDS = re.compile(r"\b(done|completed|finished|resolved)\b", re.IGNORECASE)
VALIDATION_WORDS = re.compile(r"\b(validate|validated|test|tested|lint|artifact|status|docs)\b", re.IGNORECASE)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if bool(payload.get("stop_hook_active")):
        return 0

    msg = str(payload.get("last_assistant_message") or "")
    if DONE_WORDS.search(msg) and not VALIDATION_WORDS.search(msg):
        out = {
            "decision": "block",
            "reason": (
                "Run one more pass: verify outputs, mention validation status explicitly, "
                "and update the relevant task/status documents before ending the turn."
            ),
        }
        json.dump(out, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
