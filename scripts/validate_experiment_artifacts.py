#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def _find_any(root: Path, patterns: list[str]) -> list[Path]:
    found: list[Path] = []
    for pattern in patterns:
        found.extend(sorted(root.glob(pattern)))
    # preserve order while deduplicating
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in found:
        if path not in seen:
            seen.add(path)
            unique.append(path)
    return unique


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate a bridge experiment directory artifact contract.")
    p.add_argument("experiment_dir", type=Path)
    p.add_argument("--require-video", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--require-gif", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--require-diagnostic", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument(
        "--require-qa",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Require bunny-force QA outputs: qa/report.json, qa/verdict.md, and at least one contact sheet.",
    )
    p.add_argument(
        "--summary-field",
        action="append",
        default=[],
        help="Require a field to exist in the first summary.json found. Repeatable.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = args.experiment_dir.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"[validate_experiment_artifacts] missing directory: {root}", file=sys.stderr)
        return 2

    checks: list[tuple[str, bool, str]] = []

    readmes = _find_any(root, ["README.md", "**/README.md"])
    checks.append(("README", bool(readmes), "README.md"))

    commands = _find_any(root, ["command.sh", "command.txt", "**/command.sh", "**/command.txt"])
    checks.append(("command", bool(commands), "command.sh or command.txt"))

    summaries = _find_any(root, ["summary.json", "*_summary.json", "**/summary.json", "**/*_summary.json"])
    checks.append(("summary", bool(summaries), "summary.json"))

    scenes = _find_any(root, ["scene.npz", "*_scene.npz", "**/scene.npz", "**/*_scene.npz"])
    checks.append(("scene", bool(scenes), "scene.npz"))

    videos = _find_any(root, ["*.mp4", "**/*.mp4"])
    gifs = _find_any(root, ["*.gif", "**/*.gif"])
    diagnostics = _find_any(
        root,
        [
            "force_diagnostic/force_diag_trigger_substep.npz",
            "force_diagnostic/force_diag_trigger_summary.json",
            "force_diagnostic/force_diag_trigger_snapshot.png",
            "**/force_diagnostic/force_diag_trigger_substep.npz",
            "**/force_diagnostic/force_diag_trigger_summary.json",
            "**/force_diagnostic/force_diag_trigger_snapshot.png",
        ],
    )
    qa_reports = _find_any(root, ["qa/report.json", "**/qa/report.json"])
    qa_verdicts = _find_any(root, ["qa/verdict.md", "**/qa/verdict.md"])
    qa_sheets = _find_any(root, ["qa/contact_sheets/*.png", "**/qa/contact_sheets/*.png"])

    if args.require_video:
        checks.append(("video", bool(videos), "*.mp4"))
    if args.require_gif:
        checks.append(("gif", bool(gifs), "*.gif"))
    if args.require_diagnostic:
        checks.append(("diagnostic", len(diagnostics) >= 3, "force_diagnostic/*"))
    if args.require_qa:
        checks.append(("qa_report", bool(qa_reports), "qa/report.json"))
        checks.append(("qa_verdict", bool(qa_verdicts), "qa/verdict.md"))
        checks.append(("qa_contact_sheets", bool(qa_sheets), "qa/contact_sheets/*.png"))

    missing = [name for name, ok, _ in checks if not ok]

    summary_field_errors: list[str] = []
    if summaries and args.summary_field:
        try:
            payload = json.loads(summaries[0].read_text(encoding="utf-8"))
            for field in args.summary_field:
                if field not in payload:
                    summary_field_errors.append(field)
        except Exception as exc:
            summary_field_errors.append(f"<summary parse failed: {exc}>")
    elif args.summary_field:
        summary_field_errors.extend(args.summary_field)

    print(f"[validate_experiment_artifacts] root={root}")
    for name, ok, expected in checks:
        status = "OK" if ok else "MISSING"
        print(f"  - {name}: {status} ({expected})")
    if summaries:
        print(f"  - first summary: {summaries[0]}")
    if videos:
        print(f"  - video count: {len(videos)}")
    if gifs:
        print(f"  - gif count: {len(gifs)}")
    if qa_reports:
        print(f"  - qa report: {qa_reports[0]}")
    if qa_verdicts:
        print(f"  - qa verdict: {qa_verdicts[0]}")
    if qa_sheets:
        print(f"  - qa contact sheets: {len(qa_sheets)}")

    if summary_field_errors:
        print("  - summary field errors:", ", ".join(summary_field_errors))

    if missing or summary_field_errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
