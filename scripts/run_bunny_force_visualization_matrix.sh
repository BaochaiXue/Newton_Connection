#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_CASE="${ROOT}/scripts/run_bunny_force_case.py"
RENDER_FORCE="${ROOT}/scripts/render_bunny_force_artifacts.py"
VALIDATE_VIS="${ROOT}/scripts/validate_bunny_force_visualization.py"
VALIDATE_ART="${ROOT}/scripts/validate_experiment_artifacts.py"
BOARD="${ROOT}/scripts/build_bunny_force_summary_board.py"
PYTHON="${ROOT}/Newton/newton/.venv/bin/python"
SYS_PYTHON="python"
RESULT_ROOT="${ROOT}/results/bunny_force_visualization"
RUN_ID="${1:-$(date +%Y%m%d_%H%M%S)_fullprocess_force_matrix}"
RUN_DIR="${RESULT_ROOT}/runs/${RUN_ID}"
LATEST_ATTEMPT="${RESULT_ROOT}/LATEST_ATTEMPT.txt"
LATEST_SUCCESS="${RESULT_ROOT}/LATEST_SUCCESS.txt"

mkdir -p "${RUN_DIR}/logs" "${RUN_DIR}/artifacts/matrix" "${RUN_DIR}/src_patch_summary"
printf '%s\n' "${RUN_DIR}" > "${LATEST_ATTEMPT}"

COMMON=(
  --frames 60
  --slowdown 2.5
  --post-contact-video-seconds 0
  --force-diagnostic
  --no-stop-after-diagnostic
  --no-parity-check
  --defer-force-artifacts
  --force-topk 8
  --force-topk-mode hybrid
  --force-render-mode normal_only
  --force-window-substeps-before 8
  --force-window-substeps-after 24
  --force-video-layout split
  --force-video-max-probes 6
  --force-video-topk-spatial-min-dist 0.02
  --force-camera-fov 34
  --force-camera-pitch -8
  --force-camera-yaw -40
  --auto-set-weight 0.1
  --rigid-mass 0.5
  --drop-height 0.2
)

cat > "${RUN_DIR}/commands.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "${ROOT}"
bash "${ROOT}/scripts/run_bunny_force_visualization_matrix.sh" "${RUN_ID}"
EOF
chmod +x "${RUN_DIR}/commands.sh"

cat > "${RUN_DIR}/notes.md" <<EOF
# Notes

- Goal: full-process bunny force visualization with exact active-interval force synchronization.
- This run must pass:
  - black-screen gate
  - temporal-density gate
  - full-process gate
  - force-synchronization gate
  - metric-semantics gate
- Canonical validator outputs:
  - qa/report.json
  - qa/metrics.json
  - qa/verdict.md
EOF

cat > "${RUN_DIR}/src_patch_summary/changed_files.txt" <<EOF
Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py
scripts/run_bunny_force_case.py
scripts/render_bunny_force_artifacts.py
scripts/validate_bunny_force_visualization.py
scripts/build_bunny_force_summary_board.py
scripts/run_bunny_force_visualization_matrix.sh
EOF

if git -C "${ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "${ROOT}" status --short > "${RUN_DIR}/src_patch_summary/git_status.txt" || true
else
  printf 'No top-level git repository at %s\n' "${ROOT}" > "${RUN_DIR}/src_patch_summary/git_status.txt"
fi

run_case() {
  local case_name="$1"; shift
  local case_root="${RUN_DIR}/artifacts/matrix/${case_name}"
  local phenomenon_dir="${case_root}/phenomenon"
  local force_dir="${case_root}/force_mechanism/self_off/force_diagnostic"
  local log_path="${RUN_DIR}/logs/${case_name}.log"
  local phenomenon_video="${phenomenon_dir}/cloth_bunny_drop_off_m0p5.mp4"
  local phenomenon_summary="${phenomenon_dir}/cloth_bunny_drop_off_m0p5_summary.json"
  local force_video="${force_dir}/force_diag_trigger_window.mp4"
  local force_summary="${force_dir}/force_diag_trigger_summary.json"
  local bundle_path="${phenomenon_dir}/force_diagnostic/force_render_bundle.pkl"

  rm -rf "${case_root}"
  mkdir -p "${phenomenon_dir}" "${force_dir}"
  {
    echo "[run_case] case=${case_name}"
    echo "[run_case] phenomenon_dir=${phenomenon_dir}"
    echo "[run_case] force_dir=${force_dir}"
    echo "[run_case] run=${PYTHON} ${RUN_CASE} --out-dir ${phenomenon_dir} ${COMMON[*]} $*"
    echo "[run_case] render=${PYTHON} ${RENDER_FORCE} --bundle ${bundle_path} --force-dump-dir ${force_dir}"
  } | tee "${log_path}"

  PYTHONPATH="${ROOT}/Newton/newton" \
    "${PYTHON}" "${RUN_CASE}" \
    --out-dir "${phenomenon_dir}" \
    "${COMMON[@]}" \
    "$@" 2>&1 | tee -a "${log_path}"

  PYTHONPATH="${ROOT}/Newton/newton" \
    "${PYTHON}" "${RENDER_FORCE}" \
    --bundle "${bundle_path}" \
    --force-dump-dir "${force_dir}" 2>&1 | tee -a "${log_path}"

  cp -f "${phenomenon_dir}/force_diagnostic/force_diag_trigger_summary.json" "${force_summary}"
  cp -f "${phenomenon_dir}/force_diagnostic/force_diag_trigger_substep.npz" "${force_dir}/force_diag_trigger_substep.npz"

  cat > "${case_root}/command.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
ROOT=${ROOT@Q}
PYTHON=${PYTHON@Q}
SYS_PYTHON=${SYS_PYTHON@Q}
PYTHONPATH="\$ROOT/Newton/newton" "\$PYTHON" "\$ROOT/scripts/run_bunny_force_case.py" --out-dir ${phenomenon_dir@Q} ${COMMON[*]} $*
PYTHONPATH="\$ROOT/Newton/newton" "\$PYTHON" "\$ROOT/scripts/render_bunny_force_artifacts.py" --bundle ${bundle_path@Q} --force-dump-dir ${force_dir@Q}
cp -f ${phenomenon_dir@Q}/force_diagnostic/force_diag_trigger_summary.json ${force_summary@Q}
cp -f ${phenomenon_dir@Q}/force_diagnostic/force_diag_trigger_substep.npz ${force_dir@Q}/force_diag_trigger_substep.npz
"\$SYS_PYTHON" "\$ROOT/scripts/validate_bunny_force_visualization.py" --run-dir ${case_root@Q} --sample-count 12
"\$SYS_PYTHON" "\$ROOT/scripts/validate_experiment_artifacts.py" ${case_root@Q} --require-video --require-diagnostic --require-qa
EOF
  chmod +x "${case_root}/command.sh"

  cat > "${case_root}/README.md" <<EOF
# ${case_name}

- phenomenon video: ${phenomenon_video}
- force mechanism video: ${force_video}
- phenomenon summary: ${phenomenon_summary}
- force summary: ${force_summary}
- QA report: ${case_root}/qa/report.json
- QA verdict: ${case_root}/qa/verdict.md
EOF

  "${SYS_PYTHON}" "${VALIDATE_VIS}" \
    --run-dir "${case_root}" \
    --sample-count 12 2>&1 | tee -a "${log_path}"

  "${SYS_PYTHON}" "${VALIDATE_ART}" "${case_root}" --require-video --require-diagnostic --require-qa 2>&1 | tee -a "${log_path}"
}

