#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TASK_SLUG="robot_visible_rigid_tool_baseline"
OUT_DIR="${ROOT}/formal_slide/meeting_2026_04_08/robot_visible_tool_three_views"
GIF_WIDTH="960"
GIF_FPS="10"
GIF_MAX_COLORS="128"

usage() {
  cat <<EOF
Usage: $0 [--task-slug <slug>] [--out-dir <dir>] [--gif-width <px>] [--gif-fps <fps>] [--gif-max-colors <n>]

Default task slug:
  robot_visible_rigid_tool_baseline

Default output directory:
  formal_slide/meeting_2026_04_08/robot_visible_tool_three_views
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task-slug)
      TASK_SLUG="$2"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    --gif-width)
      GIF_WIDTH="$2"
      shift 2
      ;;
    --gif-fps)
      GIF_FPS="$2"
      shift 2
      ;;
    --gif-max-colors)
      GIF_MAX_COLORS="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[export_robot_slide_views] unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

RESULT_META="${ROOT}/results_meta/tasks/${TASK_SLUG}.json"
if [[ ! -f "${RESULT_META}" ]]; then
  echo "[export_robot_slide_views] missing results_meta entry: ${RESULT_META}" >&2
  exit 2
fi

SOURCE_ROOT="$(python - <<PY
import json
from pathlib import Path
obj = json.loads(Path(${RESULT_META@Q}).read_text(encoding='utf-8'))
run = obj.get('authoritative_run') or {}
root = run.get('local_artifact_root')
if not root:
    raise SystemExit(2)
path = Path(root)
print(path if path.is_absolute() else (Path(${ROOT@Q}) / path))
PY
)"

if [[ ! -d "${SOURCE_ROOT}" ]]; then
  echo "[export_robot_slide_views] missing authoritative run root: ${SOURCE_ROOT}" >&2
  exit 2
fi

mkdir -p "${OUT_DIR}" "${OUT_DIR}/sim/history"

COMMAND_FILE="${OUT_DIR}/command.txt"
RUN_LOG="${OUT_DIR}/run.log"

{
  echo "$0 --task-slug ${TASK_SLUG} --out-dir ${OUT_DIR} --gif-width ${GIF_WIDTH} --gif-fps ${GIF_FPS} --gif-max-colors ${GIF_MAX_COLORS}"
} > "${COMMAND_FILE}"

{
  echo "[export_robot_slide_views] source_root=${SOURCE_ROOT}"
  echo "[export_robot_slide_views] out_dir=${OUT_DIR}"
} > "${RUN_LOG}"

cp -f "${SOURCE_ROOT}/hero_presentation.mp4" "${OUT_DIR}/hero_presentation.mp4"
cp -f "${SOURCE_ROOT}/hero_debug.mp4" "${OUT_DIR}/hero_debug.mp4"
cp -f "${SOURCE_ROOT}/validation_camera.mp4" "${OUT_DIR}/validation_camera.mp4"
cp -f "${SOURCE_ROOT}/summary.json" "${OUT_DIR}/source_summary.json"
cp -f "${SOURCE_ROOT}/manifest.json" "${OUT_DIR}/source_manifest.json"
cp -f "${SOURCE_ROOT}/multimodal_review.md" "${OUT_DIR}/source_multimodal_review.md"
cp -f "${SOURCE_ROOT}/validation.md" "${OUT_DIR}/source_validation.md"
cp -f "${SOURCE_ROOT}/ffprobe.json" "${OUT_DIR}/source_ffprobe.json"
cp -f "${SOURCE_ROOT}/sim/history/"*.npy "${OUT_DIR}/sim/history/"

"${ROOT}/scripts/render_gif.sh" "${OUT_DIR}/hero_presentation.mp4" "${OUT_DIR}/hero_presentation.gif" "${GIF_WIDTH}" "${GIF_FPS}" "${GIF_MAX_COLORS}"
"${ROOT}/scripts/render_gif.sh" "${OUT_DIR}/hero_debug.mp4" "${OUT_DIR}/hero_debug.gif" "${GIF_WIDTH}" "${GIF_FPS}" "${GIF_MAX_COLORS}"
"${ROOT}/scripts/render_gif.sh" "${OUT_DIR}/validation_camera.mp4" "${OUT_DIR}/validation_camera.gif" "${GIF_WIDTH}" "${GIF_FPS}" "${GIF_MAX_COLORS}"

python - <<PY
import json
from pathlib import Path

root = Path(${ROOT@Q})
out_dir = Path(${OUT_DIR@Q})
meta = json.loads(Path(${RESULT_META@Q}).read_text(encoding="utf-8"))
run = meta["authoritative_run"]
summary = json.loads((out_dir / "source_summary.json").read_text(encoding="utf-8"))

payload = {
    "task_slug": ${TASK_SLUG@Q},
    "source_run_id": run["run_id"],
    "claim_boundary": run["claim_boundary"],
    "source_root": str(Path(${SOURCE_ROOT@Q})),
    "export_root": str(out_dir),
    "views": {
        "hero_presentation": {
            "mp4": "hero_presentation.mp4",
            "gif": "hero_presentation.gif",
        },
        "hero_debug": {
            "mp4": "hero_debug.mp4",
            "gif": "hero_debug.gif",
        },
        "validation_camera": {
            "mp4": "validation_camera.mp4",
            "gif": "validation_camera.gif",
        },
    },
    "key_metrics": {
        "task_duration_s": summary.get("task_duration_s"),
        "actual_tool_first_contact_time_s": summary.get("actual_tool_first_contact_time_s"),
        "actual_finger_box_first_contact_time_s": summary.get("actual_finger_box_first_contact_time_s"),
        "contact_duration_s": summary.get("contact_duration_s"),
    },
}
(out_dir / "summary.json").write_text(json.dumps(payload, indent=2) + "\\n", encoding="utf-8")
PY

cat > "${OUT_DIR}/README.md" <<EOF
# Robot Slide Views Export

This directory is a slide-ready export of the authoritative \`${TASK_SLUG}\` run.

Source run:

- \`${SOURCE_ROOT}\`

Exported views:

- \`hero_presentation.mp4\` / \`hero_presentation.gif\`
- \`hero_debug.mp4\` / \`hero_debug.gif\`
- \`validation_camera.mp4\` / \`validation_camera.gif\`

The export keeps the copied rollout-history files under \`sim/history/\` so the
delivery bundle still satisfies the repo artifact contract.
EOF

{
  echo "[export_robot_slide_views] wrote:"
  echo "  ${OUT_DIR}/hero_presentation.mp4"
  echo "  ${OUT_DIR}/hero_presentation.gif"
  echo "  ${OUT_DIR}/hero_debug.mp4"
  echo "  ${OUT_DIR}/hero_debug.gif"
  echo "  ${OUT_DIR}/validation_camera.mp4"
  echo "  ${OUT_DIR}/validation_camera.gif"
} | tee -a "${RUN_LOG}"
