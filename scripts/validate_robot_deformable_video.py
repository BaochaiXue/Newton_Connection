#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


@dataclass
class FrameSample:
    index: int
    timestamp_s: float
    mean_luma: float
    dark_pixel_ratio: float
    black_screen_flag: bool
    diff_to_previous: float | None
    path: str


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate native robot+deformable demo videos.")
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--video", type=Path, default=None)
    p.add_argument("--summary-json", type=Path, default=None)
    p.add_argument("--output-dir", type=Path, default=None)
    p.add_argument("--sample-count", type=int, default=12)
    p.add_argument("--black-mean-threshold", type=float, default=18.0)
    p.add_argument("--black-dark-ratio-threshold", type=float, default=0.97)
    p.add_argument("--frame-dark-threshold", type=int, default=12)
    p.add_argument("--repeat-frame-threshold", type=float, default=0.20)
    p.add_argument("--resolution-min-width", type=int, default=1280)
    p.add_argument("--resolution-min-height", type=int, default=720)
    p.add_argument("--fps-min", type=float, default=20.0)
    p.add_argument("--duration-min-sec", type=float, default=6.0)
    p.add_argument("--duration-max-sec", type=float, default=15.0)
    return p.parse_args()


def _resolve_path(root: Path, path: Path | None) -> Path | None:
    if path is None:
        return None
    raw = path.expanduser()
    if raw.is_absolute():
        return raw.resolve()
    return (root / raw).resolve()


