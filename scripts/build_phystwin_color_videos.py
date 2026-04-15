#!/usr/bin/env python3
"""Build per-camera mp4 files for PhysTwin raw cases from PNG frame folders."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


DEFAULT_BASE_PATH = Path("PhysTwin/data/different_types")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Encode PhysTwin color/<camera>/ PNG frames into sibling color/<camera>.mp4 files."
        )
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        default=DEFAULT_BASE_PATH,
        help=f"PhysTwin case root (default: {DEFAULT_BASE_PATH}).",
    )
    parser.add_argument(
        "--case",
        action="append",
        required=True,
        help="Case name to process. Repeat for multiple cases.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild mp4s even if they already exist.",
    )
    return parser.parse_args()


def load_fps(case_dir: Path) -> int:
    metadata_path = case_dir / "metadata.json"
    with metadata_path.open("r", encoding="utf-8") as f:
        metadata = json.load(f)
    fps = metadata.get("fps", 30)
    if not isinstance(fps, int) or fps <= 0:
        raise ValueError(f"Invalid fps in {metadata_path}: {fps!r}")
    return fps


def sorted_frame_indices(frame_dir: Path) -> list[int]:
    indices = sorted(
        int(path.stem)
        for path in frame_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".png" and path.stem.isdigit()
    )
    if not indices:
        raise FileNotFoundError(f"No numeric PNG frames found in {frame_dir}")
    expected = list(range(indices[0], indices[-1] + 1))
    if indices != expected:
        raise ValueError(
            f"Non-contiguous frames in {frame_dir}: first={indices[0]}, last={indices[-1]}"
        )
    return indices


def encode_video(frame_dir: Path, video_path: Path, fps: int) -> None:
    frame_indices = sorted_frame_indices(frame_dir)
    start_number = frame_indices[0]
    cmd = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-framerate",
        str(fps),
        "-start_number",
        str(start_number),
        "-i",
        str(frame_dir / "%d.png"),
        "-vcodec",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(video_path),
    ]
    subprocess.run(cmd, check=True)


def build_case(case_dir: Path, force: bool) -> None:
    if not case_dir.is_dir():
        raise FileNotFoundError(f"Case directory not found: {case_dir}")

    color_dir = case_dir / "color"
    if not color_dir.is_dir():
        raise FileNotFoundError(f"Missing color directory: {color_dir}")

    fps = load_fps(case_dir)
    camera_dirs = sorted(path for path in color_dir.iterdir() if path.is_dir() and path.name.isdigit())
    if not camera_dirs:
        raise FileNotFoundError(f"No numeric camera folders found in {color_dir}")

    for camera_dir in camera_dirs:
        video_path = color_dir / f"{camera_dir.name}.mp4"
        if video_path.exists() and not force:
            print(f"[skip] {video_path}")
            continue
        print(f"[build] {camera_dir} -> {video_path} @ {fps} fps")
        encode_video(camera_dir, video_path, fps)


def main() -> int:
    args = parse_args()
    base_path = args.base_path.resolve()
    for case_name in args.case:
        build_case(base_path / case_name, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
