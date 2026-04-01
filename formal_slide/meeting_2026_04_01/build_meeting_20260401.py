#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import textwrap
from pathlib import Path

import matplotlib
import markdown
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches, Pt
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Text, Token

matplotlib.use("Agg")
from matplotlib import pyplot as plt


MEETING_DIR = Path(__file__).resolve().parent
ROOT = MEETING_DIR.parents[1]
TEMPLATE_PPTX = MEETING_DIR / "templates" / "My Adjust.pptx"
OUT_PPTX = MEETING_DIR / "bridge_meeting_20260401.pptx"
DECK_GIF_DIR = MEETING_DIR / "gif"
DEFAULT_MAX_PPTX_MB = 100.0

REF_TITLE_LEFT = 311760
REF_TITLE_TOP = 444960
REF_TITLE_W = 8520120
REF_TITLE_H = 572400

REF_BODY_LEFT = 311760
REF_BODY_TOP = 1152360
REF_BODY_W = 8520120
REF_BODY_H = 3416040

REF_TITLE_SLIDE_TOP = 744480
REF_TITLE_SLIDE_H = 2052360
REF_SUBTITLE_TOP = 2834280
REF_SUBTITLE_H = 792360

REF_GRID_COMMON_LEFT = 482040
REF_GRID_COMMON_TOP = 1170720
REF_GRID_COMMON_W = 8179560
REF_GRID_COMMON_H = 273960
REF_GRID_LABEL_W = 3983040
REF_GRID_LABEL_H = 243720
REF_GRID_PIC_W = 1735200
REF_GRID_PIC_H = 975960
REF_GRID_TL_LABEL_LEFT = 482040
REF_GRID_TR_LABEL_LEFT = 4678560
REF_GRID_TOP_LABEL_TOP = 1706760
REF_GRID_BOT_LABEL_TOP = 3129480
REF_GRID_TL_PIC_LEFT = 1605960
REF_GRID_TR_PIC_LEFT = 5802480
REF_GRID_TOP_PIC_TOP = 1999440
REF_GRID_BOT_PIC_TOP = 3421872

TABLE_LEFT = 482040
TABLE_TOP = 1524000
TABLE_W = 8179560
TABLE_H = 2857500
TABLE_NOTE_TOP = 1170720
TABLE_NOTE_H = 243720

OFFLINE_GIF_DIR = MEETING_DIR / "slides_assets" / "gif"
RESULTS_META_ROOT = ROOT / "results_meta" / "tasks"

RECALL_CLOTH_GIF_SRC = OFFLINE_GIF_DIR / "cloth_cmp2x3.gif"
RECALL_ZEBRA_GIF_SRC = OFFLINE_GIF_DIR / "zebra_cmp2x3.gif"
RECALL_SLOTH_GIF_SRC = OFFLINE_GIF_DIR / "sloth_cmp2x3.gif"
RECALL_ROPE_GIF_SRC = OFFLINE_GIF_DIR / "rope_drag_on_cmp2x3.gif"
RECALL_CLOTH_OVERLAY_GIF_SRC = OFFLINE_GIF_DIR / "cloth_overlay1x3.gif"
RECALL_ZEBRA_OVERLAY_GIF_SRC = OFFLINE_GIF_DIR / "zebra_overlay1x3.gif"
RECALL_SLOTH_OVERLAY_GIF_SRC = OFFLINE_GIF_DIR / "sloth_overlay1x3.gif"
RECALL_ROPE_OVERLAY_GIF_SRC = OFFLINE_GIF_DIR / "rope_drag_on_overlay1x3.gif"
RECALL_BUNNY_M5_GIF_SRC = OFFLINE_GIF_DIR / "bunny_drop_m5.gif"
RECALL_BUNNY_M500_GIF_SRC = OFFLINE_GIF_DIR / "bunny_drop_m500.gif"

RECALL_CLOTH_GIF = DECK_GIF_DIR / "cloth_cmp2x3_deck.gif"
RECALL_ZEBRA_GIF = DECK_GIF_DIR / "zebra_cmp2x3_deck.gif"
RECALL_SLOTH_GIF = DECK_GIF_DIR / "sloth_cmp2x3_deck.gif"
RECALL_ROPE_GIF = DECK_GIF_DIR / "rope_drag_on_cmp2x3_deck.gif"
RECALL_CLOTH_OVERLAY_GIF = DECK_GIF_DIR / "cloth_overlay1x3_deck.gif"
RECALL_ZEBRA_OVERLAY_GIF = DECK_GIF_DIR / "zebra_overlay1x3_deck.gif"
RECALL_SLOTH_OVERLAY_GIF = DECK_GIF_DIR / "sloth_overlay1x3_deck.gif"
RECALL_ROPE_OVERLAY_GIF = DECK_GIF_DIR / "rope_drag_on_overlay1x3_deck.gif"
RECALL_BUNNY_M5_GIF = DECK_GIF_DIR / "bunny_drop_m5_deck.gif"
RECALL_BUNNY_M500_GIF = DECK_GIF_DIR / "bunny_drop_m500_deck.gif"

PREV_GIF_DIR = ROOT / "formal_slide" / "meeting_2026_03_25" / "gif"
RECALL_ROPE_WEIGHT_1KG_GIF = PREV_GIF_DIR / "rope_bunny_total1kg_m5_v1.gif"
RECALL_ROPE_WEIGHT_5KG_GIF = PREV_GIF_DIR / "rope_bunny_total5kg_m5_v1.gif"
RECALL_BUNNY_SUPPORT_GIF = PREV_GIF_DIR / "cloth_rigid_compare_bunny_m5_v1.gif"
RECALL_BOX_SUPPORT_GIF = PREV_GIF_DIR / "cloth_rigid_compare_box_m5_v1.gif"
RECALL_THIN_EAR_5X_GIF = PREV_GIF_DIR / "thin_ear_ccd5x_v3.gif"
RECALL_THIN_EAR_10X_GIF = PREV_GIF_DIR / "thin_ear_ccd10x_v3.gif"

VIEWER_CODE_PATH = ROOT / "Newton" / "phystwin_bridge" / "demos" / "demo_rope_control_realtime_viewer.py"
NEWTON_CORE_BENCHMARK_PATH = ROOT / "Newton" / "newton" / "asv" / "benchmarks" / "benchmark_mujoco.py"
PHYSTWIN_SPRING_WARP_CODE_PATH = ROOT / "PhysTwin" / "qqtt" / "model" / "diff_simulator" / "spring_mass_warp.py"
IMAGE_DIR = MEETING_DIR / "images"
CODE_REPLAY_SEMANTICS_PNG = IMAGE_DIR / "code_replay_semantics.png"
CODE_GRANULAR_PROFILE_PNG = IMAGE_DIR / "code_granular_profile.png"
CODE_SELFCOLLISION_OBJECT_PNG = IMAGE_DIR / "code_selfcollision_object.png"
CODE_SELFCOLLISION_GROUND_PNG = IMAGE_DIR / "code_selfcollision_ground.png"
PERF_ATTRIBUTION_PNG = IMAGE_DIR / "perf_attribution_breakdown.png"
PERF_NSIGHT_PNG = IMAGE_DIR / "perf_nsight_breakdown.png"
FORCE_DIAG_CODE_PNG = IMAGE_DIR / "code_force_diag_capture.png"
FORCE_LAYOUT_CODE_PNG = IMAGE_DIR / "code_force_diag_layout.png"
PERF_ROPE_CASE_GIF = DECK_GIF_DIR / "rope_perf_case_anchor.gif"

ROPE_PERF_ROOT = ROOT / "results" / "rope_perf_apples_to_apples"
ROPE_PERF_SUMMARY_JSON = ROPE_PERF_ROOT / "summary.json"


def _load_results_meta(task_slug: str) -> dict:
    path = RESULTS_META_ROOT / f"{task_slug}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _meta_local_root(task_slug: str) -> Path | None:
    obj = _load_results_meta(task_slug)
    local_root = (obj.get("authoritative_run") or {}).get("local_artifact_root")
    if not local_root:
        return None
    path = Path(str(local_root))
    return path if path.is_absolute() else (ROOT / path)


def _meta_superseded_root(task_slug: str, *, run_status: str) -> Path | None:
    obj = _load_results_meta(task_slug)
    for row in obj.get("superseded_runs", []):
        if str(row.get("status")) == run_status:
            path = Path(str(row.get("local_artifact_root")))
            return path if path.is_absolute() else (ROOT / path)
    return None


def _resolve_latest_bunny_run() -> Path:
    meta_root = _meta_local_root("bunny_penetration_force_diagnostic")
    if meta_root is not None and meta_root.exists():
        return meta_root.resolve()
    fallback = (
        ROOT
        / "results"
        / "bunny_force_visualization"
        / "runs"
        / "20260330_214500_meeting_ready_force_matrix"
    )
    return fallback.resolve()


CURRENT_BUNNY_RUN = _resolve_latest_bunny_run()
HISTORICAL_BUNNY_RUN = (
    _meta_superseded_root("bunny_penetration_force_diagnostic", run_status="historical")
    or CURRENT_BUNNY_RUN
).resolve()
HISTORICAL_BUNNY_MATRIX_DIR = HISTORICAL_BUNNY_RUN / "artifacts" / "matrix"
CURRENT_BUNNY_BOARD_MP4 = CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "collision_force_board_2x2.mp4"
CURRENT_BUNNY_BOARD_SUMMARY = CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "summary.json"
CURRENT_BUNNY_BOARD_GIF = DECK_GIF_DIR / "bunny_collision_board_2x2.gif"
CURRENT_BUNNY_BOARD_FIRST_FRAME = (
    CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "collision_force_board_2x2_first_frame.png"
)
CURRENT_BUNNY_PANEL_MP4 = {
    "box_penalty": CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "panels" / "box_penalty.mp4",
    "box_total": CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "panels" / "box_total.mp4",
    "bunny_penalty": CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "panels" / "bunny_penalty.mp4",
    "bunny_total": CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "panels" / "bunny_total.mp4",
}
CURRENT_BUNNY_PANEL_GIF = {
    name: DECK_GIF_DIR / f"{name}.gif" for name in CURRENT_BUNNY_PANEL_MP4
}
ACCEPTED_BUNNY_BOARD_PNG = (
    HISTORICAL_BUNNY_MATRIX_DIR / "bunny_penetration_summary_board.png"
    if (HISTORICAL_BUNNY_MATRIX_DIR / "bunny_penetration_summary_board.png").exists()
    else CURRENT_BUNNY_BOARD_FIRST_FRAME
)
SELF_COLLISION_CAMPAIGN_DIR = (_meta_local_root("self_collision_transfer") or (ROOT / "Newton" / "phystwin_bridge" / "results" / "final_self_collision_campaign_20260331_033636_533f3d0")).resolve()
SELF_COLLISION_SLIDES_DIR = SELF_COLLISION_CAMPAIGN_DIR / "slides_update"


