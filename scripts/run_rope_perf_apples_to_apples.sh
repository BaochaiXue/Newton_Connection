#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${1:-${ROOT}/results/rope_perf_apples_to_apples}"
FRAME_LIMIT="${2:-}"

mkdir -p "${OUT_ROOT}/newton" "${OUT_ROOT}/phystwin" "${OUT_ROOT}/nsight" "${OUT_ROOT}/slides/assets" "${OUT_ROOT}/notes"

run_stage() {
  local stage_dir="$1"
  local git_repo="$2"
  shift 2

  mkdir -p "${stage_dir}"
  local command_txt="${stage_dir}/command.txt"
  local stdout_log="${stage_dir}/stdout.log"
  local stderr_log="${stage_dir}/stderr.log"
  local git_rev_txt="${stage_dir}/git_rev.txt"
  local manifest_json="${stage_dir}/manifest.json"
  local verdict_md="${stage_dir}/verdict.md"

  {
    printf '%q ' "$@"
    printf '\n'
  } > "${command_txt}"

  git -C "${ROOT}/${git_repo}" rev-parse HEAD > "${git_rev_txt}"

  set +e
  "$@" > >(tee "${stdout_log}") 2> >(tee "${stderr_log}" >&2)
  local exit_code=$?
  set -e

  python - <<PY
import json
from pathlib import Path
stage_dir = Path(${stage_dir@Q})
payload = {
    "stage_dir": str(stage_dir),
    "summary_json": str(stage_dir / "summary.json"),
    "profile_csv": str(stage_dir / "profile.csv"),
    "command_txt": str(stage_dir / "command.txt"),
    "stdout_log": str(stage_dir / "stdout.log"),
    "stderr_log": str(stage_dir / "stderr.log"),
    "git_rev_txt": str(stage_dir / "git_rev.txt"),
    "exit_code": ${exit_code},
}
(stage_dir / "manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
PY

  if [[ ${exit_code} -eq 0 ]]; then
    printf 'PASS\n' > "${verdict_md}"
  else
    printf 'FAIL (exit=%s)\n' "${exit_code}" > "${verdict_md}"
    return "${exit_code}"
  fi
}

NEWTON_COMMON=(
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
)

PHYSTWIN_COMMON=(
  python
  "${ROOT}/scripts/benchmark_phystwin_rope_headless.py"
  --base-path "${ROOT}/PhysTwin/data/different_types"
  --case-name rope_double_hand
  --device cuda:0
  --ir "${ROOT}/Newton/phystwin_bridge/ir/rope_double_hand/phystwin_ir_v2_bf_strict.npz"
)

if [[ -n "${FRAME_LIMIT}" ]]; then
  NEWTON_FRAME_ARGS=(--trajectory-frame-limit "${FRAME_LIMIT}")
  PHYSTWIN_FRAME_ARGS=(--frame-limit "${FRAME_LIMIT}")
else
  NEWTON_FRAME_ARGS=()
  PHYSTWIN_FRAME_ARGS=()
fi

run_stage \
  "${OUT_ROOT}/newton/A0_baseline_throughput" \
  "Newton" \
  "${NEWTON_COMMON[@]}" \
  --profile-runs 5 \
  --profile-warmup-runs 1 \
  --out-dir "${OUT_ROOT}/newton/A0_baseline_throughput" \
  --prefix A0_baseline_throughput \
  --profile-mode throughput \
  --controller-write-mode baseline \
  --profile-json "${OUT_ROOT}/newton/A0_baseline_throughput/summary.json" \
  --profile-csv "${OUT_ROOT}/newton/A0_baseline_throughput/profile.csv" \
  "${NEWTON_FRAME_ARGS[@]}"

run_stage \
  "${OUT_ROOT}/newton/A1_precomputed_throughput" \
  "Newton" \
  "${NEWTON_COMMON[@]}" \
  --profile-runs 5 \
  --profile-warmup-runs 1 \
  --out-dir "${OUT_ROOT}/newton/A1_precomputed_throughput" \
  --prefix A1_precomputed_throughput \
  --profile-mode throughput \
  --controller-write-mode precomputed \
  --profile-json "${OUT_ROOT}/newton/A1_precomputed_throughput/summary.json" \
  --profile-csv "${OUT_ROOT}/newton/A1_precomputed_throughput/profile.csv" \
  "${NEWTON_FRAME_ARGS[@]}"

run_stage \
  "${OUT_ROOT}/newton/A2_baseline_attribution" \
  "Newton" \
  "${NEWTON_COMMON[@]}" \
  --profile-runs 3 \
  --profile-warmup-runs 1 \
  --out-dir "${OUT_ROOT}/newton/A2_baseline_attribution" \
  --prefix A2_baseline_attribution \
  --profile-mode attribution \
  --controller-write-mode baseline \
  --profile-json "${OUT_ROOT}/newton/A2_baseline_attribution/summary.json" \
  --profile-csv "${OUT_ROOT}/newton/A2_baseline_attribution/profile.csv" \
  "${NEWTON_FRAME_ARGS[@]}"

run_stage \
  "${OUT_ROOT}/newton/A3_precomputed_attribution" \
  "Newton" \
  "${NEWTON_COMMON[@]}" \
  --profile-runs 3 \
  --profile-warmup-runs 1 \
  --out-dir "${OUT_ROOT}/newton/A3_precomputed_attribution" \
  --prefix A3_precomputed_attribution \
  --profile-mode attribution \
  --controller-write-mode precomputed \
  --profile-json "${OUT_ROOT}/newton/A3_precomputed_attribution/summary.json" \
  --profile-csv "${OUT_ROOT}/newton/A3_precomputed_attribution/profile.csv" \
  "${NEWTON_FRAME_ARGS[@]}"

run_stage \
  "${OUT_ROOT}/phystwin/B0_headless_throughput" \
  "PhysTwin" \
  "${PHYSTWIN_COMMON[@]}" \
  --out-dir "${OUT_ROOT}/phystwin/B0_headless_throughput" \
  --prefix B0_headless_throughput \
  --mode throughput \
  --runs 5 \
  --warmup-runs 1 \
  --json-out "${OUT_ROOT}/phystwin/B0_headless_throughput/summary.json" \
  --csv-out "${OUT_ROOT}/phystwin/B0_headless_throughput/profile.csv" \
  "${PHYSTWIN_FRAME_ARGS[@]}"

run_stage \
  "${OUT_ROOT}/phystwin/B1_headless_attribution" \
  "PhysTwin" \
  "${PHYSTWIN_COMMON[@]}" \
  --out-dir "${OUT_ROOT}/phystwin/B1_headless_attribution" \
  --prefix B1_headless_attribution \
  --mode attribution \
  --runs 3 \
  --warmup-runs 1 \
  --json-out "${OUT_ROOT}/phystwin/B1_headless_attribution/summary.json" \
  --csv-out "${OUT_ROOT}/phystwin/B1_headless_attribution/profile.csv" \
  "${PHYSTWIN_FRAME_ARGS[@]}"

python "${ROOT}/scripts/summarize_rope_perf_apples_to_apples.py" --root "${OUT_ROOT}"

echo "Completed rope apples-to-apples benchmark under: ${OUT_ROOT}"
