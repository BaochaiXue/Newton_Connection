#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
NEWTON_ROOT = ROOT / "Newton" / "newton"
if str(NEWTON_ROOT) not in sys.path:
    sys.path.insert(0, str(NEWTON_ROOT))

import warp as wp

import newton.examples
from newton._src.viewer.viewer_gl import ViewerGL
from newton.examples.robot.example_robot_panda_hydro import Example


def _ffmpeg_encode_mp4(width: int, height: int, fps: int, output_path: Path) -> subprocess.Popen[bytes]:
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{width}x{height}",
        "-r",
        str(fps),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def _make_gif(mp4_path: Path, gif_path: Path, fps: int = 15, width: int = 720) -> None:
    palette = gif_path.with_suffix(".palette.png")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp4_path),
            "-vf",
            f"fps={fps},scale={width}:-1:flags=lanczos,palettegen",
            str(palette),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp4_path),
            "-i",
            str(palette),
            "-lavfi",
            f"fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse",
            str(gif_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    palette.unlink(missing_ok=True)


def _save_contact_sheet(frames: list[np.ndarray], output_path: Path, cols: int = 3) -> None:
    if not frames:
        return
    h, w, _ = frames[0].shape
    rows = math.ceil(len(frames) / cols)
    canvas = Image.new("RGB", (cols * w, rows * h), (245, 245, 245))
    draw = ImageDraw.Draw(canvas)
    for idx, frame in enumerate(frames):
        r = idx // cols
        c = idx % cols
        image = Image.fromarray(frame)
        x = c * w
        y = r * h
        canvas.paste(image, (x, y))
        draw.rectangle((x, y, x + 110, y + 28), fill=(0, 0, 0))
        draw.text((x + 8, y + 6), f"frame {idx}", fill=(255, 255, 255))
    canvas.save(output_path)


def _describe_scene(scene: str) -> str:
    if scene == "pen":
        return "Franka Panda approaches a pen lying on the table, grasps it, lifts it, and places it into a cup."
    if scene == "cube":
        return "Franka Panda approaches a cube on the table, grasps it, lifts it, and places it into a cup."
    return "Franka Panda pick-and-place scene."


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the official Newton panda_hydro example to mp4/gif.")
    parser.add_argument("--scene", choices=["pen", "cube"], default="pen")
    parser.add_argument("--num-frames", type=int, default=720)
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--device", type=str, default="cuda:0")
    parser.add_argument("--world-count", type=int, default=1)
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    if args.device:
        wp.set_device(args.device)

    example_parser = Example.create_parser()
    example_args = newton.examples.default_args(example_parser)
    example_args.scene = args.scene
    example_args.world_count = args.world_count
    example_args.num_frames = args.num_frames
    example_args.headless = True
    example_args.viewer = "gl"
    example_args.test = False
    example_args.quiet = True
    example_args.device = args.device

    viewer = ViewerGL(width=args.width, height=args.height, headless=True)
    example = Example(viewer, example_args)

    mp4_path = args.outdir / "hero_presentation.mp4"
    gif_path = args.outdir / "hero_presentation.gif"
    sheet_path = args.outdir / "preview_contact_sheet.jpg"
    ffmpeg = _ffmpeg_encode_mp4(args.width, args.height, args.fps, mp4_path)
    if ffmpeg.stdin is None:
        raise RuntimeError("Failed to open ffmpeg stdin")

    preview_frames: list[np.ndarray] = []
    preview_indices = sorted(set(np.linspace(0, max(args.num_frames - 1, 0), 6, dtype=int).tolist()))

    try:
        for frame_idx in range(args.num_frames):
            example.step()
            example.render()
            frame = viewer.get_frame().numpy()
            ffmpeg.stdin.write(frame.tobytes())
            if frame_idx in preview_indices:
                preview_frames.append(frame.copy())
    finally:
        ffmpeg.stdin.close()
        ffmpeg.wait()
        viewer.close()

    _make_gif(mp4_path, gif_path)
    _save_contact_sheet(preview_frames, sheet_path)

    summary = {
        "example": "example_robot_panda_hydro.py",
        "scene": args.scene,
        "activity": _describe_scene(args.scene),
        "solver": 'SolverMuJoCo(use_mujoco_contacts=False, solver="newton", integrator="implicitfast", cone="elliptic")',
        "coupling": "two_way_rigid_contact",
        "num_frames": args.num_frames,
        "fps": args.fps,
        "resolution": [args.width, args.height],
        "artifacts": {
            "mp4": mp4_path.name,
            "gif": gif_path.name,
            "contact_sheet": sheet_path.name,
        },
    }
    (args.outdir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (args.outdir / "README.md").write_text(
        "\n".join(
            [
                "# Official Newton Example: Panda Hydro",
                "",
                f"- Scene: `{args.scene}`",
                f"- Activity: {summary['activity']}",
                f"- Solver: `{summary['solver']}`",
                "- Coupling: `two_way_rigid_contact`",
                "",
                "Artifacts:",
                f"- `{mp4_path.name}`",
                f"- `{gif_path.name}`",
                f"- `{sheet_path.name}`",
                f"- `summary.json`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
