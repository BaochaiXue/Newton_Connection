#!/usr/bin/env bash
set -euo pipefail

# =========================
# User-configurable options
# =========================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${ROOT:-$SCRIPT_DIR}"
PT="$ROOT/PhysTwin"
NW="$ROOT/Newton"
NW_PY="$NW/newton/.venv/bin/python"
ENV_PS=ps
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d_%H%M%S)}"
# 1 = run full PhysTwin (CMA + train + inference), 0 = reuse existing case files and run Newton-side import/validation/render only.
# Default to import-only mode (no PhysTwin retraining).
# Set RUN_FULL_PHYSTWIN=1 explicitly when full PhysTwin pipeline is needed.
# Import-only mode requires checkpoint topology fields to already exist.
RUN_FULL_PHYSTWIN="${RUN_FULL_PHYSTWIN:-0}"
CONDA_BIN="${CONDA_BIN:-}"
if [ -z "$CONDA_BIN" ]; then
  CONDA_BIN="$(command -v conda || true)"
fi
if [ -z "$CONDA_BIN" ] && [ -x "$HOME/miniconda3/bin/conda" ]; then
  CONDA_BIN="$HOME/miniconda3/bin/conda"
fi
if [ -z "$CONDA_BIN" ] && [ -x "$HOME/anaconda3/bin/conda" ]; then
  CONDA_BIN="$HOME/anaconda3/bin/conda"
fi
if [ -z "$CONDA_BIN" ]; then
  echo "[ERROR] Unable to find conda executable. Set CONDA_BIN explicitly."
  exit 2
fi

CLOTH_CASE=blue_cloth_double_lift_around
CLOTH_TRAIN_FRAME=211
ZEBRA_CASE=zebra_around_hard
ZEBRA_TRAIN_FRAME=368

# =========================
# Helpers
# =========================
kill_stale_waiters() {
  pkill -f "rerun_pipeline_post_cloth.log" || true
  pkill -f "still waiting cloth train" || true
  pkill -f "while pgrep -af \"python train_warp.py --base_path data/different_types --case_name ${CLOTH_CASE} --train_frame ${CLOTH_TRAIN_FRAME}\"" || true
}

is_timestamp_or_legacy_dir() {
  local name="$1"
  [[ "$name" =~ ^legacy_[0-9]{8}_[0-9]{6}([_-][A-Za-z0-9._-]+)?$ ]] && return 0
  [[ "$name" =~ ^[0-9]{8}_[0-9]{4,6}([_-][A-Za-z0-9._-]+)?$ ]] && return 0
  return 1
}

