#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


@dataclass
class VideoMetrics:
    name: str
    path: str
    ffprobe_path: str
    resolution_width: int
    resolution_height: int
    encoded_fps: float
    duration_s: float
    nb_frames: int
    decoded_frame_count: int
    decode_pass: bool
    black_frame_fraction: float
    near_exact_repeat_fraction: float
    max_static_run: int
    mean_pair_diff: float
    median_pair_diff: float
    min_pair_diff: float
    max_pair_diff: float
    sampled_indices: list[int]
    sample_paths: list[str]
    contact_sheet_path: str
    keyframe_paths: list[str]
    scene_readable_pass: bool
    motion_pass: bool
    duration_pass: bool
    resolution_pass: bool
    fps_pass: bool
    overall_pass: bool


VISUAL_QA_KEYS = [
    "output_complete",
    "robot_is_native_newton_asset",
    "table_is_present_and_supportive",
    "rope_is_resting_on_or_interacting_with_table_before_push",
    "robot_contacts_rope",
    "rope_deforms_due_to_contact",
    "rope_moves_after_contact_not_before",
    "contact_zone_is_readable",
    "no_obvious_penetration_or_teleporting",
    "presentation_ready",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Strictly validate the native Newton Franka + native Newton table + "
            "PhysTwin rope hero demo."
        )
    )
    p.add_argument("run_dir", type=Path, help="Candidate run directory to validate.")
    p.add_argument("--presentation-video", type=Path, default=None)
    p.add_argument("--debug-video", type=Path, default=None)
    p.add_argument("--validation-video", type=Path, default=None)
    p.add_argument("--summary-json", type=Path, default=None)
    p.add_argument("--manual-review-json", type=Path, default=None)
    p.add_argument(
        "--sample-count",
        type=int,
        default=4,
        help="Number of evenly sampled keyframes to save per video.",
    )
    p.add_argument("--min-duration-sec", type=float, default=6.0)
    p.add_argument("--max-duration-sec", type=float, default=12.0)
    p.add_argument("--min-resolution-width", type=int, default=1280)
    p.add_argument("--min-resolution-height", type=int, default=720)
    p.add_argument("--min-fps", type=float, default=24.0)
    p.add_argument("--black-mean-threshold", type=float, default=18.0)
    p.add_argument("--black-dark-ratio-threshold", type=float, default=0.97)
    p.add_argument("--frame-dark-threshold", type=int, default=12)
    p.add_argument(
        "--motion-threshold",
        type=float,
        default=0.25,
        help="Minimum mean inter-frame difference for readable motion. Tuned to stay conservative while not rejecting slow quasi-static tabletop pushes.",
    )
    p.add_argument("--repeat-frame-threshold", type=float, default=0.20)
    p.add_argument("--contact-sheet-cols", type=int, default=4)
    return p.parse_args()


def _load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _ffprobe(video_path: Path) -> dict[str, Any]:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_streams",
        "-show_format",
        str(video_path),
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(proc.stdout)


def _decode_check(video_path: Path, out_path: Path) -> bool:
    cmd = ["ffmpeg", "-v", "error", "-i", str(video_path), "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(proc.stderr, encoding="utf-8")
    return proc.returncode == 0 and not proc.stderr.strip()


def _open_video(video_path: Path) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"failed to open video: {video_path}")
    return cap


def _video_stream(ffprobe_payload: dict[str, Any]) -> dict[str, Any]:
    for stream in ffprobe_payload.get("streams", []):
        if str(stream.get("codec_type")) == "video":
            return stream
    return {}


