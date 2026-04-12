#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SCENE="${1:-pen}"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUTDIR="$ROOT/Newton/phystwin_bridge/results/official_examples/panda_hydro/${STAMP}_${SCENE}"
mkdir -p "$OUTDIR"

CMD=(
  python scripts/render_official_newton_example_panda_hydro.py
  --scene "$SCENE"
  --num-frames 720
  --width 960
  --height 540
  --fps 60
  --outdir "$OUTDIR"
  --device cuda:0
)

printf '%q ' "${CMD[@]}" > "$OUTDIR/command.txt"
printf '\n' >> "$OUTDIR/command.txt"
"${CMD[@]}"

echo "$OUTDIR"
