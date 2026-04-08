#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ID="${1:-$(date +%Y%m%d_%H%M%S)_blue_cloth_interactive_one_to_one_v1}"
if [[ $# -gt 0 ]]; then
  shift
fi

CASE_NAME="blue_cloth_double_lift_around"
PHYSTWIN_ENV="phystwin"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --case-name)
      CASE_NAME="$2"
      shift 2
      ;;
    --phystwin-env)
      PHYSTWIN_ENV="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

IR_PATH="${ROOT}/Newton/phystwin_bridge/ir/${CASE_NAME}/phystwin_ir_v2_bf_strict.npz"
RESULT_ROOT="${ROOT}/results/interactive_playground_profiling"
RUN_DIR="${RESULT_ROOT}/runs/${RUN_ID}"
NEWTON_ROOT="${RUN_DIR}/newton"
PHYSTWIN_ROOT="${RUN_DIR}/phystwin"
COMPARE_ROOT="${RUN_DIR}/comparison"
INPUT_ROOT="${RUN_DIR}/inputs"
LOG_DIR="${RUN_DIR}/logs"
LOG_PATH="${LOG_DIR}/run.log"

THROUGHPUT_RUNS=3
THROUGHPUT_WARMUP=1
ATTRIBUTION_RUNS=1
ATTRIBUTION_WARMUP=1

mkdir -p "${NEWTON_ROOT}" "${PHYSTWIN_ROOT}" "${COMPARE_ROOT}" "${INPUT_ROOT}" "${LOG_DIR}"
cp -f "${IR_PATH}" "${INPUT_ROOT}/scene.npz"

cat > "${RUN_DIR}/command.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "${ROOT}"
bash "${ROOT}/scripts/run_interactive_playground_apples_to_apples.sh" "${RUN_ID}"
EOF
chmod +x "${RUN_DIR}/command.sh"

run_stage() {
  local stage_dir="$1"
  shift
  mkdir -p "${stage_dir}"
  {
    printf '#!/usr/bin/env bash\nset -euo pipefail\n'
    printf '%q ' "$@"
    printf '\n'
  } > "${stage_dir}/command.sh"
  chmod +x "${stage_dir}/command.sh"
  {
    echo "[stage] dir=${stage_dir}"
    echo "[stage] cmd=$*"
  } | tee -a "${LOG_PATH}"
  "$@" 2>&1 | tee -a "${LOG_PATH}"
}

{
  echo "[run_interactive_playground_apples_to_apples] run_dir=${RUN_DIR}"
  echo "[run_interactive_playground_apples_to_apples] case_name=${CASE_NAME}"
  echo "[run_interactive_playground_apples_to_apples] ir=${IR_PATH}"
  echo "[run_interactive_playground_apples_to_apples] phystwin_env=${PHYSTWIN_ENV}"
  echo "[run_interactive_playground_apples_to_apples] throughput_runs=${THROUGHPUT_RUNS}"
  echo "[run_interactive_playground_apples_to_apples] attribution_runs=${ATTRIBUTION_RUNS}"
} | tee "${LOG_PATH}"

run_stage \
  "${NEWTON_ROOT}/N0_baseline_throughput" \
  python "${ROOT}/Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py" \
    --viewer null \
    --runtime-device cuda:0 \
    --ir "${IR_PATH}" \
    --profile-only \
    --profile-mode throughput \
    --profile-runs "${THROUGHPUT_RUNS}" \
    --profile-warmup-runs "${THROUGHPUT_WARMUP}" \
    --controller-write-mode baseline \
    --out-dir "${NEWTON_ROOT}/N0_baseline_throughput" \
    --prefix newton_baseline_throughput \
    --profile-json "${NEWTON_ROOT}/N0_baseline_throughput/summary.json" \
    --profile-csv "${NEWTON_ROOT}/N0_baseline_throughput/profile.csv"

run_stage \
  "${NEWTON_ROOT}/N1_precomputed_throughput" \
  python "${ROOT}/Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py" \
    --viewer null \
    --runtime-device cuda:0 \
    --ir "${IR_PATH}" \
    --profile-only \
    --profile-mode throughput \
    --profile-runs "${THROUGHPUT_RUNS}" \
    --profile-warmup-runs "${THROUGHPUT_WARMUP}" \
    --controller-write-mode precomputed \
    --out-dir "${NEWTON_ROOT}/N1_precomputed_throughput" \
    --prefix newton_precomputed_throughput \
    --profile-json "${NEWTON_ROOT}/N1_precomputed_throughput/summary.json" \
    --profile-csv "${NEWTON_ROOT}/N1_precomputed_throughput/profile.csv"

run_stage \
  "${NEWTON_ROOT}/N2_baseline_attribution" \
  python "${ROOT}/Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py" \
    --viewer null \
    --runtime-device cuda:0 \
    --ir "${IR_PATH}" \
    --profile-only \
    --profile-mode attribution \
    --profile-runs "${ATTRIBUTION_RUNS}" \
    --profile-warmup-runs "${ATTRIBUTION_WARMUP}" \
    --controller-write-mode baseline \
    --out-dir "${NEWTON_ROOT}/N2_baseline_attribution" \
    --prefix newton_baseline_attribution \
    --profile-json "${NEWTON_ROOT}/N2_baseline_attribution/summary.json" \
    --profile-csv "${NEWTON_ROOT}/N2_baseline_attribution/profile.csv"

