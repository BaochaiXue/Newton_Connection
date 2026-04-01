#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


PANEL_CROP = {
    "box_penalty": "0:0",
    "box_total": "iw/2:0",
    "bunny_penalty": "0:ih/2",
    "bunny_total": "iw/2:ih/2",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export four single-panel mp4s from a bunny 2x2 collision board video."
    )
    parser.add_argument("--board-summary", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=None)
    return parser.parse_args()


def _run_ffmpeg(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")


def main() -> int:
    args = parse_args()
    summary_path = args.board_summary.expanduser().resolve()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    board_video = Path(str(summary["board_video"])).expanduser().resolve()
    if not board_video.exists():
        raise FileNotFoundError(f"missing board video: {board_video}")

    out_dir = (
        args.out_dir.expanduser().resolve()
        if args.out_dir is not None
        else summary_path.parent / "panels"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg not found in PATH")

    panel_w = int(summary.get("panel_width", int(summary["board_width"]) // 2))
    panel_h = int(summary.get("panel_height", int(summary["board_height"]) // 2))

    outputs: dict[str, str] = {}
    for panel_name, origin in PANEL_CROP.items():
        out_path = out_dir / f"{panel_name}.mp4"
        crop = f"crop={panel_w}:{panel_h}:{origin}"
        cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(board_video),
            "-vf",
            crop,
            "-an",
            "-vcodec",
            "libx264",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            str(out_path),
        ]
        _run_ffmpeg(cmd)
        outputs[panel_name] = str(out_path)

    panel_summary = {
        "source_board_summary": str(summary_path),
        "source_board_video": str(board_video),
        "panel_width": panel_w,
        "panel_height": panel_h,
        "outputs": outputs,
    }
    (out_dir / "summary.json").write_text(json.dumps(panel_summary, indent=2), encoding="utf-8")
    print(f"[export_bunny_collision_board_panels] out_dir={out_dir}")
    for name, path in outputs.items():
        print(f"[export_bunny_collision_board_panels] {name}={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
