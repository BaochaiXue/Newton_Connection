#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


DEFAULT_SAMPLE_PCTS = [5, 15, 25, 40, 55, 70, 82, 92, 98]


@dataclass
class FrameStats:
    index: int
    percentage: float
    timestamp_s: float
    mean_gray: float
    std_gray: float
    entropy_bits: float
    nonblack_fraction: float
    pass_black_blank: bool
    path: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="General bridge video QC with multi-frame veto checks.")
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, default=None)
    parser.add_argument(
        "--scene-profile",
        choices=["generic", "cloth_box", "parity_2x3", "parity_top_bottom"],
        default="generic",
    )
    parser.add_argument("--sample-percentages", default="5,15,25,40,55,70,82,92,98")
    parser.add_argument("--mean-gray-min", type=float, default=12.0)
    parser.add_argument("--mean-gray-max", type=float, default=245.0)
    parser.add_argument("--std-gray-min", type=float, default=8.0)
    parser.add_argument("--entropy-min", type=float, default=3.0)
    parser.add_argument("--nonblack-min", type=float, default=0.15)
    parser.add_argument("--black-threshold", type=int, default=10)
    parser.add_argument("--full-motion-min", type=float, default=2.0)
    parser.add_argument("--roi-motion-min", type=float, default=2.0)
    parser.add_argument("--roi-nonblack-min", type=float, default=0.03)
    return parser.parse_args()


def _effective_black_blank_thresholds(args: argparse.Namespace) -> dict[str, float]:
    thresholds = {
        "mean_gray_min": float(args.mean_gray_min),
        "mean_gray_max": float(args.mean_gray_max),
        "std_gray_min": float(args.std_gray_min),
        "entropy_min": float(args.entropy_min),
        "nonblack_min": float(args.nonblack_min),
    }
    # Clean presentation renders for cloth-box and parity overlays are often
    # bright and intentionally minimal. In these scenes, full-frame entropy is
    # systematically lower than the bunny-force diagnostic clips even when the
    # objects and process are clearly visible. Keep the std/non-black gates
    # intact, but use scene-specific entropy floors.
    if args.scene_profile == "cloth_box":
        thresholds["entropy_min"] = min(thresholds["entropy_min"], 2.2)
    elif args.scene_profile == "parity_2x3":
        thresholds["entropy_min"] = min(thresholds["entropy_min"], 2.0)
    elif args.scene_profile == "parity_top_bottom":
        thresholds["entropy_min"] = min(thresholds["entropy_min"], 2.0)
    return thresholds


def _open_video(path: Path) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {path}")
    return cap


def _read_frame(cap: cv2.VideoCapture, index: int) -> np.ndarray:
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(index))
    ok, frame = cap.read()
    if not ok or frame is None:
        raise RuntimeError(f"Failed to read frame {index}")
    return frame


def _sample_indices(frame_count: int, percentages: list[float]) -> list[int]:
    if frame_count <= 1:
        return [0]
    out: list[int] = []
    seen: set[int] = set()
    for pct in percentages:
        idx = int(round((max(0.0, min(100.0, pct)) / 100.0) * float(frame_count - 1)))
        idx = max(0, min(frame_count - 1, idx))
        if idx not in seen:
            seen.add(idx)
            out.append(idx)
    return out


def _entropy_bits(gray: np.ndarray) -> float:
    hist, _ = np.histogram(gray, bins=32, range=(0, 256))
    total = float(np.sum(hist))
    if total <= 0.0:
        return 0.0
    probs = hist.astype(np.float64) / total
    probs = probs[probs > 0.0]
    return float(-np.sum(probs * np.log2(probs)))


def _gray(frame_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)


def _frame_stats(
    gray: np.ndarray,
    *,
    black_threshold: int,
    mean_gray_min: float,
    mean_gray_max: float,
    std_gray_min: float,
    entropy_min: float,
    nonblack_min: float,
) -> tuple[float, float, float, float, bool]:
    mean_gray = float(np.mean(gray))
    std_gray = float(np.std(gray))
    entropy_bits = _entropy_bits(gray)
    nonblack_fraction = float(np.mean(gray > int(black_threshold)))
    frame_pass = (
        mean_gray_min <= mean_gray <= mean_gray_max
        and std_gray >= std_gray_min
        and entropy_bits >= entropy_min
        and nonblack_fraction >= nonblack_min
    )
    return mean_gray, std_gray, entropy_bits, nonblack_fraction, bool(frame_pass)


