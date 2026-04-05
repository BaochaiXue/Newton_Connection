#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys


DONE_WORDS = re.compile(r"\b(done|completed|finished|resolved)\b", re.IGNORECASE)
VALIDATION_WORDS = re.compile(r"\b(validate|validated|test|tested|lint|artifact|status|docs)\b", re.IGNORECASE)
VERDICT_WORDS = re.compile(r"\b(verdict|pass|passed|fail|failed)\b", re.IGNORECASE)
VIDEO_TASK_WORDS = re.compile(r"\b(video|mp4|gif|render|visual|demo|slide)\b", re.IGNORECASE)
SKEPTICAL_WORDS = re.compile(r"\b(skeptical|video audit|review bundle|contact sheet|event sheet)\b", re.IGNORECASE)
REGISTRY_WORDS = re.compile(r"\b(results_meta|results registry|LATEST\.md|INDEX\.md)\b", re.IGNORECASE)
MARKDOWN_CHANGE_WORDS = re.compile(r"\b(deprecated|deprecate|archived|archive|historical|renamed|rename|markdown cleanup|truthfulness cleanup)\b", re.IGNORECASE)
INVENTORY_WORDS = re.compile(r"\b(md_inventory|md_cleanup_report|md_staleness_report|task_surface_matrix|harness_deprecations|doc_gardening|generate_md_inventory)\b", re.IGNORECASE)
META_REPORT_PATTERNS = (
    re.compile(r"\bbefore vs after\b", re.IGNORECASE),
    re.compile(r"\bfiles deleted\b", re.IGNORECASE),
    re.compile(r"\bfiles archived\b", re.IGNORECASE),
    re.compile(r"\bfiles converted to deprecated stubs\b", re.IGNORECASE),
    re.compile(r"\bfiles moved out of active execution directories\b", re.IGNORECASE),
    re.compile(r"\bfiles reformatted\b", re.IGNORECASE),
    re.compile(r"\bvalidation commands run\b", re.IGNORECASE),
    re.compile(r"\bexact validation commands run\b", re.IGNORECASE),
    re.compile(r"\bcanonical public entrypoint\b", re.IGNORECASE),
    re.compile(r"\bupdated markdown maintenance policy\b", re.IGNORECASE),
    re.compile(r"\bcurrent pass type\b", re.IGNORECASE),
    re.compile(r"\bcontinued the same maintenance line\b", re.IGNORECASE),
    re.compile(r"\bstructural cleanup\b", re.IGNORECASE),
)
OUTCOME_REPORT_PATTERNS = (
    re.compile(r"\bwhat changed\b", re.IGNORECASE),
    re.compile(r"\b(problem|issue) (solved|fixed|clarified)\b", re.IGNORECASE),
    re.compile(r"\b(findings?|conclusions?)\b", re.IGNORECASE),
    re.compile(r"\bnext step\b", re.IGNORECASE),
    re.compile(r"\b(gif|video|artifact)s?\b", re.IGNORECASE),
)
PROCESS_CHATTER_PATTERNS = (
    re.compile(r"\bi read\b", re.IGNORECASE),
    re.compile(r"\bi started by\b", re.IGNORECASE),
    re.compile(r"\bi used\b", re.IGNORECASE),
    re.compile(r"\bsubagent\b", re.IGNORECASE),
    re.compile(r"\bskill\b", re.IGNORECASE),
    re.compile(r"\bfile-reading order\b", re.IGNORECASE),
)


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
    if DONE_WORDS.search(msg) and VIDEO_TASK_WORDS.search(msg) and not (VERDICT_WORDS.search(msg) and SKEPTICAL_WORDS.search(msg)):
        out = {
            "decision": "block",
            "reason": (
                "Video/deliverable completion claims must mention a skeptical video audit or equivalent conservative verdict evidence, "
                "not only optimistic automatic QC."
            ),
        }
        json.dump(out, sys.stdout)
        return 0
    if DONE_WORDS.search(msg) and ("authoritative" in msg.lower() or "promoted" in msg.lower()) and not REGISTRY_WORDS.search(msg):
        out = {
            "decision": "block",
            "reason": (
                "If you claim something is authoritative or promoted, mention the results registry update explicitly before ending the turn."
            ),
        }
        json.dump(out, sys.stdout)
        return 0
    if DONE_WORDS.search(msg) and MARKDOWN_CHANGE_WORDS.search(msg) and not (INVENTORY_WORDS.search(msg) and VALIDATION_WORDS.search(msg)):
        out = {
            "decision": "block",
            "reason": (
                "Markdown cleanup / deprecation / archive claims must mention the inventory refresh and lint outcome explicitly before ending the turn."
            ),
        }
        json.dump(out, sys.stdout)
        return 0

    if DONE_WORDS.search(msg) and any(pattern.search(msg) for pattern in PROCESS_CHATTER_PATTERNS):
        out = {
            "decision": "block",
            "reason": (
                "Completion reports should not lead with process chatter such as skill usage, subagent usage, or file-reading order. "
                "Reframe the message around changes, solved problem, conclusion, artifact to inspect, and next step."
            ),
        }
        json.dump(out, sys.stdout)
        return 0

    meta_hits = sum(1 for pattern in META_REPORT_PATTERNS if pattern.search(msg))
    outcome_hits = sum(1 for pattern in OUTCOME_REPORT_PATTERNS if pattern.search(msg))
    if meta_hits >= 2 and outcome_hits < 2:
        out = {
            "decision": "block",
            "reason": (
                "User-facing reports must be outcome-first. Summarize what changed, what problem was solved, "
                "what conclusion now holds, what artifact is worth checking, and the next step. "
                "Do not lead with pass labels or file-inventory bookkeeping."
            ),
        }
        json.dump(out, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
