#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PHYSTWIN_ROOT="${ROOT}/PhysTwin"

PHYSTWIN_ENV="${PHYSTWIN_ENV:-phystwin}"
MODE="data-process"
CONFIG_PATH="PhysTwin/data_config.csv"
INPUT_BASE_PATH="PhysTwin/data/different_types"
TASK_NAME="phystwin_local_$(date +%Y%m%d_%H%M%S)"
RUN_DIR=""
START_STAGE="script_process_data"
DRY_RUN=0

usage() {
  cat <<'EOF'
Run a local PhysTwin pipeline stage through the repo harness.

Usage:
  scripts/run_phystwin_local_pipeline.sh [options]

Options:
  --mode data-process|full       Run only script_process_data.py, or the full PhysTwin pipeline.
  --config-path PATH             Case allowlist CSV. Default: PhysTwin/data_config.csv
  --input-base-path PATH         Case root. Default: PhysTwin/data/different_types
  --task-name NAME               Stable run/archive name. Default: phystwin_local_<timestamp>
  --run-dir PATH                 Harness run directory. Default: PhysTwin/logs/harness_runs/<task-name>
  --start-stage STAGE            Full-pipeline resume stage. Default: script_process_data
  --dry-run                      Write/print the command but do not execute it.
  -h, --help                     Show this help.

Environment:
  PHYSTWIN_ENV                   Conda environment name. Default: phystwin
  CONDA_BIN                      Conda executable path, if auto-discovery is not enough.

Examples:
  scripts/run_phystwin_local_pipeline.sh \
    --mode data-process \
    --config-path PhysTwin/configs/data_config_four_new_cases.csv \
    --task-name phystwin_four_cases_reprocess_20260427

  scripts/run_phystwin_local_pipeline.sh \
    --mode full \
    --config-path PhysTwin/configs/data_config_four_new_cases.csv \
    --task-name phystwin_four_cases_full_20260427
EOF
}

die() {
  echo "[run_phystwin_local_pipeline] ERROR: $*" >&2
  exit 2
}

