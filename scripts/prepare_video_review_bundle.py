#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Prepare a skeptical-review bundle for a video artifact.")
    p.add_argument("--video", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--sample-count", type=int, default=12)
    p.add_argument("--window-count", type=int, default=3)
    p.add_argument("--window-radius", type=int, default=2)
    p.add_argument("--event-frame", type=int, action="append", default=[])
    p.add_argument("--event-label", action="append", default=[])
    p.add_argument("--frame-dark-threshold", type=int, default=12)
    p.add_argument("--black-mean-threshold", type=float, default=18.0)
    p.add_argument("--black-dark-ratio-threshold", type=float, default=0.97)
    p.add_argument("--motion-threshold", type=float, default=0.75)
    p.add_argument("--repeat-frame-threshold", type=float, default=0.20)
    return p.parse_args()


def _ffprobe(video_path: Path) -> dict:
    cmd = ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(video_path)]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(proc.stdout)


def _video_stream(ffprobe_payload: dict) -> dict:
    for stream in ffprobe_payload.get("streams", []):
        if str(stream.get("codec_type")) == "video":
            return stream
    return {}


def _fps_from_stream(stream: dict) -> float:
    raw = str(stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/1")
    if "/" in raw:
        a, b = raw.split("/", 1)
        try:
            return float(a) / max(float(b), 1.0e-12)
        except Exception:
            return 0.0
    try:
        return float(raw)
    except Exception:
        return 0.0


def _duration_from_payload(payload: dict) -> float:
    try:
        return float(payload.get("format", {}).get("duration", 0.0) or 0.0)
    except Exception:
        return 0.0


def _open_video(video_path: Path) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"failed to open video: {video_path}")
    return cap


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


def _window_centers(frame_count: int, window_count: int, event_frames: list[int]) -> list[tuple[str, int]]:
    centers: list[tuple[str, int]] = []
    for idx, frame in enumerate(event_frames):
        frame = max(0, min(frame_count - 1, int(frame)))
        centers.append((f"event_{idx+1}", frame))
    if centers:
        return centers
    if frame_count <= 1:
        return [("window_1", 0)]
    raw = np.linspace(0, frame_count - 1, num=max(window_count, 1) + 2)[1:-1]
    return [(f"window_{i+1}", int(round(float(v)))) for i, v in enumerate(raw)]


def _read_frame(cap: cv2.VideoCapture, idx: int) -> np.ndarray:
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, frame = cap.read()
    if not ok or frame is None:
        raise RuntimeError(f"failed to read frame {idx}")
    return frame


def _gray(frame_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)


def _frame_metrics(gray: np.ndarray, frame_dark_threshold: int, black_mean_threshold: float, black_dark_ratio_threshold: float) -> tuple[float, float, bool]:
    mean_luma = float(gray.mean())
    dark_ratio = float((gray < frame_dark_threshold).mean())
    black_flag = mean_luma < black_mean_threshold and dark_ratio > black_dark_ratio_threshold
    return mean_luma, dark_ratio, black_flag


def _motion(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a.astype(np.float32) - b.astype(np.float32))))


def _make_sheet(image_paths: list[Path], labels: list[str], out_path: Path, cols: int = 4) -> None:
    font = None
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            font = ImageFont.truetype(candidate, 18)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
    images = [Image.open(path).convert("RGB") for path in image_paths]
    thumb_w = 360
    thumbs = []
    for img in images:
        scale = thumb_w / max(img.width, 1)
        thumb_h = max(1, int(round(img.height * scale)))
        thumbs.append(img.resize((thumb_w, thumb_h)))
    thumb_h = max(img.height for img in thumbs)
    label_h = 40
    rows = int(math.ceil(len(thumbs) / cols))
    gutter = 12
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
        draw.text((x + 10, y + thumb.height + 8), labels[i], fill=(255, 255, 255), font=font)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)


