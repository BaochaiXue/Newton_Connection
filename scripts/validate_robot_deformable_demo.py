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
    p = argparse.ArgumentParser(
        description="Validate a robot+deformable demo run and generate review artifacts."
    )
    p.add_argument("run_dir", type=Path)
    p.add_argument("--video", type=Path, default=None, help="Override final mp4 path")
    p.add_argument("--summary", type=Path, default=None, help="Override summary json path")
    p.add_argument(
        "--manual-review-json",
        type=Path,
        default=None,
        help="Optional json file with explicit manual review booleans.",
    )
    p.add_argument("--sample-count", type=int, default=12)
    p.add_argument("--black-mean-threshold", type=float, default=18.0)
    p.add_argument("--black-dark-ratio-threshold", type=float, default=0.97)
    p.add_argument("--frame-dark-threshold", type=int, default=12)
    p.add_argument(
        "--near-exact-repeat-threshold",
        type=float,
        default=0.001,
        help="Mean absolute grayscale diff below this is treated as a near-exact repeated frame.",
    )
    p.add_argument(
        "--near-exact-repeat-fraction-threshold",
        type=float,
        default=0.10,
        help="Fail smoothness when too many adjacent decoded frames are near-exact repeats.",
    )
    p.add_argument(
        "--near-exact-max-run-threshold",
        type=int,
        default=8,
        help="Fail smoothness when too many consecutive decoded frames are near-exact repeats.",
    )
    return p.parse_args()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_one(root: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        found = sorted(root.glob(pattern))
        if found:
            return found[0]
    return None


def _ffprobe(video_path: Path) -> dict:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def _decode_check(video_path: Path, out_path: Path) -> bool:
    cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        str(video_path),
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(proc.stderr, encoding="utf-8")
    return proc.returncode == 0 and not proc.stderr.strip()


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


def _open_video(video_path: Path) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")
    return cap


def _sample_indices(frame_count: int, sample_count: int) -> list[int]:
    if frame_count <= 1:
        return [0]
    raw = np.linspace(0, frame_count - 1, num=min(sample_count, frame_count))
    out: list[int] = []
    seen: set[int] = set()
    for x in raw:
        idx = int(round(float(x)))
        idx = max(0, min(frame_count - 1, idx))
        if idx not in seen:
            seen.add(idx)
            out.append(idx)
    return out


def _read_frame(cap: cv2.VideoCapture, idx: int) -> np.ndarray:
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, frame = cap.read()
    if not ok or frame is None:
        raise RuntimeError(f"Failed to read frame {idx}")
    return frame


def _read_all_grayscale_frames(video_path: Path, *, resize_to: tuple[int, int] = (320, 180)) -> list[np.ndarray]:
    cap = _open_video(video_path)
    frames: list[np.ndarray] = []
    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if resize_to is not None:
                gray = cv2.resize(gray, resize_to)
            frames.append(gray)
    finally:
        cap.release()
    return frames


def _grayscale(frame_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)


def _make_sheet(
    frames_rgb: list[np.ndarray],
    labels: list[str],
    out_path: Path,
    *,
    cols: int = 4,
) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pil_frames = [Image.fromarray(f) for f in frames_rgb]
    w = max(img.width for img in pil_frames)
    h = max(img.height for img in pil_frames)
    rows = math.ceil(len(pil_frames) / cols)
    title_h = 28
    canvas = Image.new("RGB", (cols * w, rows * (h + title_h)), color=(242, 244, 247))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    for i, (img, label) in enumerate(zip(pil_frames, labels)):
        r = i // cols
        c = i % cols
        x = c * w
        y = r * (h + title_h)
        draw.rectangle((x, y, x + w, y + title_h), fill=(228, 232, 238))
        draw.text((x + 8, y + 4), label, fill=(25, 29, 38), font=font)
        canvas.paste(img, (x, y + title_h))
    canvas.save(out_path)
    return out_path


def _find_peak_frame(run_dir: Path, summary: dict) -> int | None:
    hist = _find_one(run_dir, ["particle_q_object.npy", "sim/history/particle_q_object.npy", "work/particle_q_object.npy"])
    if hist is None:
        return None
    arr = np.load(hist, mmap_mode="r")
    if arr.ndim != 3 or arr.shape[0] == 0:
        return None
    com = arr.mean(axis=1)
    disp = np.linalg.norm(com - com[0:1], axis=1)
    return int(np.argmax(disp))


def _map_sim_frame_to_video_frame(sim_idx: int | None, summary: dict, video_frame_count: int) -> int | None:
    if sim_idx is None:
        return None
    sim_frame_count = int(summary.get("frames") or 0)
    if sim_frame_count <= 1 or video_frame_count <= 1:
        return max(0, min(video_frame_count - 1, int(sim_idx)))
    ratio = float(sim_idx) / float(sim_frame_count - 1)
    return int(round(np.clip(ratio, 0.0, 1.0) * float(video_frame_count - 1)))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.expanduser().resolve()
    qa_dir = run_dir / "qa"
    keyframes_dir = run_dir / "keyframes"
    qa_dir.mkdir(parents=True, exist_ok=True)
    keyframes_dir.mkdir(parents=True, exist_ok=True)

    summary_path = args.summary or _find_one(run_dir, ["summary.json", "*_summary.json", "work/*_summary.json"])
    if summary_path is None:
        raise FileNotFoundError(f"No summary json found under {run_dir}")
    summary = _read_json(summary_path)

    video_path = args.video or _find_one(run_dir, ["media/final.mp4", "*.mp4", "work/*.mp4"])
    if video_path is None:
        raise FileNotFoundError(f"No mp4 found under {run_dir}")

    ffprobe_json = _ffprobe(video_path)
    ffprobe_path = qa_dir / "ffprobe.json"
    _write_json(ffprobe_path, ffprobe_json)
    decode_log_path = qa_dir / "decode.log"
    decode_pass = _decode_check(video_path, decode_log_path)

    stream = next((s for s in ffprobe_json.get("streams", []) if s.get("codec_type") == "video"), {})
    width = int(stream.get("width") or 0)
    height = int(stream.get("height") or 0)
    fps = _fps_from_stream(stream)
    duration = float(stream.get("duration") or ffprobe_json.get("format", {}).get("duration") or 0.0)
    nb_frames = int(stream.get("nb_frames") or 0)

    cap = _open_video(video_path)
    try:
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        sampled_indices = _sample_indices(frame_count, args.sample_count)
        sampled_frames_bgr = [_read_frame(cap, idx) for idx in sampled_indices]
        sampled_frames_rgb = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in sampled_frames_bgr]
        sampled_grays = [_grayscale(f) for f in sampled_frames_bgr]
    finally:
        cap.release()

    black_flags: list[bool] = []
    mean_lumas: list[float] = []
    dark_ratios: list[float] = []
    for gray in sampled_grays:
        mean_luma = float(gray.mean())
        dark_ratio = float((gray < args.frame_dark_threshold).mean())
        mean_lumas.append(mean_luma)
        dark_ratios.append(dark_ratio)
        black_flags.append(
            mean_luma < args.black_mean_threshold
            and dark_ratio > args.black_dark_ratio_threshold
        )

    all_grays = _read_all_grayscale_frames(video_path)
    pair_diffs: list[float] = []
    for i in range(1, len(all_grays)):
        diff = np.abs(all_grays[i].astype(np.float32) - all_grays[i - 1].astype(np.float32))
        pair_diffs.append(float(diff.mean()))
    if pair_diffs:
        repeated = [v <= args.near_exact_repeat_threshold for v in pair_diffs]
        near_exact_repeat_fraction = float(np.mean(repeated))
        max_static_run = 0
        cur = 0
        for flag in repeated:
            cur = cur + 1 if flag else 0
            max_static_run = max(max_static_run, cur)
        max_static_run_fraction = float(max_static_run / max(len(pair_diffs), 1))
        mean_pair_diff = float(np.mean(pair_diffs))
        median_pair_diff = float(np.median(pair_diffs))
        max_pair_diff = float(np.max(pair_diffs))
        min_pair_diff = float(np.min(pair_diffs))
    else:
        near_exact_repeat_fraction = 1.0
        max_static_run = 0
        max_static_run_fraction = 0.0
        mean_pair_diff = 0.0
        median_pair_diff = 0.0
        max_pair_diff = 0.0
        min_pair_diff = 0.0

    black_screen_pass = not all(black_flags)
    smoothness_pass = (
        near_exact_repeat_fraction <= args.near_exact_repeat_fraction_threshold
        and max_static_run <= args.near_exact_max_run_threshold
    )
    encoding_pass = width >= 1280 and height >= 720 and fps >= 24.0 and duration >= 2.5 and (nb_frames == 0 or nb_frames >= 75)

    contact_sheet_path = _make_sheet(
        sampled_frames_rgb,
        [f"sample_{i+1:02d} | frame {idx}" for i, idx in enumerate(sampled_indices)],
        qa_dir / "contact_sheet.png",
        cols=4,
    )

    first_contact_frame = _map_sim_frame_to_video_frame(summary.get("first_contact_frame"), summary, frame_count)
    release_frame = _map_sim_frame_to_video_frame(summary.get("release_frame"), summary, frame_count)
    peak_frame = _map_sim_frame_to_video_frame(_find_peak_frame(run_dir, summary), summary, frame_count)
    event_indices = []
    for item in [0, first_contact_frame, peak_frame, release_frame, frame_count - 1]:
        if item is None:
            continue
        idx = max(0, min(frame_count - 1, int(item)))
        if idx not in event_indices:
            event_indices.append(idx)
    cap = _open_video(video_path)
    try:
        event_frames_bgr = [_read_frame(cap, idx) for idx in event_indices]
        event_frames_rgb = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in event_frames_bgr]
    finally:
        cap.release()
    event_labels: list[str] = []
    for idx_i, idx in enumerate(event_indices):
        if idx_i == 0:
            label = f"setup | frame {idx}"
        elif first_contact_frame is not None and idx == first_contact_frame:
            label = f"first_contact | frame {idx}"
        elif release_frame is not None and idx == release_frame:
            label = f"release | frame {idx}"
        elif idx_i == len(event_indices) - 1:
            label = f"outcome | frame {idx}"
        else:
            label = f"strongest_interaction | frame {idx}"
        event_labels.append(label)
    event_sheet_path = _make_sheet(
        event_frames_rgb,
        event_labels,
        qa_dir / "event_sheet.png",
        cols=max(1, min(4, len(event_indices))),
    )

    for i, (idx, rgb) in enumerate(zip(event_indices, event_frames_rgb), start=1):
        Image.fromarray(rgb).save(keyframes_dir / f"event_{i:02d}_frame_{idx:06d}.png")

    manual_review = {
        "black_or_nearly_black": None,
        "robot_and_rope_visible_for_most_of_clip": None,
        "contact_region_readable": None,
        "task_understandable_in_15s": None,
        "approach_contact_manipulation_outcome_visible": None,
        "two_way_coupling_visually_defensible": None,
        "camera_presentation_ready": None,
        "motion_smooth_enough": None,
        "visible_ground_and_support_context": None,
        "rope_through_table_or_support_visible": None,
    }
    if args.manual_review_json is not None and args.manual_review_json.exists():
        supplied = _read_json(args.manual_review_json)
        for key, value in supplied.items():
            if key in manual_review:
                manual_review[key] = value
    manual_review_complete = all(value is not None for value in manual_review.values())
    manual_gate_pass = bool(manual_review_complete and all(bool(value) for value in manual_review.values()))

    validation = {
        "video_path": str(video_path),
        "summary_path": str(summary_path),
        "ffprobe_path": str(ffprobe_path),
        "decode_log_path": str(decode_log_path),
        "contact_sheet_path": str(contact_sheet_path),
        "event_sheet_path": str(event_sheet_path),
        "keyframes_dir": str(keyframes_dir),
        "resolution_width": width,
        "resolution_height": height,
        "encoded_fps": fps,
        "duration_s": duration,
        "nb_frames": nb_frames,
        "sampled_indices": sampled_indices,
        "event_indices": event_indices,
        "mean_luma": mean_lumas,
        "dark_pixel_ratio": dark_ratios,
        "black_frame_fraction": float(np.mean(black_flags)) if black_flags else 1.0,
        "near_exact_repeat_fraction": near_exact_repeat_fraction,
        "max_static_run": max_static_run,
        "max_static_run_fraction": max_static_run_fraction,
        "near_exact_repeat_threshold": float(args.near_exact_repeat_threshold),
        "near_exact_repeat_fraction_threshold": float(args.near_exact_repeat_fraction_threshold),
        "near_exact_max_run_threshold": int(args.near_exact_max_run_threshold),
        "all_frame_count": len(all_grays),
        "mean_pair_diff": mean_pair_diff,
        "min_pair_diff": min_pair_diff,
        "median_pair_diff": median_pair_diff,
        "max_pair_diff": max_pair_diff,
        "encoding_gate_pass": bool(encoding_pass),
        "decode_gate_pass": bool(decode_pass),
        "black_screen_gate_pass": bool(black_screen_pass),
        "smoothness_gate_pass": bool(smoothness_pass),
        "manual_review": manual_review,
        "manual_review_complete": bool(manual_review_complete),
        "manual_gate_pass": bool(manual_gate_pass),
        "overall_gate_pass": bool(
            encoding_pass
            and decode_pass
            and black_screen_pass
            and smoothness_pass
            and manual_gate_pass
        ),
        "summary_metrics": {
            "task": summary.get("task"),
            "render_mode": summary.get("render_mode"),
            "first_contact_frame": summary.get("first_contact_frame"),
            "first_contact_time_s": summary.get("first_contact_time_s"),
            "first_contact_phase": summary.get("first_contact_phase"),
            "release_frame": summary.get("release_frame"),
            "contact_duration_s": summary.get("contact_duration_s"),
            "contact_active_frames": summary.get("contact_active_frames"),
            "contact_proxy_mode": summary.get("contact_proxy_mode"),
            "contact_peak_proxy": summary.get("contact_peak_proxy"),
            "min_clearance_min_m": summary.get("min_clearance_min_m"),
            "rope_com_displacement_m": summary.get("rope_com_displacement_m"),
            "rope_mid_segment_peak_z_delta_m": summary.get("rope_mid_segment_peak_z_delta_m"),
            "rope_mid_segment_final_z_delta_m": summary.get("rope_mid_segment_final_z_delta_m"),
            "gripper_center_tracking_error_mean_m": summary.get("gripper_center_tracking_error_mean_m"),
            "gripper_center_tracking_error_max_m": summary.get("gripper_center_tracking_error_max_m"),
            "gripper_center_path_length_m": summary.get("gripper_center_path_length_m"),
        },
    }
    _write_json(qa_dir / "validation.json", validation)

    verdict_lines = [
        "# Robot + Deformable Video Verdict",
        "",
        "## Automatic Gates",
        f"- Encoding gate: {'PASS' if encoding_pass else 'FAIL'}",
        f"- Decode gate: {'PASS' if decode_pass else 'FAIL'}",
        f"- Black-screen gate: {'PASS' if black_screen_pass else 'FAIL'}",
        f"- Smoothness gate: {'PASS' if smoothness_pass else 'FAIL'}",
        f"- Near-exact repeat fraction: {near_exact_repeat_fraction:.4f}",
        f"- Max near-exact repeat run: {max_static_run}",
        "",
        "## Files",
        f"- Video: `{video_path}`",
        f"- Summary: `{summary_path}`",
        f"- ffprobe: `{ffprobe_path}`",
        f"- Decode log: `{decode_log_path}`",
        f"- Contact sheet: `{contact_sheet_path}`",
        f"- Event sheet: `{event_sheet_path}`",
        "",
        "## Manual Review Questions",
        f"- Black or nearly black: {manual_review['black_or_nearly_black']}",
        f"- Robot and rope visible for most of the clip: {manual_review['robot_and_rope_visible_for_most_of_clip']}",
        f"- Contact region readable: {manual_review['contact_region_readable']}",
        f"- Task understandable in 15 seconds: {manual_review['task_understandable_in_15s']}",
        f"- Approach -> contact -> manipulation -> outcome visible: {manual_review['approach_contact_manipulation_outcome_visible']}",
        f"- Two-way coupling visually defensible: {manual_review['two_way_coupling_visually_defensible']}",
        f"- Camera presentation-ready: {manual_review['camera_presentation_ready']}",
        f"- Motion smooth enough: {manual_review['motion_smooth_enough']}",
        f"- Visible ground and support context: {manual_review['visible_ground_and_support_context']}",
        f"- Rope through table/support visible: {manual_review['rope_through_table_or_support_visible']}",
        "",
        "## Final Status",
        f"- Manual review complete: {'YES' if manual_review_complete else 'NO'}",
        f"- Manual gate: {'PASS' if manual_gate_pass else 'FAIL'}",
        f"- Overall gate: {'PASS' if validation['overall_gate_pass'] else 'FAIL'}",
    ]
    _write_markdown(qa_dir / "verdict.md", verdict_lines)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