def _fps_from_stream(stream: dict[str, Any]) -> float:
    raw = str(stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/1")
    if "/" in raw:
        num, den = raw.split("/", 1)
        try:
            num_f = float(num)
            den_f = float(den)
            return num_f / den_f if den_f != 0.0 else 0.0
        except Exception:
            return 0.0
    try:
        return float(raw)
    except Exception:
        return 0.0


def _duration_from_payload(ffprobe_payload: dict[str, Any]) -> float:
    try:
        return float(ffprobe_payload.get("format", {}).get("duration", 0.0) or 0.0)
    except Exception:
        return 0.0


def _sample_indices(frame_count: int, sample_count: int) -> list[int]:
    if frame_count <= 1:
        return [0]
    raw = np.linspace(0, frame_count - 1, num=min(sample_count, frame_count))
    out: list[int] = []
    seen: set[int] = set()
    for value in raw:
        idx = max(0, min(frame_count - 1, int(round(float(value)))))
        if idx not in seen:
            seen.add(idx)
            out.append(idx)
    return out


def _read_frame(cap: cv2.VideoCapture, idx: int) -> np.ndarray:
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, frame = cap.read()
    if not ok or frame is None:
        raise RuntimeError(f"failed to read frame {idx}")
    return frame


def _gray(frame_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)


def _motion(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a.astype(np.float32) - b.astype(np.float32))))


def _make_sheet(image_paths: list[Path], labels: list[str], out_path: Path, *, cols: int = 4) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except Exception:
        font = ImageFont.load_default()
    images = [Image.open(path).convert("RGB") for path in image_paths]
    if not images:
        raise ValueError("no images supplied for contact sheet")
    thumb_w = 360
    thumbs: list[Image.Image] = []
    for img in images:
        scale = thumb_w / max(img.width, 1)
        thumb_h = max(1, int(round(img.height * scale)))
        thumbs.append(img.resize((thumb_w, thumb_h)))
    thumb_h = max(img.height for img in thumbs)
    label_h = 36
    gutter = 14
    rows = int(math.ceil(len(thumbs) / max(cols, 1)))
    canvas = Image.new(
        "RGB",
        (cols * thumb_w + (cols + 1) * gutter, rows * (thumb_h + label_h) + (rows + 1) * gutter),
        (241, 243, 246),
    )
    draw = ImageDraw.Draw(canvas)
    for i, thumb in enumerate(thumbs):
        r = i // cols
        c = i % cols
        x = gutter + c * (thumb_w + gutter)
        y = gutter + r * (thumb_h + label_h + gutter)
        canvas.paste(thumb, (x, y))
        draw.rectangle((x, y + thumb.height, x + thumb_w, y + thumb.height + label_h), fill=(28, 32, 40))
        draw.text((x + 8, y + thumb.height + 8), labels[i], fill=(255, 255, 255), font=font)
    canvas.save(out_path)
    return out_path


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "pass"}
    return False


def _discover_video(run_dir: Path, explicit: Path | None, candidates: list[str]) -> Path | None:
    if explicit is not None:
        raw = explicit.expanduser()
        return raw.resolve() if raw.is_absolute() else (run_dir / raw).resolve()
    for pattern in candidates:
        found = sorted(run_dir.glob(pattern))
        if found:
            return found[0].resolve()
    return None


