#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


CASE_ORDER = [
    "bunny_baseline",
    "box_control",
    "bunny_low_inertia",
    "bunny_larger_scale",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the meeting-ready bunny force summary board.")
    parser.add_argument("--run-dir", type=Path, required=True)
    return parser.parse_args()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _first_match(root: Path, pattern: str) -> Path:
    matches = sorted(root.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"missing {pattern} under {root}")
    return matches[0]


def _select_video_report(report: dict, *, force: bool) -> dict:
    for item in report["videos"]:
        name = Path(item["path"]).name.lower()
        if force and "force_diag" in name:
            return item
        if not force and "force_diag" not in name:
            return item
    raise KeyError(f"missing {'force' if force else 'phenomenon'} video report")


def _select_key_frame(report_item: dict, *, force: bool) -> Path:
    samples = report_item["samples"]
    if not samples:
        raise ValueError("video report has no samples")
    if force:
        chosen = max(samples[1:] or samples, key=lambda item: float(item.get("pair_diff_to_previous") or 0.0))
    else:
        chosen = samples[min(len(samples) - 1, max(0, int(round(len(samples) * 0.58))))]
    return Path(chosen["path"])


def _fit_frame(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as image:
        fitted = ImageOps.contain(image.convert("RGB"), size)
    canvas = Image.new("RGB", size, (18, 18, 18))
    canvas.paste(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
    return canvas


def _font(size: int, *, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=max(10, int(size)))
        except Exception:
            continue
    return ImageFont.load_default()


def _case_takeaway(case_name: str, issue: str) -> str:
    mapping = {
        "bunny_baseline": "Baseline bunny: sparse ear contact, force remains magnitude-limited.",
        "box_control": "Box control: broad support keeps contact dense and readable.",
        "bunny_low_inertia": "Lower inertia reduces early penetration, but the mechanism stays magnitude-limited.",
        "bunny_larger_scale": "Larger bunny helps geometry coverage, but does not remove the failure mode.",
    }
    text = mapping.get(case_name, case_name.replace("_", " "))
    return f"{text} Issue={issue}."


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.expanduser().resolve()
    matrix_dir = run_dir / "artifacts" / "matrix"
    board_path = matrix_dir / "bunny_penetration_summary_board.png"
    board_json_path = matrix_dir / "bunny_penetration_summary_board.json"
    summary_path = run_dir / "summary.json"

    title_font = _font(30, bold=True)
    section_font = _font(20, bold=True)
    body_font = _font(16)

    cell_w = 920
    cell_h = 520
    phenomenon_size = (420, 236)
    force_size = (420, 236)
    canvas = Image.new("RGB", (cell_w * 2 + 60, cell_h * 2 + 120), (244, 242, 236))
    draw = ImageDraw.Draw(canvas)
    draw.text((24, 18), "Bunny Penetration: Phenomenon + Force Mechanism", fill=(20, 20, 20), font=title_font)

    run_summary = {"run_id": run_dir.name, "cases": []}
    board_summary = {"run_dir": str(run_dir), "cases": []}

    for idx, case_name in enumerate(CASE_ORDER):
        case_dir = matrix_dir / case_name
        qa_report = _load_json(case_dir / "qa" / "report.json")
        case_summary = _load_json(_first_match(case_dir / "phenomenon", "*_summary.json"))
        force_summary = _load_json(case_dir / "force_mechanism" / "self_off" / "force_diagnostic" / "force_diag_trigger_summary.json")
        phenomenon_report = _select_video_report(qa_report, force=False)
        force_report = _select_video_report(qa_report, force=True)
        phenomenon_frame = _select_key_frame(phenomenon_report, force=False)
        force_frame = _select_key_frame(force_report, force=True)

        row = idx // 2
        col = idx % 2
        origin_x = 24 + col * cell_w
        origin_y = 74 + row * cell_h
        draw.rounded_rectangle((origin_x, origin_y, origin_x + cell_w - 24, origin_y + cell_h - 24), radius=18, fill=(255, 255, 255), outline=(196, 188, 175), width=2)
        draw.text((origin_x + 18, origin_y + 16), case_name.replace("_", " ").title(), fill=(20, 20, 20), font=section_font)

        phenomenon_img = _fit_frame(phenomenon_frame, phenomenon_size)
        force_img = _fit_frame(force_frame, force_size)
        canvas.paste(phenomenon_img, (origin_x + 18, origin_y + 54))
        canvas.paste(force_img, (origin_x + 470, origin_y + 54))
        draw.text((origin_x + 18, origin_y + 296), "Phenomenon", fill=(50, 50, 50), font=body_font)
        draw.text((origin_x + 470, origin_y + 296), "Force Mechanism", fill=(50, 50, 50), font=body_font)

        metrics_lines = [
            f"QA: {force_report['verdict']}",
            f"issue={force_summary['dominant_issue_guess']}",
            f"wrong_dir={force_summary['wrong_direction_ratio']:.2f}",
            f"geom/force={force_summary['geom_contact_node_count']}/{force_summary['force_contact_node_count']}",
            f"ext/stop={force_summary['median_ext_over_stop']:.3f}",
            f"max_pen={1000.0 * float(case_summary.get('max_penetration_depth_bunny_mesh_m') or case_summary.get('max_penetration_depth_rigid_m') or 0.0):.3f} mm",
            _case_takeaway(case_name, str(force_summary['dominant_issue_guess'])),
        ]
        text_y = origin_y + 326
        for line in metrics_lines[:-1]:
            draw.text((origin_x + 18, text_y), line, fill=(35, 35, 35), font=body_font)
            text_y += 22
        draw.text((origin_x + 18, text_y + 4), metrics_lines[-1], fill=(80, 44, 18), font=body_font)

        run_summary["cases"].append(
            {
                "case": case_name,
                "qa_verdict": force_report["verdict"],
                "issue": force_summary["dominant_issue_guess"],
                "wrong_direction_ratio": force_summary["wrong_direction_ratio"],
                "geom_contact_without_force_ratio": force_summary["geom_contact_without_force_ratio"],
                "internal_dominates_ratio": force_summary["internal_dominates_ratio"],
                "median_ext_over_stop": force_summary["median_ext_over_stop"],
                "median_penetration_mm": force_summary["median_penetration_mm"],
                "geom_contact_node_count": force_summary["geom_contact_node_count"],
                "force_contact_node_count": force_summary["force_contact_node_count"],
                "max_mesh_pen_mm": 1000.0 * float(case_summary.get("max_penetration_depth_bunny_mesh_m") or case_summary.get("max_penetration_depth_rigid_m") or 0.0),
                "render_video": phenomenon_report["path"],
                "force_video": force_report["path"],
            }
        )
        board_summary["cases"].append(
            {
                "case": case_name,
                "phenomenon_frame": str(phenomenon_frame),
                "force_frame": str(force_frame),
                "takeaway": metrics_lines[-1],
            }
        )

    canvas.save(board_path)
    summary_path.write_text(json.dumps(run_summary, indent=2), encoding="utf-8")
    board_json_path.write_text(json.dumps(board_summary, indent=2), encoding="utf-8")
    print(f"[build_bunny_force_summary_board] board={board_path}")
    print(f"[build_bunny_force_summary_board] summary={summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
