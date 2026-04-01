#!/usr/bin/env python3
from __future__ import annotations

import json
import sys


WATCH_TERMS = (
    "run_bunny_force_diag.sh",
    "run_realtime_profile.sh",
    "run_robot_rope_franka.sh",
    "run_native_robot_rope_drop_release.sh",
    "render_answer_pdf.py",
    "render_gif.sh",
    "prepare_video_review_bundle.py",
    "run_skeptical_video_audit.py",
    "sync_results_registry.py",
    "render_bunny_penetration_collision_board",
    "validate_experiment_artifacts.py",
    "validate_bridge_video_qc.py",
    "validate_bunny_force_visualization.py",
    "validate_robot_deformable_demo.py",
    "validate_native_robot_rope_drop_release_video.py",
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
                "record artifact paths, update task/status docs, and refresh results_meta when authoritative meaning changed."
            ),
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    "If this command produced deliverables, run scripts/validate_experiment_artifacts.py when relevant "
                    "and write the result into tasks/status and docs/bridge/current_status.md. "
                    "For meeting-facing video tasks, prepare a skeptical review bundle and do not treat automatic QC as final acceptance."
                ),
            },
        }
        json.dump(out, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