def _resolve_case_video_maps() -> tuple[dict[str, Path], dict[str, Path]]:
    summary_path = HISTORICAL_BUNNY_RUN / "summary.json"
    if summary_path.exists():
        obj = json.loads(summary_path.read_text(encoding="utf-8"))
        pheno: dict[str, Path] = {}
        force: dict[str, Path] = {}
        for case in obj.get("cases", []):
            slug = str(case.get("slug") or case.get("case"))
            if not slug:
                continue
            render_video = case.get("render_video")
            force_video = case.get("force_video")
            if render_video:
                pheno[slug] = Path(str(render_video))
            if force_video:
                force[slug] = Path(str(force_video))
        if pheno and force:
            return pheno, force

    pheno = {
        "bunny_baseline": HISTORICAL_BUNNY_MATRIX_DIR / "bunny_baseline" / "phenomenon" / "self_off" / "cloth_bunny_drop_off_m0p5.mp4",
        "box_control": HISTORICAL_BUNNY_MATRIX_DIR / "box_control" / "phenomenon" / "self_off" / "cloth_bunny_drop_off_m0p5.mp4",
        "bunny_low_inertia": HISTORICAL_BUNNY_MATRIX_DIR / "bunny_low_inertia" / "phenomenon" / "self_off" / "cloth_bunny_drop_off_m0p5.mp4",
        "bunny_larger_scale": HISTORICAL_BUNNY_MATRIX_DIR / "bunny_larger_scale" / "phenomenon" / "self_off" / "cloth_bunny_drop_off_m0p5.mp4",
    }
    force = {
        "bunny_baseline": HISTORICAL_BUNNY_MATRIX_DIR / "bunny_baseline" / "force_mechanism" / "self_off" / "force_diagnostic" / "force_diag_trigger_window.mp4",
        "box_control": HISTORICAL_BUNNY_MATRIX_DIR / "box_control" / "force_mechanism" / "self_off" / "force_diagnostic" / "force_diag_trigger_window.mp4",
        "bunny_low_inertia": HISTORICAL_BUNNY_MATRIX_DIR / "bunny_low_inertia" / "force_mechanism" / "self_off" / "force_diagnostic" / "force_diag_trigger_window.mp4",
        "bunny_larger_scale": HISTORICAL_BUNNY_MATRIX_DIR / "bunny_larger_scale" / "force_mechanism" / "self_off" / "force_diagnostic" / "force_diag_trigger_window.mp4",
    }
    return pheno, force


ACCEPTED_PHENO_MP4, ACCEPTED_FORCE_MP4 = _resolve_case_video_maps()
ACCEPTED_PHENO_GIF = {name: DECK_GIF_DIR / f"{name}_phenomenon.gif" for name in ACCEPTED_PHENO_MP4}
ACCEPTED_FORCE_GIF = {name: DECK_GIF_DIR / f"{name}_force.gif" for name in ACCEPTED_FORCE_MP4}
SLIDE_QUESTION_CLAIM_PNG = SELF_COLLISION_SLIDES_DIR / "01_question_and_claim.png"
SLIDE_SOURCE_EVIDENCE_PNG = SELF_COLLISION_SLIDES_DIR / "02_native_source_code_evidence.png"
SLIDE_NATIVE_FAILURE_PNG = SELF_COLLISION_SLIDES_DIR / "03_native_failure_matrix.png"
SLIDE_EXACTNESS_PNG = SELF_COLLISION_SLIDES_DIR / "04_phystwin_exactness.png"
SLIDE_FINAL_DEMO_PNG = SELF_COLLISION_SLIDES_DIR / "05_final_demo_frames.png"
SLIDE_STRICT_PARITY_PNG = SELF_COLLISION_SLIDES_DIR / "06_strict_parity.png"
ROBOT_DROP_OFF_ROOT = (_meta_local_root("native_robot_rope_drop_release") or (ROOT / "results" / "native_robot_rope_drop_release" / "runs" / "20260331_232106_native_franka_recoilfix_drag_off_w5")).resolve()
ROBOT_DROP_ON_ROOT = (_meta_superseded_root("native_robot_rope_drop_release", run_status="validated_ab_compare") or (ROOT / "results" / "native_robot_rope_drop_release" / "runs" / "20260331_232459_native_franka_recoilfix_drag_on_w5")).resolve()
ROBOT_DROP_BASELINE_OFF_MP4 = ROBOT_DROP_OFF_ROOT / "final_presentation.mp4"
ROBOT_DROP_BASELINE_ON_MP4 = ROBOT_DROP_ON_ROOT / "final_presentation.mp4"
ROBOT_DROP_BASELINE_OFF_GIF = DECK_GIF_DIR / "robot_drop_release_drag_off.gif"
ROBOT_DROP_BASELINE_ON_GIF = DECK_GIF_DIR / "robot_drop_release_drag_on.gif"
SELF_MATRIX_OFF_MP4 = SELF_COLLISION_CAMPAIGN_DIR / "matrix" / "off" / "self_off" / "cloth_box_decision_off_m10.mp4"
SELF_MATRIX_NATIVE_MP4 = SELF_COLLISION_CAMPAIGN_DIR / "matrix" / "native" / "self_native" / "cloth_box_decision_native_m10.mp4"
SELF_MATRIX_CUSTOM_H2_MP4 = SELF_COLLISION_CAMPAIGN_DIR / "matrix" / "custom_h2" / "self_custom" / "cloth_box_decision_custom_h2_m10.mp4"
SELF_MATRIX_PHYSTWIN_MP4 = SELF_COLLISION_CAMPAIGN_DIR / "matrix" / "phystwin" / "self_phystwin" / "cloth_box_decision_phystwin_m10.mp4"
SELF_MATRIX_OFF_GIF = DECK_GIF_DIR / "self_matrix_off.gif"
SELF_MATRIX_NATIVE_GIF = DECK_GIF_DIR / "self_matrix_native.gif"
SELF_MATRIX_CUSTOM_H2_GIF = DECK_GIF_DIR / "self_matrix_custom_h2.gif"
SELF_MATRIX_PHYSTWIN_GIF = DECK_GIF_DIR / "self_matrix_phystwin.gif"
SELF_HERO_MP4 = SELF_COLLISION_CAMPAIGN_DIR / "selected" / "self_collision_on_cloth_box_phystwin.mp4"
SELF_PARITY_SUPPORT_MP4 = (
    ROOT
    / "Newton"
    / "phystwin_bridge"
    / "results"
    / "tmp_off_vs_phystwin_302_compare_20260401"
    / "parity_support_demo"
    / "parity_support_demo.mp4"
)
SELF_HERO_GIF = DECK_GIF_DIR / "self_collision_hero.gif"
SELF_PARITY_SUPPORT_GIF = DECK_GIF_DIR / "self_collision_parity_support.gif"

RECALL_DIRECT_GIF_SPECS = [
    (RECALL_CLOTH_GIF_SRC, RECALL_CLOTH_GIF, 800, 6, 80),
    (RECALL_ZEBRA_GIF_SRC, RECALL_ZEBRA_GIF, 800, 6, 80),
    (RECALL_SLOTH_GIF_SRC, RECALL_SLOTH_GIF, 800, 6, 80),
    (RECALL_ROPE_GIF_SRC, RECALL_ROPE_GIF, 800, 6, 80),
    (RECALL_CLOTH_OVERLAY_GIF_SRC, RECALL_CLOTH_OVERLAY_GIF, 800, 6, 80),
    (RECALL_ZEBRA_OVERLAY_GIF_SRC, RECALL_ZEBRA_OVERLAY_GIF, 800, 6, 80),
    (RECALL_SLOTH_OVERLAY_GIF_SRC, RECALL_SLOTH_OVERLAY_GIF, 800, 6, 80),
    (RECALL_ROPE_OVERLAY_GIF_SRC, RECALL_ROPE_OVERLAY_GIF, 800, 6, 80),
    (RECALL_BUNNY_M5_GIF_SRC, RECALL_BUNNY_M5_GIF, 800, 8, 96),
    (RECALL_BUNNY_M500_GIF_SRC, RECALL_BUNNY_M500_GIF, 800, 8, 96),
]


def _load_rope_perf_summary() -> dict:
    if not ROPE_PERF_SUMMARY_JSON.exists():
        return {"rows": []}
    return json.loads(ROPE_PERF_SUMMARY_JSON.read_text(encoding="utf-8"))


ROPE_PERF_SUMMARY = _load_rope_perf_summary()
ROPE_PERF_ROWS = {row["stage"]: row for row in ROPE_PERF_SUMMARY.get("rows", [])}


def _rope_row(stage: str) -> dict:
    return ROPE_PERF_ROWS.get(stage, {})


def _fmt(row: dict, key: str, fmt: str) -> str:
    value = row.get(key)
    if value is None:
        return "n/a"
    return format(value, fmt)


A0_ROW = _rope_row("A0_baseline_throughput")
A1_ROW = _rope_row("A1_precomputed_throughput")
A2_ROW = _rope_row("A2_baseline_attribution")
A3_ROW = _rope_row("A3_precomputed_attribution")
B0_ROW = _rope_row("B0_headless_throughput")
B1_ROW = _rope_row("B1_headless_attribution")


def _rope_payload(stage: str) -> dict:
    return _rope_row(stage).get("payload", {})
A0_PAYLOAD = _rope_payload("A0_baseline_throughput")
A1_PAYLOAD = _rope_payload("A1_precomputed_throughput")
A2_PAYLOAD = _rope_payload("A2_baseline_attribution")
A3_PAYLOAD = _rope_payload("A3_precomputed_attribution")
B0_PAYLOAD = _rope_payload("B0_headless_throughput")
B1_PAYLOAD = _rope_payload("B1_headless_attribution")

A3_AGG = A3_PAYLOAD.get("aggregate", {})
B1_AGG = B1_PAYLOAD.get("aggregate", {})

A3_BRIDGE_MS = (
    float(A3_AGG.get("write_kinematic_state", {}).get("mean_of_run_means_ms", 0.0))
    + float(A3_AGG.get("drag_correction", {}).get("mean_of_run_means_ms", 0.0))
)
A3_INTERNAL_MS = (
    float(A3_AGG.get("spring_forces", {}).get("mean_of_run_means_ms", 0.0))
    + float(A3_AGG.get("triangle_forces", {}).get("mean_of_run_means_ms", 0.0))
    + float(A3_AGG.get("bending_forces", {}).get("mean_of_run_means_ms", 0.0))
    + float(A3_AGG.get("tetra_forces", {}).get("mean_of_run_means_ms", 0.0))
    + float(A3_AGG.get("body_joint_forces", {}).get("mean_of_run_means_ms", 0.0))
)
A3_COLLISION_MS = (
    float(A3_AGG.get("particle_grid_build", {}).get("mean_of_run_means_ms", 0.0))
    + float(A3_AGG.get("model_collide", {}).get("mean_of_run_means_ms", 0.0))
    + float(A3_AGG.get("particle_contact_forces", {}).get("mean_of_run_means_ms", 0.0))
    + float(A3_AGG.get("triangle_contact_forces", {}).get("mean_of_run_means_ms", 0.0))
    + float(A3_AGG.get("body_contact_forces", {}).get("mean_of_run_means_ms", 0.0))
    + float(A3_AGG.get("particle_body_contact_forces", {}).get("mean_of_run_means_ms", 0.0))
)
A3_INTEGRATION_MS = (
    float(A3_AGG.get("integrate_particles", {}).get("mean_of_run_means_ms", 0.0))
    + float(A3_AGG.get("integrate_bodies", {}).get("mean_of_run_means_ms", 0.0))
)
A3_TOTAL_SUBSTEP_MS = float(A3_AGG.get("total_substep", {}).get("mean_of_run_means_ms", 0.0))
A3_UNEXPLAINED_MS = max(
    A3_TOTAL_SUBSTEP_MS - A3_BRIDGE_MS - A3_INTERNAL_MS - A3_COLLISION_MS - A3_INTEGRATION_MS,
    0.0,
)