run_stage \
  "${NEWTON_ROOT}/N3_precomputed_attribution" \
  python "${ROOT}/Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py" \
    --viewer null \
    --runtime-device cuda:0 \
    --ir "${IR_PATH}" \
    --profile-only \
    --profile-mode attribution \
    --profile-runs "${ATTRIBUTION_RUNS}" \
    --profile-warmup-runs "${ATTRIBUTION_WARMUP}" \
    --controller-write-mode precomputed \
    --out-dir "${NEWTON_ROOT}/N3_precomputed_attribution" \
    --prefix newton_precomputed_attribution \
    --profile-json "${NEWTON_ROOT}/N3_precomputed_attribution/summary.json" \
    --profile-csv "${NEWTON_ROOT}/N3_precomputed_attribution/profile.csv"

run_stage \
  "${PHYSTWIN_ROOT}/P0_headless_throughput" \
  conda run -n "${PHYSTWIN_ENV}" python "${ROOT}/scripts/benchmark_phystwin_rope_headless.py" \
    --case-name "${CASE_NAME}" \
    --ir "${IR_PATH}" \
    --out-dir "${PHYSTWIN_ROOT}/P0_headless_throughput" \
    --prefix phystwin_headless_throughput \
    --runs "${THROUGHPUT_RUNS}" \
    --warmup-runs "${THROUGHPUT_WARMUP}" \
    --json-out "${PHYSTWIN_ROOT}/P0_headless_throughput/summary.json" \
    --csv-out "${PHYSTWIN_ROOT}/P0_headless_throughput/profile.csv"

run_stage \
  "${PHYSTWIN_ROOT}/P1_kernel_attribution" \
  conda run -n "${PHYSTWIN_ENV}" python "${ROOT}/scripts/profile_phystwin_playground_kernels.py" \
    --case-name "${CASE_NAME}" \
    --ir "${IR_PATH}" \
    --out-dir "${PHYSTWIN_ROOT}/P1_kernel_attribution" \
    --prefix phystwin_kernel_attribution \
    --runs "${ATTRIBUTION_RUNS}" \
    --warmup-runs "${ATTRIBUTION_WARMUP}" \
    --json-out "${PHYSTWIN_ROOT}/P1_kernel_attribution/summary.json" \
    --csv-out "${PHYSTWIN_ROOT}/P1_kernel_attribution/profile.csv"

run_stage \
  "${COMPARE_ROOT}" \
  python "${ROOT}/scripts/compare_interactive_playground_profiles.py" \
    --newton-baseline-throughput "${NEWTON_ROOT}/N0_baseline_throughput/summary.json" \
    --newton-precomputed-throughput "${NEWTON_ROOT}/N1_precomputed_throughput/summary.json" \
    --newton-baseline-attribution "${NEWTON_ROOT}/N2_baseline_attribution/summary.json" \
    --newton-precomputed-attribution "${NEWTON_ROOT}/N3_precomputed_attribution/summary.json" \
    --phystwin-throughput "${PHYSTWIN_ROOT}/P0_headless_throughput/summary.json" \
    --phystwin-kernel-attribution "${PHYSTWIN_ROOT}/P1_kernel_attribution/summary.json" \
    --out-dir "${COMPARE_ROOT}"

python - <<PY
from pathlib import Path
import json

run_dir = Path(${RUN_DIR@Q})
compare = json.loads((run_dir / "comparison" / "summary.json").read_text(encoding="utf-8"))
summary = {
    "task": "interactive_playground_profiling",
    "case_name": compare["case_name"],
    "goal": f"Same-case no-render one-to-one Newton-vs-PhysTwin interactive-playground profiling for {compare['case_name']}.",
    "throughput": compare["throughput"],
    "comparison_markdown": str(run_dir / "comparison" / "comparison.md"),
    "comparison_csv": str(run_dir / "comparison" / "operation_matchup_grouped.csv"),
    "top_newton_baseline_ops": compare["top_newton_baseline_ops"][:5],
    "top_newton_precomputed_ops": compare["top_newton_precomputed_ops"][:5],
    "top_phystwin_ops": compare["top_phystwin_ops"][:5],
}
(run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

manifest = {
    "task": "interactive_playground_profiling",
    "run_id": run_dir.name,
    "result_root": "results/interactive_playground_profiling",
    "case_name": compare["case_name"],
    "command": str(run_dir / "command.sh"),
    "artifacts": {
        "summary": "summary.json",
        "log": "logs/run.log",
        "inputs": "inputs/scene.npz",
        "newton": "newton/",
        "phystwin": "phystwin/",
        "comparison": "comparison/",
    },
}
(run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

readme = [
    "# Interactive Playground Apples-To-Apples Profiling",
    "",
    f"- case: {compare['case_name']}",
    "- scope: no-render same-case controller replay on both Newton and PhysTwin",
    "- Newton throughput stages: N0 baseline, N1 precomputed",
    "- Newton attribution stages: N2 baseline, N3 precomputed",
    "- PhysTwin stages: P0 throughput, P1 kernel attribution",
    "- primary comparison: comparison/comparison.md",
    "",
]
(run_dir / "README.md").write_text("\\n".join(readme), encoding="utf-8")
PY

echo
echo "Artifacts:"
echo "  Run root: ${RUN_DIR}"
echo "  Summary: ${RUN_DIR}/summary.json"
echo "  Comparison: ${COMPARE_ROOT}/comparison.md"
echo "  Log: ${LOG_PATH}"