def _sample_video(
    video_path: Path,
    *,
    slug: str,
    run_dir: Path,
    keyframes_dir: Path,
    contact_sheets_dir: Path,
    sample_count: int,
    black_mean_threshold: float,
    black_dark_ratio_threshold: float,
    frame_dark_threshold: int,
    min_duration_sec: float,
    max_duration_sec: float,
    min_resolution_width: int,
    min_resolution_height: int,
    min_fps: float,
    motion_threshold: float,
    repeat_frame_threshold: float,
) -> tuple[VideoMetrics, dict[str, Any], list[Path], list[str]]:
    ffprobe_payload = _ffprobe(video_path)
    ffprobe_path = run_dir / "ffprobe" / f"{slug}.json"
    _write_json(ffprobe_path, ffprobe_payload)
    decode_log = run_dir / "qa" / f"{slug}_decode.log"
    decode_pass = _decode_check(video_path, decode_log)

    stream = _video_stream(ffprobe_payload)
    width = int(stream.get("width") or 0)
    height = int(stream.get("height") or 0)
    fps = _fps_from_stream(stream)
    duration = _duration_from_payload(ffprobe_payload)
    nb_frames = int(stream.get("nb_frames") or 0)

    cap = _open_video(video_path)
    try:
        decoded_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        sampled_indices = _sample_indices(decoded_frame_count, sample_count)
        sampled_paths: list[Path] = []
        sampled_labels: list[str] = []
        sampled_grays: list[np.ndarray] = []
        for idx_i, idx in enumerate(sampled_indices, start=1):
            frame = _read_frame(cap, idx)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out_path = keyframes_dir / f"{slug}_sample_{idx_i:02d}_frame_{idx:06d}.png"
            Image.fromarray(rgb).save(out_path)
            sampled_paths.append(out_path)
            sampled_labels.append(f"{slug} | frame {idx}")
            sampled_grays.append(_gray(frame))
    finally:
        cap.release()

    pair_diffs: list[float] = []
    all_grays: list[np.ndarray] = []
    cap = _open_video(video_path)
    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                break
            gray = _gray(frame)
            if gray.shape[1] > 320:
                gray = cv2.resize(gray, (320, 180))
            all_grays.append(gray)
    finally:
        cap.release()
    for i in range(1, len(all_grays)):
        pair_diffs.append(_motion(all_grays[i - 1], all_grays[i]))

    if pair_diffs:
        repeated = [v <= repeat_frame_threshold for v in pair_diffs]
        near_exact_repeat_fraction = float(np.mean(repeated))
        max_static_run = 0
        cur = 0
        for flag in repeated:
            cur = cur + 1 if flag else 0
            max_static_run = max(max_static_run, cur)
        mean_pair_diff = float(np.mean(pair_diffs))
        median_pair_diff = float(np.median(pair_diffs))
        min_pair_diff = float(np.min(pair_diffs))
        max_pair_diff = float(np.max(pair_diffs))
    else:
        near_exact_repeat_fraction = 1.0
        max_static_run = 0
        mean_pair_diff = 0.0
        median_pair_diff = 0.0
        min_pair_diff = 0.0
        max_pair_diff = 0.0

    sampled_mean_luma = [float(gray.mean()) for gray in sampled_grays]
    sampled_dark_ratio = [float((gray < frame_dark_threshold).mean()) for gray in sampled_grays]
    black_flags = [
        mean_luma < black_mean_threshold and dark_ratio > black_dark_ratio_threshold
        for mean_luma, dark_ratio in zip(sampled_mean_luma, sampled_dark_ratio)
    ]
    black_frame_fraction = float(np.mean(black_flags)) if black_flags else 1.0
    scene_readable_pass = width >= min_resolution_width and height >= min_resolution_height and black_frame_fraction < 0.5
    motion_pass = mean_pair_diff >= motion_threshold and near_exact_repeat_fraction < 0.85
    duration_pass = min_duration_sec <= duration <= max_duration_sec
    resolution_pass = width >= min_resolution_width and height >= min_resolution_height
    fps_pass = fps >= min_fps
    overall_pass = bool(decode_pass and scene_readable_pass and motion_pass and duration_pass and resolution_pass and fps_pass)

    contact_sheet = _make_sheet(
        sampled_paths,
        sampled_labels,
        contact_sheets_dir / f"{slug}.png",
        cols=max(1, min(4, len(sampled_paths))),
    )

    metrics = VideoMetrics(
        name=slug,
        path=str(video_path),
        ffprobe_path=str(ffprobe_path),
        resolution_width=width,
        resolution_height=height,
        encoded_fps=float(fps),
        duration_s=float(duration),
        nb_frames=nb_frames,
        decoded_frame_count=decoded_frame_count,
        decode_pass=bool(decode_pass),
        black_frame_fraction=black_frame_fraction,
        near_exact_repeat_fraction=near_exact_repeat_fraction,
        max_static_run=max_static_run,
        mean_pair_diff=mean_pair_diff,
        median_pair_diff=median_pair_diff,
        min_pair_diff=min_pair_diff,
        max_pair_diff=max_pair_diff,
        sampled_indices=sampled_indices,
        sample_paths=[str(path) for path in sampled_paths],
        contact_sheet_path=str(contact_sheet),
        keyframe_paths=[str(path) for path in sampled_paths],
        scene_readable_pass=bool(scene_readable_pass),
        motion_pass=bool(motion_pass),
        duration_pass=bool(duration_pass),
        resolution_pass=bool(resolution_pass),
        fps_pass=bool(fps_pass),
        overall_pass=bool(overall_pass),
    )
    ffprobe_record = {
        "name": slug,
        "video_path": str(video_path),
        "ffprobe_path": str(ffprobe_path),
        "decode_log_path": str(decode_log),
        "ffprobe": ffprobe_payload,
        "metrics": asdict(metrics),
    }
    return metrics, ffprobe_record, sampled_paths, sampled_labels


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.expanduser().resolve()
    if not run_dir.exists():
        raise FileNotFoundError(f"run_dir does not exist: {run_dir}")

    qa_dir = run_dir / "qa"
    keyframes_dir = run_dir / "keyframes"
    contact_sheets_dir = run_dir / "contact_sheets"
    ffprobe_dir = run_dir / "ffprobe"
    qa_dir.mkdir(parents=True, exist_ok=True)
    keyframes_dir.mkdir(parents=True, exist_ok=True)
    contact_sheets_dir.mkdir(parents=True, exist_ok=True)
    ffprobe_dir.mkdir(parents=True, exist_ok=True)

    presentation_video = _discover_video(
        run_dir,
        args.presentation_video,
        ["hero_presentation.mp4", "final_presentation.mp4", "presentation.mp4", "media/final.mp4", "*.mp4"],
    )
    debug_video = _discover_video(
        run_dir,
        args.debug_video,
        ["hero_debug.mp4", "final_debug.mp4", "debug.mp4", "media/debug.mp4"],
    )
    validation_video = _discover_video(
        run_dir,
        args.validation_video,
        ["validation_camera.mp4", "validation.mp4", "camera_validation.mp4"],
    )
    if presentation_video is None:
        raise FileNotFoundError(f"missing hero presentation video under {run_dir}")
    if debug_video is None:
        raise FileNotFoundError(f"missing hero debug video under {run_dir}")
    if validation_video is None:
        raise FileNotFoundError(f"missing validation camera video under {run_dir}")

    summary_path = _discover_video(run_dir, args.summary_json, ["summary.json", "*_summary.json", "work/*_summary.json"])
    summary_payload = _load_json(summary_path)
    manual_review_path = args.manual_review_json.expanduser().resolve() if args.manual_review_json else run_dir / "manual_review.json"
    manual_review_payload = _load_json(manual_review_path if manual_review_path.exists() else None)
    manual_review_supplied = bool(manual_review_payload)

    command_pointer = run_dir / "run_command.txt"
    if (run_dir / "command.txt").exists() and not command_pointer.exists():
        shutil.copyfile(run_dir / "command.txt", command_pointer)
    elif not command_pointer.exists():
        command_pointer.write_text(
            "python scripts/validate_robot_rope_franka_hero.py "
            f"{run_dir}\n",
            encoding="utf-8",
        )

    video_inputs = {
        "hero_presentation": presentation_video,
        "hero_debug": debug_video,
        "validation_camera": validation_video,
    }

    video_reports: dict[str, dict[str, Any]] = {}
    ffprobe_records: list[dict[str, Any]] = []
    all_keyframes: list[Path] = []
    all_labels: list[str] = []
    objective_gates: dict[str, bool] = {}
    for slug, video_path in video_inputs.items():
        metrics, ffprobe_record, sampled_paths, sampled_labels = _sample_video(
            video_path,
            slug=slug,
            run_dir=run_dir,
            keyframes_dir=keyframes_dir,
            contact_sheets_dir=contact_sheets_dir,
            sample_count=args.sample_count,
            black_mean_threshold=args.black_mean_threshold,
            black_dark_ratio_threshold=args.black_dark_ratio_threshold,
            frame_dark_threshold=args.frame_dark_threshold,
            min_duration_sec=args.min_duration_sec,
            max_duration_sec=args.max_duration_sec,
            min_resolution_width=args.min_resolution_width,
            min_resolution_height=args.min_resolution_height,
            min_fps=args.min_fps,
            motion_threshold=args.motion_threshold,
            repeat_frame_threshold=args.repeat_frame_threshold,
        )
        video_reports[slug] = asdict(metrics)
        ffprobe_records.append(ffprobe_record)
        all_keyframes.extend(sampled_paths)
        all_labels.extend(sampled_labels)
        objective_gates[f"{slug}_present"] = video_path.exists()
        objective_gates[f"{slug}_decode_pass"] = bool(metrics.decode_pass)
        objective_gates[f"{slug}_duration_pass"] = bool(metrics.duration_pass)
        objective_gates[f"{slug}_resolution_pass"] = bool(metrics.resolution_pass)
        objective_gates[f"{slug}_fps_pass"] = bool(metrics.fps_pass)
        objective_gates[f"{slug}_scene_readable_pass"] = bool(metrics.scene_readable_pass)
        objective_gates[f"{slug}_motion_pass"] = bool(metrics.motion_pass)

    combined_contact_sheet = _make_sheet(
        all_keyframes,
        all_labels,
        run_dir / "contact_sheet.png",
        cols=max(1, min(args.contact_sheet_cols, 4)),
    )

    visual_qa_defaults = {key: False for key in VISUAL_QA_KEYS}
    visual_qa = dict(visual_qa_defaults)
    if manual_review_supplied:
        for key in VISUAL_QA_KEYS:
            if key in manual_review_payload:
                visual_qa[key] = _coerce_bool(manual_review_payload[key])
    visual_qa["output_complete"] = bool(
        presentation_video.exists()
        and debug_video.exists()
        and validation_video.exists()
        and run_dir.joinpath("contact_sheet.png").exists()
        and keyframes_dir.exists()
    )

    objective_pass = bool(
        visual_qa["output_complete"]
        and all(objective_gates.values())
    )
    visual_pass = bool(all(visual_qa.values()))
    overall_pass = bool(objective_pass and visual_pass)

    ffprobe_payload = {
        "run_dir": str(run_dir),
        "summary_path": None if summary_path is None else str(summary_path),
        "summary": summary_payload,
        "videos": ffprobe_records,
    }
    _write_json(run_dir / "ffprobe.json", ffprobe_payload)

    metrics = {
        "run_dir": str(run_dir),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "videos": video_reports,
        "objective_gates": objective_gates,
        "visual_qa": visual_qa,
        "manual_review_path": str(manual_review_path),
        "manual_review_supplied": bool(manual_review_supplied),
        "summary_path": None if summary_path is None else str(summary_path),
        "command_pointer": str(command_pointer),
        "artifacts": {
            "ffprobe_json": str(run_dir / "ffprobe.json"),
            "metrics_json": str(run_dir / "metrics.json"),
            "validation_md": str(run_dir / "validation.md"),
            "contact_sheet": str(run_dir / "contact_sheet.png"),
            "keyframes_dir": str(keyframes_dir),
            "contact_sheets_dir": str(contact_sheets_dir),
        },
        "overall_pass": overall_pass,
    }
    _write_json(run_dir / "metrics.json", metrics)

    if not (run_dir / "manifest.json").exists():
        manifest = {
            "run_id": run_dir.name,
            "task": "robot_rope_franka_hero",
            "status": "candidate",
            "output_root": str(run_dir),
            "videos": {
                "hero_presentation": str(presentation_video),
                "hero_debug": str(debug_video),
                "validation_camera": str(validation_video),
            },
            "artifacts": metrics["artifacts"],
            "validation": {
                "metrics_json": "metrics.json",
                "validation_md": "validation.md",
                "ffprobe_json": "ffprobe.json",
                "contact_sheet": "contact_sheet.png",
                "keyframes_dir": "keyframes",
            },
        }
        _write_json(run_dir / "manifest.json", manifest)

    verdict_lines = [
        "# Native Robot + Native Table + PhysTwin Rope Hero Validation",
        "",
        "## Objective Gates",
    ]
    for slug in ["hero_presentation", "hero_debug", "validation_camera"]:
        report = video_reports[slug]
        verdict_lines.extend(
            [
                f"- `{slug}` present: {'YES' if objective_gates[f'{slug}_present'] else 'NO'}",
                f"- `{slug}` decode: {'YES' if objective_gates[f'{slug}_decode_pass'] else 'NO'}",
                f"- `{slug}` duration in range: {'YES' if objective_gates[f'{slug}_duration_pass'] else 'NO'}",
                f"- `{slug}` resolution in range: {'YES' if objective_gates[f'{slug}_resolution_pass'] else 'NO'}",
                f"- `{slug}` fps in range: {'YES' if objective_gates[f'{slug}_fps_pass'] else 'NO'}",
                f"- `{slug}` scene readable: {'YES' if objective_gates[f'{slug}_scene_readable_pass'] else 'NO'}",
                f"- `{slug}` motion readable: {'YES' if objective_gates[f'{slug}_motion_pass'] else 'NO'}",
                f"- `{slug}` duration_s: {report['duration_s']:.3f}",
                f"- `{slug}` resolution: {report['resolution_width']}x{report['resolution_height']}",
                f"- `{slug}` fps: {report['encoded_fps']:.3f}",
                f"- `{slug}` black_frame_fraction: {report['black_frame_fraction']:.3f}",
                f"- `{slug}` mean_pair_diff: {report['mean_pair_diff']:.3f}",
            ]
        )

    verdict_lines.extend(
        [
            "",
            "## Visual QA",
            f"- Output complete: {'YES' if visual_qa['output_complete'] else 'NO'}",
            f"- Robot is a native Newton asset: {'YES' if visual_qa['robot_is_native_newton_asset'] else 'NO'}",
            f"- Table is present and supportive: {'YES' if visual_qa['table_is_present_and_supportive'] else 'NO'}",
            f"- Rope rests on / interacts with table before push: {'YES' if visual_qa['rope_is_resting_on_or_interacting_with_table_before_push'] else 'NO'}",
            f"- Robot visibly contacts rope: {'YES' if visual_qa['robot_contacts_rope'] else 'NO'}",
            f"- Rope deforms due to contact: {'YES' if visual_qa['rope_deforms_due_to_contact'] else 'NO'}",
            f"- Rope moves after contact rather than before: {'YES' if visual_qa['rope_moves_after_contact_not_before'] else 'NO'}",
            f"- Contact zone is readable: {'YES' if visual_qa['contact_zone_is_readable'] else 'NO'}",
            f"- No obvious penetration or teleporting: {'YES' if visual_qa['no_obvious_penetration_or_teleporting'] else 'NO'}",
            f"- Presentation ready: {'YES' if visual_qa['presentation_ready'] else 'NO'}",
            "",
            "## Files",
            f"- ffprobe: `{run_dir / 'ffprobe.json'}`",
            f"- metrics: `{run_dir / 'metrics.json'}`",
            f"- validation: `{run_dir / 'validation.md'}`",
            f"- contact sheet: `{run_dir / 'contact_sheet.png'}`",
            f"- keyframes: `{keyframes_dir}`",
            f"- command pointer: `{command_pointer}`",
            "",
            "## Verdict",
            f"- Objective pass: {'YES' if objective_pass else 'NO'}",
            f"- Visual pass: {'YES' if visual_pass else 'NO'}",
            f"- Overall pass: {'YES' if overall_pass else 'NO'}",
        ]
    )
    _write_markdown(run_dir / "validation.md", verdict_lines)

    print(f"[validate_robot_rope_franka_hero] run_dir={run_dir}")
    print(f"[validate_robot_rope_franka_hero] ffprobe={run_dir / 'ffprobe.json'}")
    print(f"[validate_robot_rope_franka_hero] metrics={run_dir / 'metrics.json'}")
    print(f"[validate_robot_rope_franka_hero] validation={run_dir / 'validation.md'}")
    print(f"[validate_robot_rope_franka_hero] contact_sheet={run_dir / 'contact_sheet.png'}")
    print(f"[validate_robot_rope_franka_hero] keyframes={keyframes_dir}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