B1_CONTROLLER_FRAME_MS = float(B1_AGG.get("controller_target", {}).get("mean_of_run_means_ms", 0.0))
B1_SIM_LAUNCH_MS = float(B1_AGG.get("simulator_launch", {}).get("mean_of_run_means_ms", 0.0))
B1_STATE_RESET_MS = float(B1_AGG.get("state_reset", {}).get("mean_of_run_means_ms", 0.0))

RECALL_SLIDES: list[dict] = [
    {
        "kind": "title",
        "title": "Xinjie Zhang",
        "subtitle": [
            "April 1 meeting opening.",
            "Today's five-part agenda:",
            "1. Recall",
            "2. Performance analysis",
            "3. Penetration analysis",
            "4. Self-collision, Newton way",
            "5. Robotic with deformable objects",
        ],
        "transcript": [
            "这一页是 opening speaker page。",
            "这次 meeting 我会按五段讲：1. recall，2. performance analysis，3. penetration analysis，4. self-collision Newton way，5. robotic with deformable objects。",
            "所以 opening 要做的不是再把会议压成“short recall + two results”，而是先把这五段主线直接说清楚。",
        ],
    },
    {
        "kind": "grid",
        "title": "Recall R1: The Bridge Baseline Was Already Established",
        "common_settings": "These four PASS cases were already established before this week's new discussion.",
        "items": [
            ("Cloth baseline already worked", RECALL_CLOTH_GIF),
            ("Zebra baseline already worked", RECALL_ZEBRA_GIF),
            ("Sloth baseline already worked", RECALL_SLOTH_GIF),
            ("Rope baseline already worked", RECALL_ROPE_GIF),
        ],
        "transcript": [
            "第一页 recall 压成一张图就够了。",
            "cloth、zebra、sloth、rope 这四条 baseline 不是今天新证明的内容。",
            "这页的作用只是提醒老师：PhysTwin object import into Newton 这条大主线，上周已经建立了。",
        ],
    },
    {
        "kind": "grid",
        "title": "Recall R2: The Baseline Already Matched The Reference Motion",
        "common_settings": "Visual recall only: last week already had direct reference-vs-Newton motion overlays for the baseline bridge cases.",
        "items": [
            ("Cloth overlay recall", RECALL_CLOTH_OVERLAY_GIF),
            ("Zebra overlay recall", RECALL_ZEBRA_OVERLAY_GIF),
            ("Sloth overlay recall", RECALL_SLOTH_OVERLAY_GIF),
            ("Rope overlay recall", RECALL_ROPE_OVERLAY_GIF),
        ],
        "transcript": [
            "第二页 recall 继续只做 visual reminder。",
            "上周不只是说“大概像”，而是已经把这些 baseline case 做成了更直接的 motion overlay 对照。",
            "所以现在不是 bridge baseline 还没站住，而是 baseline 已经站住以后继续收窄问题。",
        ],
    },
    {
        "kind": "twocol",
        "title": "Recall R3: Deformable-Rigid Interaction Already Existed",
        "common_settings": "Last week already established that deformable-rigid interaction exists; the later question was why cloth still penetrates bunny.",
        "left_label": "Rope + bunny recall\nbunny mass = 5 kg",
        "left_path": RECALL_BUNNY_M5_GIF,
        "right_label": "Rope + bunny recall\nbunny mass = 500 kg",
        "right_path": RECALL_BUNNY_M500_GIF,
        "transcript": [
            "这一页只回忆一件事：novel rigid bunny interaction 早就不是空想，而是已经能工作。",
            "所以这周的讨论，不再是“能不能 interact”，而是“interaction 已经有了以后，还剩下哪些真正的问题”。",
        ],
    },
    {
        "kind": "twocol",
        "title": "Recall R4: Weight Change Did Not Remove Interaction",
        "common_settings": "Visual recall: last week already showed that changing deformable total weight did not remove deformable-rigid interaction itself.",
        "left_label": "Rope total mass = 1 kg",
        "left_path": RECALL_ROPE_WEIGHT_1KG_GIF,
        "right_label": "Rope total mass = 5 kg",
        "right_path": RECALL_ROPE_WEIGHT_5KG_GIF,
        "transcript": [
            "这一页 recall 上周的 weight compare。",
            "它的作用不是再讲参数，而是提醒老师：weight 改了以后，interaction 仍然在。",
            "所以后面 bunny penetration 的问题，不应该被讲成“bridge 根本没有 interaction”。",
        ],
    },
    {
        "kind": "twocol",
        "title": "Recall R5: Bunny Was Harder Than Thick Box",
        "common_settings": "This was the key visual diagnosis from last week: the rigid support problem was geometry-dependent, not a missing bridge baseline.",
        "left_label": "Same cloth + bunny support",
        "left_path": RECALL_BUNNY_SUPPORT_GIF,
        "right_label": "Same cloth + thick-box support",
        "right_path": RECALL_BOX_SUPPORT_GIF,
        "transcript": [
            "这一页 recall 的作用很直接。",
            "同样是 rigid support，换成 thick box 就明显更稳定。",
            "所以上周真正被收窄出来的问题，是 bunny local geometry 和 support patch，不是 bridge 连 contact 都没有。",
        ],
    },
    {
        "kind": "twocol",
        "title": "Recall R6: Radius Helped, But Thin Geometry Still Survived",
        "common_settings": "Last week already showed the hardest visual counterexample: larger radius helped, but thin geometry still kept nonzero penetration.",
        "left_label": "Thin-ear close-up\n5x radius",
        "left_path": RECALL_THIN_EAR_5X_GIF,
        "right_label": "Thin-ear close-up\n10x radius",
        "right_path": RECALL_THIN_EAR_10X_GIF,
        "transcript": [
            "最后一页 recall 只保留最后一个最难反驳的 visual point。",
            "radius 变大确实会帮忙，但 thin-ear geometry 仍然会留下 penetration。",
            "所以这周应该从一个更窄、更清楚的 baseline 继续往下做，而不是重新回去证明 bridge baseline。",
        ],
    },
    {
        "kind": "perf_gif_bullets",
        "title": "Hypothesis P1: Fair Benchmark Before Optimization",
        "gif_label": "Same `rope_double_hand` replay case used later for the no-render benchmark.",
        "gif_path": PERF_ROPE_CASE_GIF,
        "note": "Visual anchor only: the speed claim still comes from the no-render benchmark, not from this GIF.",
        "bullets": [
            "**Same replay:** one rope case, one controller trajectory, one `dt/substeps`, one GPU, no render.",
            "**Throughput first:** A0/A1 vs B0 answer who is slower.",
            "**Attribution second:** A2/A3/B1 explain why.",
            "**Optimization last:** no fixes before the benchmark is fair.",
        ],
        "transcript": [
            "这里开始进入第二段 performance analysis。",
            "这一页现在只保留 hypothesis 和 benchmark contract，本来放在 slide 上的很多解释都移回 transcript。",
            "左边这个 GIF 只是 visual anchor，提醒老师后面所有 profiling 数字对应的是同一个 `rope_double_hand` replay case，而不是另一个 playground scene。",
            "真正的 speed claim 不是从 GIF 看出来的，而是从 no-render benchmark 里算出来的。",
            "这里最重要的 methodological point 只有四个：same case、same controller trajectory、same `dt/substeps`、same GPU，而且主比较必须把 rendering 排除掉。",
            "所以这次 profiling section 的逻辑固定成两步：先用 Newton A0、Newton A1、PhysTwin B0 回答谁快谁慢；再用 A2、A3、B1 和 Nsight 解释为什么慢。",
            "这样做是为了避免把 attribution 模式自己的同步开销误当成真实吞吐，也避免把不公平的 GUI path 混进主表。",
            f"另外 same-case identity 不是口头假设，而是已经检查到 PhysTwin controller trajectory 和 IR 的 max abs diff 是 {B0_PAYLOAD.get('trajectory_parity', {}).get('controller_traj_max_abs_diff', 0.0):.1e}，所以 benchmark 的输入本身是对上的。",
        ],
    },
    {
        "kind": "code_twocol_large",
        "title": "Source Proof P1: Same Replay, Different Execution Style",
        "note": "Real upstream source only. Newton core shows the optional CUDA-graph path; PhysTwin rope source captures and replays a forward graph.",
        "left_label": "Newton core benchmark: optional CUDA graph path, otherwise a substep loop + solver.step.",
        "left_path": CODE_REPLAY_SEMANTICS_PNG,
        "right_label": "PhysTwin rope source: use_graph, ScopedCapture, graph, forward_graph.",
        "right_path": CODE_GRANULAR_PROFILE_PNG,
        "transcript": [
            "这一页我按你的反馈改成了真正有意义的 upstream source proof，不再引用我们自己写的 wrapper CLI。",
            "左边现在引用的是 Newton core 里的 `asv/benchmarks/benchmark_mujoco.py`。它同时保留了三件关键事情：`if self.use_cuda_graph`、`with wp.ScopedCapture()`、以及 fallback 的 `for sim_substeps -> solver.step -> self.simulate()` 路径。",
            "这段代码的作用不是说 rope benchmark 就是跑这个 benchmark 文件，而是说明 Newton upstream 自己就已经有一套 graph-capture execution idiom；如果不用这条 idiom，默认结构仍然像 repeated substep loop。",
            "右边保留的是 PhysTwin `spring_mass_warp.py` 里的 upstream source code，而且只保留 `cfg.use_graph`、`ScopedCapture`、`self.graph`、`self.forward_graph` 这些最能说明 execution style 的行。",
            "所以这页真正要证明的不是我们的 wrapper 参数，而是 upstream code 层面上，两边对 graph replay 的组织方式本来就不同；这才是后面 Nsight interpretation 的源码背景。",
        ],
    },
    {
        "kind": "table",
        "title": "Result P1: A1 Is Still 3.30x Slower Than B0",
        "note": "Same `rope_double_hand` replay. No render. RTX 4090.",
        "columns": ["Config", "Replay Path", "ms/substep", "RTF", "Meaning"],
        "rows": [
            [
                "Newton A0",
                "controller targets uploaded every substep",
                _fmt(A0_ROW, "ms_per_substep_mean", ".6f"),
                _fmt(A0_ROW, "rtf_mean", ".3f"),
                "repeated controller-write overhead is included",
            ],
            [
                "Newton A1",
                "controller targets precomputed once",
                _fmt(A1_ROW, "ms_per_substep_mean", ".6f"),
                _fmt(A1_ROW, "rtf_mean", ".3f"),
                "controller-write cost is reduced, but Newton is still slower",
            ],
            [
                "PhysTwin B0",
                "graph-captured headless replay",
                _fmt(B0_ROW, "ms_per_substep_mean", ".6f"),
                _fmt(B0_ROW, "rtf_mean", ".3f"),
                "same replay runs through a graph-launch path",
            ],
        ],
        "transcript": [
            "这一页保留 table，因为这里的核心就是一个 bounded benchmark result。",
            "我把 slide note 压短了，只保留同 case、no render、RTX 4090 这三个最重要的 reading keys；更细的 methodology 现在都回到 transcript。",
            "完整 rope replay 现在已经做成 same-case apples-to-apples throughput table。264 个 trajectory frame 展开以后是 175421 个 substep，对应 8.77 秒物理时间。",
            f"authoritative 数字很直接：Newton A0 `{_fmt(A0_ROW, 'ms_per_substep_mean', '.6f')} ms/substep`，Newton A1 `{_fmt(A1_ROW, 'ms_per_substep_mean', '.6f')} ms/substep`，PhysTwin B0 `{_fmt(B0_ROW, 'ms_per_substep_mean', '.6f')} ms/substep`。",
            f"所以这里的结论仍然不变：即使把 controller bridge tax 降下去，Newton 在 clean rope replay 上仍然比 PhysTwin 慢 `{_fmt(A1_ROW, 'slowdown_vs_phystwin_headless', '.3f')}x`。",
            "这一页不再重复太多 caveat，因为 fairness caveat 已经在前两页讲完了。",
        ],
    },
    {
        "kind": "body",
        "title": "Conclusion P2: Bridge Tax Exists, But Collision Is Still Tiny",
        "bullets": [
            "**A0 -> A1:** `1.87x` faster, so controller bridge tax is real.",
            "**A3:** collision is only about `0.004 ms/substep`; bridge and residual overhead are much larger.",
            "**B1:** PhysTwin frame cost is still dominated by simulator launch, not controller/reset.",
        ],
        "transcript": [
            "这一页不再用数据图，而是只保留 progress statement。",
            f"首先 H1 还是一样硬：A0 到 A1 是 `{A0_ROW.get('ms_per_substep_mean', 0.0) / max(A1_ROW.get('ms_per_substep_mean', 1.0e-12), 1.0e-12):.3f}x` 的提升，所以 controller bridge tax 是真实存在的。",
            f"但 bridge tax 不是全部。Newton A3 的 precomputed attribution 里，bridge 是 `{A3_BRIDGE_MS:.3f} ms/substep`，internal force `{A3_INTERNAL_MS:.3f}`，integration `{A3_INTEGRATION_MS:.3f}`，collision 只有 `{A3_COLLISION_MS:.3f}`，还剩 `{A3_UNEXPLAINED_MS:.3f}` 的 runtime overhead。",
            f"右边的 PhysTwin B1 frame-level attribution 则说明它的大头基本就是 simulator launch，本身大约 `{B1_SIM_LAUNCH_MS:.3f} ms/frame`；controller target `{B1_CONTROLLER_FRAME_MS:.3f}` 和 state reset `{B1_STATE_RESET_MS:.3f}` 都是小头。",
            "所以这一页的真正 point 还是结构：bridge tax 确实存在，但 clean rope replay 的 remaining gap 不是 collision story。",
        ],
    },
    {
        "kind": "body",
        "title": "Conclusion P3: The Residual Gap Still Looks Like Launch Structure",
        "bullets": [
            "**Nsight A1:** `cuLaunchKernel 77.2%`, `cudaMemsetAsync 21.5%`.",
            "**Nsight B0:** `cudaGraphLaunch 92.6%`, `cuCtxSynchronize 2.9%`.",
            "**Next move:** optimize batching / graph-like replay before blaming collision.",
        ],
        "transcript": [
            "这一页也不再用数据图，只保留最终解释。",
            "Newton A1 的 CUDA API 时间里，`cuLaunchKernel` 占到 77.2%，其余主要是 `cudaMemsetAsync` 21.5%。这说明 Newton replay 仍然像 many decoupled launches。",
            "PhysTwin B0 的 CUDA API 时间里，92.6% 是 `cudaGraphLaunch`，`cuCtxSynchronize` 只有 2.9%。所以它不是 GUI path，而是 graph-captured replay execution style。",
            "这页真正要堵住的反驳是：如果 residual gap 主要来自 collision，Nsight 不会长成现在这样；现在它长成了 launch structure 的样子。",
            "因此 optimization implication 保持不变：先保留 precomputed writes，再优先研究更 graph-like 或更 batched 的 Newton replay，弱接触 rope profiling 继续独立处理。",
        ],
    },
    {
        "kind": "body",
        "title": "Hypothesis F1: A Force Video Must Preserve Both Global Cloth Behavior And Local Contact Mechanism",
        "bullets": [
            "**Failure condition:** a local patch alone is not enough; we must still see the full cloth and bunny.",
            "**Method:** split the explanation into **phenomenon** and **force mechanism**, but keep the force video itself as **global panel + local zoom panel**.",
            "**Acceptance gate:** no black frames, no fake slideshow, and no loss of the global cloth in the main panel.",
            "**Progress:** we now have one accepted 4-case package instead of one fragile single-case debug clip.",
        ],
        "transcript": [
            "这里开始进入第三段 penetration analysis。",
            "这一页先把新的 hypothesis 说清楚。",
            "教授要的不是一个只剩局部 probe 的 force patch，也不是一个 static trigger snapshot。",
            "真正需要的是两件事同时成立：第一，看到整块 cloth 相对于 bunny 的整体 penetration 过程；第二，在 local patch 里看到 outward normal、external force、internal force 和 acceleration 的机制解释。",
            "所以这次我把输出正式拆成 phenomenon video 和 force mechanism video，但 force mechanism 本身仍然保留 global panel 加 local zoom panel，而不是只放局部 close-up。",
        ],
    },
    {
        "kind": "grid",
        "title": "Result F1: Global Phenomenon Videos Now Cover The Whole Penetration Process",
        "common_settings": None,
        "items": [
            ("Bunny baseline\nfull process", ACCEPTED_PHENO_GIF["bunny_baseline"]),
            ("Box control\nfull process", ACCEPTED_PHENO_GIF["box_control"]),
            ("Bunny low inertia\nfull process", ACCEPTED_PHENO_GIF["bunny_low_inertia"]),
            ("Bunny larger scale\nfull process", ACCEPTED_PHENO_GIF["bunny_larger_scale"]),
        ],
        "transcript": [
            "这一页只讲 phenomenon，不讲 force。",
            "现在四个 case 都有 accepted 的 global process video，而且都过了 black-screen、motion 和 temporal-density 的 QA。",
            "从这里可以清楚看到四种情况里，pre-contact、first contact、penetration growth 和后续 settle 的整体行为。",
            "也就是说，我们现在已经不再依赖单帧截图来讲 penetration，而是真正有了 meeting-ready 的过程视频。",
        ],
    },
    {
        "kind": "grid",
        "title": "Result F2: Split Single-Panel Videos Now Match The Current 2x2 Board",
        "common_settings": "Same workpoint: cloth 0.1 kg, rigid 0.5 kg.",
        "items": [
            ("Box penalty\nsingle panel", CURRENT_BUNNY_PANEL_GIF["box_penalty"]),
            ("Box total\nsingle panel", CURRENT_BUNNY_PANEL_GIF["box_total"]),
            ("Bunny penalty\nsingle panel", CURRENT_BUNNY_PANEL_GIF["bunny_penalty"]),
            ("Bunny total\nsingle panel", CURRENT_BUNNY_PANEL_GIF["bunny_total"]),
        ],
        "transcript": [
            "这一页现在不再放旧的四个历史 force mechanism 视频了。",
            "这里也把实验设定说清楚：cloth total mass 是 0.1 kg，rigid target mass 是 0.5 kg。",
            "现在 F2 里的四个单视频，都是直接从当前 canonical `2 x 2` board 裁出来的单面板。",
            "也就是说，这一页只负责把四个 panel 单独放大给老师看：box penalty、box total、bunny penalty、bunny total。",
            "这样 F2 和下一页 F3 就不会再出现“这一页还是旧结果、下一页才是新结果”的割裂了。",
        ],
    },
    {
        "kind": "image",
        "title": "Result F3: The New 2x2 Board Makes The Box-vs-Bunny Comparison Immediate",
        "note": "TL box penalty, TR box total, BL bunny penalty, BR bunny total.",
        "path": CURRENT_BUNNY_BOARD_GIF,
        "transcript": [
            "这一页就是新的 `2 x 2` board video，我把它直接放进 PPT 里了。",
            "这里必须把实验设定写明：self-collision 是 OFF，cloth total mass 是 0.1 kg，rigid target mass 是 0.5 kg。",
            "它的结构非常直接：左上是 box penalty，右上是 box total，左下是 bunny penalty，右下是 bunny total。",
            "所以这一页的价值不是再讲一个局部 mechanism patch，而是把 box versus bunny、penalty versus total 这两个对比同时压进一个 meeting-readable clip。",
            "如果现场只想停一页讲 penetration，我现在会优先停这一页，因为它最接近老师要的最终 visual comparison。",
        ],
    },
    {
        "kind": "body",
        "title": "Hypothesis S1: Native Newton Is Not Enough For The Final Self-Collision Claim",
        "bullets": [
            "**Claim boundary:** strict parity only covers PhysTwin-native self-collision plus implicit ground.",
            "**Decision scene:** cloth+box is the controlled scene for video comparison, not the exactness scope itself.",
            "**Progress:** operator exactness passed, but rollout parity is still blocked.",
        ],
        "transcript": [
            "这里开始进入第四段 self-collision, Newton way。",
            "这一章不再用静态 campaign board 讲，而是收成一个 hypothesis-driven block。",
            "这一页先把 hypothesis 说清楚：如果 native Newton 已经足够，我们就不需要 bridge-side phystwin 这条更窄的 exact path。",
            "同时 claim boundary 也要收紧：strict parity 只针对 PhysTwin 原生定义的 cloth self-collision 加 implicit ground，不把 box-support semantics 混进 exact claim 里。",
            "当前 progress 也要一句话说死：operator exactness 已经过，但 rollout parity 仍然 blocked。",
        ],
    },
    {
        "kind": "code_twocol_large",
        "title": "Source Proof S1: PhysTwin Native Contact Scope Is Pairwise Self-Collision + Ground",
        "note": "PhysTwin upstream source only.",
        "left_label": "PhysTwin object_collision: pairwise self-collision updates velocity from collision impulses.",
        "left_path": CODE_SELFCOLLISION_OBJECT_PNG,
        "right_label": "PhysTwin integrate_ground_collision: implicit ground-plane TOI + velocity update.",
        "right_path": CODE_SELFCOLLISION_GROUND_PNG,
        "transcript": [
            "这一页只用 PhysTwin upstream source 来证明 strict parity 的 scope，不再 cite 我们自己的 bridge code。",
            "左边这段是 `object_collision`，说明 PhysTwin 原生的 cloth contact 里有 pairwise object self-collision，而且速度修正是基于 collision impulse average。",
            "右边这段是 `integrate_ground_collision`，说明 PhysTwin 原生还定义了 implicit ground-plane TOI 和 velocity update。",
            "所以 strict parity 的 claim boundary 不是拍脑袋收窄，而是直接从 PhysTwin native contact source 推出来的：object self-collision 加 ground collision。",
            "也正因为这个 source scope，本章后面的 cloth+box scene 只能作为 decision/demo evidence，不能被包装成 strict parity scene。",
        ],
    },
    {
        "kind": "grid",
        "title": "Result S1: Native Is Not Enough On The Controlled Cloth+Box Scene",
        "common_settings": None,
        "items": [
            ("OFF", SELF_MATRIX_OFF_GIF),
            ("Native", SELF_MATRIX_NATIVE_GIF),
            ("Custom H2", SELF_MATRIX_CUSTOM_H2_GIF),
            ("Phystwin", SELF_MATRIX_PHYSTWIN_GIF),
        ],
        "transcript": [
            "这一页是 scene-level video evidence，不是源码页。",
            "这里直接放 controlled cloth+box decision videos：OFF、native、custom H2、phystwin。",
            "这页要回答的 hypothesis 很窄：native 能不能直接承担 final self-collision claim。",
            "目前 answer 仍然是否定的。能继续 defend 下去的是 bridge-side phystwin candidate，而不是 native。",
            "所以这页的 progress 不是“所有问题都 solved”，而是 decision scene 已经把 native 不足这件事视频化、可比较化了。",
        ],
    },
    {
        "kind": "twocol",
        "title": "Progress S2: The Demo Is Ready, But Strict Parity Is Still Blocked",
        "common_settings": None,
        "left_label": "QC-passing cloth+box `phystwin` hero demo",
        "left_path": SELF_HERO_GIF,
        "right_label": "Parity support demo on the in-scope reference path",
        "right_path": SELF_PARITY_SUPPORT_GIF,
        "transcript": [
            "最后这一页把当前 self-collision progress 和 blocker 同时讲清楚。",
            "左边是已经可汇报的 cloth+box `phystwin` hero demo，它通过了 black/blank、motion 和 scene-visibility 的 QC，所以 video claim 已经成立。",
            "右边是 parity support video，用来提醒老师：strict parity 的 in-scope reference path 仍然在，而且我们不是拿错 scene 在讲 parity。",
            "同时 exactness 本身也已经过了，`max_abs_dv` 在 1e-6 量级、`median_rel_dv` 在 1e-8 量级。",
            "但 full rollout parity 仍然停在 1e-2 量级，所以当前 honest progress 应该讲成：demo-ready yes，operator exact yes，strict rollout parity not yet。",
        ],
    },
    {
        "kind": "twocol",
        "title": "Conclusion R1: The Current Robot-Deformable Claim Is A Defendable Native Baseline",
        "common_settings": "Native Franka release/drop baseline, not full manipulation.",
        "left_label": "Drag OFF\npromoted best run",
        "left_path": ROBOT_DROP_BASELINE_OFF_GIF,
        "right_label": "Drag ON\nmatched A/B run",
        "right_path": ROBOT_DROP_BASELINE_ON_GIF,
        "transcript": [
            "最后一段是 robotic with deformable objects。",
            "这一章今天的可 defend 结论，不是“完整 manipulation 已经完成”，而是 native Franka 的 release/drop baseline 已经成立，所以 robot-deformable chapter 至少有了一个物理上可信、视频上可读的起点。",
            "更具体地说，它用 `demo_robot_rope_franka.py` 里的 `drop_release_baseline` 证明了：robot visible、rope 先被 support、release 前先过 settle gate、release 后以 gravity-dominated free fall 落到 real ground collider，而且 presentation video 保持 1:1 time。",
            "所以这页不是把 robot 章节降格成一个无关小 demo，而是把它收敛成当前最能 defend 的子结论。",
            "右边保留 matched drag ON 版本，只是为了说明 A/B 已经做过。结论不是“drag 救了 free fall”，而是 OFF 和 ON 都通过主 gate，所以 drag 不是这个 baseline 的根因解释。",
        ],
    },
]