def _discover_first(root: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        matches = sorted(root.glob(pattern))
        if matches:
            return matches[0].resolve()
    return None


def _load_summary(summary_path: Path | None) -> dict[str, Any]:
    if summary_path is None or not summary_path.exists():
        return {}
    return json.loads(summary_path.read_text(encoding="utf-8"))


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


def _video_stream(ffprobe_payload: dict[str, Any]) -> dict[str, Any]:
    for stream in ffprobe_payload.get("streams", []):
        if str(stream.get("codec_type")) == "video":
            return stream
    return {}


def _fps_from_stream(stream: dict[str, Any]) -> float:
    value = str(stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/1")
    if "/" in value:
        num, den = value.split("/", 1)
        try:
            num_f = float(num)
            den_f = float(den)
            return num_f / den_f if den_f != 0.0 else 0.0
        except Exception:
            return 0.0
    try:
        return float(value)
    except Exception:
        return 0.0


def _duration_from_payload(ffprobe_payload: dict[str, Any]) -> float:
    try:
        return float(ffprobe_payload.get("format", {}).get("duration", 0.0) or 0.0)
    except Exception:
        return 0.0


def _open_video(video_path: Path) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"failed to open video: {video_path}")
    return cap


def _frame_count(cap: cv2.VideoCapture) -> int:
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    return count if count > 0 else 0


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


def _make_sample(
    frame_bgr: np.ndarray,
    *,
    idx: int,
    fps: float,
    frame_dark_threshold: int,
    black_mean_threshold: float,
    black_dark_ratio_threshold: float,
    out_path: Path,
    diff_to_previous: float | None,
) -> FrameSample:
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    Image.fromarray(rgb).save(out_path)
    gray = _gray(frame_bgr)
    mean_luma = float(gray.mean())
    dark_ratio = float((gray < frame_dark_threshold).mean())
    black_flag = mean_luma < black_mean_threshold and dark_ratio > black_dark_ratio_threshold
    return FrameSample(
        index=int(idx),
        timestamp_s=float(idx / fps) if fps > 0.0 else float(idx),
        mean_luma=mean_luma,
        dark_pixel_ratio=dark_ratio,
        black_screen_flag=black_flag,
        diff_to_previous=diff_to_previous,
        path=str(out_path),
    )


def _grid_sheet(
    image_paths: list[Path],
    labels: list[str],
    *,
    out_path: Path,
    cols: int,
    thumb_w: int = 360,
) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    font = None
    for font_path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            font = ImageFont.truetype(font_path, size=20)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()

    images = [Image.open(p).convert("RGB") for p in image_paths]
    thumbs: list[Image.Image] = []
    for img in images:
        scale = thumb_w / max(1, img.width)
        thumb_h = max(1, int(round(img.height * scale)))
        thumbs.append(img.resize((thumb_w, thumb_h)))

    rows = int(math.ceil(len(thumbs) / max(cols, 1)))
    thumb_h = max(img.height for img in thumbs)
    label_h = 38
    gutter = 16
    canvas = Image.new(
        "RGB",
        (cols * thumb_w + (cols + 1) * gutter, rows * (thumb_h + label_h) + (rows + 1) * gutter),
        (247, 245, 238),
    )
    draw = ImageDraw.Draw(canvas)

    for i, thumb in enumerate(thumbs):
        row = i // cols
        col = i % cols
        x = gutter + col * (thumb_w + gutter)
        y = gutter + row * (thumb_h + label_h + gutter)
        canvas.paste(thumb, (x, y))
        draw.rectangle((x, y + thumb.height, x + thumb_w, y + thumb.height + label_h), fill=(30, 30, 30))
        draw.text((x + 10, y + thumb.height + 8), labels[i], fill=(255, 255, 255), font=font)
    canvas.save(out_path)
    return out_path


def _map_summary_frame_to_video_frame(summary_frame: int | None, *, summary_frames: int, video_frames: int) -> int | None:
    if summary_frame is None:
        return None
    if summary_frames <= 1 or video_frames <= 1:
        return 0
    ratio = float(summary_frame) / float(max(summary_frames - 1, 1))
    mapped = int(round(ratio * float(video_frames - 1)))
    return max(0, min(video_frames - 1, mapped))


def _event_indices(frame_count: int, summary: dict[str, Any]) -> list[tuple[str, int]]:
    first_contact = summary.get("first_contact_frame")
    contact_peak_frame = summary.get("contact_peak_frame")
    release_frame = summary.get("release_frame")
    contact_active = int(summary.get("contact_active_frames", 0) or 0)
    rope_peak_frame = summary.get("rope_mid_segment_peak_frame")
    summary_frames = int(summary.get("frames", frame_count) or frame_count)

    first_contact_video = _map_summary_frame_to_video_frame(
        first_contact if isinstance(first_contact, int) else None,
        summary_frames=summary_frames,
        video_frames=frame_count,
    )
    release_frame_video = _map_summary_frame_to_video_frame(
        release_frame if isinstance(release_frame, int) else None,
        summary_frames=summary_frames,
        video_frames=frame_count,
    )
    if isinstance(contact_peak_frame, int):
        approx_mid_contact_summary = int(contact_peak_frame)
    elif isinstance(rope_peak_frame, int):
        approx_mid_contact_summary = int(rope_peak_frame)
    elif first_contact_video is not None and contact_active > 0:
        approx_mid_contact_summary = int(first_contact) + max(1, contact_active // 2)
    else:
        approx_mid_contact_summary = None
    if approx_mid_contact_summary is not None:
        mid_contact_video = _map_summary_frame_to_video_frame(
            approx_mid_contact_summary,
            summary_frames=summary_frames,
            video_frames=frame_count,
        )
    else:
        mid_contact_video = None

    indices: list[tuple[str, int]] = [("setup", 0)]
    if first_contact_video is not None:
        pre = max(0, int(first_contact_video) - max(1, int(frame_count * 0.05)))
        indices = [("pre_contact", pre), ("first_contact", int(first_contact_video))]
        if mid_contact_video is not None:
            indices.append(("mid_contact", int(mid_contact_video)))
    if release_frame_video is not None:
        indices.append(("release", int(release_frame_video)))
    indices.append(("final", frame_count - 1))

    dedup: list[tuple[str, int]] = []
    seen: set[int] = set()
    for label, idx in indices:
        idx = max(0, min(frame_count - 1, idx))
        if idx not in seen:
            seen.add(idx)
            dedup.append((label, idx))
    return dedup


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.expanduser().resolve()
    video_path = _resolve_path(run_dir, args.video)
    if video_path is None:
        video_path = _discover_first(run_dir, ["final.mp4", "*.mp4", "**/*.mp4"])
    if video_path is None or not video_path.exists():
        raise FileNotFoundError(f"Could not locate mp4 under {run_dir}")

    summary_path = _resolve_path(run_dir, args.summary_json)
    if summary_path is None:
        summary_path = _discover_first(run_dir, ["summary.json", "*_summary.json", "**/summary.json", "**/*_summary.json"])
    summary = _load_summary(summary_path)

    out_dir = _resolve_path(run_dir, args.output_dir) or run_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    keyframes_dir = out_dir / "keyframes"
    keyframes_dir.mkdir(parents=True, exist_ok=True)

    ffprobe_payload = _ffprobe(video_path)
    stream = _video_stream(ffprobe_payload)
    fps = _fps_from_stream(stream)
    duration_s = _duration_from_payload(ffprobe_payload)
    width = int(stream.get("width") or 0)
    height = int(stream.get("height") or 0)

    ffprobe_path = out_dir / "ffprobe.json"
    ffprobe_path.write_text(json.dumps(ffprobe_payload, indent=2), encoding="utf-8")

    cap = _open_video(video_path)
    try:
        frame_count = _frame_count(cap)
        sample_ids = _sample_indices(frame_count, args.sample_count)
        sampled_paths: list[Path] = []
        samples: list[FrameSample] = []
        prev_gray: np.ndarray | None = None
        for idx in sample_ids:
            frame = _read_frame(cap, idx)
            gray = _gray(frame)
            diff = None
            if prev_gray is not None:
                diff = float(np.abs(gray.astype(np.float32) - prev_gray.astype(np.float32)).mean())
            out_path = keyframes_dir / f"sample_{idx:05d}.png"
            sampled_paths.append(out_path)
            samples.append(
                _make_sample(
                    frame,
                    idx=idx,
                    fps=fps,
                    frame_dark_threshold=args.frame_dark_threshold,
                    black_mean_threshold=args.black_mean_threshold,
                    black_dark_ratio_threshold=args.black_dark_ratio_threshold,
                    out_path=out_path,
                    diff_to_previous=diff,
                )
            )
            prev_gray = gray

        contact_sheet = _grid_sheet(
            sampled_paths,
            [f"f={s.index} t={s.timestamp_s:.2f}s" for s in samples],
            out_path=out_dir / "contact_sheet.png",
            cols=4,
        )

        event_ids = _event_indices(frame_count, summary)
        event_paths: list[Path] = []
        for label, idx in event_ids:
            frame = _read_frame(cap, idx)
            event_path = keyframes_dir / f"{label}_{idx:05d}.png"
            Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).save(event_path)
            event_paths.append(event_path)
        event_sheet = _grid_sheet(
            event_paths,
            [f"{label} @ {idx}" for label, idx in event_ids],
            out_path=out_dir / "event_sheet.png",
            cols=min(4, max(1, len(event_paths))),
        )
    finally:
        cap.release()

    black_fraction = float(sum(1 for s in samples if s.black_screen_flag) / max(1, len(samples)))
    pair_diffs = [float(s.diff_to_previous) for s in samples if s.diff_to_previous is not None]
    mean_pair_diff = float(np.mean(pair_diffs)) if pair_diffs else 0.0
    repeat_fraction = float(sum(1 for v in pair_diffs if v < args.repeat_frame_threshold) / max(1, len(pair_diffs))) if pair_diffs else 1.0

    validation = {
        "video_path": str(video_path),
        "summary_json": str(summary_path) if summary_path is not None else "",
        "resolution": {"width": width, "height": height},
        "fps": fps,
        "duration_s": duration_s,
        "frame_count": frame_count,
        "gates": {
            "resolution_pass": bool(width >= args.resolution_min_width and height >= args.resolution_min_height),
            "fps_pass": bool(fps >= args.fps_min),
            "duration_pass": bool(args.duration_min_sec <= duration_s <= args.duration_max_sec),
            "black_screen_pass": bool(black_fraction < 0.5),
            "smoothness_pass": bool(repeat_fraction < 0.75),
        },
        "metrics": {
            "black_frame_fraction": black_fraction,
            "mean_pair_diff": mean_pair_diff,
            "repeat_transition_fraction": repeat_fraction,
        },
        "sampled_frames": [asdict(s) for s in samples],
        "event_frames": [{"label": label, "frame_index": idx} for label, idx in event_ids],
        "outputs": {
            "ffprobe_json": str(ffprobe_path),
            "contact_sheet": str(contact_sheet),
            "event_sheet": str(event_sheet),
            "keyframes_dir": str(keyframes_dir),
        },
        "manual_visual_review_required": True,
        "questions_for_manual_review": [
            "Are robot and deformable both visible for most of the clip?",
            "Is the contact region readable?",
            "Can a human see approach -> contact -> manipulation -> outcome?",
            "Does the clip read like native robot manipulation rather than a probe touch?",
            "Is two-way coupling visually defensible?",
        ],
    }
    validation_path = out_dir / "validation.json"
    validation_path.write_text(json.dumps(validation, indent=2), encoding="utf-8")

    verdict_lines = [
        "# Robot + Deformable Video Verdict",
        "",
        f"- Video: `{video_path}`",
        f"- Summary: `{summary_path}`" if summary_path is not None else "- Summary: `<missing>`",
        f"- ffprobe: `{ffprobe_path}`",
        f"- Contact sheet: `{contact_sheet}`",
        f"- Event sheet: `{event_sheet}`",
        "",
        "## Automatic Gates",
        "",
        f"- Resolution pass: `{validation['gates']['resolution_pass']}`",
        f"- FPS pass: `{validation['gates']['fps_pass']}`",
        f"- Duration pass: `{validation['gates']['duration_pass']}`",
        f"- Black-screen pass: `{validation['gates']['black_screen_pass']}`",
        f"- Smoothness pass: `{validation['gates']['smoothness_pass']}`",
        "",
        "## Manual Review Required",
        "",
    ]
    verdict_lines.extend(f"- {q}" for q in validation["questions_for_manual_review"])
    verdict_path = out_dir / "verdict.md"
    verdict_path.write_text("\n".join(verdict_lines) + "\n", encoding="utf-8")

    print(f"ffprobe: {ffprobe_path}")
    print(f"contact_sheet: {contact_sheet}")
    print(f"event_sheet: {event_sheet}")
    print(f"validation: {validation_path}")
    print(f"verdict: {verdict_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