resolve_repo_path() {
  local path="$1"
  if [[ "$path" = /* ]]; then
    printf '%s\n' "$path"
  else
    printf '%s/%s\n' "$ROOT" "$path"
  fi
}

valid_stage() {
  case "$1" in
    script_process_data|export_video_human_mask|dynamic_export_gs_data|script_optimize|script_train|script_inference|dynamic_fast_gs|final_eval)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    --config-path)
      CONFIG_PATH="${2:-}"
      shift 2
      ;;
    --input-base-path)
      INPUT_BASE_PATH="${2:-}"
      shift 2
      ;;
    --task-name)
      TASK_NAME="${2:-}"
      shift 2
      ;;
    --run-dir)
      RUN_DIR="${2:-}"
      shift 2
      ;;
    --start-stage)
      START_STAGE="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown option: $1"
      ;;
  esac
done

[[ "$MODE" = "data-process" || "$MODE" = "full" ]] || die "--mode must be data-process or full"
[[ -n "$TASK_NAME" ]] || die "--task-name cannot be empty"
valid_stage "$START_STAGE" || die "Invalid --start-stage: $START_STAGE"
[[ -d "$PHYSTWIN_ROOT" ]] || die "Missing PhysTwin checkout: $PHYSTWIN_ROOT"

CONFIG_ABS="$(resolve_repo_path "$CONFIG_PATH")"
INPUT_BASE_ABS="$(resolve_repo_path "$INPUT_BASE_PATH")"
[[ -f "$CONFIG_ABS" ]] || die "Missing config CSV: $CONFIG_ABS"
[[ -d "$INPUT_BASE_ABS" ]] || die "Missing input case root: $INPUT_BASE_ABS"

if [[ -z "$RUN_DIR" ]]; then
  RUN_DIR="${PHYSTWIN_ROOT}/logs/harness_runs/${TASK_NAME}"
else
  RUN_DIR="$(resolve_repo_path "$RUN_DIR")"
fi
COMMAND_SH="${RUN_DIR}/command.sh"
RUN_LOG="${RUN_DIR}/run.log"
SUMMARY_JSON="${RUN_DIR}/summary.json"
STAGE_LOGS_DIR="${RUN_DIR}/stage_logs"
ARCHIVE_DIR="${PHYSTWIN_ROOT}/archive_result/${TASK_NAME}"

if [[ -e "$RUN_DIR" ]]; then
  die "Run directory already exists: $RUN_DIR"
fi

CONDA_BIN="${CONDA_BIN:-}"
if [[ -z "$CONDA_BIN" ]]; then
  CONDA_BIN="$(command -v conda || true)"
fi
if [[ -z "$CONDA_BIN" && -x "$HOME/miniconda3/bin/conda" ]]; then
  CONDA_BIN="$HOME/miniconda3/bin/conda"
fi
if [[ -z "$CONDA_BIN" && -x "$HOME/anaconda3/bin/conda" ]]; then
  CONDA_BIN="$HOME/anaconda3/bin/conda"
fi
[[ -n "$CONDA_BIN" ]] || die "Unable to find conda. Set CONDA_BIN explicitly."

mkdir -p "$RUN_DIR"

if [[ "$MODE" = "data-process" ]]; then
  COMMAND=(
    "$CONDA_BIN" run --no-capture-output -n "$PHYSTWIN_ENV"
    python "$PHYSTWIN_ROOT/script_process_data.py"
    --config-path "$CONFIG_ABS"
    --base-path "$INPUT_BASE_ABS"
  )
else
  COMMAND=(
    "$CONDA_BIN" run --no-capture-output -n "$PHYSTWIN_ENV"
    python "$PHYSTWIN_ROOT/pipeline_commnad.py"
    --config-path "$CONFIG_ABS"
    --input-base-path "$INPUT_BASE_ABS"
    --task-name "$TASK_NAME"
    --logs-dir "$STAGE_LOGS_DIR"
    --start-stage "$START_STAGE"
  )
fi

COMMAND_TEXT=""
printf -v COMMAND_TEXT '%q ' "${COMMAND[@]}"

{
  printf '#!/usr/bin/env bash\n'
  printf 'set -euo pipefail\n'
  printf 'cd %q\n' "$ROOT"
  printf '%s\n' "$COMMAND_TEXT"
} > "$COMMAND_SH"
chmod +x "$COMMAND_SH"

write_summary() {
  local status="$1"
  SUMMARY_STATUS="$status" \
  SUMMARY_MODE="$MODE" \
  SUMMARY_TASK_NAME="$TASK_NAME" \
  SUMMARY_ROOT="$ROOT" \
  SUMMARY_CONFIG="$CONFIG_ABS" \
  SUMMARY_INPUT_BASE="$INPUT_BASE_ABS" \
  SUMMARY_RUN_DIR="$RUN_DIR" \
  SUMMARY_COMMAND_SH="$COMMAND_SH" \
  SUMMARY_RUN_LOG="$RUN_LOG" \
  SUMMARY_STAGE_LOGS="$STAGE_LOGS_DIR" \
  SUMMARY_ARCHIVE="$ARCHIVE_DIR" \
  SUMMARY_COMMAND="$COMMAND_TEXT" \
  python3 - "$SUMMARY_JSON" <<'PY'
import json
import os
import sys
from datetime import datetime, timezone

path = sys.argv[1]
mode = os.environ["SUMMARY_MODE"]
expected = {
    "data_process_case_outputs": [
        "mask/",
        "cotracker/",
        "pcd/",
        "track_process_data.pkl",
        "final_data.pkl",
        "split.json",
    ]
}
if mode == "full":
    expected["full_pipeline_archive"] = os.environ["SUMMARY_ARCHIVE"]
    expected["stage_logs_dir"] = os.environ["SUMMARY_STAGE_LOGS"]

summary = {
    "status": os.environ["SUMMARY_STATUS"],
    "mode": mode,
    "task_name": os.environ["SUMMARY_TASK_NAME"],
    "created_at": datetime.now(timezone.utc).isoformat(),
    "repo_root": os.environ["SUMMARY_ROOT"],
    "config_path": os.environ["SUMMARY_CONFIG"],
    "input_base_path": os.environ["SUMMARY_INPUT_BASE"],
    "run_dir": os.environ["SUMMARY_RUN_DIR"],
    "command_sh": os.environ["SUMMARY_COMMAND_SH"],
    "run_log": os.environ["SUMMARY_RUN_LOG"],
    "command": os.environ["SUMMARY_COMMAND"].strip(),
    "expected_outputs": expected,
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
    f.write("\n")
PY
}

echo "[run_phystwin_local_pipeline] mode=${MODE}"
echo "[run_phystwin_local_pipeline] task_name=${TASK_NAME}"
echo "[run_phystwin_local_pipeline] run_dir=${RUN_DIR}"
echo "[run_phystwin_local_pipeline] command_sh=${COMMAND_SH}"

if [[ "$DRY_RUN" -eq 1 ]]; then
  write_summary "dry_run"
  echo "[run_phystwin_local_pipeline] dry-run command:"
  echo "  ${COMMAND_TEXT}"
  echo "[run_phystwin_local_pipeline] summary_json=${SUMMARY_JSON}"
  exit 0
fi

set +e
(
  cd "$ROOT"
  "${COMMAND[@]}"
) > >(tee "$RUN_LOG") 2>&1
STATUS=$?
set -e

if [[ "$STATUS" -eq 0 ]]; then
  write_summary "completed"
else
  write_summary "failed"
fi

echo "[run_phystwin_local_pipeline] run_log=${RUN_LOG}"
echo "[run_phystwin_local_pipeline] summary_json=${SUMMARY_JSON}"
if [[ "$MODE" = "full" ]]; then
  echo "[run_phystwin_local_pipeline] expected_archive=${ARCHIVE_DIR}"
fi
exit "$STATUS"