def _build_transcript_md(slides: list[dict] | None = None) -> str:
    lines = [
        "# Meeting Transcript — PhysTwin -> Newton Bridge",
        "",
        "语言：中文主讲 + English terminology  ",
        "形式：five-part agenda  ",
        "结构：1. recall  2. performance analysis  3. penetration analysis  4. self-collision, Newton way  5. robotic with deformable objects  ",
        "目标：让 opening framing、transcript framing 和实际 deck 章节结构完全对齐",
        "",
        "---",
        "",
    ]
    active_slides = slides or list(RECALL_SLIDES)
    for idx, slide in enumerate(active_slides, start=1):
        lines.append(f"## Slide {idx} — {slide['title']}")
        for paragraph in slide["transcript"]:
            lines.append(paragraph)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _prepare_generated_assets() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    DECK_GIF_DIR.mkdir(parents=True, exist_ok=True)
    for src, out, width, fps, max_colors in RECALL_DIRECT_GIF_SPECS:
        _ensure_resized_gif(src, out, width=width, fps=fps, max_colors=max_colors)
    _ensure_resized_gif(RECALL_ROPE_GIF_SRC, PERF_ROPE_CASE_GIF, width=720, fps=8, max_colors=96)
    _code_excerpt_image(
        NEWTON_CORE_BENCHMARK_PATH,
        "newton_core_graph_path",
        _extract_code_segments(
            NEWTON_CORE_BENCHMARK_PATH,
            [(338, 345), (348, 352), (358, 362)],
            highlight_lines={339, 344, 349, 351, 360},
        ),
        CODE_REPLAY_SEMANTICS_PNG,
    )
    _code_excerpt_image(
        PHYSTWIN_SPRING_WARP_CODE_PATH,
        "phystwin_graph_capture",
        _extract_code_segments(
            PHYSTWIN_SPRING_WARP_CODE_PATH,
            [(768, 780), (800, 802)],
            highlight_lines={769, 772, 779, 800, 802},
        ),
        CODE_GRANULAR_PROFILE_PNG,
    )
    _code_excerpt_image(
        PHYSTWIN_SPRING_WARP_CODE_PATH,
        "phystwin_object_collision",
        _extract_code_segments(
            PHYSTWIN_SPRING_WARP_CODE_PATH,
            [(261, 269), (286, 293)],
            highlight_lines={261, 287, 289, 291},
        ),
        CODE_SELFCOLLISION_OBJECT_PNG,
    )
    _code_excerpt_image(
        PHYSTWIN_SPRING_WARP_CODE_PATH,
        "phystwin_ground_collision",
        _extract_code_segments(
            PHYSTWIN_SPRING_WARP_CODE_PATH,
            [(303, 307), (319, 324), (342, 347)],
            highlight_lines={303, 320, 322, 342, 346},
        ),
        CODE_SELFCOLLISION_GROUND_PNG,
    )
    for name, src in ACCEPTED_PHENO_MP4.items():
        _ensure_gif(src, ACCEPTED_PHENO_GIF[name], width=640, fps=8, max_colors=96)
    if CURRENT_BUNNY_BOARD_MP4.exists():
        _ensure_current_bunny_panel_mp4s()
        _ensure_gif(CURRENT_BUNNY_BOARD_MP4, CURRENT_BUNNY_BOARD_GIF, width=960, fps=8, max_colors=128)
        for name, src in CURRENT_BUNNY_PANEL_MP4.items():
            _ensure_gif(src, CURRENT_BUNNY_PANEL_GIF[name], width=640, fps=8, max_colors=96)
    for name, src in ACCEPTED_FORCE_MP4.items():
        _ensure_gif(src, ACCEPTED_FORCE_GIF[name], width=640, fps=8, max_colors=96)
    for src, out in (
        (SELF_MATRIX_OFF_MP4, SELF_MATRIX_OFF_GIF),
        (SELF_MATRIX_NATIVE_MP4, SELF_MATRIX_NATIVE_GIF),
        (SELF_MATRIX_CUSTOM_H2_MP4, SELF_MATRIX_CUSTOM_H2_GIF),
        (SELF_MATRIX_PHYSTWIN_MP4, SELF_MATRIX_PHYSTWIN_GIF),
        (SELF_HERO_MP4, SELF_HERO_GIF),
        (SELF_PARITY_SUPPORT_MP4, SELF_PARITY_SUPPORT_GIF),
    ):
        if src.exists():
            _ensure_gif(src, out, width=640, fps=8, max_colors=96)
    _ensure_gif(ROBOT_DROP_BASELINE_OFF_MP4, ROBOT_DROP_BASELINE_OFF_GIF, width=640, fps=8, max_colors=96)
    _ensure_gif(ROBOT_DROP_BASELINE_ON_MP4, ROBOT_DROP_BASELINE_ON_GIF, width=640, fps=8, max_colors=96)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the 2026-04-01 recall-only meeting deck.")
    parser.add_argument("--out-dir", type=Path, default=MEETING_DIR)
    parser.add_argument(
        "--out-pptx",
        type=Path,
        default=None,
        help="Optional explicit PPTX output path. Defaults to bridge_meeting_20260401.pptx in --out-dir.",
    )
    parser.add_argument(
        "--slide-range",
        type=str,
        default=None,
        help="Optional 1-based inclusive slide range like 8-12. When omitted, build the full deck.",
    )
    parser.add_argument(
        "--max-pptx-mb",
        type=float,
        default=DEFAULT_MAX_PPTX_MB,
        help="Hard size budget for the generated PPTX in MB. Set <= 0 to disable the size gate.",
    )
    return parser.parse_args()


