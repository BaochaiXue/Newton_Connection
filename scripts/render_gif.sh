#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <input.mp4> <output.gif> [width] [fps] [max_colors]" >&2
  exit 1
fi

IN_MP4="$1"
OUT_GIF="$2"
WIDTH="${3:-960}"
FPS="${4:-10}"
MAX_COLORS="${5:-128}"

ffmpeg -y -loglevel error \
  -i "${IN_MP4}" \
  -vf "fps=${FPS},scale=${WIDTH}:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=${MAX_COLORS}:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4" \
  -loop 0 \
  "${OUT_GIF}"