def _roi(gray: np.ndarray, x0f: float, y0f: float, x1f: float, y1f: float) -> np.ndarray:
    h, w = gray.shape
    x0 = max(0, min(w - 1, int(round(x0f * w))))
    x1 = max(x0 + 1, min(w, int(round(x1f * w))))
    y0 = max(0, min(h - 1, int(round(y0f * h))))
    y1 = max(y0 + 1, min(h, int(round(y1f * h))))
    return gray[y0:y1, x0:x1]


def _motion(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a.astype(np.float32) - b.astype(np.float32))))


def _cloth_box_checks(
    sampled_gray: list[np.ndarray],
    args: argparse.Namespace,
) -> tuple[bool, dict[str, float | bool]]:
    early = sampled_gray[0]
    mid = sampled_gray[len(sampled_gray) // 2]
    late = sampled_gray[-1]
    top_early = _roi(early, 0.20, 0.05, 0.80, 0.55)
    support_early = _roi(early, 0.20, 0.35, 0.80, 0.92)
    contact_early = _roi(early, 0.25, 0.45, 0.75, 0.82)
    contact_mid = _roi(mid, 0.25, 0.45, 0.75, 0.82)
    support_late = _roi(late, 0.20, 0.35, 0.80, 0.92)

    top_early_nonblack = float(np.mean(top_early > int(args.black_threshold)))
    support_early_nonblack = float(np.mean(support_early > int(args.black_threshold)))
    support_late_nonblack = float(np.mean(support_late > int(args.black_threshold)))
    early_mid_contact_motion = _motion(contact_early, contact_mid)
    mid_late_full_motion = _motion(mid, late)

    checks = {
        "early_top_visible": top_early_nonblack >= float(args.roi_nonblack_min),
        "early_support_visible": support_early_nonblack >= float(args.roi_nonblack_min),
        "late_support_visible": support_late_nonblack >= float(args.roi_nonblack_min),
        "early_mid_contact_motion": early_mid_contact_motion >= float(args.roi_motion_min),
        "mid_late_full_motion": mid_late_full_motion >= float(args.full_motion_min),
        "top_early_nonblack": top_early_nonblack,
        "support_early_nonblack": support_early_nonblack,
        "support_late_nonblack": support_late_nonblack,
        "early_mid_contact_motion_value": early_mid_contact_motion,
        "mid_late_full_motion_value": mid_late_full_motion,
    }
    passed = bool(
        checks["early_top_visible"]
        and checks["early_support_visible"]
        and checks["late_support_visible"]
        and checks["early_mid_contact_motion"]
        and checks["mid_late_full_motion"]
    )
    return passed, checks


def _parity_2x3_checks(
    sampled_gray: list[np.ndarray],
    args: argparse.Namespace,
) -> tuple[bool, dict[str, float | bool]]:
    early = sampled_gray[0]
    mid = sampled_gray[len(sampled_gray) // 2]
    late = sampled_gray[-1]
    top_early = _roi(early, 0.0, 0.0, 1.0, 0.48)
    bot_early = _roi(early, 0.0, 0.52, 1.0, 1.0)
    top_late = _roi(late, 0.0, 0.0, 1.0, 0.48)
    bot_late = _roi(late, 0.0, 0.52, 1.0, 1.0)

    top_early_nonblack = float(np.mean(top_early > int(args.black_threshold)))
    bot_early_nonblack = float(np.mean(bot_early > int(args.black_threshold)))
    top_late_nonblack = float(np.mean(top_late > int(args.black_threshold)))
    bot_late_nonblack = float(np.mean(bot_late > int(args.black_threshold)))
    early_mid_motion = _motion(early, mid)
    mid_late_motion = _motion(mid, late)

    checks = {
        "top_early_visible": top_early_nonblack >= float(args.roi_nonblack_min),
        "bottom_early_visible": bot_early_nonblack >= float(args.roi_nonblack_min),
        "top_late_visible": top_late_nonblack >= float(args.roi_nonblack_min),
        "bottom_late_visible": bot_late_nonblack >= float(args.roi_nonblack_min),
        "early_mid_motion": early_mid_motion >= float(args.full_motion_min),
        "mid_late_motion": mid_late_motion >= float(args.full_motion_min),
        "top_early_nonblack": top_early_nonblack,
        "bottom_early_nonblack": bot_early_nonblack,
        "top_late_nonblack": top_late_nonblack,
        "bottom_late_nonblack": bot_late_nonblack,
        "early_mid_motion_value": early_mid_motion,
        "mid_late_motion_value": mid_late_motion,
    }
    passed = bool(
        checks["top_early_visible"]
        and checks["bottom_early_visible"]
        and checks["top_late_visible"]
        and checks["bottom_late_visible"]
        and checks["early_mid_motion"]
        and checks["mid_late_motion"]
    )
    return passed, checks


def _parity_top_bottom_checks(
    sampled_gray: list[np.ndarray],
    args: argparse.Namespace,
) -> tuple[bool, dict[str, float | bool]]:
    early = sampled_gray[0]
    mid = sampled_gray[len(sampled_gray) // 2]
    late = sampled_gray[-1]
    top_early = _roi(early, 0.0, 0.0, 1.0, 0.48)
    bot_early = _roi(early, 0.0, 0.52, 1.0, 1.0)
    top_late = _roi(late, 0.0, 0.0, 1.0, 0.48)
    bot_late = _roi(late, 0.0, 0.52, 1.0, 1.0)

    top_early_nonblack = float(np.mean(top_early > int(args.black_threshold)))
    bot_early_nonblack = float(np.mean(bot_early > int(args.black_threshold)))
    top_late_nonblack = float(np.mean(top_late > int(args.black_threshold)))
    bot_late_nonblack = float(np.mean(bot_late > int(args.black_threshold)))
    early_mid_motion = _motion(early, mid)
    mid_late_motion = _motion(mid, late)

    checks = {
        "top_early_visible": top_early_nonblack >= float(args.roi_nonblack_min),
        "bottom_early_visible": bot_early_nonblack >= float(args.roi_nonblack_min),
        "top_late_visible": top_late_nonblack >= float(args.roi_nonblack_min),
        "bottom_late_visible": bot_late_nonblack >= float(args.roi_nonblack_min),
        "early_mid_motion": early_mid_motion >= float(args.full_motion_min),
        "mid_late_motion": mid_late_motion >= float(args.full_motion_min),
        "top_early_nonblack": top_early_nonblack,
        "bottom_early_nonblack": bot_early_nonblack,
        "top_late_nonblack": top_late_nonblack,
        "bottom_late_nonblack": bot_late_nonblack,
        "early_mid_motion_value": early_mid_motion,
        "mid_late_motion_value": mid_late_motion,
    }
    passed = bool(
        checks["top_early_visible"]
        and checks["bottom_early_visible"]
        and checks["top_late_visible"]
        and checks["bottom_late_visible"]
        and checks["early_mid_motion"]
        and checks["mid_late_motion"]
    )
    return passed, checks


def _build_contact_sheet(
    out_path: Path,
    samples: list[FrameStats],
    summary: dict[str, object],
    *,
    video_name: str,
) -> None:
    tile_w = 320
    frame_h = 180
    caption_h = 82
    pad = 16
    columns = 3
    rows = max(1, math.ceil(len(samples) / columns))
    width = columns * tile_w + (columns + 1) * pad
    header_h = 160
    height = header_h + rows * (frame_h + caption_h + pad) + pad
    canvas = Image.new("RGB", (width, height), (24, 24, 24))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    lines = [
        f"Bridge Video QC: {video_name}",
        f"scene_profile={summary['scene_profile']} verdict={summary['verdict']}",
        f"black_blank={summary['black_blank_pass']} motion={summary['motion_pass']} scene={summary['scene_visibility_pass']}",
        f"frames={summary['frame_count']} fps={summary['fps']:.2f} duration={summary['duration_s']:.2f}s",
    ]
    y = pad
    for line in lines:
        draw.text((pad, y), line, fill=(245, 245, 245), font=font)
        y += 22

    for i, sample in enumerate(samples):
        row = i // columns
        col = i % columns
        x = pad + col * (tile_w + pad)
        y0 = header_h + row * (frame_h + caption_h + pad)
        with Image.open(sample.path) as img:
            tile = Image.new("RGB", (tile_w, frame_h + caption_h), (36, 36, 36))
            fitted = ImageOps.contain(img.convert("RGB"), (tile_w, frame_h))
            fx = (tile_w - fitted.width) // 2
            fy = (frame_h - fitted.height) // 2
            tile.paste(fitted, (fx, fy))
            tdraw = ImageDraw.Draw(tile)
            border = (110, 190, 120) if sample.pass_black_blank else (205, 75, 75)
            tdraw.rectangle([0, 0, tile_w - 1, frame_h - 1], outline=border, width=3)
            captions = [
                f"{sample.percentage:.0f}% idx={sample.index} t={sample.timestamp_s:.2f}s",
                f"mean={sample.mean_gray:.1f} std={sample.std_gray:.1f}",
                f"ent={sample.entropy_bits:.2f} nonblack={sample.nonblack_fraction:.2f}",
            ]
            cap_y = frame_h + 6
            for line in captions:
                tdraw.text((8, cap_y), line, fill=(240, 240, 240), font=font)
                cap_y += 18
            canvas.paste(tile, (x, y0))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)


def _write_verdict_md(path: Path, payload: dict[str, object]) -> None:
    lines = [
        "# Bridge Video QC Verdict",
        "",
        f"- Video: `{payload['video']}`",
        f"- Scene profile: `{payload['scene_profile']}`",
        f"- Verdict: **{payload['verdict']}**",
        f"- Black / blank pass: `{payload['black_blank_pass']}`",
        f"- Motion pass: `{payload['motion_pass']}`",
        f"- Scene visibility pass: `{payload['scene_visibility_pass']}`",
        f"- Contact sheet: `{payload['contact_sheet']}`",
        "",
        "## Failure reasons",
    ]
    reasons = payload.get("failure_reasons", [])
    if reasons:
        lines.extend([f"- {reason}" for reason in reasons])
    else:
        lines.append("- none")
    lines.extend(["", "## Scene checks", ""])
    for key, value in sorted(dict(payload.get("scene_checks", {})).items()):
        lines.append(f"- `{key}`: `{value}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    video_path = args.video.expanduser().resolve()
    out_dir = args.out_dir.expanduser().resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    summary_json = None
    if args.summary_json is not None:
        summary_json = json.loads(args.summary_json.expanduser().resolve().read_text(encoding="utf-8"))
    black_blank_thresholds = _effective_black_blank_thresholds(args)

    percentages = [float(part.strip()) for part in str(args.sample_percentages).split(",") if part.strip()]
    cap = _open_video(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0) or 30.0
    duration_s = frame_count / fps if fps > 0.0 else 0.0
    indices = _sample_indices(frame_count, percentages)

    samples: list[FrameStats] = []
    sampled_gray: list[np.ndarray] = []
    for pct, idx in zip(percentages, indices):
        frame = _read_frame(cap, idx)
        gray = _gray(frame)
        sampled_gray.append(gray)
        sample_path = frames_dir / f"frame_{idx:06d}.png"
        Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).save(sample_path)
        mean_gray, std_gray, entropy_bits, nonblack_fraction, frame_pass = _frame_stats(
            gray,
            black_threshold=int(args.black_threshold),
            mean_gray_min=float(black_blank_thresholds["mean_gray_min"]),
            mean_gray_max=float(black_blank_thresholds["mean_gray_max"]),
            std_gray_min=float(black_blank_thresholds["std_gray_min"]),
            entropy_min=float(black_blank_thresholds["entropy_min"]),
            nonblack_min=float(black_blank_thresholds["nonblack_min"]),
        )
        samples.append(
            FrameStats(
                index=int(idx),
                percentage=float(pct),
                timestamp_s=float(idx / fps if fps > 0.0 else idx),
                mean_gray=mean_gray,
                std_gray=std_gray,
                entropy_bits=entropy_bits,
                nonblack_fraction=nonblack_fraction,
                pass_black_blank=bool(frame_pass),
                path=str(sample_path),
            )
        )
    cap.release()

    black_blank_pass = bool(all(sample.pass_black_blank for sample in samples))
    pairwise_motion = [
        _motion(sampled_gray[i - 1], sampled_gray[i]) for i in range(1, len(sampled_gray))
    ]
    early_mid_motion = _motion(sampled_gray[0], sampled_gray[len(sampled_gray) // 2]) if len(sampled_gray) >= 3 else 0.0
    mid_late_motion = _motion(sampled_gray[len(sampled_gray) // 2], sampled_gray[-1]) if len(sampled_gray) >= 3 else 0.0
    motion_pass = bool(
        pairwise_motion
        and max(pairwise_motion) >= float(args.full_motion_min)
        and early_mid_motion >= float(args.full_motion_min)
        and mid_late_motion >= float(args.full_motion_min)
    )

    scene_checks: dict[str, object] = {}
    if args.scene_profile == "cloth_box":
        scene_visibility_pass, scene_checks = _cloth_box_checks(sampled_gray, args)
    elif args.scene_profile == "parity_2x3":
        scene_visibility_pass, scene_checks = _parity_2x3_checks(sampled_gray, args)
    elif args.scene_profile == "parity_top_bottom":
        scene_visibility_pass, scene_checks = _parity_top_bottom_checks(sampled_gray, args)
    else:
        scene_visibility_pass = motion_pass
        scene_checks = {}

    failure_reasons: list[str] = []
    if not black_blank_pass:
        failure_reasons.append("black_blank_failed")
    if not motion_pass:
        failure_reasons.append("motion_failed")
    if not scene_visibility_pass:
        failure_reasons.append("scene_visibility_failed")

    verdict = "PASS" if not failure_reasons else "FAIL"
    contact_sheet = out_dir / "contact_sheet.png"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "video": str(video_path),
        "scene_profile": str(args.scene_profile),
        "summary_json": None if args.summary_json is None else str(args.summary_json.expanduser().resolve()),
        "frame_count": int(frame_count),
        "fps": float(fps),
        "duration_s": float(duration_s),
        "black_blank_thresholds": black_blank_thresholds,
        "sampled_indices": [int(i) for i in indices],
        "sample_percentages": [float(p) for p in percentages[: len(indices)]],
        "black_blank_pass": bool(black_blank_pass),
        "motion_pass": bool(motion_pass),
        "scene_visibility_pass": bool(scene_visibility_pass),
        "pairwise_motion": [float(v) for v in pairwise_motion],
        "early_mid_motion": float(early_mid_motion),
        "mid_late_motion": float(mid_late_motion),
        "scene_checks": scene_checks,
        "verdict": verdict,
        "failure_reasons": failure_reasons,
        "samples": [asdict(sample) for sample in samples],
        "contact_sheet": str(contact_sheet),
        "summary_excerpt": {
            key: summary_json[key]
            for key in (
                "self_contact_mode",
                "frames",
                "particle_radius_median_m",
                "peak_nonexcluded_self_contact_p95_overlap_m_over_time",
                "final_penetration_p99_box_m",
                "render_video",
            )
            if isinstance(summary_json, dict) and key in summary_json
        },
    }
    _build_contact_sheet(contact_sheet, samples, payload, video_name=video_path.name)
    (out_dir / "video_qc.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_verdict_md(out_dir / "verdict.md", payload)
    _write_verdict_md(out_dir / "video_qc.md", payload)
    (out_dir / "README.md").write_text(
        "\n".join(
            [
                "# Bridge Video QC",
                "",
                f"- video: `{video_path}`",
                f"- scene profile: `{args.scene_profile}`",
                f"- summary: `{out_dir / 'video_qc.json'}`",
                f"- verdict: `{out_dir / 'video_qc.md'}`",
                f"- contact sheet: `{contact_sheet}`",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
