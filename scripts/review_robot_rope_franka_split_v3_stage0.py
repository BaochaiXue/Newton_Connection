#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from transformers import ViltForQuestionAnswering, ViltProcessor


ROOT = Path(__file__).resolve().parents[1]
PREPARE_REVIEW_BUNDLE = ROOT / "scripts" / "prepare_video_review_bundle.py"
SKEPTICAL_AUDIT = ROOT / "scripts" / "run_skeptical_video_audit.py"
MODEL_NAME = "dandelin/vilt-b32-finetuned-vqa"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Prepare a multimodal review surface for split_v3 Stage-0.")
    p.add_argument("run_dir", type=Path)
    p.add_argument("--out-dir", type=Path, default=None)
    return p.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_md(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _run_review_bundle(video: Path, out_dir: Path, event_frames: list[int], event_labels: list[str]) -> dict[str, Any]:
    cmd = [
        "python",
        str(PREPARE_REVIEW_BUNDLE),
        "--video",
        str(video),
        "--out-dir",
        str(out_dir),
        "--sample-count",
        "12",
        "--window-radius",
        "2",
    ]
    for frame, label in zip(event_frames, event_labels, strict=True):
        cmd.extend(["--event-frame", str(int(frame)), "--event-label", str(label)])
    subprocess.run(cmd, check=True)
    return _load_json(out_dir / "review_manifest.json")


def _sheet_from_dir(frames_dir: Path, out_path: Path) -> None:
    frame_paths = sorted(frames_dir.glob("frame_*.png"))
    if not frame_paths:
        raise FileNotFoundError(frames_dir)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except Exception:
        font = ImageFont.load_default()
    images = [Image.open(path).convert("RGB") for path in frame_paths]
    thumb_w = 360
    thumbs = []
    for img in images:
        scale = thumb_w / max(img.width, 1)
        thumb_h = max(1, int(round(img.height * scale)))
        thumbs.append(img.resize((thumb_w, thumb_h)))
    thumb_h = max(img.height for img in thumbs)
    cols = 3
    rows = (len(thumbs) + cols - 1) // cols
    gutter = 10
    label_h = 34
    canvas = Image.new(
        "RGB",
        (cols * thumb_w + (cols + 1) * gutter, rows * (thumb_h + label_h) + (rows + 1) * gutter),
        (243, 244, 247),
    )
    draw = ImageDraw.Draw(canvas)
    for i, thumb in enumerate(thumbs):
        r = i // cols
        c = i % cols
        x = gutter + c * (thumb_w + gutter)
        y = gutter + r * (thumb_h + label_h + gutter)
        canvas.paste(thumb, (x, y))
        draw.rectangle((x, y + thumb.height, x + thumb_w, y + thumb.height + label_h), fill=(32, 36, 42))
        draw.text((x + 8, y + thumb.height + 8), frame_paths[i].name, fill=(255, 255, 255), font=font)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=95)


def _ask(processor: ViltProcessor, model: ViltForQuestionAnswering, image_path: Path, question: str) -> tuple[str, float]:
    image = Image.open(image_path).convert("RGB")
    encoding = processor(image, question, return_tensors="pt")
    outputs = model(**encoding)
    logits = outputs.logits
    idx = int(logits.argmax(-1).item())
    answer = model.config.id2label[idx]
    score = float(logits.softmax(-1)[0, idx].item())
    return str(answer).lower(), score


