#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys


WATCH_TERMS = (
    "run_bunny_force_diag.sh",
    "run_realtime_profile.sh",
    "render_answer_pdf.py",
    "render_gif.sh",
    "prepare_video_review_bundle.py",
    "run_skeptical_video_audit.py",
    "sync_results_registry.py",
    "generate_md_inventory.py",
    "generate_md_truth_inventory.py",
    "tasks/contracts/",
    "tasks/handoffs/",
    "docs/archive/tasks/",
    "docs/bridge/tasks/",
    "docs/bridge/current_status.md",
    "docs/bridge/open_questions.md",
    "results_meta/schema.md",
    "render_bunny_penetration_collision_board",
    "validate_experiment_artifacts.py",
    "validate_bridge_video_qc.py",
    "validate_bunny_force_visualization.py",
    "formal_slide",
    "result_for_slides",
    "git mv ",
    " mv ",
    "results_meta/",
    "plans/completed/",
)

READ_ONLY_PATTERNS = (
    re.compile(r"^\s*(cat|head|tail|sed\s+-n|rg|grep|ls|stat|wc|awk)\b"),
    re.compile(r"^\s*git\s+(status|diff|show|ls-files|grep)\b"),
    re.compile(r"^\s*find\b(?!.*-delete)"),
    re.compile(r"^\s*python\s+-m\s+py_compile\b"),
)

GUARDED_ACTION_PATTERNS = (
    re.compile(r"\bgit\s+(mv|rm|add|commit|push|update-index)\b"),
    re.compile(r"(^|[;&|]\s*)mv\b"),
    re.compile(r"(^|[;&|]\s*)cp\b"),
    re.compile(r"(^|[;&|]\s*)rm\b"),
    re.compile(r"(^|[;&|]\s*)mkdir\b"),
    re.compile(r"(^|[;&|]\s*)touch\b"),
    re.compile(r"\bfind\b.*-delete\b"),
    re.compile(
        r"\b(?:python|python3)\b.*\b("
        r"sync_results_registry|generate_md_inventory|generate_md_truth_inventory|"
        r"validate_experiment_artifacts|validate_bridge_video_qc|validate_bunny_force_visualization|"
        r"prepare_video_review_bundle|run_skeptical_video_audit|render_answer_pdf"
        r")\.py\b"
    ),
    re.compile(r"\b(?:bash|sh)\b.*\b(run_bunny_force_diag|run_realtime_profile|render_gif)\.sh\b"),
)


def _is_read_only(command: str) -> bool:
    stripped = command.strip()
    if any(pattern.search(stripped) for pattern in GUARDED_ACTION_PATTERNS):
        return False
    return any(pattern.search(stripped) for pattern in READ_ONLY_PATTERNS)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    command = str(payload.get("tool_input", {}).get("command", ""))
    if any(term in command for term in WATCH_TERMS) and not _is_read_only(command):
        out = {
            "decision": "block",
            "reason": (
                "This command likely changed or validated artifacts. Before moving on, review the output, "
                "record artifact paths, update task/status docs, and refresh results_meta when authoritative meaning changed."
            ),
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                "If this command produced deliverables, run scripts/validate_experiment_artifacts.py when relevant "
                "and write the result into tasks/status and docs/bridge/current_status.md. "
                "For meeting-facing video tasks, prepare a skeptical review bundle and do not treat automatic QC as final acceptance."
                " If this command renamed or deprecated Markdown/control-plane surfaces, refresh docs/generated/md_inventory.*, "
                "docs/generated/md_staleness_report.md, docs/generated/task_surface_matrix.md, "
                "docs/generated/md_deprecation_matrix.md, and rerun scripts/lint_harness_consistency.py. "
                " Historical bridge task pages should move to docs/archive/tasks/, not remain in docs/bridge/tasks/. "
                " If the task is in the required workflow class, make sure its contract and handoff exist before you move on. "
                " If you added or changed a contract/handoff, regenerate task_surface_matrix.md so workflow usage stays auditable. "
                "If you touched tracked local-only pointers under results/ or subtree status stubs, keep them explicitly local-only "
                "and aligned with results_meta before you move on. When you summarize the work, foreground the user-facing outcome "
                "(what changed, what problem was solved, what conclusion now holds, what artifact to inspect, and the next step) "
                "instead of hook/process bookkeeping."
            ),
        },
    }
        json.dump(out, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