run_case bunny_baseline --rigid-shape bunny --initial-velocity-z -1.0 --bunny-scale 0.12
run_case box_control --rigid-shape box --initial-velocity-z -1.0
run_case bunny_low_inertia --rigid-shape bunny --initial-velocity-z 0.0 --bunny-scale 0.12
run_case bunny_larger_scale --rigid-shape bunny --initial-velocity-z -1.0 --bunny-scale 0.18

"${SYS_PYTHON}" "${BOARD}" --run-dir "${RUN_DIR}" | tee -a "${RUN_DIR}/logs/summary_board.log"

python - <<PY
from pathlib import Path
import json
run_dir = Path(${RUN_DIR@Q})
summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
status = "passed" if all(case["qa_verdict"] == "PASS" for case in summary["cases"]) else "failed"
manifest = {
    "run_id": run_dir.name,
    "created_at": "$(date +%F)",
    "status": status,
    "result_bundle": "results/bunny_force_visualization",
    "entrypoint": "scripts/run_bunny_force_visualization_matrix.sh",
    "command": str(run_dir / "commands.sh"),
    "code_paths": [
        "Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py",
        "scripts/run_bunny_force_case.py",
        "scripts/render_bunny_force_artifacts.py",
        "scripts/run_bunny_force_visualization_matrix.sh",
        "scripts/build_bunny_force_summary_board.py",
        "scripts/validate_bunny_force_visualization.py",
    ],
    "inputs": [
        "Newton/phystwin_bridge/ir/blue_cloth_double_lift_around/phystwin_ir_v2_bf_strict.npz"
    ],
    "outputs": [
        str(run_dir / "summary.json"),
        str(run_dir / "artifacts" / "matrix" / "bunny_penetration_summary_board.png"),
    ],
    "summary_path": "summary.json",
    "readme_path": "README.md",
    "artifacts": {
        "summary": "summary.json",
        "logs": "logs/",
        "matrix": "artifacts/matrix/",
        "patch_summary": "src_patch_summary/",
    },
    "validation": {
        "validator": "scripts/validate_bunny_force_visualization.py",
        "status": status,
        "notes": "All four cases must pass phenomenon+force QA under the full-process contract.",
    },
}
(run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
readme_lines = [
    "# Bunny Force Visualization Matrix",
    "",
    f"- run_id: `{run_dir.name}`",
    f"- status: `{status}`",
    "",
    "## Outputs",
    "",
    f"- summary: `{run_dir / 'summary.json'}`",
    f"- board: `{run_dir / 'artifacts' / 'matrix' / 'bunny_penetration_summary_board.png'}`",
    "",
    "## Cases",
]
for case in summary["cases"]:
    readme_lines.extend([
        f"- {case['case']}: phenomenon=`{case['render_video']}` force=`{case['force_video']}` qa=`{case['qa_verdict']}` issue=`{case['issue']}`",
    ])
(run_dir / "README.md").write_text("\\n".join(readme_lines) + "\\n", encoding="utf-8")
print(status)
PY

STATUS="$(python - <<PY
from pathlib import Path
import json
run_dir = Path(${RUN_DIR@Q})
summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
print("PASS" if all(case["qa_verdict"] == "PASS" for case in summary["cases"]) else "FAIL")
PY
)"

if [[ "${STATUS}" == "PASS" ]]; then
  printf '%s\n' "${RUN_DIR}" > "${LATEST_SUCCESS}"
fi

echo "[run_bunny_force_visualization_matrix] run_dir=${RUN_DIR}"
echo "[run_bunny_force_visualization_matrix] status=${STATUS}"