def main() -> int:
    args = parse_args()
    video_path = args.video.expanduser().resolve()
    out_dir = args.out_dir.expanduser().resolve()
    sampled_dir = out_dir / "sampled_frames"
    windows_dir = out_dir / "windows"
    sampled_dir.mkdir(parents=True, exist_ok=True)
    windows_dir.mkdir(parents=True, exist_ok=True)

    ffprobe_payload = _ffprobe(video_path)
    stream = _video_stream(ffprobe_payload)
    fps = _fps_from_stream(stream)
    duration = _duration_from_payload(ffprobe_payload)

    cap = _open_video(video_path)
    try:
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        sampled_indices = _sample_indices(frame_count, args.sample_count)
        sample_records = []
        sample_paths: list[Path] = []
        sample_labels: list[str] = []
        sampled_gray: list[np.ndarray] = []
        for idx in sampled_indices:
            frame = _read_frame(cap, idx)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out_path = sampled_dir / f"frame_{idx:06d}.png"
            Image.fromarray(rgb).save(out_path)
            gray = _gray(frame)
            mean_luma, dark_ratio, black_flag = _frame_metrics(
                gray,
                args.frame_dark_threshold,
                args.black_mean_threshold,
                args.black_dark_ratio_threshold,
            )
            sample_records.append(
                {
                    "frame_index": idx,
                    "timestamp_s": (idx / fps) if fps > 0.0 else float(idx),
                    "frame_path": str(out_path.relative_to(out_dir)),
                    "mean_luma": mean_luma,
                    "dark_pixel_ratio": dark_ratio,
                    "black_screen_flag": black_flag,
                }
            )
            sample_paths.append(out_path)
            sample_labels.append(f"idx={idx} t={(idx / fps) if fps > 0.0 else idx:.2f}s")
            sampled_gray.append(gray)
    finally:
        cap.release()

    pair_diffs = [_motion(sampled_gray[i], sampled_gray[i + 1]) for i in range(len(sampled_gray) - 1)]
    black_frame_fraction = float(np.mean([item["black_screen_flag"] for item in sample_records])) if sample_records else 0.0
    repeat_transition_fraction = float(np.mean([d < args.repeat_frame_threshold for d in pair_diffs])) if pair_diffs else 0.0
    motion_density = float(np.mean([d >= args.motion_threshold for d in pair_diffs])) if pair_diffs else 0.0
    max_static_run = 0
    current_static_run = 0
    for diff in pair_diffs:
        if diff < args.repeat_frame_threshold:
            current_static_run += 1
            max_static_run = max(max_static_run, current_static_run)
        else:
            current_static_run = 0
    max_static_run_fraction = (max_static_run / max(len(pair_diffs), 1)) if pair_diffs else 0.0

    centers = _window_centers(frame_count, args.window_count, args.event_frame)
    if args.event_label and len(args.event_label) == len(centers):
        centers = [(label, center) for label, (_, center) in zip(args.event_label, centers)]
    window_records = []
    event_sheet_paths: list[Path] = []
    event_sheet_labels: list[str] = []
    cap = _open_video(video_path)
    try:
        for label, center in centers:
            window_dir = windows_dir / label
            window_dir.mkdir(parents=True, exist_ok=True)
            frames = []
            for frame_idx in range(max(0, center - args.window_radius), min(frame_count - 1, center + args.window_radius) + 1):
                frame = _read_frame(cap, frame_idx)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out_path = window_dir / f"frame_{frame_idx:06d}.png"
                Image.fromarray(rgb).save(out_path)
                frames.append(
                    {
                        "frame_index": frame_idx,
                        "timestamp_s": (frame_idx / fps) if fps > 0.0 else float(frame_idx),
                        "frame_path": str(out_path.relative_to(out_dir)),
                    }
                )
            window_records.append({"label": label, "center_frame": center, "frames": frames})
            event_sheet_paths.append(window_dir / f"frame_{center:06d}.png")
            event_sheet_labels.append(f"{label} idx={center}")
    finally:
        cap.release()

    contact_sheet_path = out_dir / "contact_sheet.png"
    event_sheet_path = out_dir / "event_sheet.png"
    _make_sheet(sample_paths, sample_labels, contact_sheet_path, cols=4)
    _make_sheet(event_sheet_paths, event_sheet_labels, event_sheet_path, cols=min(len(event_sheet_paths), 4) or 1)

    manifest = {
        "video_path": str(video_path),
        "frame_count": frame_count,
        "fps": fps,
        "duration_s": duration,
        "sample_count": len(sample_records),
        "sampled_frames": sample_records,
        "windows": window_records,
        "contact_sheet": str(contact_sheet_path),
        "event_sheet": str(event_sheet_path),
        "black_frame_fraction": black_frame_fraction,
        "repeat_transition_fraction": repeat_transition_fraction,
        "motion_density": motion_density,
        "max_static_run_fraction": max_static_run_fraction,
        "pair_diff_mean": float(np.mean(pair_diffs)) if pair_diffs else 0.0,
        "pair_diff_max": float(np.max(pair_diffs)) if pair_diffs else 0.0,
        "required_assets_present": {
            "sampled_frames": bool(sample_records),
            "windows": bool(window_records),
            "contact_sheet": contact_sheet_path.exists(),
            "event_sheet": event_sheet_path.exists(),
        },
    }
    manifest_path = out_dir / "review_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
