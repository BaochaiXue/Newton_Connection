#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate physical blocking for the tabletop Franka rope push task.")
    p.add_argument("run_dir", type=Path)
    p.add_argument("--contact-report", type=Path, default=None)
    p.add_argument("--max-penetration-m", type=float, default=0.002)
    p.add_argument("--min-blocking-error-m", type=float, default=0.001)
    p.add_argument("--min-table-contact-duration-s", type=float, default=0.10)
    return p.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.expanduser().resolve()
    report_path = (
        args.contact_report.expanduser().resolve()
        if args.contact_report is not None
        else run_dir / "diagnostics_blocking" / "robot_table_contact_report.json"
    )
    summary_path = run_dir / "summary.json"
    if not report_path.exists():
        raise FileNotFoundError(report_path)
    if not summary_path.exists():
        raise FileNotFoundError(summary_path)

    summary = _load_json(summary_path)
    report = _load_json(report_path)
    penetration = float(report.get("robot_table_penetration_min_m") or 0.0)
    duration = float(report.get("robot_table_contact_duration_s") or 0.0)
    error_max = report.get("ee_target_to_actual_error_during_block_max_m")
    error_max = None if error_max is None else float(error_max)
    hidden_helper = bool(report.get("hidden_helper_detected"))
    rope_contact_started = bool(summary.get("actual_finger_box_contact_started"))

    gates = {
        "robot_table_contact_present": report.get("robot_table_first_contact_time_s") is not None,
        "robot_table_contact_duration_pass": duration >= float(args.min_table_contact_duration_s),
        "penetration_tolerance_pass": penetration >= -float(args.max_penetration_m),
        "blocking_error_present": error_max is not None and error_max >= float(args.min_blocking_error_m),
        "rope_contact_still_present": rope_contact_started,
        "hidden_helper_absent": not hidden_helper,
    }
    overall_pass = all(gates.values())

    payload = {
        "run_dir": str(run_dir),
        "summary_path": str(summary_path),
        "contact_report_path": str(report_path),
        "gates": gates,
        "metrics": {
            "robot_table_penetration_min_m": penetration,
            "robot_table_contact_duration_s": duration,
            "ee_target_to_actual_error_during_block_max_m": error_max,
        },
        "overall_pass": overall_pass,
    }
    _write_json(run_dir / "blocking_metrics.json", payload)
    _write_md(
        run_dir / "blocking_validation.md",
        [
            "# Physical Blocking Validation",
            "",
            f"- robot-table contact present: {'YES' if gates['robot_table_contact_present'] else 'NO'}",
            f"- robot-table contact duration pass: {'YES' if gates['robot_table_contact_duration_pass'] else 'NO'}",
            f"- penetration tolerance pass: {'YES' if gates['penetration_tolerance_pass'] else 'NO'}",
            f"- blocking error present: {'YES' if gates['blocking_error_present'] else 'NO'}",
            f"- rope contact still present: {'YES' if gates['rope_contact_still_present'] else 'NO'}",
            f"- hidden helper absent: {'YES' if gates['hidden_helper_absent'] else 'NO'}",
            "",
            f"- robot_table_penetration_min_m: `{penetration}`",
            f"- robot_table_contact_duration_s: `{duration}`",
            f"- ee_target_to_actual_error_during_block_max_m: `{error_max}`",
            "",
            f"- overall pass: {'YES' if overall_pass else 'NO'}",
        ],
    )
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