def _layout(prs: Presentation):
    blank_idx = 6 if len(prs.slide_layouts) > 6 else 0
    return prs.slide_layouts[blank_idx]


def _delete_all_slides(prs: Presentation) -> None:
    sld_id_list = prs.slides._sldIdLst
    for sld_id in list(sld_id_list):
        prs.part.drop_rel(sld_id.rId)
        sld_id_list.remove(sld_id)


def _clear_placeholders(slide) -> None:
    for shape in list(slide.placeholders):
        try:
            sp = shape.element
            sp.getparent().remove(sp)
        except Exception:
            pass


def _set_marked_paragraph(
    paragraph,
    text: str,
    *,
    font_name: str,
    font_size: int,
    color: RGBColor,
    accent_color: RGBColor | None = None,
    bold_default: bool = False,
) -> None:
    paragraph.clear()
    parts = text.split("**")
    for idx, part in enumerate(parts):
        if not part:
            continue
        highlighted = idx % 2 == 1
        run = paragraph.add_run()
        run.text = part
        run.font.name = font_name
        run.font.size = Pt(font_size)
        run.font.bold = True if highlighted else bold_default
        run.font.color.rgb = accent_color if highlighted and accent_color else color


def _set_lines(shape, lines: list[str]) -> None:
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    lines = [line for line in lines if str(line).strip()]
    for i, raw in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        stripped = str(raw).lstrip(" ")
        indent = len(str(raw)) - len(stripped)
        p.level = 1 if indent >= 2 else 0
        _set_marked_paragraph(
            p,
            stripped,
            font_name="Arial",
            font_size=18 if p.level == 0 else 16,
            color=RGBColor(0x22, 0x22, 0x22),
            accent_color=RGBColor(0x1F, 0x4E, 0x79),
        )