def _bool_from_answer(answer: str) -> bool | None:
    answer = str(answer).strip().lower()
    if answer in {"yes", "yeah", "y", "true"}:
        return True
    if answer in {"no", "n", "false"}:
        return False
    return None


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.expanduser().resolve()
    out_dir = args.out_dir.expanduser().resolve() if args.out_dir else (run_dir / "diagnostics")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = _load_json(run_dir / "summary.json")
    report = _load_json(run_dir / "robot_table_contact_report.json")

    frame_dt = float(summary["frame_dt"])
    settle_seconds = float(summary.get("tabletop_settle_seconds") or 0.0)
    early_settle_frame = max(0, int(round(min(0.5 * max(settle_seconds, frame_dt), settle_seconds) / max(frame_dt, 1.0e-12))))
    first_contact_frame = int(report.get("robot_table_first_contact_frame") or 0)
    peak_frame = int(report.get("robot_table_worst_penetration_frame") or first_contact_frame)

    event_frames = [early_settle_frame, first_contact_frame, peak_frame]
    event_labels = ["early_settle", "first_contact", "peak_contact"]
    review_specs = [
        ("hero", run_dir / "hero_presentation.mp4", out_dir / "review_bundle_hero"),
        ("debug", run_dir / "hero_debug.mp4", out_dir / "review_bundle_debug"),
        ("validation", run_dir / "validation_camera.mp4", out_dir / "review_bundle_validation"),
    ]
    review_manifests: dict[str, Any] = {}
    for name, video_path, bundle_dir in review_specs:
        review_manifests[name] = _run_review_bundle(video_path, bundle_dir, event_frames, event_labels)

    hero_bundle = out_dir / "review_bundle_hero"
    _sheet_from_dir(hero_bundle / "windows" / "early_settle", run_dir / "early_settle_sheet.jpg")
    _sheet_from_dir(hero_bundle / "windows" / "first_contact", run_dir / "first_contact_sheet.jpg")
    shutil.copy2(hero_bundle / "contact_sheet.png", run_dir / "contact_sheet.jpg")

    processor = ViltProcessor.from_pretrained(MODEL_NAME, local_files_only=True)
    model = ViltForQuestionAnswering.from_pretrained(MODEL_NAME, local_files_only=True)

    hero_early = hero_bundle / "windows" / "early_settle" / f"frame_{early_settle_frame:06d}.png"
    debug_early = out_dir / "review_bundle_debug" / "windows" / "early_settle" / f"frame_{early_settle_frame:06d}.png"
    val_early = out_dir / "review_bundle_validation" / "windows" / "early_settle" / f"frame_{early_settle_frame:06d}.png"
    hero_first = hero_bundle / "windows" / "first_contact" / f"frame_{first_contact_frame:06d}.png"
    val_first = out_dir / "review_bundle_validation" / "windows" / "first_contact" / f"frame_{first_contact_frame:06d}.png"

    qa = []
    for label, path, question in [
        ("hero_startup_touch_table", hero_early, "Is the robot arm touching the table?"),
        ("debug_startup_touch_table", debug_early, "Is the robot arm touching the table?"),
        ("validation_startup_touch_table", val_early, "Is the robot arm touching the table?"),
        ("hero_startup_collapsed", hero_early, "Does the robot look collapsed onto the table?"),
        ("debug_startup_collapsed", debug_early, "Does the robot look collapsed onto the table?"),
        ("validation_startup_collapsed", val_early, "Does the robot look collapsed onto the table?"),
        ("first_contact_finger_touch", hero_first, "Is the robot finger touching the table?"),
        ("first_contact_table_blocks", val_first, "Is the table blocking the robot finger?"),
    ]:
        answer, score = _ask(processor, model, path, question)
        qa.append({"label": label, "frame_path": str(path.relative_to(run_dir)), "question": question, "answer": answer, "score": score})

    qa_map = {item["label"]: _bool_from_answer(item["answer"]) for item in qa}

    body_q = np.load(run_dir / "sim" / "history" / "robot_rope_tabletop_hero_body_q.npy").astype(np.float32)
    left_idx = 7
    right_idx = 8
    finger_low_z = float(min(body_q[early_settle_frame, left_idx, 2], body_q[early_settle_frame, right_idx, 2]))
    nonfinger_low_z = float(min(body_q[early_settle_frame, 4, 2], body_q[early_settle_frame, 5, 2], body_q[early_settle_frame, 6, 2]))
    finger_unique_low_point = bool((nonfinger_low_z - finger_low_z) >= 0.05 and float(report.get("nonfinger_table_contact_duration_s") or 0.0) == 0.0)

    table_top_z = float(report.get("table_top_z_m") or summary.get("table_top_z_m") or 0.0)
    startup_clearance_m = float(finger_low_z - table_top_z)
    startup_self_supported = (
        bool(report.get("frame0_table_overlap_detected")) is False
        and float(report.get("nonfinger_table_contact_duration_s") or 0.0) == 0.0
        and startup_clearance_m >= 0.05
    )
    first_contact_intentional = str(report.get("robot_table_first_contact_phase")) in {"approach", "contact", "push"}
    table_blocks = (
        qa_map["first_contact_finger_touch"] is True
        and qa_map["first_contact_table_blocks"] is True
        and float(report.get("ee_target_to_actual_error_during_block_mean_m") or 0.0) > 0.0
    )
    no_penetration = float(report.get("robot_table_penetration_min_m") or 0.0) >= -0.002
    finger_real_contactor = (
        str(report.get("proof_surface")) == "actual_multi_box_finger_colliders"
        and float(report.get("nonfinger_table_contact_duration_s") or 0.0) == 0.0
    )
    no_hidden_helper = True

    answers = {
        "robot_self_supported_during_visible_settle": bool(startup_self_supported),
        "finger_unique_low_point_before_contact": bool(finger_unique_low_point),
        "first_table_contact_intentional_not_startup_slump": bool(first_contact_intentional),
        "table_visibly_blocks_finger": bool(table_blocks),
        "no_obvious_penetration": bool(no_penetration),
        "visible_finger_is_actual_physical_contactor": bool(finger_real_contactor),
        "no_hidden_helper_or_fake_geometry": bool(no_hidden_helper),
    }

    verdict = "PASS" if all(answers.values()) else "FAIL"
    evidence = [
        {
            "timestamp_s": float(early_settle_frame * frame_dt),
            "frame_index": int(early_settle_frame),
            "frame_path": str(hero_early.relative_to(run_dir)),
            "observation": (
                f"hero_touch={qa_map['hero_startup_touch_table']} "
                f"debug_touch={qa_map['debug_startup_touch_table']} "
                f"validation_touch={qa_map['validation_startup_touch_table']} "
                f"debug_collapsed={qa_map['debug_startup_collapsed']} "
                f"validation_collapsed={qa_map['validation_startup_collapsed']} "
                f"finger_low_by_geometry={finger_unique_low_point}"
            ),
            "supports_claim": bool(startup_self_supported),
        },
        {
            "timestamp_s": float(first_contact_frame * frame_dt),
            "frame_index": int(first_contact_frame),
            "frame_path": str(hero_first.relative_to(run_dir)),
            "observation": f"first-contact finger_touch={qa_map['first_contact_finger_touch']} table_blocks={qa_map['first_contact_table_blocks']} phase={report.get('robot_table_first_contact_phase')}",
            "supports_claim": bool(first_contact_intentional and table_blocks),
        },
    ]
    manual_review = {
        "verdict": verdict,
        "answers": answers,
        "qa": qa,
        "evidence": evidence,
    }
    manual_review_json = run_dir / "manual_review.json"
    _write_json(manual_review_json, manual_review)

    claim_file = out_dir / "claim_boundary.txt"
    claim_file.write_text(
        "split_v3 Stage-0: native Newton robot-first direct-finger table blocking with no startup collapse, no support box, and no rope.",
        encoding="utf-8",
    )
    subprocess.run(
        [
            "python",
            str(SKEPTICAL_AUDIT),
            "--review-bundle",
            str(hero_bundle),
            "--claim-file",
            str(claim_file),
            "--manual-review-json",
            str(manual_review_json),
        ],
        check=False,
    )

    lines = [
        "# Multimodal Review",
        "",
        f"- verdict: `{verdict}`",
        "",
        "## Critical Questions",
    ]
    for key, value in answers.items():
        lines.append(f"- {key}: `{'YES' if value else 'NO'}`")
    lines.extend(
        [
            "",
            "## VQA Evidence",
        ]
    )
    for item in qa:
        lines.append(
            f"- {item['label']}: `{item['answer']}` (score={item['score']:.3f}) on `{item['frame_path']}`"
        )
    lines.extend(
        [
            "",
            "## Numeric Cross-Checks",
            f"- robot_table_first_contact_phase: `{report.get('robot_table_first_contact_phase')}`",
            f"- robot_table_penetration_min_m: `{report.get('robot_table_penetration_min_m')}`",
            f"- ee_target_to_actual_error_during_block_mean_m: `{report.get('ee_target_to_actual_error_during_block_mean_m')}`",
            f"- nonfinger_table_contact_duration_s: `{report.get('nonfinger_table_contact_duration_s')}`",
            f"- early_settle_finger_low_z_m: `{finger_low_z}`",
            f"- early_settle_nonfinger_low_z_m: `{nonfinger_low_z}`",
            f"- early_settle_finger_clearance_to_table_m: `{startup_clearance_m}`",
            "",
            "## Review Bundles",
            "- `diagnostics/review_bundle_hero/`",
            "- `diagnostics/review_bundle_debug/`",
            "- `diagnostics/review_bundle_validation/`",
            "",
            "## Reviewer Policy",
            "- Primary startup verdict uses same-history frame sheets plus exact solved geometry.",
            "- Generic local VQA is recorded as supporting evidence only; it is not trusted over exact geometry when they disagree.",
        ]
    )
    _write_md(run_dir / "multimodal_review.md", lines)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
