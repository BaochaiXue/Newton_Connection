#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WRAPPER="${ROOT}/scripts/run_robot_table_rope_split_demo.sh"
STAMP="$(date +%Y%m%d_%H%M%S)"
DEFAULT_OUT_DIR="${ROOT}/tmp/robot_table_rope_split_support_sweep_${STAMP}"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") [out_dir] [extra args...]

Examples:
  $(basename "$0")
  $(basename "$0") ${ROOT}/tmp/robot_table_rope_split_support_default --width 960 --height 540

This wrapper:
  1. searches support-only candidates on the truthful split demo path
  2. runs the selected candidate end-to-end

Artifacts will be written inside:
  <out_dir>/
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

OUT_DIR="${1:-${DEFAULT_OUT_DIR}}"
if [[ $# -gt 0 ]]; then
  shift
fi

exec bash "${WRAPPER}" "${OUT_DIR}" \
  --num-frames 30 \
  --coupling-mode one_way \
  --auto-calibrate-support \
  "$@"