def _set_title_textbox(box, title: str, *, size_pt: int = 28) -> None:
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    p = tf.paragraphs[0]
    _set_marked_paragraph(
        p,
        title,
        font_name="Arial",
        font_size=size_pt,
        color=RGBColor(0x00, 0x00, 0x00),
        accent_color=RGBColor(0x1F, 0x4E, 0x79),
    )


def _add_label(
    slide,
    left: int,
    top: int,
    width: int,
    height: int,
    text: str,
    *,
    font_size: int = 12,
    bold: bool = True,
) -> None:
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    p = tf.paragraphs[0]
    _set_marked_paragraph(
        p,
        text,
        font_name="Arial",
        font_size=font_size,
        color=RGBColor(0x22, 0x22, 0x22),
        accent_color=RGBColor(0x1F, 0x4E, 0x79),
        bold_default=bold,
    )


def _fit_box(iw: int, ih: int, bw: int, bh: int) -> tuple[int, int, int, int]:
    scale = min(bw / max(iw, 1), bh / max(ih, 1))
    w, h = max(1, int(iw * scale)), max(1, int(ih * scale))
    return (bw - w) // 2, (bh - h) // 2, w, h


def _load_mono_font(size: int = 18, *, bold: bool = False):
    candidates = (
        [
            "/usr/share/fonts/truetype/cascadia/CascadiaCode-Bold.ttf",
            "/usr/share/fonts/truetype/cascadia/CascadiaMono-Bold.ttf",
            "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Consolas Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
        ]
        if bold
        else [
            "/usr/share/fonts/truetype/cascadia/CascadiaCode.ttf",
            "/usr/share/fonts/truetype/cascadia/CascadiaMono.ttf",
            "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Consolas.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        ]
    )
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def _middle_truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    keep_left = max(8, (max_chars - 3) // 2)
    keep_right = max(8, max_chars - keep_left - 3)
    return f"{text[:keep_left]}...{text[-keep_right:]}"


def _trim_code_line(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return text[:max_chars]
    return f"{text[: max_chars - 3]}..."


def _render_code_png(
    out_path: Path,
    header_title: str,
    header_subtitle: str,
    lines: list[str],
    *,
    font_size: int = 24,
    max_chars: int = 76,
) -> Path:
    panel_bg = (30, 30, 30)
    chrome_bg = (37, 37, 38)
    gutter_bg = (37, 37, 38)
    border = (58, 58, 58)
    text_color = (212, 212, 212)
    path_color = (156, 220, 254)
    gutter_color = (133, 133, 133)
    highlight_fill = (47, 93, 143, 228)
    highlight_accent = (55, 148, 255, 255)
    shadow_color = (0, 0, 0, 110)
    token_colors = {
        Comment: (106, 153, 85),
        Keyword: (86, 156, 214),
        Keyword.Constant: (86, 156, 214),
        Keyword.Namespace: (86, 156, 214),
        Name.Function: (220, 220, 170),
        Name.Class: (78, 201, 176),
        Name.Builtin: (78, 201, 176),
        Name.Builtin.Pseudo: (78, 201, 176),
        Name.Decorator: (197, 134, 192),
        Name.Exception: (78, 201, 176),
        String: (206, 145, 120),
        Number: (181, 206, 168),
        Operator.Word: (86, 156, 214),
        Token.Error: (244, 71, 71),
        Text: text_color,
    }

    font = _load_mono_font(font_size)
    font_bold = _load_mono_font(font_size, bold=True)
    chrome_font = _load_mono_font(max(14, int(font_size * 0.78)), bold=True)
    chrome_meta_font = _load_mono_font(max(12, int(font_size * 0.62)))
    probe = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    probe_draw = ImageDraw.Draw(probe)
    glyph_box = probe_draw.textbbox((0, 0), "Mg", font=font)
    char_w = max(10, glyph_box[2] - glyph_box[0])
    line_h = max(24, int(font_size * 1.48))

    gutter_w = 118
    panel_pad_x = 34
    panel_pad_bottom = 30
    title_bar_h = 64
    code_top_pad = 24
    max_line_px = 0
    visible_lines = [_trim_code_line(ln, max_chars) for ln in lines]
    for raw in visible_lines:
        highlight = raw.lstrip().startswith(">>>")
        ln = raw.replace(">>>", "", 1).lstrip() if highlight else raw
        stripped = ln.lstrip()
        code = ln
        if stripped and stripped[0].isdigit():
            parts = stripped.split(" ", 1)
            if len(parts) == 2 and parts[0].isdigit():
                leading = len(ln) - len(stripped)
                code = " " * leading + parts[1]
        width_px = int(probe_draw.textlength(code, font=font))
        max_line_px = max(max_line_px, width_px)

    width = min(max(1720, gutter_w + panel_pad_x * 2 + max_line_px + 120), 2100)
    height = min(max(980, title_bar_h + code_top_pad + len(visible_lines) * line_h + panel_pad_bottom + 46), 1480)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    panel_left, panel_top = 22, 18
    panel_right, panel_bottom = width - 22, height - 18

    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow, "RGBA")
    shadow_draw.rounded_rectangle(
        [panel_left + 10, panel_top + 14, panel_right + 8, panel_bottom + 14],
        radius=28,
        fill=shadow_color,
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=14))
    img.alpha_composite(shadow)

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle(
        [panel_left, panel_top, panel_right, panel_bottom],
        radius=24,
        fill=panel_bg + (255,),
        outline=border + (255,),
        width=2,
    )
    draw.rounded_rectangle(
        [panel_left, panel_top, panel_right, panel_top + title_bar_h],
        radius=24,
        fill=chrome_bg + (255,),
    )
    draw.rectangle(
        [panel_left, panel_top + 26, panel_right, panel_top + title_bar_h],
        fill=chrome_bg + (255,),
    )

    for idx, color in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        cx = panel_left + 28 + idx * 26
        cy = panel_top + title_bar_h // 2
        draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=color + (240,))

    display_title = _middle_truncate(header_title, 34)
    display_subtitle = _middle_truncate(header_subtitle, 56)
    draw.text((panel_left + 120, panel_top + 17), display_title, font=chrome_font, fill=(230, 230, 230, 255))
    subtitle_w = int(draw.textlength(display_subtitle, font=chrome_meta_font))
    draw.text((panel_right - 26 - subtitle_w, panel_top + 20), display_subtitle, font=chrome_meta_font, fill=path_color + (225,))

    code_top = panel_top + title_bar_h + code_top_pad
    gutter_left = panel_left + 14
    gutter_right = gutter_left + gutter_w
    draw.rounded_rectangle(
        [gutter_left, code_top - 8, gutter_right, panel_bottom - 18],
        radius=16,
        fill=gutter_bg + (255,),
    )
    code_x = gutter_right + 26

    def _color_for_token(tok):
        for ttype, color in token_colors.items():
            if tok in ttype:
                return color
        return text_color

    def _boost(color: tuple[int, int, int], *, amount: int = 26) -> tuple[int, int, int]:
        return tuple(min(255, channel + amount) for channel in color)

    lexer = PythonLexer(stripnl=False)
    for row_idx, raw_line in enumerate(visible_lines):
        y = code_top + row_idx * line_h
        highlight = raw_line.lstrip().startswith(">>>")
        ln = raw_line.replace(">>>", "", 1).lstrip() if highlight else raw_line
        line_no = ""
        code = ln
        stripped = ln.lstrip()
        leading = len(ln) - len(stripped)
        if stripped and stripped[0].isdigit():
            parts = stripped.split(" ", 1)
            if len(parts) == 2 and parts[0].isdigit():
                line_no = parts[0]
                code = " " * leading + parts[1]
        code = _trim_code_line(code, max_chars)

        row_top = y - 4
        row_bottom = y + line_h - 2
        if highlight:
            draw.rounded_rectangle(
                [panel_left + 14, row_top, panel_right - 14, row_bottom],
                radius=10,
                fill=highlight_fill,
                outline=(118, 179, 245, 255),
                width=2,
            )
            draw.rounded_rectangle(
                [panel_left + 14, row_top, panel_left + 20, row_bottom],
                radius=4,
                fill=highlight_accent,
            )

        if line_no:
            line_no_w = int(draw.textlength(f"{line_no:>4}", font=font))
            draw.text(
                (gutter_right - 18 - line_no_w, y),
                f"{line_no:>4}",
                font=font_bold if highlight else font,
                fill=(_boost(gutter_color, amount=40) if highlight else gutter_color) + (255,),
            )

        x = code_x
        for tok, value in lex(code, lexer):
            clean = value.replace("\n", "")
            if not clean:
                continue
            color = _color_for_token(tok)
            if highlight:
                color = _boost(color, amount=30)
            draw.text((x, y), clean, font=font_bold if highlight else font, fill=color + (255,))
            x += int(draw.textlength(clean, font=font))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return out_path


def _extract_code_segments(path: Path, segments: list[tuple[int, int]], *, highlight_lines: set[int] | None = None) -> list[str]:
    source_lines = path.read_text(encoding="utf-8").splitlines()
    highlight_lines = highlight_lines or set()
    out: list[str] = []
    for seg_i, (start, end) in enumerate(segments):
        for lineno in range(start, end + 1):
            prefix = ">>> " if lineno in highlight_lines else ""
            out.append(f"{prefix}{lineno:4d} {source_lines[lineno - 1]}")
        if seg_i != len(segments) - 1:
            out.append("...")
    return out


def _code_excerpt_image(path: Path, title: str, lines: list[str], out_path: Path) -> Path:
    try:
        rel_path = path.relative_to(ROOT)
    except ValueError:
        rel_path = path
    return _render_code_png(
        out_path,
        path.name,
        str(rel_path),
        lines,
    )


