#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate direct-finger physical blocking for the tabletop Franka task.")
    p.add_argument("run_dir", type=Path)
    p.add_argument("--contact-report", type=Path, default=None)
    p.add_argument("--max-penetration-m", type=float, default=0.002)
    p.add_argument("--max-nonfinger-penetration-m", type=float, default=0.001)
    p.add_argument("--max-support-box-penetration-m", type=float, default=0.002)
    p.add_argument("--min-blocking-error-m", type=float, default=0.001)
    p.add_argument("--min-table-contact-duration-s", type=float, default=0.10)
    p.add_argument("--max-nonfinger-table-contact-duration-s", type=float, default=0.25)
    p.add_argument("--require-support-box", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--min-support-box-contact-duration-s", type=float, default=0.05)
    p.add_argument("--max-support-box-contact-duration-s", type=float, default=0.50)
    p.add_argument(
        "--allow-first-contact-during-settle",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="If false, rope-integrated runs fail when first finger-table contact already happens in the settle phase.",
    )
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
        else run_dir / "robot_table_contact_report.json"
    )
    summary_path = run_dir / "summary.json"
    if not report_path.exists():
        raise FileNotFoundError(report_path)
    if not summary_path.exists():
        raise FileNotFoundError(summary_path)

    summary = _load_json(summary_path)
    report = _load_json(report_path)
    stage = str(summary.get("blocking_stage", "rope_integrated"))
    penetration = float(report.get("robot_table_penetration_min_m") or 0.0)
    duration = float(report.get("robot_table_contact_duration_s") or 0.0)
    error_mean = report.get("ee_target_to_actual_error_during_block_mean_m")
    error_max = report.get("ee_target_to_actual_error_during_block_max_m")
    error_mean = None if error_mean is None else float(error_mean)
    error_max = None if error_max is None else float(error_max)
    hidden_helper = bool(report.get("hidden_helper_detected"))
    nonfinger_duration = report.get("nonfinger_table_contact_duration_s")
    nonfinger_duration = None if nonfinger_duration is None else float(nonfinger_duration)
    nonfinger_penetration = report.get("nonfinger_penetration_min_m")
    nonfinger_penetration = None if nonfinger_penetration is None else float(nonfinger_penetration)
    collapse_after_retract = bool(report.get("collapse_after_retract_detected"))
    support_box_duration = report.get("support_box_contact_duration_s")
    support_box_duration = None if support_box_duration is None else float(support_box_duration)
    support_box_penetration = report.get("support_box_penetration_min_m")
    support_box_penetration = None if support_box_penetration is None else float(support_box_penetration)
    support_box_is_physical = bool(report.get("support_box_is_physical_collider", False))
    frame0_support_overlap = bool(report.get("frame0_support_box_overlap_detected", False))
    frame0_table_overlap = bool(report.get("frame0_table_overlap_detected", False))
    first_table_phase = report.get("robot_table_first_contact_phase")
    first_support_phase = report.get("first_support_box_contact_phase")
    first_support_time = report.get("robot_support_box_first_contact_time_s")
    first_support_time = None if first_support_time is None else float(first_support_time)
    support_links = [str(v) for v in report.get("support_box_contact_link_names", [])]
    settle_seconds = summary.get("tabletop_settle_seconds")
    settle_seconds = None if settle_seconds is None else float(settle_seconds)
    first_contact_phase = summary.get("first_contact_phase")
    first_contact_time = summary.get("first_contact_time_s")
    first_contact_time = None if first_contact_time is None else float(first_contact_time)

    rope_contact_started = bool(
        summary.get("actual_finger_box_contact_started") or summary.get("actual_tool_contact_started")
    )

    gates = {
        "robot_table_contact_present": report.get("robot_table_first_contact_time_s") is not None,
        "robot_table_contact_duration_pass": duration >= float(args.min_table_contact_duration_s),
        "penetration_tolerance_pass": penetration >= -float(args.max_penetration_m),
        "blocking_error_present": error_max is not None and error_max >= float(args.min_blocking_error_m),
        "hidden_helper_absent": not hidden_helper,
    }
    if stage == "rope_integrated":
        gates["rope_contact_still_present"] = rope_contact_started
        gates["frame0_table_overlap_absent"] = not frame0_table_overlap
        table_phase_for_gate = first_table_phase or first_contact_phase
        table_time_for_gate = report.get("robot_table_first_contact_time_s")
        table_time_for_gate = first_contact_time if table_time_for_gate is None else float(table_time_for_gate)
        gates["first_contact_not_during_settle"] = bool(args.allow_first_contact_during_settle) or table_phase_for_gate in {"approach", "push", "hold", "retract"}
        gates["first_contact_after_settle"] = (
            bool(args.allow_first_contact_during_settle)
            or table_time_for_gate is None
            or settle_seconds is None
            or table_time_for_gate > settle_seconds
        )
        gates["nonfinger_table_contact_duration_pass"] = (
            nonfinger_duration is None or nonfinger_duration <= float(args.max_nonfinger_table_contact_duration_s)
        )
        gates["nonfinger_penetration_tolerance_pass"] = (
            nonfinger_penetration is None or nonfinger_penetration >= -float(args.max_nonfinger_penetration_m)
        )
        gates["collapse_after_retract_absent"] = not collapse_after_retract
        if bool(args.require_support_box):
            gates["support_box_is_physical"] = support_box_is_physical
            gates["frame0_support_box_overlap_absent"] = not frame0_support_overlap
            gates["support_box_contact_phase_pass"] = first_support_phase in {"approach", "push"}
            gates["support_box_first_contact_after_settle"] = (
                first_support_time is not None
                and settle_seconds is not None
                and first_support_time > settle_seconds
            )
            gates["support_box_contact_duration_pass"] = (
                support_box_duration is not None
                and support_box_duration >= float(args.min_support_box_contact_duration_s)
                and support_box_duration <= float(args.max_support_box_contact_duration_s)
            )
            gates["support_box_penetration_tolerance_pass"] = (
                support_box_penetration is not None and support_box_penetration >= -float(args.max_support_box_penetration_m)
            )
            gates["support_box_contact_links_pass"] = all(
                link.endswith(("/fr3_link5", "/fr3_link6", "/fr3_link7", "/fr3_hand")) for link in support_links
            )

    overall_pass = all(gates.values())

    payload = {
        "run_dir": str(run_dir),
        "summary_path": str(summary_path),
        "contact_report_path": str(report_path),
        "blocking_stage": stage,
        "gates": gates,
        "metrics": {
            "robot_table_penetration_min_m": penetration,
            "robot_table_contact_duration_s": duration,
            "ee_target_to_actual_error_during_block_mean_m": error_mean,
            "ee_target_to_actual_error_during_block_max_m": error_max,
            "nonfinger_table_contact_duration_s": nonfinger_duration,
            "nonfinger_penetration_min_m": nonfinger_penetration,
            "collapse_after_retract_detected": collapse_after_retract,
            "support_box_contact_duration_s": support_box_duration,
            "support_box_penetration_min_m": support_box_penetration,
            "support_box_is_physical_collider": support_box_is_physical,
            "frame0_support_box_overlap_detected": frame0_support_overlap,
            "frame0_table_overlap_detected": frame0_table_overlap,
            "robot_table_first_contact_phase": first_table_phase,
            "first_contact_phase": first_contact_phase,
            "first_contact_time_s": first_contact_time,
            "first_support_box_contact_phase": first_support_phase,
            "robot_support_box_first_contact_time_s": first_support_time,
            "support_box_contact_link_names": support_links,
        },
        "overall_pass": overall_pass,
    }
    _write_json(run_dir / "blocking_metrics.json", payload)
    _write_json(run_dir / "physical_blocking_validation.json", payload)
    md_lines = [
        "# Physical Blocking Validation",
        "",
        f"- blocking stage: `{stage}`",
        f"- robot-table contact present: {'YES' if gates['robot_table_contact_present'] else 'NO'}",
        f"- robot-table contact duration pass: {'YES' if gates['robot_table_contact_duration_pass'] else 'NO'}",
        f"- penetration tolerance pass: {'YES' if gates['penetration_tolerance_pass'] else 'NO'}",
        f"- blocking error present: {'YES' if gates['blocking_error_present'] else 'NO'}",
        f"- hidden helper absent: {'YES' if gates['hidden_helper_absent'] else 'NO'}",
    ]
    if stage == "rope_integrated":
        md_lines.append(f"- rope contact still present: {'YES' if gates['rope_contact_still_present'] else 'NO'}")
        md_lines.append(f"- frame-0 table overlap absent: {'YES' if gates['frame0_table_overlap_absent'] else 'NO'}")
        md_lines.append(f"- first contact not during settle: {'YES' if gates['first_contact_not_during_settle'] else 'NO'}")
        md_lines.append(f"- first contact after settle: {'YES' if gates['first_contact_after_settle'] else 'NO'}")
        md_lines.append(f"- non-finger table-contact duration pass: {'YES' if gates['nonfinger_table_contact_duration_pass'] else 'NO'}")
        md_lines.append(f"- non-finger penetration tolerance pass: {'YES' if gates['nonfinger_penetration_tolerance_pass'] else 'NO'}")
        md_lines.append(f"- collapse after retract absent: {'YES' if gates['collapse_after_retract_absent'] else 'NO'}")
        if bool(args.require_support_box):
            md_lines.append(f"- support box is physical: {'YES' if gates['support_box_is_physical'] else 'NO'}")
            md_lines.append(f"- frame-0 support-box overlap absent: {'YES' if gates['frame0_support_box_overlap_absent'] else 'NO'}")
            md_lines.append(f"- support box first-contact phase pass: {'YES' if gates['support_box_contact_phase_pass'] else 'NO'}")
            md_lines.append(f"- support box first-contact after settle: {'YES' if gates['support_box_first_contact_after_settle'] else 'NO'}")
            md_lines.append(f"- support box contact duration pass: {'YES' if gates['support_box_contact_duration_pass'] else 'NO'}")
            md_lines.append(f"- support box penetration tolerance pass: {'YES' if gates['support_box_penetration_tolerance_pass'] else 'NO'}")
            md_lines.append(f"- support box contact links pass: {'YES' if gates['support_box_contact_links_pass'] else 'NO'}")
    md_lines.extend(
        [
            "",
            f"- robot_table_penetration_min_m: `{penetration}`",
            f"- robot_table_contact_duration_s: `{duration}`",
            f"- ee_target_to_actual_error_during_block_mean_m: `{error_mean}`",
            f"- ee_target_to_actual_error_during_block_max_m: `{error_max}`",
            f"- nonfinger_table_contact_duration_s: `{nonfinger_duration}`",
            f"- nonfinger_penetration_min_m: `{nonfinger_penetration}`",
            f"- collapse_after_retract_detected: `{collapse_after_retract}`",
            f"- frame0_table_overlap_detected: `{frame0_table_overlap}`",
            f"- robot_table_first_contact_phase: `{first_table_phase}`",
            f"- first_contact_phase: `{first_contact_phase}`",
            f"- first_contact_time_s: `{first_contact_time}`",
            f"- support_box_is_physical_collider: `{support_box_is_physical}`",
            f"- frame0_support_box_overlap_detected: `{frame0_support_overlap}`",
            f"- first_support_box_contact_phase: `{first_support_phase}`",
            f"- robot_support_box_first_contact_time_s: `{first_support_time}`",
            f"- support_box_contact_duration_s: `{support_box_duration}`",
            f"- support_box_penetration_min_m: `{support_box_penetration}`",
            f"- support_box_contact_link_names: `{support_links}`",
            "",
            f"- overall pass: {'YES' if overall_pass else 'NO'}",
        ]
    )
    _write_md(run_dir / "blocking_validation.md", md_lines)
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
