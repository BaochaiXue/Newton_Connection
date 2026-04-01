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
PANEL_GIF_PROFILES = [
    (960, 15, 224),
    (960, 12, 192),
    (896, 12, 192),
    (832, 10, 160),
    (768, 10, 160),
    (640, 8, 128),
]
PANEL_GIF_MAX_MB = 40.0


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


def _render_gif_from_video(
    *,
    ffmpeg: str,
    src_video: Path,
    gif_path: Path,
    quality_profiles: list[tuple[int, int, int]],
    max_size_mb: float,
) -> Path:
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path = gif_path.with_suffix(f"{gif_path.suffix}.meta.json")
    signature = {
        "profiles": [[int(w), int(f), int(c)] for w, f, c in quality_profiles],
        "max_size_mb": float(max_size_mb),
        "palette_stats_mode": "full",
        "palette_dither": "sierra2_4a",
    }
    if gif_path.exists() and meta_path.exists() and gif_path.stat().st_mtime >= src_video.stat().st_mtime:
        try:
            meta_obj = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta_obj = {}
        if meta_obj.get("signature") == signature:
            return gif_path

    budget_bytes = int(round(float(max_size_mb) * 1_000_000.0))
    candidate_path = gif_path.with_name(f"{gif_path.stem}.tmp{gif_path.suffix}")
    chosen_profile: list[int] | None = None
    chosen_size = 0
    for render_width, render_fps, render_colors in quality_profiles:
        cmd = [
            ffmpeg,
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(src_video),
            "-vf",
            (
                f"fps={int(render_fps)},scale={int(render_width)}:-1:flags=lanczos,"
                f"split[s0][s1];[s0]palettegen=max_colors={int(render_colors)}:stats_mode=full[p];"
                "[s1][p]paletteuse=dither=sierra2_4a"
            ),
            "-loop",
            "0",
            str(candidate_path),
        ]
        _run_ffmpeg(cmd)
        chosen_profile = [int(render_width), int(render_fps), int(render_colors)]
        chosen_size = int(candidate_path.stat().st_size)
        if chosen_size <= budget_bytes:
            break

    candidate_path.replace(gif_path)
    meta_path.write_text(
        json.dumps(
            {
                "signature": signature,
                "chosen_profile": chosen_profile,
                "size_bytes": chosen_size,
                "source": str(src_video),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return gif_path


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
    output_gifs: dict[str, str] = {}
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
        gif_path = _render_gif_from_video(
            ffmpeg=ffmpeg,
            src_video=out_path,
            gif_path=out_dir / f"{panel_name}.gif",
            quality_profiles=PANEL_GIF_PROFILES,
            max_size_mb=PANEL_GIF_MAX_MB,
        )
        output_gifs[panel_name] = str(gif_path)

    panel_summary = {
        "source_board_summary": str(summary_path),
        "source_board_video": str(board_video),
        "panel_width": panel_w,
        "panel_height": panel_h,
        "outputs": outputs,
        "output_gifs": output_gifs,
    }
    (out_dir / "summary.json").write_text(json.dumps(panel_summary, indent=2), encoding="utf-8")
    print(f"[export_bunny_collision_board_panels] out_dir={out_dir}")
    for name, path in outputs.items():
        print(f"[export_bunny_collision_board_panels] {name}={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