def _ensure_transcoded_gif(
    src_path: Path,
    gif_path: Path,
    *,
    width: int = 640,
    fps: int = 8,
    max_colors: int = 96,
) -> Path:
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    if gif_path.exists() and gif_path.stat().st_mtime >= src_path.stat().st_mtime:
        return gif_path
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(src_path),
            "-vf",
            (
                f"fps={fps},scale={width}:-1:flags=lanczos,"
                f"split[s0][s1];[s0]palettegen=max_colors={max_colors}:stats_mode=diff[p];"
                "[s1][p]paletteuse=dither=bayer:bayer_scale=4"
            ),
            "-loop",
            "0",
            str(gif_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return gif_path


def _ensure_gif(mp4_path: Path, gif_path: Path, *, width: int = 640, fps: int = 8, max_colors: int = 96) -> Path:
    return _ensure_transcoded_gif(mp4_path, gif_path, width=width, fps=fps, max_colors=max_colors)


def _ensure_current_bunny_panel_mp4s() -> None:
    if not CURRENT_BUNNY_BOARD_SUMMARY.exists():
        raise FileNotFoundError(f"missing bunny board summary: {CURRENT_BUNNY_BOARD_SUMMARY}")
    missing = [path for path in CURRENT_BUNNY_PANEL_MP4.values() if not path.exists()]
    if not missing:
        return
    helper = ROOT / "scripts" / "export_bunny_collision_board_panels.py"
    subprocess.run(
        [
            "python",
            str(helper),
            "--board-summary",
            str(CURRENT_BUNNY_BOARD_SUMMARY),
        ],
        check=True,
    )


def _ensure_resized_gif(
    src_path: Path,
    out_path: Path,
    *,
    width: int = 720,
    fps: int = 8,
    max_colors: int = 96,
) -> Path:
    return _ensure_transcoded_gif(src_path, out_path, width=width, fps=fps, max_colors=max_colors)


def _mb(byte_count: int) -> float:
    return float(byte_count) / 1_000_000.0


def _validate_pptx_size(pptx_path: Path, *, max_pptx_mb: float) -> None:
    if max_pptx_mb <= 0.0:
        return
    actual_mb = _mb(pptx_path.stat().st_size)
    if actual_mb > max_pptx_mb:
        raise RuntimeError(
            f"PPTX size gate failed: {pptx_path} is {actual_mb:.1f} MB, above the {max_pptx_mb:.1f} MB budget."
        )


def _render_perf_attribution_png(out_path: Path) -> Path:
    labels_newton = ["bridge", "internal", "integration", "collision", "unexplained"]
    values_newton = [A3_BRIDGE_MS, A3_INTERNAL_MS, A3_INTEGRATION_MS, A3_COLLISION_MS, A3_UNEXPLAINED_MS]
    labels_phystwin = ["sim launch", "controller", "state reset"]
    values_phystwin = [B1_SIM_LAUNCH_MS, B1_CONTROLLER_FRAME_MS, B1_STATE_RESET_MS]
    colors_newton = ["#3B6EA8", "#E07A5F", "#81B29A", "#F2CC8F", "#8D99AE"]
    colors_phystwin = ["#264653", "#2A9D8F", "#E9C46A"]

    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.6), dpi=160, gridspec_kw={"width_ratios": [1.35, 1.0]})
    fig.patch.set_facecolor("#F7F5EE")
    for ax in axes:
        ax.set_facecolor("#F7F5EE")

    left = axes[0]
    start = 0.0
    for label, value, color in zip(labels_newton, values_newton, colors_newton):
        left.barh(["Newton A3 ms/substep"], [value], left=start, color=color, edgecolor="white", height=0.46)
        left.text(start + value / 2.0, 0, f"{label}\n{value:.3f}", ha="center", va="center", fontsize=10, color="#111111")
        start += value
    left.set_title("Newton A3 Breakdown", fontsize=16, fontweight="bold", loc="left")
    left.set_xlabel("ms / substep", fontsize=12)
    left.spines[["top", "right", "left"]].set_visible(False)
    left.grid(axis="x", alpha=0.18)
    left.tick_params(axis="y", length=0, labelsize=12)
    left.tick_params(axis="x", labelsize=10)

    right = axes[1]
    y_pos = list(range(len(labels_phystwin)))
    bars = right.barh(y_pos, values_phystwin, color=colors_phystwin, edgecolor="white", height=0.48)
    right.set_yticks(y_pos, labels_phystwin, fontsize=12)
    right.invert_yaxis()
    right.set_title("PhysTwin B1 Frame Attribution", fontsize=16, fontweight="bold", loc="left")
    right.set_xlabel("ms / frame", fontsize=12)
    right.spines[["top", "right"]].set_visible(False)
    right.grid(axis="x", alpha=0.18)
    right.tick_params(axis="x", labelsize=10)
    for bar, value in zip(bars, values_phystwin):
        right.text(value + max(values_phystwin) * 0.02, bar.get_y() + bar.get_height() / 2.0, f"{value:.3f}", va="center", fontsize=10)

    fig.suptitle("Bridge Tax Exists, But Collision Is Still Tiny On The Clean Rope Replay", fontsize=18, fontweight="bold", x=0.5, y=0.98)
    fig.text(
        0.075,
        0.03,
        "A0→A1 proves bridge tax. The remaining A3 split still leaves collision near zero on the clean replay baseline.",
        fontsize=11,
        color="#1F4E79",
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0.02, 0.06, 0.98, 0.93])
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def _render_perf_nsight_png(out_path: Path) -> Path:
    labels = ["dominant API", "next API", "other"]
    newton_vals = [77.2, 21.5, 1.3]
    phystwin_vals = [92.6, 2.9, 4.5]
    colors = ["#355070", "#E56B6F", "#BFC7D5"]

    fig, axes = plt.subplots(2, 1, figsize=(12.8, 5.6), dpi=160, sharex=True)
    fig.patch.set_facecolor("#F7F5EE")
    for ax in axes:
        ax.set_facecolor("#F7F5EE")
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.grid(axis="x", alpha=0.18)
        ax.tick_params(axis="y", length=0, labelsize=12)
        ax.tick_params(axis="x", labelsize=10)
        ax.set_xlim(0.0, 100.0)

    for ax, vals, title, dominant, secondary in [
        (axes[0], newton_vals, "Newton A1 CUDA API", "cuLaunchKernel 77.2%", "cudaMemsetAsync 21.5%"),
        (axes[1], phystwin_vals, "PhysTwin B0 CUDA API", "cudaGraphLaunch 92.6%", "cuCtxSynchronize 2.9%"),
    ]:
        start = 0.0
        for label, value, color in zip(labels, vals, colors):
            ax.barh([title], [value], left=start, color=color, edgecolor="white", height=0.42)
            if value >= 8.0:
                ax.text(start + value / 2.0, 0, f"{value:.1f}%", ha="center", va="center", fontsize=10, color="#111111")
            start += value
        ax.text(1.0, 0.34, dominant, fontsize=11, color="#1F4E79")
        ax.text(1.0, -0.34, secondary, fontsize=10, color="#444444")

    axes[1].set_xlabel("share of CUDA API time (%)", fontsize=12)
    fig.suptitle("Nsight Supports A Launch-Structure Story, Not A Collision Story", fontsize=18, fontweight="bold", x=0.5, y=0.98)
    fig.text(
        0.075,
        0.03,
        "Newton still looks like many decoupled launches; PhysTwin replay is graph-launch-dominated on the same rope case.",
        fontsize=11,
        color="#1F4E79",
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0.02, 0.08, 0.98, 0.92])
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def _add_pic(slide, path: Path, left: int, top: int, width: int, height: int):
    with Image.open(path) as img:
        dx, dy, w, h = _fit_box(img.size[0], img.size[1], width, height)
    return slide.shapes.add_picture(str(path), left + dx, top + dy, width=w, height=h)


def _title_slide(prs: Presentation, title: str, sub: list[str]) -> None:
    slide = prs.slides.add_slide(_layout(prs))
    _clear_placeholders(slide)
    title_box = slide.shapes.add_textbox(
        REF_TITLE_LEFT, REF_TITLE_SLIDE_TOP, REF_TITLE_W, REF_TITLE_SLIDE_H
    )
    _set_title_textbox(title_box, title, size_pt=28)
    body_box = slide.shapes.add_textbox(
        REF_BODY_LEFT, REF_SUBTITLE_TOP, REF_BODY_W, REF_SUBTITLE_H
    )
    _set_lines(body_box, sub)


def _body(prs: Presentation, title: str, bullets: list[str]) -> None:
    slide = prs.slides.add_slide(_layout(prs))
    _clear_placeholders(slide)
    title_box = slide.shapes.add_textbox(
        REF_TITLE_LEFT, REF_TITLE_TOP, REF_TITLE_W, REF_TITLE_H
    )
    _set_title_textbox(title_box, title, size_pt=28)
    body_box = slide.shapes.add_textbox(
        REF_BODY_LEFT, REF_BODY_TOP, REF_BODY_W, REF_BODY_H
    )
    _set_lines(body_box, bullets)


def _table(prs: Presentation, title: str, columns: list[str], rows: list[list[str]], note: str | None = None) -> None:
    slide = prs.slides.add_slide(_layout(prs))
    _clear_placeholders(slide)
    title_box = slide.shapes.add_textbox(
        REF_TITLE_LEFT, REF_TITLE_TOP, REF_TITLE_W, REF_TITLE_H
    )
    _set_title_textbox(title_box, title, size_pt=28)
    if note:
        _add_label(
            slide,
            TABLE_LEFT,
            TABLE_NOTE_TOP,
            TABLE_W,
            TABLE_NOTE_H,
            note,
            font_size=11,
            bold=False,
        )
    table_shape = slide.shapes.add_table(
        len(rows) + 1,
        len(columns),
        TABLE_LEFT,
        TABLE_TOP,
        TABLE_W,
        TABLE_H,
    )
    table = table_shape.table
    if len(columns) == 4:
        widths = [
            int(TABLE_W * 0.14),
            int(TABLE_W * 0.24),
            int(TABLE_W * 0.18),
            int(TABLE_W * 0.44),
        ]
    else:
        widths = [
            int(TABLE_W * 0.12),
            int(TABLE_W * 0.32),
            int(TABLE_W * 0.18),
            int(TABLE_W * 0.14),
            int(TABLE_W * 0.24),
        ]
    for idx, width in enumerate(widths[: len(columns)]):
        table.columns[idx].width = width

    def set_cell_text(
        cell,
        text: str,
        *,
        bold: bool,
        align_center: bool = False,
        fill_color: RGBColor | None = None,
    ) -> None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill_color or RGBColor(0xFF, 0xFF, 0xFF)
        cell.text_frame.clear()
        cell.text_frame.word_wrap = True
        p = cell.text_frame.paragraphs[0]
        _set_marked_paragraph(
            p,
            text,
            font_name="Arial",
            font_size=15,
            color=RGBColor(0x22, 0x22, 0x22),
            accent_color=RGBColor(0x1F, 0x4E, 0x79),
            bold_default=bold,
        )
        if align_center:
            p.alignment = 1

    for c, heading in enumerate(columns):
        header = table.cell(0, c)
        header.fill.solid()
        header.fill.fore_color.rgb = RGBColor(0xD9, 0xE2, 0xF3)
        set_cell_text(header, heading, bold=True, align_center=True)

    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            fill = None
            if len(columns) == 4 and c == 3:
                if "1.00x" in str(value):
                    fill = RGBColor(0xE2, 0xF0, 0xD9)
                else:
                    fill = RGBColor(0xF4, 0xCC, 0xCC)
            elif len(columns) == 4 and c == 2:
                try:
                    fill = RGBColor(0xE2, 0xF0, 0xD9) if float(value) >= 1.0 else RGBColor(0xFF, 0xF2, 0xCC)
                except Exception:
                    fill = None
            set_cell_text(
                table.cell(r, c),
                str(value),
                bold=(c == 0),
                align_center=(c != 0),
                fill_color=fill,
            )


