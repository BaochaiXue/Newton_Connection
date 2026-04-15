#!/usr/bin/env python3
"""Build labeled native-vs-ffs 2x3 overlay comparison boards and GIFs."""

from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE_ROOT = (
    ROOT / "PhysTwin" / "archive_result" / "phystwin_four_new_cases_20260415"
)
DEFAULT_OUT_DIR = DEFAULT_ARCHIVE_ROOT / "comparison_boards"
FONT_FILE = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
GIF_MAX_BYTES = 50 * 1024 * 1024


@dataclass(frozen=True)
class PairSpec:
    slug: str
    title: str
    native_case: str
    ffs_case: str


PAIR_SPECS = (
    PairSpec(
        slug="base_motion_native_vs_ffs_overlay_2x3_labeled",
        title="Base Motion | Overlay Comparison | Native vs FFS",
        native_case="sloth_base_motion_native",
        ffs_case="sloth_base_motion_ffs",
    ),
    PairSpec(
        slug="set2_motion_native_vs_ffs_overlay_2x3_labeled",
        title="Set 2 Motion | Overlay Comparison | Native vs FFS",
        native_case="sloth_set_2_motion_native",
        ffs_case="sloth_set_2_motion_ffs",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build 2x3 overlay comparison boards (native row, ffs row; 3 camera columns) "
            "plus GIF exports."
        )
    )
    parser.add_argument(
        "--archive-root",
        type=Path,
        default=DEFAULT_ARCHIVE_ROOT,
        help=f"PhysTwin archive root (default: {DEFAULT_ARCHIVE_ROOT}).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help=f"Output directory for comparison boards (default: {DEFAULT_OUT_DIR}).",
    )
    return parser.parse_args()


def integrate_video_path(archive_root: Path, case_name: str, cam_idx: int) -> Path:
    video_dir = archive_root / "gaussian_output_dynamic_white" / case_name
    pattern = f"*_{case_name}_{cam_idx}_integrate.mp4"
    matches = sorted(video_dir.glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one integrate mp4 for {case_name} cam{cam_idx} under {video_dir}, found {len(matches)}"
        )
    return matches[0]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, cwd=str(ROOT))


def build_board(archive_root: Path, out_dir: Path, spec: PairSpec) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    board_mp4 = out_dir / f"{spec.slug}.mp4"
    board_gif = out_dir / f"{spec.slug}.gif"

    inputs = [
        integrate_video_path(archive_root, spec.native_case, 0),
        integrate_video_path(archive_root, spec.native_case, 1),
        integrate_video_path(archive_root, spec.native_case, 2),
        integrate_video_path(archive_root, spec.ffs_case, 0),
        integrate_video_path(archive_root, spec.ffs_case, 1),
        integrate_video_path(archive_root, spec.ffs_case, 2),
    ]
    cell_labels = (
        "Native | Cam 0",
        "Native | Cam 1",
        "Native | Cam 2",
        "FFS | Cam 0",
        "FFS | Cam 1",
        "FFS | Cam 2",
    )

    filter_parts: list[str] = []
    for idx, label in enumerate(cell_labels):
        filter_parts.append(
            (
                f"[{idx}:v]scale=426:240:flags=lanczos,"
                f"drawbox=x=0:y=0:w=iw:h=34:color=black@0.65:t=fill,"
                f"drawtext=fontfile='{FONT_FILE}':text='{label}':"
                f"fontcolor=white:fontsize=20:x=10:y=8[v{idx}]"
            )
        )

    stack_inputs = "".join(f"[v{idx}]" for idx in range(6))
    filter_parts.append(
        (
            f"{stack_inputs}xstack=inputs=6:"
            "layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0:"
            "fill=black[stack]"
        )
    )
    filter_parts.append(
        (
            "[stack]pad=iw:ih+48:0:48:color=black,"
            f"drawtext=fontfile='{FONT_FILE}':text='{spec.title}':"
            "fontcolor=white:fontsize=24:x=(w-text_w)/2:y=12[outv]"
        )
    )
    filter_complex = ";".join(filter_parts)

    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for input_path in inputs:
        cmd.extend(["-i", str(input_path)])
    cmd.extend(
        [
            "-filter_complex",
            filter_complex,
            "-map",
            "[outv]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(board_mp4),
        ]
    )
    run(cmd)

    gif_attempts = (
        (960, 10, 96),
        (900, 10, 96),
        (840, 9, 80),
        (760, 8, 80),
        (680, 8, 64),
    )
    for width, fps, colors in gif_attempts:
        run(
            [
                "bash",
                str(ROOT / "scripts" / "render_gif.sh"),
                str(board_mp4),
                str(board_gif),
                str(width),
                str(fps),
                str(colors),
            ]
        )
        if board_gif.stat().st_size < GIF_MAX_BYTES:
            break
    else:
        raise RuntimeError(
            f"Unable to compress GIF below {GIF_MAX_BYTES} bytes for {board_mp4}"
        )

    return board_mp4, board_gif


def main() -> int:
    args = parse_args()
    archive_root = args.archive_root.resolve()
    out_dir = args.out_dir.resolve()

    for spec in PAIR_SPECS:
        mp4_path, gif_path = build_board(archive_root, out_dir, spec)
        print(f"[board] mp4={mp4_path}")
        print(f"[board] gif={gif_path} size_bytes={gif_path.stat().st_size}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
