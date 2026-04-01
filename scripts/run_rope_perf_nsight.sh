#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${1:-${ROOT}/results/rope_perf_apples_to_apples/nsight}"
FRAME_LIMIT="${2:-}"

mkdir -p "${OUT_ROOT}/newton_A1" "${OUT_ROOT}/phystwin_B0"

run_nsys_stage() {
  local stage_dir="$1"
  local git_repo="$2"
  shift 2

  mkdir -p "${stage_dir}"
  local command_txt="${stage_dir}/command.txt"
  local stdout_log="${stage_dir}/stdout.log"
  local stderr_log="${stage_dir}/stderr.log"
  local git_rev_txt="${stage_dir}/git_rev.txt"
  local stats_txt="${stage_dir}/stats.txt"
  local summary_json="${stage_dir}/summary.json"
  local manifest_json="${stage_dir}/manifest.json"
  local verdict_md="${stage_dir}/verdict.md"
  local report_prefix="${stage_dir}/trace"
  local report_file="${report_prefix}.nsys-rep"

  {
    printf '%q ' "$@"
    printf '\n'
  } > "${command_txt}"

  git -C "${ROOT}/${git_repo}" rev-parse HEAD > "${git_rev_txt}"

  set +e
  nsys profile \
    --force-overwrite=true \
    --sample=none \
    --trace=cuda,nvtx,osrt \
    --cuda-graph-trace=node \
    -o "${report_prefix}" \
    "$@" > >(tee "${stdout_log}") 2> >(tee "${stderr_log}" >&2)
  local exit_code=$?
  set -e

  if [[ ${exit_code} -ne 0 ]]; then
    printf 'FAIL (exit=%s)\n' "${exit_code}" > "${verdict_md}"
    return "${exit_code}"
  fi

  nsys stats --report cuda_api_sum,gpu_kern_sum,osrt_sum "${report_file}" > "${stats_txt}"

  python - <<PY
import json
from pathlib import Path
stage_dir = Path(${stage_dir@Q})
payload = {
    "stage_dir": str(stage_dir),
    "report_file": str(stage_dir / "trace.nsys-rep"),
    "sqlite_file": str(stage_dir / "trace.sqlite"),
    "stats_txt": str(stage_dir / "stats.txt"),
    "command_txt": str(stage_dir / "command.txt"),
    "stdout_log": str(stage_dir / "stdout.log"),
    "stderr_log": str(stage_dir / "stderr.log"),
    "git_rev_txt": str(stage_dir / "git_rev.txt"),
}
(stage_dir / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
(stage_dir / "manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
PY

  printf 'PASS\n' > "${verdict_md}"
}

NEWTON_CMD=(
  python
  "${ROOT}/Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py"
  --viewer null
  --profile-only
  --runtime-device cuda:0
  --ir "${ROOT}/Newton/phystwin_bridge/ir/rope_double_hand/phystwin_ir_v2_bf_strict.npz"
  --sim-dt 5e-05
  --segment-substeps 667
  --no-add-ground-plane
  --no-shape-contacts
  --profile-runs 1
  --profile-warmup-runs 0
  --out-dir "${OUT_ROOT}/newton_A1"
  --prefix nsys_newton_A1
  --profile-mode throughput
  --controller-write-mode precomputed
  --profile-json "${OUT_ROOT}/newton_A1/profile_summary.json"
  --profile-csv "${OUT_ROOT}/newton_A1/profile_summary.csv"
)

PHYSTWIN_CMD=(
  python
  "${ROOT}/scripts/benchmark_phystwin_rope_headless.py"
  --base-path "${ROOT}/PhysTwin/data/different_types"
  --case-name rope_double_hand
  --device cuda:0
  --ir "${ROOT}/Newton/phystwin_bridge/ir/rope_double_hand/phystwin_ir_v2_bf_strict.npz"
  --out-dir "${OUT_ROOT}/phystwin_B0"
  --prefix nsys_phystwin_B0
  --mode throughput
  --runs 1
  --warmup-runs 0
  --json-out "${OUT_ROOT}/phystwin_B0/profile_summary.json"
  --csv-out "${OUT_ROOT}/phystwin_B0/profile_summary.csv"
)

if [[ -n "${FRAME_LIMIT}" ]]; then
  NEWTON_CMD+=(--trajectory-frame-limit "${FRAME_LIMIT}")
  PHYSTWIN_CMD+=(--frame-limit "${FRAME_LIMIT}")
fi

run_nsys_stage "${OUT_ROOT}/newton_A1" "Newton" "${NEWTON_CMD[@]}"
run_nsys_stage "${OUT_ROOT}/phystwin_B0" "PhysTwin" "${PHYSTWIN_CMD[@]}"

echo "Completed rope Nsight capture under: ${OUT_ROOT}"