def _gif_grid_2x2(
    prs: Presentation,
    title: str,
    items: list[tuple[str, Path]],
    *,
    common_settings: str | None = None,
) -> None:
    slide = prs.slides.add_slide(_layout(prs))
    _clear_placeholders(slide)
    title_box = slide.shapes.add_textbox(
        REF_TITLE_LEFT, REF_TITLE_TOP, REF_TITLE_W, REF_TITLE_H
    )
    _set_title_textbox(title_box, title, size_pt=28)
    if common_settings:
        _add_label(
            slide,
            REF_GRID_COMMON_LEFT,
            REF_GRID_COMMON_TOP,
            REF_GRID_COMMON_W,
            REF_GRID_COMMON_H,
            common_settings,
            font_size=11,
            bold=False,
        )
    label_w = 3000000
    label_h = 250000
    pic_w = 2350000
    pic_h = 1320000
    label_positions = [
        (520000, 1700000),
        (4720000, 1700000),
        (520000, 3380000),
        (4720000, 3380000),
    ]
    pic_positions = [
        (1280000, 1980000),
        (5780000, 1980000),
        (1280000, 3660000),
        (5780000, 3660000),
    ]
    for idx, (label, path) in enumerate(items[:4]):
        lx, ly = label_positions[idx]
        px, py = pic_positions[idx]
        _add_label(slide, lx, ly, label_w, label_h, label, font_size=11, bold=False)
        _add_pic(slide, path, px, py, pic_w, pic_h)


def _gif_twocol(
    prs: Presentation,
    title: str,
    left_label: str,
    left_path: Path,
    right_label: str,
    right_path: Path,
    *,
    common_settings: str | None = None,
) -> None:
    slide = prs.slides.add_slide(_layout(prs))
    _clear_placeholders(slide)
    title_box = slide.shapes.add_textbox(
        REF_TITLE_LEFT, REF_TITLE_TOP, REF_TITLE_W, REF_TITLE_H
    )
    _set_title_textbox(title_box, title, size_pt=28)
    if common_settings:
        _add_label(
            slide,
            REF_GRID_COMMON_LEFT,
            REF_GRID_COMMON_TOP,
            REF_GRID_COMMON_W,
            REF_GRID_COMMON_H,
            common_settings,
            font_size=11,
            bold=False,
        )
    label_y = 1730000
    pic_y = 2010000
    label_w = 3300000
    label_h = 250000
    pic_w = 3000000
    pic_h = 1760000
    left_label_x = 520000
    right_label_x = 4670000
    left_pic_x = 920000
    right_pic_x = 5090000
    _add_label(
        slide,
        left_label_x,
        label_y,
        label_w,
        label_h,
        left_label,
        font_size=11,
        bold=False,
    )
    _add_pic(
        slide,
        left_path,
        left_pic_x,
        pic_y,
        pic_w,
        pic_h,
    )
    _add_label(
        slide,
        right_label_x,
        label_y,
        label_w,
        label_h,
        right_label,
        font_size=11,
        bold=False,
    )
    _add_pic(
        slide,
        right_path,
        right_pic_x,
        pic_y,
        pic_w,
        pic_h,
    )


def _perf_gif_bullets(
    prs: Presentation,
    title: str,
    gif_label: str,
    gif_path: Path,
    bullets: list[str],
    *,
    note: str | None = None,
) -> None:
    slide = prs.slides.add_slide(_layout(prs))
    _clear_placeholders(slide)
    title_box = slide.shapes.add_textbox(REF_TITLE_LEFT, REF_TITLE_TOP, REF_TITLE_W, REF_TITLE_H)
    _set_title_textbox(title_box, title, size_pt=28)
    if note:
        _add_label(
            slide,
            REF_GRID_COMMON_LEFT,
            REF_GRID_COMMON_TOP,
            REF_GRID_COMMON_W,
            REF_GRID_COMMON_H,
            note,
            font_size=12,
            bold=False,
        )
    _add_label(slide, 540000, 1620000, 3920000, 260000, gif_label, font_size=11, bold=False)
    _add_pic(slide, gif_path, 540000, 1930000, 3920000, 2360000)
    body_box = slide.shapes.add_textbox(4540000, 1680000, 3800000, 2580000)
    _set_lines(body_box, bullets)


def _code_twocol_large(
    prs: Presentation,
    title: str,
    left_label: str,
    left_path: Path,
    right_label: str,
    right_path: Path,
    *,
    note: str | None = None,
) -> None:
    slide = prs.slides.add_slide(_layout(prs))
    _clear_placeholders(slide)
    title_box = slide.shapes.add_textbox(REF_TITLE_LEFT, REF_TITLE_TOP, REF_TITLE_W, REF_TITLE_H)
    _set_title_textbox(title_box, title, size_pt=24)
    if note:
        _add_label(
            slide,
            REF_GRID_COMMON_LEFT,
            REF_GRID_COMMON_TOP,
            REF_GRID_COMMON_W,
            REF_GRID_COMMON_H,
            note,
            font_size=10,
            bold=False,
        )
    left_x = 420000
    right_x = 4550000
    label_y = 1560000
    pic_y = 1815000
    pic_w = 3900000
    pic_h = 2950000
    _add_label(slide, left_x, label_y, pic_w, 200000, left_label, font_size=10, bold=False)
    _add_pic(slide, left_path, left_x, pic_y, pic_w, pic_h)
    _add_label(slide, right_x, label_y, pic_w, 200000, right_label, font_size=10, bold=False)
    _add_pic(slide, right_path, right_x, pic_y, pic_w, pic_h)


def _image_slide(prs: Presentation, title: str, path: Path, *, note: str | None = None) -> None:
    slide = prs.slides.add_slide(_layout(prs))
    _clear_placeholders(slide)
    title_box = slide.shapes.add_textbox(
        REF_TITLE_LEFT, REF_TITLE_TOP, REF_TITLE_W, REF_TITLE_H
    )
    _set_title_textbox(title_box, title, size_pt=28)
    if note:
        _add_label(
            slide,
            REF_GRID_COMMON_LEFT,
            REF_GRID_COMMON_TOP,
            REF_GRID_COMMON_W,
            REF_GRID_COMMON_H,
            note,
            font_size=12,
            bold=False,
        )
    pic_left = 420000
    pic_top = 1650000
    pic_w = 8550000
    pic_h = 4300000
    _add_pic(slide, path, pic_left, pic_top, pic_w, pic_h)


def _parse_slide_range(spec: str | None) -> list[dict]:
    if not spec:
        return list(RECALL_SLIDES)
    match = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", spec)
    if not match:
        raise ValueError(f"Unsupported --slide-range format: {spec!r}. Expected START-END, e.g. 8-12.")
    start = int(match.group(1))
    end = int(match.group(2))
    if start < 1 or end < start or end > len(RECALL_SLIDES):
        raise ValueError(
            f"Slide range {spec!r} is out of bounds for a {len(RECALL_SLIDES)}-slide deck."
        )
    return list(RECALL_SLIDES[start - 1 : end])


def build_recall_only_deck(prs: Presentation, slides: list[dict] | None = None) -> None:
    _delete_all_slides(prs)
    active_slides = slides or list(RECALL_SLIDES)
    for slide in active_slides:
        kind = slide["kind"]
        if kind == "title":
            _title_slide(prs, slide["title"], slide["subtitle"])
        elif kind == "grid":
            _gif_grid_2x2(
                prs,
                slide["title"],
                slide["items"],
                common_settings=slide.get("common_settings"),
            )
        elif kind == "twocol":
            _gif_twocol(
                prs,
                slide["title"],
                slide["left_label"],
                slide["left_path"],
                slide["right_label"],
                slide["right_path"],
                common_settings=slide.get("common_settings"),
            )
        elif kind == "code_twocol":
            _code_twocol_large(
                prs,
                slide["title"],
                slide["left_label"],
                slide["left_path"],
                slide["right_label"],
                slide["right_path"],
                note=slide.get("common_settings") or slide.get("note"),
            )
        elif kind == "code_twocol_large":
            _code_twocol_large(
                prs,
                slide["title"],
                slide["left_label"],
                slide["left_path"],
                slide["right_label"],
                slide["right_path"],
                note=slide.get("note"),
            )
        elif kind == "perf_gif_bullets":
            _perf_gif_bullets(
                prs,
                slide["title"],
                slide["gif_label"],
                slide["gif_path"],
                slide["bullets"],
                note=slide.get("note"),
            )
        elif kind == "body":
            _body(prs, slide["title"], slide["bullets"])
        elif kind == "table":
            _table(
                prs,
                slide["title"],
                slide["columns"],
                slide["rows"],
                note=slide.get("note"),
            )
        elif kind == "image":
            _image_slide(
                prs,
                slide["title"],
                slide["path"],
                note=slide.get("note"),
            )
        else:
            raise ValueError(f"Unknown recall slide kind: {kind}")


def _markdown_to_pdf(md_text: str, html_path: Path, pdf_path: Path) -> None:
    html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: 'DejaVu Sans', sans-serif; line-height: 1.55; margin: 36px 48px; color: #222; }}
    h1, h2, h3 {{ color: #1f3d5a; }}
    code {{ background: #f2f4f7; padding: 1px 4px; border-radius: 4px; }}
    pre {{ background: #f2f4f7; padding: 10px; overflow-x: auto; }}
    blockquote {{ color: #555; border-left: 4px solid #ccd5e0; padding-left: 12px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccd5e0; padding: 6px 8px; }}
    a {{ color: #1f5d99; text-decoration: none; }}
  </style>
</head>
<body>{html_body}</body>
</html>"""
    html_path.write_text(html, encoding="utf-8")
    try:
        from weasyprint import HTML

        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        return
    except Exception:
        pass

    subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(pdf_path.parent),
            str(html_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    _prepare_generated_assets()
    active_slides = _parse_slide_range(args.slide_range)

    if not TEMPLATE_PPTX.exists():
        raise FileNotFoundError(f"Missing local template: {TEMPLATE_PPTX}")

    prs = Presentation(str(TEMPLATE_PPTX))
    build_recall_only_deck(prs, slides=active_slides)
    out_pptx = args.out_pptx.resolve() if args.out_pptx else (out_dir / OUT_PPTX.name)
    out_pptx.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_pptx))

    transcript_text = _build_transcript_md(active_slides)
    transcript_md = out_dir / "transcript.md"
    transcript_md.write_text(transcript_text, encoding="utf-8")
    transcript_html = out_dir / "transcript.html"
    transcript_pdf = out_dir / "transcript.pdf"
    _markdown_to_pdf(transcript_text, transcript_html, transcript_pdf)
    _validate_pptx_size(out_pptx, max_pptx_mb=float(args.max_pptx_mb))

    print(f"PPTX: {out_pptx}")
    print(f"PPTX size: {_mb(out_pptx.stat().st_size):.1f} MB (budget {float(args.max_pptx_mb):.1f} MB)")
    print(f"Transcript MD: {transcript_md}")
    print(f"Transcript PDF: {transcript_pdf}")
    print(f"Slides: {len(prs.slides)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
