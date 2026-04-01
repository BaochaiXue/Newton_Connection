#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import textwrap
from pathlib import Path

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

MEETING_DIR = Path(__file__).resolve().parent
ROOT = MEETING_DIR.parents[1]
TEMPLATE_PPTX = MEETING_DIR / "templates" / "My Adjust.pptx"
OUT_PPTX = MEETING_DIR / "bridge_meeting_20260401.pptx"
DECK_GIF_DIR = MEETING_DIR / "gif"
DEFAULT_MAX_PPTX_MB = 100.0
DEFAULT_MAX_GIF_MB = 40.0

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

RENDER_BUNNY_BOARD_PATH = ROOT / "scripts" / "render_bunny_penetration_collision_board.py"
NEWTON_CORE_SPRING_PATH = ROOT / "Newton" / "newton" / "newton" / "_src" / "solvers" / "semi_implicit" / "kernels_particle.py"
NEWTON_CORE_SEMIIMPLICIT_PATH = ROOT / "Newton" / "newton" / "newton" / "_src" / "solvers" / "semi_implicit" / "solver_semi_implicit.py"
PHYSTWIN_SPRING_WARP_CODE_PATH = ROOT / "PhysTwin" / "qqtt" / "model" / "diff_simulator" / "spring_mass_warp.py"
IMAGE_DIR = MEETING_DIR / "images"
CODE_PERF_PHYSICS_NEWTON_PNG = IMAGE_DIR / "code_perf_physics_newton.png"
CODE_PERF_PHYSICS_PHYSTWIN_PNG = IMAGE_DIR / "code_perf_physics_phystwin.png"
CODE_PERF_EXECUTION_NEWTON_PNG = IMAGE_DIR / "code_perf_execution_newton.png"
CODE_PERF_EXECUTION_PHYSTWIN_PNG = IMAGE_DIR / "code_perf_execution_phystwin.png"
PERF_NEWTON_SYSTEM_PNG = IMAGE_DIR / "perf_newton_system_summary.png"
PERF_PHYSTWIN_SYSTEM_PNG = IMAGE_DIR / "perf_phystwin_system_summary.png"
CODE_SELFCOLLISION_OBJECT_PNG = IMAGE_DIR / "code_selfcollision_object.png"
CODE_SELFCOLLISION_GROUND_PNG = IMAGE_DIR / "code_selfcollision_ground.png"
CODE_SELFCOLLISION_TABLE_PHYSTWIN_PNG = IMAGE_DIR / "code_selfcollision_table_phystwin.png"
CODE_SELFCOLLISION_TABLE_BRIDGE_PNG = IMAGE_DIR / "code_selfcollision_table_bridge.png"
CODE_SELFCOLLISION_MATCHED_PHYSTWIN_PNG = IMAGE_DIR / "code_selfcollision_matched_phystwin.png"
CODE_SELFCOLLISION_MATCHED_BRIDGE_PNG = IMAGE_DIR / "code_selfcollision_matched_bridge.png"
CODE_SELFCOLLISION_CONTROLLER_PHYSTWIN_PNG = IMAGE_DIR / "code_selfcollision_controller_phystwin.png"
CODE_SELFCOLLISION_CONTROLLER_BRIDGE_PNG = IMAGE_DIR / "code_selfcollision_controller_bridge.png"
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
CURRENT_BUNNY_BOARD_PUBLISH_GIF = CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "collision_force_board_2x2.gif"
CURRENT_BUNNY_BOARD_GIF = DECK_GIF_DIR / "bunny_collision_board_2x2.gif"
CURRENT_BUNNY_BOARD_FIRST_FRAME = (
    CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "collision_force_board_2x2_first_frame.png"
)
CURRENT_BUNNY_SLOW_BOARD_DIR = CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board_slow4x"
CURRENT_BUNNY_SLOW_BOARD_STEM = "collision_force_board_2x2_slow4x"
CURRENT_BUNNY_SLOW_BOARD_MP4 = CURRENT_BUNNY_SLOW_BOARD_DIR / f"{CURRENT_BUNNY_SLOW_BOARD_STEM}.mp4"
CURRENT_BUNNY_SLOW_BOARD_SUMMARY = CURRENT_BUNNY_SLOW_BOARD_DIR / "summary.json"
CURRENT_BUNNY_SLOW_BOARD_PUBLISH_GIF = CURRENT_BUNNY_SLOW_BOARD_DIR / f"{CURRENT_BUNNY_SLOW_BOARD_STEM}.gif"
CURRENT_BUNNY_SLOW_BOARD_GIF = DECK_GIF_DIR / "bunny_collision_board_2x2_slow4x.gif"
CURRENT_BUNNY_PANEL_MP4 = {
    "box_penalty": CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "panels" / "box_penalty.mp4",
    "box_total": CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "panels" / "box_total.mp4",
    "bunny_penalty": CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "panels" / "bunny_penalty.mp4",
    "bunny_total": CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "panels" / "bunny_total.mp4",
}
CURRENT_BUNNY_PANEL_PUBLISH_GIF = {
    name: CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "panels" / f"{name}.gif"
    for name in CURRENT_BUNNY_PANEL_MP4
}
CURRENT_BUNNY_PANEL_GIF = {
    name: DECK_GIF_DIR / f"{name}.gif" for name in CURRENT_BUNNY_PANEL_MP4
}
CURRENT_BUNNY_BOARD_PUBLISH_GIF_PROFILES = [
    (1600, 15, 224),
    (1440, 12, 224),
    (1280, 12, 192),
    (1120, 10, 192),
    (960, 10, 160),
    (960, 8, 128),
]
CURRENT_BUNNY_SLOW_BOARD_PUBLISH_GIF_PROFILES = list(CURRENT_BUNNY_BOARD_PUBLISH_GIF_PROFILES)
CURRENT_BUNNY_PANEL_PUBLISH_GIF_PROFILES = [
    (960, 15, 224),
    (960, 12, 192),
    (896, 12, 192),
    (832, 10, 160),
    (768, 10, 160),
    (640, 8, 128),
]
CURRENT_BUNNY_BOARD_GIF_PROFILES = [
    (1280, 12, 192),
    (1120, 10, 160),
    (960, 10, 160),
    (960, 8, 128),
]
CURRENT_BUNNY_SLOW_BOARD_GIF_PROFILES = list(CURRENT_BUNNY_BOARD_GIF_PROFILES)
CURRENT_BUNNY_PANEL_GIF_PROFILES = [
    (832, 10, 160),
    (768, 10, 160),
    (640, 8, 128),
]
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
SELF_PARITY_SUPPORT_MP4 = (
    ROOT
    / "Newton"
    / "phystwin_bridge"
    / "results"
    / "tmp_off_vs_phystwin_302_compare_20260401"
    / "parity_support_demo"
    / "parity_support_demo.mp4"
)
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
A0_VS_B0 = float(A0_ROW.get("ms_per_substep_mean", 0.0)) / max(float(B0_ROW.get("ms_per_substep_mean", 1.0e-12)), 1.0e-12)
A1_VS_B0 = float(A1_ROW.get("ms_per_substep_mean", 0.0)) / max(float(B0_ROW.get("ms_per_substep_mean", 1.0e-12)), 1.0e-12)
A0_TO_A1 = float(A0_ROW.get("ms_per_substep_mean", 0.0)) / max(float(A1_ROW.get("ms_per_substep_mean", 1.0e-12)), 1.0e-12)
A3_POST_BRIDGE_MS = A3_INTERNAL_MS + A3_INTEGRATION_MS + A3_UNEXPLAINED_MS

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
        "kind": "table_gif",
        "title": "Method: Fair Rope Benchmark Before Optimization",
        "note": "Method only. The main comparison is simulator-only, with rendering removed on both sides.",
        "gif_label": "Rope replay case",
        "gif_path": PERF_ROPE_CASE_GIF,
        "columns": ["Control", "Setting", "Why it matters"],
        "rows": [
            ["Case", "`rope_double_hand`", "same rope object, same spring graph"],
            ["Replay", "same controller trajectory", "same input history, not two tasks"],
            ["Physics", "`dt=5e-05`, `667` substeps", "same time resolution"],
            ["Hardware", "same RTX 4090", "same GPU path"],
            ["Render", "disabled on both sides", "no viewer/UI contamination"],
        ],
        "transcript": [
            "这里开始进入第二段 rope-case performance analysis，而且这次明确只讲 rope case，不再讲 robot case。",
            "第一张 slide 的作用不是给结论，而是先把 benchmark method 锁死：same case、same replay、same physics settings、same GPU、no render。",
            "Newton 侧的方法学是用 realtime viewer 的同一个 rope replay 入口，但切到 `--viewer null --profile-only`，所以这一步只说明 benchmark setup，不把 wrapper 当成 core proof。",
            "PhysTwin 侧的方法学是 same trajectory 的 headless replay。因为教授先要 apples-to-apples throughput，所以这里故意不把 GUI / Gaussian / viewer loop 混进主比较。",
            f"同 case identity 也不是口头假设：当前 committed benchmark 里，PhysTwin controller trajectory 和 IR 的 max abs diff 是 {B0_PAYLOAD.get('trajectory_parity', {}).get('controller_traj_max_abs_diff', 0.0):.1e}。",
        ],
    },
    {
        "kind": "code_twocol_large",
        "title": "H2: Comparable Spring-Damper Rope Update Intent",
        "note": "Core source only. Claim strength: comparable update intent, not exact formula identity.",
        "left_label": "[Newton/newton/newton/_src/solvers/semi_implicit/kernels_particle.py : 27-29, 43-52]\nNewton spring kernel uses stretch + relative-velocity damping.",
        "left_path": CODE_PERF_PHYSICS_NEWTON_PNG,
        "right_label": "[PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py : 121-132, 156-160]\nPhysTwin rope core builds spring+damp force, then updates velocity from force.",
        "right_path": CODE_PERF_PHYSICS_PHYSTWIN_PNG,
        "transcript": [
            "这一页回答的是更基础的 H2：两边是不是至少在做可比较的 spring-damper rope update intent。",
            "",
            "[Newton/newton/newton/_src/solvers/semi_implicit/kernels_particle.py : 27-29, 43-52]",
            "[What | Newton]",
            "L27-L29 先把每条边的 stiffness、damping 和 rest length 取出来，说明 Newton rope force 不是黑箱约束，而是按 edge-wise spring parameter 逐条计算。",
            "L43-L44 用当前边向量归一化得到 `dir`，这一步把几何形变投到当前边方向上，决定了后面恢复力和阻尼力的方向。",
            "L46-L47 同时计算 stretch `c = l - rest` 和沿边方向的相对速度 `dcdt`，也就是把弹性形变和速度阻尼拆成两个独立物理量。",
            "L50 用 `fs = dir * (ke * c + kd * dcdt)` 把弹性项和阻尼项重新合成一个 spring-damper force，这就是 Newton rope edge 的核心力学表达。",
            "L52-L53 把这一对 edge force 以反向方式原子加回两个端点，所以这个 kernel 的物理意义是 pairwise internal spring force assembly，而不是接触求解。",
            "[Why | Newton]",
            "这段代码足以支撑一个比较谨慎但重要的判断：Newton rope core 至少不是在用完全不同于 spring-damper 的奇异更新思路。",
            "它明确是边级别的 stretch + relative-velocity damping force assembly，所以后面 benchmark 里出现的 gap，不能直接归结成“Newton 做的不是 rope spring physics”。",
            "[Risk | Newton]",
            "这段源码只证明 Newton core 的 rope-side force assembly intent，不能单独推出整条 replay path 与 PhysTwin 逐项完全同构，因为完整 replay 还包括积分、控制点写入和 runtime organization。",
            "",
            "[PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py : 121-132, 156-160]",
            "[What | PhysTwin]",
            "L121-L127 先用当前边方向 `d` 和应变 `(dis_len / rest - 1)` 写出 `spring_force`，这里 PhysTwin 同样是 edge-wise 弹簧恢复力，而不是位置投影式约束。",
            "L129-L130 再把相对速度在边方向上的投影乘上 `dashpot_damping`，得到 `dashpot_forces`，这和 Newton 侧的 damping term 是同一类物理对象。",
            "L132 把 spring 和 dashpot 合成 `overall_force`，说明 PhysTwin rope 主内力同样是 spring-damper force，而不是 collision-first path。",
            "L156-L160 再把总力转成加速度，用 `v1 = v0 + a * dt` 更新速度，并在最后施加 drag 衰减，所以它仍然是 force-driven time update。",
            "[Why | PhysTwin]",
            "这段代码把 PhysTwin 侧的 rope update intent 讲得更直接：spring-damper internal force 加 gravity，然后按 `dt` 推速度，这和 Newton 侧至少在物理意图上是可比较的。",
            "因此 Q1 的 apples-to-apples benchmark 可以被解释成同类 rope update path 的性能比较，而不是两套毫无关系的 physics 在碰运气。",
            "[Risk | PhysTwin]",
            "这里也不能过强宣称“same formula means same runtime”。代码只能支持 comparable physical intent；runtime gap 还可能来自 graph replay、launch structure、bookkeeping 和 control feed path。",
        ],
    },
    {
        "kind": "table_gif",
        "title": "Result: Newton A1 Is 3.30x Slower Than PhysTwin B0",
        "note": "264 replay frames, 175421 substeps, 8.77 s physical time. No render on either side.",
        "gif_label": "Same rope replay",
        "gif_path": PERF_ROPE_CASE_GIF,
        "columns": ["Config", "ms/substep", "RTF", "vs B0", "Meaning"],
        "rows": [
            ["Newton A0", _fmt(A0_ROW, "ms_per_substep_mean", ".6f"), _fmt(A0_ROW, "rtf_mean", ".3f"), f"{A0_VS_B0:.2f}x", "baseline controller write"],
            ["Newton A1", _fmt(A1_ROW, "ms_per_substep_mean", ".6f"), _fmt(A1_ROW, "rtf_mean", ".3f"), f"{A1_VS_B0:.2f}x", "precomputed controller write"],
            ["PhysTwin B0", _fmt(B0_ROW, "ms_per_substep_mean", ".6f"), _fmt(B0_ROW, "rtf_mean", ".3f"), "1.00x", "headless graph replay"],
        ],
        "transcript": [
            "这一页只回答 Q1，不提前解释原因。",
            "完整 rope replay 现在已经做成 same-case apples-to-apples throughput table。264 个 trajectory frame 展开以后是 175421 个 substep，对应 8.77 秒物理时间。",
            f"主结果很直接：Newton A0 是 `{_fmt(A0_ROW, 'ms_per_substep_mean', '.6f')} ms/substep`，Newton A1 是 `{_fmt(A1_ROW, 'ms_per_substep_mean', '.6f')} ms/substep`，PhysTwin B0 是 `{_fmt(B0_ROW, 'ms_per_substep_mean', '.6f')} ms/substep`。",
            "A0 和 A1 的差别只在 controller feed path，不是换了一套 rope task。",
            f"所以这页真正要让老师带走的结论只有一句：在公平 rope replay benchmark 下，Newton A1 仍然比 PhysTwin B0 慢 `{A1_VS_B0:.2f}x`，也就是大约 `3.30x`。",
        ],
    },
    {
        "kind": "table_gif",
        "title": "H4: Controller-Write Overhead Is Real, But Not The Whole Gap",
        "note": "Attribution is synchronized evidence. Use it to bound likely causes, not to replace the throughput table.",
        "gif_label": "Same rope replay",
        "gif_path": PERF_ROPE_CASE_GIF,
        "columns": ["Evidence", "Value", "What it supports"],
        "rows": [
            ["A0 -> A1 speedup", f"{A0_TO_A1:.2f}x", "controller-write overhead is real"],
            ["Newton A3 controller-write side", f"{A3_BRIDGE_MS:.3f} ms/substep", "some feed-path cost remains after precompute"],
            ["Newton A3 post-write residual", f"{A3_POST_BRIDGE_MS:.3f} ms/substep", "the gap survives after controller-write reduction"],
            ["Newton A3 collision", f"{A3_COLLISION_MS:.3f} ms/substep", "pure rope replay is not collision-dominated"],
        ],
        "transcript": [
            "这一页回答 Q2 的第一半：controller-write overhead 到底有多真，以及它是不是全部解释。",
            f"A0 到 A1 的 speedup 是 `{A0_TO_A1:.3f}x`，这说明 baseline path 里每个 substep 反复做 controller interpolation、target assign 和 state write 的开销是真实存在的。",
            f"但这不是全部，因为 Newton A3 里这部分开销只有 `{A3_BRIDGE_MS:.3f} ms/substep`，而在把它降下来以后，post-write residual 仍然有 `{A3_POST_BRIDGE_MS:.3f} ms/substep`。",
            f"同一张表里 collision bucket 只有 `{A3_COLLISION_MS:.3f} ms/substep`，而且这个 baseline 本身就是 weak-contact rope replay，所以 collision-first explanation 在这里不够强。",
            "所以这一页要传达的不是一个模糊术语，而是一个直接句子：controller-write overhead 真实存在，但它解释不了全部 slowdown。",
        ],
    },
    {
        "kind": "code_twocol_large",
        "title": "Source Proof P2: Newton Still Executes The Replay As Many Solver Stages",
        "note": "Core code on the left, synchronized runtime evidence on the right.",
        "left_label": "[Newton/newton/newton/_src/solvers/semi_implicit/solver_semi_implicit.py : 141-145, 160-165, 172-177]\nNewton still advances the rope by walking through many force/contact stages.",
        "left_path": CODE_PERF_EXECUTION_NEWTON_PNG,
        "right_label": "Newton experiment + Nsight summary\nEven after replay-overhead reduction, many separated launches still remain.",
        "right_path": PERF_NEWTON_SYSTEM_PNG,
        "transcript": [
            "这一页先把 Newton 侧剩余 gap 的证据单独讲清楚，不和 PhysTwin graph 证据混在一页里。",
            "",
            "[Newton/newton/newton/_src/solvers/semi_implicit/solver_semi_implicit.py : 141-145, 160-165, 172-177]",
            "左边这段 Newton core 代码最重要的信息其实很简单：rope replay 不是一口气走完的，而是要一段一段地走 solver stages。",
            "它会先后经过 spring、triangle、bending、tetra、contact，最后才 integrate particles。换句话说，当前 replay path 更像很多小步骤依次推进，而不是一次性回放完一整步。",
            "这页右边再把实验和 Nsight 摆在一起看：A3 里 controller-write overhead 已经被压下去了，但 residual 还在；同时 Newton A1 的 CUDA API 时间里，`77.2%` 还是 `cuLaunchKernel`。",
            "所以这一页真正想说的不是『已经证明就是某一个唯一原因』，而是更收敛的一句话：在 Newton 这一侧，剩余 slowdown 更像很多分开的 solver step 和 launch 继续存在，而不是 collision 还在主导。",
            "这里也必须留一个风险提示：这只能说明方向更像运行组织方式的问题，不能单独给出精确归因比例。",
        ],
    },
    {
        "kind": "code_twocol_large",
        "title": "Source Proof P3: PhysTwin Replays The Rope Case Through One Captured Graph Path",
        "note": "Core code on the left, system evidence on the right.",
        "left_label": "[PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py : 768-782, 800-802]\nPhysTwin core explicitly captures and replays a forward graph.",
        "left_path": CODE_PERF_EXECUTION_PHYSTWIN_PNG,
        "right_label": "PhysTwin experiment + Nsight summary\nThe same clean rope replay mainly runs through graph replay in Nsight.",
        "right_path": PERF_PHYSTWIN_SYSTEM_PNG,
        "transcript": [
            "这一页再补 PhysTwin 侧，这样『为什么更像 execution / launch structure』就不是单边推断，而是两边证据对齐。",
            "",
            "[PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py : 768-782, 800-802]",
            "PhysTwin 这段源码就更直接了：只要 `cfg.use_graph` 打开，它就会 capture `self.step()`，而且还专门保留一个 `forward_graph` 给前向 replay。",
            "所以这里不是我们在外面套了一个 benchmark 技巧，而是 PhysTwin rope core 自己就把这条 replay path 做成了 graph path。",
            "右边的系统证据把这件事闭合起来：B0 throughput summary 里写了 `use_graph = true`，而 Nsight 又显示 PhysTwin B0 的 CUDA API 时间里有 `92.6%` 是 `cudaGraphLaunch_v10000`。",
            "因此这页的说服力来自三件事是一致的：实验是 clean rope replay，源码里真的有 core graph path，运行时也真的主要在 graph replay。",
            "这里同样要诚实：这仍然不能推出『Newton 只差一个 graph 就一定追平』；但它足以支持更稳的判断，PhysTwin 这一侧的快路径确实带有明确的 graph-replay 特征。",
        ],
    },
    {
        "kind": "body",
        "title": "Conclusion: Newton Still Launches Many Small Steps, While PhysTwin Replays A Graph",
        "bullets": [
            "**What the experiment says:** Newton A1 is still about `3.30x` slower on the same clean rope replay.",
            "**What A0 -> A1 says:** reducing controller-write overhead helps, but a large residual gap remains.",
            "**What the code says:** Newton still walks a staged step path, while PhysTwin exposes a captured graph replay path.",
            "**Most likely explanation:** the remaining gap is more about launch organization than collision.",
            "**Only now optimize:** keep A1, then study more graph-like or more batched Newton replay.",
        ],
        "transcript": [
            "这一页只讲一句最直接的话：为什么我们现在更怀疑 launch organization，而不是 collision。",
            "实验先给出第一层事实：在同一个 clean rope replay 上，Newton A1 还是比 PhysTwin B0 慢大约 `3.30x`。",
            "A0 到 A1 再给出第二层事实：把 controller-write overhead 降下来以后，速度确实会变好，但大的差距并没有消失。",
            "然后源码和 Nsight 再把最后一层补上：Newton 这边还是很多分阶段的小 step 和小 launch；PhysTwin 那边则是明确的 graph replay path，而且运行时也确实主要在 graph launch。",
            "所以这页真正的结论不是一个抽象词，而是一句人话：Newton 现在更像是在一小步一小步地发很多 launch，PhysTwin 更像是在回放一张已经 capture 好的 graph。",
            "也正因为这样，下一步最合理的优化方向才不是先调 collision，而是先研究能不能把 Newton rope replay 做得更 graph-like、或者至少更 batched。",
        ],
    },
    {
        "kind": "body",
        "title": "Hypothesis F1: A Force Video Must Preserve Both Global Cloth Behavior And Local Contact Mechanism",
        "bullets": [
            "**Hypothesis:** a local patch alone is not enough; the whole cloth must stay visible.",
            "**Method:** pair a global phenomenon view with a local force zoom.",
            "**Expected result:** one force video should explain both motion and contact mechanism.",
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
        "common_settings": None,
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
        "kind": "image",
        "title": "Result F4: A 4x Slow-Motion Board Makes Contact Development Easier To Read",
        "note": "Same board as F3, but the video is slowed 4x and labeled `4x slow motion` inside the clip.",
        "path": CURRENT_BUNNY_SLOW_BOARD_GIF,
        "transcript": [
            "这一页是 F3 的补充版本，不改实验设定，只改播放节奏。",
            "也就是说，self-collision 还是 OFF，cloth total mass 还是 0.1 kg，rigid target mass 还是 0.5 kg。",
            "这里放的是同一套 `2 x 2` board，但是视频整体放慢四倍，而且每个 panel 里都显式写了 `4x slow motion`。",
            "这页的作用不是替代正常速度版本，而是让老师在会议里更容易看清 pre-contact、first contact 和 penetration growth 的过渡。",
        ],
    },
    {
        "kind": "body",
        "title": "What Strict `phystwin` Now Means",
        "bullets": [
            "**Strict scope:** pairwise self-collision + implicit `z=0` ground plane.",
            "**Bridge-only implementation:** `Newton/phystwin_bridge/tools/core/phystwin_contact_stack.py`.",
            "**No Newton core change:** this mode lives outside `Newton/newton/`.",
            "**Parity target:** the PhysTwin-native cloth reference case only.",
            "**Code/doc paths on this section:** `docs/bridge/current_status.md`, `docs/bridge/tasks/self_collision_transfer.md`, `Newton/phystwin_bridge/tools/core/newton_import_ir.py`, `Newton/phystwin_bridge/tools/core/validate_parity.py`.",
            "**Takeaway:** This mode only targets the in-scope cloth reference path.",
        ],
        "transcript": [
            "这里开始进入第四段 self-collision, Newton way。",
            "这一页先把 target scene 说清楚，避免把不在 scope 里的 scene 混进 strict parity。",
            "现在我们只 claim PhysTwin 原生 cloth contact scope，也就是 pairwise self-collision 加 implicit z 等于零 ground plane。",
            "这条实现完全在 bridge 层，没有改 Newton core，而且 parity validator 也是围绕这条 cloth reference path 组织的。",
            "所以这一页的 take-home message 很简单：strict phystwin 只针对 in-scope cloth reference case。",
        ],
    },
    {
        "kind": "code_twocol_large",
        "title": "Code Compare A: What Is Already Aligned",
        "note": "Left: PhysTwin native contact code. Right: our strict `phystwin` contact code. Files: `PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py`, `Newton/phystwin_bridge/demos/self_contact_bridge_kernels.py`.",
        "left_label": "PhysTwin native: `object_collision` + `integrate_ground_collision`",
        "left_path": CODE_SELFCOLLISION_MATCHED_PHYSTWIN_PNG,
        "right_label": "Our strict `phystwin`: bridge-side self-collision + ground integrator",
        "right_path": CODE_SELFCOLLISION_MATCHED_BRIDGE_PNG,
        "transcript": [
            "第二页直接拿代码对代码，不再用抽象名词。",
            "左边是 PhysTwin 原生的 `object_collision` 和 `integrate_ground_collision`，右边是我们 bridge 里的 strict phystwin 对应实现。",
            "这页要说的结论很窄但很重要：strict scope 里的 self-collision law 和 ground contact law 已经对齐到 operator level。",
            "所以 blocked parity 现在不应该再被描述成 self-collision 或 ground law 本身还没抄对。",
        ],
    },
    {
        "kind": "code_twocol_large",
        "title": "Code Compare B: Collision Table Is Closer, But Not Yet The Same Runtime",
        "note": "Left: PhysTwin builds `collision_indices / collision_number` inside its runtime. Right: our strict `phystwin` now also freezes one table per frame, but rebuilds it inside the bridge runtime. Files: `PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py`, `Newton/phystwin_bridge/tools/core/phystwin_contact_stack.py`.",
        "left_label": "PhysTwin native: `update_collision_graph()` + `update_potential_collision`",
        "left_path": CODE_SELFCOLLISION_TABLE_PHYSTWIN_PNG,
        "right_label": "Our strict `phystwin`: `prepare_strict_phystwin_contact_frame()`",
        "right_path": CODE_SELFCOLLISION_TABLE_BRIDGE_PNG,
        "transcript": [
            "第三页继续只看代码，而且只看 collision table 这一个点。",
            "左边是 PhysTwin 原版：每帧先 build collision graph，再填 `collision_indices / collision_number`，整帧 substeps 复用这张表。",
            "右边是我们当前 strict phystwin：生命周期已经同步成 per-frame frozen table，但这张表还是 bridge runtime 自己重建的。",
            "所以这页的结论是：collision table 这边已经更像 PhysTwin 了，但 provenance 和 runtime 语义还没有完全一样。",
        ],
    },
    {
        "kind": "code_twocol_large",
        "title": "Code Compare C: Controller Handling Is Still Not PhysTwin-Native",
        "note": "Left: PhysTwin spring code reads separate `control_x / control_v`. Right: our bridge still writes controller points into Newton particle state. Files: `PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py`, `Newton/phystwin_bridge/tools/core/newton_import_ir.py`.",
        "left_label": "PhysTwin native: `eval_springs(..., control_x, control_v, ...)`",
        "left_path": CODE_SELFCOLLISION_CONTROLLER_PHYSTWIN_PNG,
        "right_label": "Our bridge: write controller particle positions into `state_in.particle_q / qd`",
        "right_path": CODE_SELFCOLLISION_CONTROLLER_BRIDGE_PNG,
        "transcript": [
            "第四页还是代码对代码，但这次看 controller handling。",
            "左边 PhysTwin 的 spring path 直接吃 `control_x / control_v`；右边我们当前 bridge 还是把 controller 点写进 Newton particle state 里。",
            "这也是为什么 current status 现在把 controller-spring diagnostic 当成下一阶段最像 blocker 的信号。",
            "所以这页的结论是：如果还要继续压 full-rollout parity，这一层比继续纠缠 self-collision law 更值得先改。",
        ],
    },
    {
        "kind": "body",
        "title": "Where The Full-Rollout Mismatch Now Shows Up",
        "bullets": [
            "**Strict parity is still blocked on the in-scope cloth reference case:** `docs/bridge/current_status.md`.",
            "**60-frame frozen-table result improved:** `0.001314889290370047` vs dynamic `0.001589029561728239`.",
            "**302-frame strict run still stalls around `1e-2`:** `rmse_mean = 0.010103434324264526`, `last30_rmse = 0.014149246737360954`.",
            "**Full-rollout A/B still fails:** OFF `rmse_mean = 0.009786468930542469`, strict `phystwin` `rmse_mean = 0.010103434324264526`.",
            "**Current next blocker signal:** controller-spring diagnostic in `docs/bridge/current_status.md` reports `one-step force_abs_max = 0.006733048971410349`, `short-rollout force_abs_max = 389.3789927564146`, `pass = false`.",
            "**Takeaway:** The remaining gap is now better described as whole-step cloth rollout mismatch, especially the controller-spring side, not simply “self-collision law still wrong”.",
        ],
        "transcript": [
            "第五页才讲数字，而且只讲 full rollout blocker。",
            "现在 frozen-table 默认已经把短窗口拉得更好了，但 full 302-frame strict run 还是停在 1e-2 量级。",
            "更关键的是 full-rollout A/B 现在仍然没过线，而且 controller-spring diagnostic 已经给出一个更像主因的信号。",
            "所以这一页的 take-home message 是：剩下的 gap 更像是 whole-step cloth rollout mismatch，尤其是 controller-spring side，而不是一句话说成 self-collision law 还错。",
        ],
    },
    {
        "kind": "table_gif",
        "title": "Full-Rollout A/B On The In-Scope Cloth Reference Case",
        "note": "Source paths used on this page: `docs/bridge/current_status.md`, `Newton/phystwin_bridge/tools/core/validate_parity.py`, `Newton/phystwin_bridge/results/tmp_off_vs_phystwin_302_compare_20260401/compare_summary.json`.",
        "columns": ["Mode", "rmse_mean", "rmse_max", "first30_rmse", "last30_rmse"],
        "rows": [
            ["OFF", "0.009786468930542469", "0.01691424660384655", "0.0023693302646279335", "0.012819756753742695"],
            ["Strict phystwin", "0.010103434324264526", "0.018793748691678047", "0.0005582491285167634", "0.014149246737360954"],
        ],
        "gif_path": SELF_PARITY_SUPPORT_GIF,
        "gif_label": "302-frame parity support video",
        "transcript": [
            "最后一页只看 in-scope cloth reference case 的 full-rollout A/B，不再混 box scene。",
            "右边是最新 302-frame parity support video，左边的表直接列 OFF 和 strict phystwin 的 full-rollout 数字。",
            "现在 strict phystwin 只在前 30 帧更好，但 full-rollout 的 rmse_mean 还没有低于 OFF。",
            "所以这一页的 take-home message 很直接：当前 strict phystwin 还没有通过 full-rollout A/B gate。",
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
        NEWTON_CORE_SPRING_PATH,
        "newton_rope_spring_force",
        _extract_code_segments(
            NEWTON_CORE_SPRING_PATH,
            [(27, 29), (43, 52)],
            highlight_lines={27, 28, 46, 47, 50},
        ),
        CODE_PERF_PHYSICS_NEWTON_PNG,
    )
    _code_excerpt_image(
        PHYSTWIN_SPRING_WARP_CODE_PATH,
        "phystwin_rope_force_update",
        _extract_code_segments(
            PHYSTWIN_SPRING_WARP_CODE_PATH,
            [(121, 132), (156, 160)],
            highlight_lines={123, 124, 129, 157, 159},
        ),
        CODE_PERF_PHYSICS_PHYSTWIN_PNG,
    )
    _code_excerpt_image(
        NEWTON_CORE_SEMIIMPLICIT_PATH,
        "newton_semimplicit_step_path",
        _extract_code_segments(
            NEWTON_CORE_SEMIIMPLICIT_PATH,
            [(141, 145), (160, 165), (172, 177)],
            highlight_lines={142, 145, 161, 173, 177},
        ),
        CODE_PERF_EXECUTION_NEWTON_PNG,
    )
    _code_excerpt_image(
        PHYSTWIN_SPRING_WARP_CODE_PATH,
        "phystwin_graph_replay_path",
        _extract_code_segments(
            PHYSTWIN_SPRING_WARP_CODE_PATH,
            [(769, 782), (800, 802)],
            highlight_lines={769, 772, 780, 782, 802},
        ),
        CODE_PERF_EXECUTION_PHYSTWIN_PNG,
    )
    _system_summary_image(
        PERF_NEWTON_SYSTEM_PNG,
        "System Evidence",
        "results/rope_perf_apples_to_apples/newton/A3_precomputed_attribution + nsight/newton_A1",
        [
            "A3 bridge: 0.037 ms/substep",
            f"A3 post-bridge residual: {A3_POST_BRIDGE_MS:.3f} ms/substep",
            f"A3 collision: {A3_COLLISION_MS:.3f} ms/substep",
            "Nsight API: 77.2% cuLaunchKernel",
            "Interpretation: many staged launches still survive after bridge precompute",
        ],
        font_size=22,
        max_chars=78,
    )
    _system_summary_image(
        PERF_PHYSTWIN_SYSTEM_PNG,
        "System Evidence",
        "results/rope_perf_apples_to_apples/phystwin/B0_headless_throughput + nsight/phystwin_B0",
        [
            "B0 use_graph: True",
            "B0 object_collision_flag: False",
            "B1 simulator_launch: 6.601 ms/frame",
            "Nsight API: 92.6% cudaGraphLaunch_v10000",
            "Interpretation: replay path is graph-driven in the PhysTwin core",
        ],
        font_size=22,
        max_chars=78,
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
    _code_excerpt_image(
        PHYSTWIN_SPRING_WARP_CODE_PATH,
        "phystwin_matched_contact_scope",
        _extract_code_segments(
            PHYSTWIN_SPRING_WARP_CODE_PATH,
            [(260, 297), (301, 350)],
            highlight_lines={261, 268, 281, 295, 302, 323, 332, 343, 349},
        ),
        CODE_SELFCOLLISION_MATCHED_PHYSTWIN_PNG,
    )
    _code_excerpt_image(
        PHYSTWIN_SPRING_WARP_CODE_PATH,
        "phystwin_collision_graph",
        _extract_code_segments(
            PHYSTWIN_SPRING_WARP_CODE_PATH,
            [(926, 940), (229, 257)],
            highlight_lines={926, 928, 930, 931, 935, 939, 246, 255, 256, 257},
        ),
        CODE_SELFCOLLISION_TABLE_PHYSTWIN_PNG,
    )
    bridge_self_contact_code = ROOT / "Newton" / "phystwin_bridge" / "demos" / "self_contact_bridge_kernels.py"
    _code_excerpt_image(
        bridge_self_contact_code,
        "bridge_matched_contact_scope",
        _extract_code_segments(
            bridge_self_contact_code,
            [(521, 557), (629, 687)],
            highlight_lines={523, 540, 544, 556, 629, 660, 669, 680, 686},
        ),
        CODE_SELFCOLLISION_MATCHED_BRIDGE_PNG,
    )
    bridge_phystwin_stack = ROOT / "Newton" / "phystwin_bridge" / "tools" / "core" / "phystwin_contact_stack.py"
    _code_excerpt_image(
        bridge_phystwin_stack,
        "bridge_phystwin_collision_table",
        _extract_code_segments(
            bridge_phystwin_stack,
            [(297, 328)],
            highlight_lines={297, 302, 309, 312, 315, 322, 324, 327},
        ),
        CODE_SELFCOLLISION_TABLE_BRIDGE_PNG,
    )
    _code_excerpt_image(
        PHYSTWIN_SPRING_WARP_CODE_PATH,
        "phystwin_controller_springs",
        _extract_code_segments(
            PHYSTWIN_SPRING_WARP_CODE_PATH,
            [(64, 78), (82, 137)],
            highlight_lines={64, 69, 74, 75, 85, 86, 103, 105, 109, 111, 129, 132},
        ),
        CODE_SELFCOLLISION_CONTROLLER_PHYSTWIN_PNG,
    )
    bridge_import_code = ROOT / "Newton" / "phystwin_bridge" / "tools" / "core" / "newton_import_ir.py"
    _code_excerpt_image(
        bridge_import_code,
        "bridge_controller_particles",
        _extract_code_segments(
            bridge_import_code,
            [(1591, 1600), (1606, 1626)],
            highlight_lines={1591, 1596, 1606, 1608, 1610, 1615, 1619, 1623},
        ),
        CODE_SELFCOLLISION_CONTROLLER_BRIDGE_PNG,
    )
    for name, src in ACCEPTED_PHENO_MP4.items():
        _ensure_gif(src, ACCEPTED_PHENO_GIF[name], width=640, fps=8, max_colors=96)
    if CURRENT_BUNNY_BOARD_MP4.exists():
        _ensure_current_bunny_publish_gifs()
        _ensure_current_bunny_slow_board()
        _ensure_gif(
            CURRENT_BUNNY_BOARD_MP4,
            CURRENT_BUNNY_BOARD_GIF,
            max_size_mb=DEFAULT_MAX_GIF_MB,
            quality_profiles=CURRENT_BUNNY_BOARD_GIF_PROFILES,
        )
        if CURRENT_BUNNY_SLOW_BOARD_MP4.exists():
            _ensure_gif(
                CURRENT_BUNNY_SLOW_BOARD_MP4,
                CURRENT_BUNNY_SLOW_BOARD_GIF,
                max_size_mb=DEFAULT_MAX_GIF_MB,
                quality_profiles=CURRENT_BUNNY_SLOW_BOARD_GIF_PROFILES,
            )
        for name, src in CURRENT_BUNNY_PANEL_MP4.items():
            _ensure_gif(
                src,
                CURRENT_BUNNY_PANEL_GIF[name],
                max_size_mb=DEFAULT_MAX_GIF_MB,
                quality_profiles=CURRENT_BUNNY_PANEL_GIF_PROFILES,
            )
    for name, src in ACCEPTED_FORCE_MP4.items():
        _ensure_gif(src, ACCEPTED_FORCE_GIF[name], width=640, fps=8, max_colors=96)
    if SELF_PARITY_SUPPORT_MP4.exists():
        _ensure_gif(SELF_PARITY_SUPPORT_MP4, SELF_PARITY_SUPPORT_GIF, width=640, fps=8, max_colors=96)
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


def _system_summary_image(
    out_path: Path,
    title: str,
    subtitle: str,
    lines: list[str],
    *,
    font_size: int = 24,
    max_chars: int = 72,
) -> Path:
    return _render_code_png(
        out_path,
        title,
        subtitle,
        lines,
        font_size=font_size,
        max_chars=max_chars,
    )


def _ensure_transcoded_gif(
    src_path: Path,
    gif_path: Path,
    *,
    width: int = 640,
    fps: int = 8,
    max_colors: int = 96,
    max_size_mb: float | None = None,
    quality_profiles: list[tuple[int, int, int]] | None = None,
) -> Path:
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    profile_rows = [
        [int(w), int(f), int(c)]
        for w, f, c in (quality_profiles or [(width, fps, max_colors)])
    ]
    meta_path = gif_path.with_suffix(f"{gif_path.suffix}.meta.json")
    signature = {
        "profiles": profile_rows,
        "max_size_mb": None if max_size_mb is None else float(max_size_mb),
        "palette_stats_mode": "full",
        "palette_dither": "sierra2_4a",
    }
    if gif_path.exists() and meta_path.exists() and gif_path.stat().st_mtime >= src_path.stat().st_mtime:
        try:
            meta_obj = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta_obj = {}
        if meta_obj.get("signature") == signature:
            return gif_path
    budget_bytes = None
    if max_size_mb is not None and float(max_size_mb) > 0.0:
        budget_bytes = int(round(float(max_size_mb) * 1_000_000.0))
    candidate_path = gif_path.with_name(f"{gif_path.stem}.tmp{gif_path.suffix}")
    chosen_profile: list[int] | None = None
    chosen_size = 0
    for render_width, render_fps, render_colors in profile_rows:
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
                    f"fps={int(render_fps)},scale={int(render_width)}:-1:flags=lanczos,"
                    f"split[s0][s1];[s0]palettegen=max_colors={int(render_colors)}:stats_mode=full[p];"
                    "[s1][p]paletteuse=dither=sierra2_4a"
                ),
                "-loop",
                "0",
                str(candidate_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        candidate_size = candidate_path.stat().st_size
        chosen_profile = [int(render_width), int(render_fps), int(render_colors)]
        chosen_size = int(candidate_size)
        if budget_bytes is None or candidate_size <= budget_bytes:
            break
    candidate_path.replace(gif_path)
    meta_path.write_text(
        json.dumps(
            {
                "signature": signature,
                "chosen_profile": chosen_profile,
                "size_bytes": chosen_size,
                "source": str(src_path),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return gif_path


def _ensure_gif(
    mp4_path: Path,
    gif_path: Path,
    *,
    width: int = 640,
    fps: int = 8,
    max_colors: int = 96,
    max_size_mb: float | None = None,
    quality_profiles: list[tuple[int, int, int]] | None = None,
) -> Path:
    return _ensure_transcoded_gif(
        mp4_path,
        gif_path,
        width=width,
        fps=fps,
        max_colors=max_colors,
        max_size_mb=max_size_mb,
        quality_profiles=quality_profiles,
    )


def _ensure_current_bunny_panel_mp4s() -> None:
    if not CURRENT_BUNNY_BOARD_SUMMARY.exists():
        raise FileNotFoundError(f"missing bunny board summary: {CURRENT_BUNNY_BOARD_SUMMARY}")
    board_mtime = 0.0
    if CURRENT_BUNNY_BOARD_MP4.exists():
        board_mtime = CURRENT_BUNNY_BOARD_MP4.stat().st_mtime
    expected = list(CURRENT_BUNNY_PANEL_MP4.values()) + list(CURRENT_BUNNY_PANEL_PUBLISH_GIF.values())
    stale_or_missing = [
        path
        for path in expected
        if (not path.exists()) or (board_mtime > 0.0 and path.stat().st_mtime < board_mtime)
    ]
    if not stale_or_missing:
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


def _ensure_current_bunny_publish_gifs() -> None:
    if not CURRENT_BUNNY_BOARD_MP4.exists():
        return
    _ensure_gif(
        CURRENT_BUNNY_BOARD_MP4,
        CURRENT_BUNNY_BOARD_PUBLISH_GIF,
        max_size_mb=DEFAULT_MAX_GIF_MB,
        quality_profiles=CURRENT_BUNNY_BOARD_PUBLISH_GIF_PROFILES,
    )
    _ensure_current_bunny_panel_mp4s()
    for name, src in CURRENT_BUNNY_PANEL_MP4.items():
        _ensure_gif(
            src,
            CURRENT_BUNNY_PANEL_PUBLISH_GIF[name],
            max_size_mb=DEFAULT_MAX_GIF_MB,
            quality_profiles=CURRENT_BUNNY_PANEL_PUBLISH_GIF_PROFILES,
        )


def _ensure_current_bunny_slow_board() -> None:
    if not CURRENT_BUNNY_BOARD_SUMMARY.exists():
        return
    main_summary = json.loads(CURRENT_BUNNY_BOARD_SUMMARY.read_text(encoding="utf-8"))
    box_summary = Path(str(main_summary["cases"]["box_control"]["detector_summary_path"])).expanduser().resolve()
    bunny_summary = Path(str(main_summary["cases"]["bunny_baseline"]["detector_summary_path"])).expanduser().resolve()
    slow_inputs = [CURRENT_BUNNY_BOARD_SUMMARY, box_summary, bunny_summary, RENDER_BUNNY_BOARD_PATH]
    newest_input_mtime = max(path.stat().st_mtime for path in slow_inputs if path.exists())
    slow_outputs = [CURRENT_BUNNY_SLOW_BOARD_MP4, CURRENT_BUNNY_SLOW_BOARD_PUBLISH_GIF, CURRENT_BUNNY_SLOW_BOARD_SUMMARY]
    needs_render = any((not path.exists()) or path.stat().st_mtime < newest_input_mtime for path in slow_outputs)
    if needs_render:
        CURRENT_BUNNY_SLOW_BOARD_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "python",
                str(RENDER_BUNNY_BOARD_PATH),
                "--box-summary",
                str(box_summary),
                "--bunny-summary",
                str(bunny_summary),
                "--out-dir",
                str(CURRENT_BUNNY_SLOW_BOARD_DIR),
                "--output-stem",
                CURRENT_BUNNY_SLOW_BOARD_STEM,
                "--slowdown-factor",
                "4",
                "--playback-label",
                "4x slow motion",
            ],
            check=True,
        )
    elif CURRENT_BUNNY_SLOW_BOARD_MP4.exists():
        _ensure_gif(
            CURRENT_BUNNY_SLOW_BOARD_MP4,
            CURRENT_BUNNY_SLOW_BOARD_PUBLISH_GIF,
            max_size_mb=DEFAULT_MAX_GIF_MB,
            quality_profiles=CURRENT_BUNNY_SLOW_BOARD_PUBLISH_GIF_PROFILES,
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


def _table_with_gif(
    prs: Presentation,
    title: str,
    columns: list[str],
    rows: list[list[str]],
    gif_path: Path,
    gif_label: str,
    *,
    note: str | None = None,
) -> None:
    slide = prs.slides.add_slide(_layout(prs))
    _clear_placeholders(slide)
    title_box = slide.shapes.add_textbox(REF_TITLE_LEFT, REF_TITLE_TOP, REF_TITLE_W, REF_TITLE_H)
    _set_title_textbox(title_box, title, size_pt=28)
    if note:
        _add_label(slide, 420000, 1180000, 5600000, 220000, note, font_size=11, bold=False)
    _add_label(slide, 6670000, 1500000, 1900000, 220000, gif_label, font_size=11, bold=False)
    _add_pic(slide, gif_path, 6420000, 1780000, 2250000, 1380000)

    table_left = 420000
    table_top = 1540000
    table_w = 5750000
    table_h = 3150000
    table_shape = slide.shapes.add_table(len(rows) + 1, len(columns), table_left, table_top, table_w, table_h)
    table = table_shape.table
    widths = [
        int(table_w * 0.14),
        int(table_w * 0.34),
        int(table_w * 0.16),
        int(table_w * 0.12),
        int(table_w * 0.24),
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
            font_size=13,
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
            set_cell_text(
                table.cell(r, c),
                str(value),
                bold=(c == 0),
                align_center=(c != 0),
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
        elif kind == "table_gif":
            _table_with_gif(
                prs,
                slide["title"],
                slide["columns"],
                slide["rows"],
                slide["gif_path"],
                slide["gif_label"],
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