archive_nonconforming_case_outputs() {
  local case_name="$1"
  local case_out_root="$NW/phystwin_bridge/outputs/$case_name"
  local legacy_dir="$case_out_root/legacy_${RUN_TIMESTAMP}_cleanup"
  local moved=0

  mkdir -p "$case_out_root"
  shopt -s nullglob dotglob
  for entry in "$case_out_root"/*; do
    [ -e "$entry" ] || continue
    local base
    base=$(basename "$entry")

    # Keep timestamped run dirs and existing legacy dirs in place.
    if [ -d "$entry" ] && is_timestamp_or_legacy_dir "$base"; then
      continue
    fi

    mkdir -p "$legacy_dir"
    mv "$entry" "$legacy_dir/"
    moved=1
  done
  shopt -u nullglob dotglob

  if [ "$moved" -eq 1 ]; then
    echo "[cleanup] Archived nonconforming outputs for $case_name -> $legacy_dir"
  fi
}

run_case_full() {
  local case_name="$1"
  local train_frame="$2"
  cd "$PT"
  "$CONDA_BIN" run --no-capture-output -n "$ENV_PS" python optimize_cma.py \
    --base_path data/different_types --case_name "$case_name" --train_frame "$train_frame"
  "$CONDA_BIN" run --no-capture-output -n "$ENV_PS" python train_warp.py \
    --base_path data/different_types --case_name "$case_name" --train_frame "$train_frame"
  "$CONDA_BIN" run --no-capture-output -n "$ENV_PS" python inference_warp.py \
    --base_path data/different_types --case_name "$case_name"
}

copy_case_to_newton() {
  local case_name="$1"
  local src_case="$PT/data/different_types/$case_name"
  local src_exp="$PT/experiments/$case_name"
  local src_opt="$PT/experiments_optimization/$case_name"
  local dst="$NW/phystwin_bridge/inputs/cases/$case_name"

  mkdir -p "$dst"
  local best
  best=$(ls "$src_exp"/train/best_*.pth | sort -V | tail -n 1)

  cp -f "$best"                       "$dst/best.pth"
  cp -f "$src_opt/optimal_params.pkl" "$dst/optimal_params.pkl"
  cp -f "$src_exp/inference.pkl"      "$dst/inference.pkl"
  cp -f "$src_case/final_data.pkl"    "$dst/final_data.pkl"
  cp -f "$src_case/calibrate.pkl"     "$dst/calibrate.pkl"
  cp -f "$src_case/metadata.json"     "$dst/metadata.json"
  if [ -f "$src_exp/topology.npz" ]; then
    cp -f "$src_exp/topology.npz"     "$dst/topology.npz"
  fi
}

topology_sidecar_ready() {
  local topology_path="$1"
  "$CONDA_BIN" run --no-capture-output -n "$ENV_PS" python - "$topology_path" <<'PY'
import sys
import numpy as np
from pathlib import Path

topology_path = Path(sys.argv[1])

has_topology_sidecar = False
if topology_path.exists():
    with np.load(topology_path, allow_pickle=False) as topo:
        has_topology_sidecar = (
            "spring_edges" in topo
            and ("spring_rest_lengths" in topo or "spring_rest_length" in topo)
        )

if has_topology_sidecar:
    print(f"[topology-check] OK via sidecar: {topology_path}")
    raise SystemExit(0)

print(f"[topology-check] missing/invalid topology sidecar: {topology_path}")
raise SystemExit(1)
PY
}

run_newton_case() {
  local case_name="$1"
  local cfg_name="$2"

  local case_dir="$NW/phystwin_bridge/inputs/cases/$case_name"
  local case_out_root="$NW/phystwin_bridge/outputs/$case_name"
  local topology_path="$case_dir/topology.npz"
  local out_dir="$case_out_root/$RUN_TIMESTAMP"
  local ir_path="$out_dir/${case_name}_ir.npz"
  local prefix="semi_native_${case_name}"
  local report_path="$out_dir/${prefix}_rollout_report.json"
  local video_2x3="$out_dir/${prefix}_cmp_2x3_labeled.mp4"
  local video_1x3="$out_dir/${prefix}_overlay_1x3_labeled.mp4"
  local result_json="$out_dir/result.json"
  local result_csv="$out_dir/result.csv"
  mkdir -p "$out_dir"

  if ! topology_sidecar_ready "$topology_path"; then
    echo "[ERROR] Case '$case_name' missing usable topology sidecar: $topology_path"
    echo "[ERROR] export_ir.py now reads topology only from topology.npz."
    echo "[ERROR] Rerun PhysTwin inference/export_topology and copy topology sidecar to Newton inputs."
    if [ "$RUN_FULL_PHYSTWIN" != "1" ]; then
      echo "[ERROR] Re-run this script with RUN_FULL_PHYSTWIN=1."
    fi
    return 2
  fi

  "$CONDA_BIN" run --no-capture-output -n "$ENV_PS" python "$NW/phystwin_bridge/tools/core/export_ir.py" \
    --case-dir "$case_dir" \
    --config "$NW/phystwin_bridge/inputs/configs/$cfg_name" \
    --out "$ir_path" \
    --topology "$topology_path" \
    --spring-ke-mode y_over_rest

  local validate_status=0
  set +e
  "$NW_PY" "$NW/phystwin_bridge/tools/core/validate_parity.py" \
    --ir "$ir_path" \
    --out-dir "$out_dir" \
    --output-prefix "$prefix" \
    --python "$NW_PY" \
    --importer "$NW/phystwin_bridge/tools/core/newton_import_ir.py" \
    --threshold-config "$NW/phystwin_bridge/inputs/configs/parity_thresholds.yaml" \
    --threshold-case "$case_name"
  validate_status=$?
  set -e

  if [ ! -f "$report_path" ]; then
    echo "[ERROR] Missing rollout report: $report_path"
    return "${validate_status}"
  fi

  PHYSTWIN_OVERLAY_BASE="$PT/data/different_types" \
  "$NW_PY" "$NW/phystwin_bridge/tools/other/render_comparison_2x3_mp4.py" \
    --report "$report_path" \
    --python "$NW_PY" \
    --visualizer "$NW/phystwin_bridge/tools/other/visualize_rollout_mp4.py" \
    --camera-indices 0,1,2 \
    --newton-label "Newton Rollout (SemiImplicit)" \
    --phystwin-label "PhysTwin Rollout" \
    --out-mp4 "$video_2x3"

  "$NW_PY" "$NW/phystwin_bridge/tools/other/render_overlay_1x3_diff_mp4.py" \
    --report "$report_path" \
    --camera-indices 0,1,2 \
    --newton-label "Newton Rollout" \
    --phystwin-label "PhysTwin Rollout" \
    --newton-color "0,255,255" \
    --phystwin-color "255,180,0" \
    --out-mp4 "$video_1x3"

  "$NW_PY" - "$report_path" "$case_name" "$RUN_TIMESTAMP" "$video_2x3" "$video_1x3" "$result_json" "$result_csv" <<'PY'
import json
import csv
import sys
from pathlib import Path

report_path = Path(sys.argv[1]).resolve()
case_name = sys.argv[2]
run_timestamp = sys.argv[3]
video_2x3 = Path(sys.argv[4]).resolve()
video_1x3 = Path(sys.argv[5]).resolve()
result_path = Path(sys.argv[6]).resolve()
result_csv_path = Path(sys.argv[7]).resolve()

with report_path.open("r", encoding="utf-8") as f:
    report = json.load(f)

def _extract_stats(key: str) -> dict:
    stats = report.get(key) or {}
    return {
        "mean": stats.get("mean"),
        "max": stats.get("max"),
        "first30": stats.get("first30"),
        "last30": stats.get("last30"),
        "valid_frames": stats.get("valid_frames"),
    }

newton_stats = _extract_stats("newton_vs_gt_chamfer")
inference_stats = _extract_stats("inference_vs_gt_chamfer")
comparison = report.get("gt_comparison") or {}

result_csv_path.parent.mkdir(parents=True, exist_ok=True)
with result_csv_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "case_name",
            "run_timestamp",
            "metric",
            "mean",
            "max",
            "first30",
            "last30",
            "valid_frames",
            "better_vs_gt",
            "mean_delta_inference_minus_newton",
        ],
    )
    writer.writeheader()
    writer.writerow(
        {
            "case_name": case_name,
            "run_timestamp": run_timestamp,
            "metric": "newton_vs_gt_chamfer",
            "mean": newton_stats["mean"],
            "max": newton_stats["max"],
            "first30": newton_stats["first30"],
            "last30": newton_stats["last30"],
            "valid_frames": newton_stats["valid_frames"],
            "better_vs_gt": comparison.get("better_vs_gt"),
            "mean_delta_inference_minus_newton": comparison.get("mean_delta_inference_minus_newton"),
        }
    )
    writer.writerow(
        {
            "case_name": case_name,
            "run_timestamp": run_timestamp,
            "metric": "inference_vs_gt_chamfer",
            "mean": inference_stats["mean"],
            "max": inference_stats["max"],
            "first30": inference_stats["first30"],
            "last30": inference_stats["last30"],
            "valid_frames": inference_stats["valid_frames"],
            "better_vs_gt": comparison.get("better_vs_gt"),
            "mean_delta_inference_minus_newton": comparison.get("mean_delta_inference_minus_newton"),
        }
    )

result = {
    "case_name": case_name,
    "run_timestamp": run_timestamp,
    "passed": report.get("passed"),
    "newton_vs_gt_chamfer": newton_stats,
    "inference_vs_gt_chamfer": inference_stats,
    "gt_comparison": report.get("gt_comparison"),
    "checks": report.get("checks"),
    "rollout_summary": report.get("rollout_summary"),
    "artifacts": {
        "report_json": str(report_path),
        "rollout_npz": report.get("rollout_npz"),
        "rollout_json": report.get("rollout_json"),
        "gt_chamfer_curve_csv": report.get("gt_chamfer_curve_csv"),
        "result_csv": str(result_csv_path),
        "video_cmp_2x3": str(video_2x3),
        "video_overlay_1x3": str(video_1x3),
    },
}

result_path.parent.mkdir(parents=True, exist_ok=True)
with result_path.open("w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(json.dumps({"result_json": str(result_path), "result_csv": str(result_csv_path)}, indent=2))
PY

  if [ "$validate_status" -ne 0 ]; then
    echo "[WARN] validate_parity returned non-zero for case $case_name (threshold checks failed)."
  fi
  return "$validate_status"
}

# =========================
# Pipeline
# =========================
echo "[1/6] Kill stale waiting scripts"
kill_stale_waiters

echo "[2/6] Normalize output folder layout"
archive_nonconforming_case_outputs "$CLOTH_CASE"
archive_nonconforming_case_outputs "$ZEBRA_CASE"

if [ "$RUN_FULL_PHYSTWIN" = "1" ]; then
  echo "[3/6] Run PhysTwin pipeline (full: CMA + train + inference)"
  run_case_full "$CLOTH_CASE" "$CLOTH_TRAIN_FRAME"
  run_case_full "$ZEBRA_CASE" "$ZEBRA_TRAIN_FRAME"

  echo "[4/6] Copy required case files to Newton inputs"
  copy_case_to_newton "$CLOTH_CASE"
  copy_case_to_newton "$ZEBRA_CASE"
else
  echo "[3/6] Skip full PhysTwin run (RUN_FULL_PHYSTWIN=$RUN_FULL_PHYSTWIN)"
  echo "[4/6] Reuse existing Newton input cases under $NW/phystwin_bridge/inputs/cases"
fi

echo "[5/6] Newton export/parity/video for cloth"
overall_status=0
run_newton_case "$CLOTH_CASE" "cloth.yaml" || overall_status=1

echo "[6/6] Newton export/parity/video for zebra"
run_newton_case "$ZEBRA_CASE" "real.yaml" || overall_status=1

echo "[7/7] Done"
echo "Run timestamp: $RUN_TIMESTAMP"
echo "Outputs:"
echo "  $NW/phystwin_bridge/outputs/$CLOTH_CASE/$RUN_TIMESTAMP"
echo "  $NW/phystwin_bridge/outputs/$ZEBRA_CASE/$RUN_TIMESTAMP"
exit "$overall_status"
