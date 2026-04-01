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
from PIL import Image, ImageDraw, ImageFont
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

RECALL_CLOTH_GIF = OFFLINE_GIF_DIR / "cloth_cmp2x3.gif"
RECALL_ZEBRA_GIF = OFFLINE_GIF_DIR / "zebra_cmp2x3.gif"
RECALL_SLOTH_GIF = OFFLINE_GIF_DIR / "sloth_cmp2x3.gif"
RECALL_ROPE_GIF = OFFLINE_GIF_DIR / "rope_drag_on_cmp2x3.gif"
RECALL_CLOTH_OVERLAY_GIF = OFFLINE_GIF_DIR / "cloth_overlay1x3.gif"
RECALL_ZEBRA_OVERLAY_GIF = OFFLINE_GIF_DIR / "zebra_overlay1x3.gif"
RECALL_SLOTH_OVERLAY_GIF = OFFLINE_GIF_DIR / "sloth_overlay1x3.gif"
RECALL_ROPE_OVERLAY_GIF = OFFLINE_GIF_DIR / "rope_drag_on_overlay1x3.gif"
RECALL_BUNNY_M5_GIF = OFFLINE_GIF_DIR / "bunny_drop_m5.gif"
RECALL_BUNNY_M500_GIF = OFFLINE_GIF_DIR / "bunny_drop_m500.gif"

PREV_GIF_DIR = ROOT / "formal_slide" / "meeting_2026_03_25" / "gif"
RECALL_ROPE_WEIGHT_1KG_GIF = PREV_GIF_DIR / "rope_bunny_total1kg_m5_v1.gif"
RECALL_ROPE_WEIGHT_5KG_GIF = PREV_GIF_DIR / "rope_bunny_total5kg_m5_v1.gif"
RECALL_BUNNY_SUPPORT_GIF = PREV_GIF_DIR / "cloth_rigid_compare_bunny_m5_v1.gif"
RECALL_BOX_SUPPORT_GIF = PREV_GIF_DIR / "cloth_rigid_compare_box_m5_v1.gif"
RECALL_THIN_EAR_5X_GIF = PREV_GIF_DIR / "thin_ear_ccd5x_v3.gif"
RECALL_THIN_EAR_10X_GIF = PREV_GIF_DIR / "thin_ear_ccd10x_v3.gif"

VIEWER_CODE_PATH = ROOT / "Newton" / "phystwin_bridge" / "demos" / "demo_rope_control_realtime_viewer.py"
PHYSTWIN_SPRING_WARP_CODE_PATH = ROOT / "PhysTwin" / "qqtt" / "model" / "diff_simulator" / "spring_mass_warp.py"
IMAGE_DIR = MEETING_DIR / "images"
CODE_REPLAY_SEMANTICS_PNG = IMAGE_DIR / "code_replay_semantics.png"
CODE_GRANULAR_PROFILE_PNG = IMAGE_DIR / "code_granular_profile.png"
PERF_ATTRIBUTION_PNG = IMAGE_DIR / "perf_attribution_breakdown.png"
PERF_NSIGHT_PNG = IMAGE_DIR / "perf_nsight_breakdown.png"
FORCE_DIAG_CODE_PNG = IMAGE_DIR / "code_force_diag_capture.png"
FORCE_LAYOUT_CODE_PNG = IMAGE_DIR / "code_force_diag_layout.png"
PERF_ROPE_CASE_GIF = MEETING_DIR / "gif" / "rope_perf_case_anchor.gif"

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
CURRENT_BUNNY_BOARD_GIF = MEETING_DIR / "gif" / "bunny_collision_board_2x2.gif"
CURRENT_BUNNY_BOARD_FIRST_FRAME = (
    CURRENT_BUNNY_RUN / "artifacts" / "collision_force_board" / "collision_force_board_2x2_first_frame.png"
)
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
ACCEPTED_PHENO_GIF = {name: MEETING_DIR / "gif" / f"{name}_phenomenon.gif" for name in ACCEPTED_PHENO_MP4}
ACCEPTED_FORCE_GIF = {name: MEETING_DIR / "gif" / f"{name}_force.gif" for name in ACCEPTED_FORCE_MP4}
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
ROBOT_DROP_BASELINE_OFF_GIF = MEETING_DIR / "gif" / "robot_drop_release_drag_off.gif"
ROBOT_DROP_BASELINE_ON_GIF = MEETING_DIR / "gif" / "robot_drop_release_drag_on.gif"


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
        "title": "Recall 1: Earlier Bridge Baseline Already Worked",
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
        "title": "Recall 2: Earlier Bridge Baseline Also Matched The Reference Motion",
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
        "title": "Recall 3: Bunny+Rope Already Showed Deformable-Rigid Interaction",
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
        "title": "Recall 4: Weight Changes Already Preserved Interaction",
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
        "title": "Recall 5: Bunny Was Harder Than Thick Box",
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
        "title": "Recall 6: Radius Helped, But Thin Geometry Still Survived",
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
        "note": "Real source excerpts only. The evidence here is replay interface shape, not full implementation detail.",
        "left_label": "Newton: `--profile-only`, `throughput|attribution`, `baseline|precomputed`.",
        "left_path": CODE_REPLAY_SEMANTICS_PNG,
        "right_label": "PhysTwin: `use_graph=True`, capture once, replay by `forward_graph`.",
        "right_path": CODE_GRANULAR_PROFILE_PNG,
        "transcript": [
            "这一页是 source proof，不是结果页，所以 slide 上只放两段短 code excerpt 和一句短分析。",
            "左边这段 Newton source code 现在只保留三件事：`--profile-only`、`--profile-mode`、`--controller-write-mode`。这已经足够说明 A0 到 A3 不是临时 hack，而是这个 benchmark interface 原生支持的路径。",
            "右边这段 PhysTwin source code 现在只保留 `cfg.use_graph`、`ScopedCapture`、`self.graph` 和 `self.forward_graph`。这已经足够说明 B0 是 graph-captured replay path，而不是 GUI loop。",
            "所以这页真正的分析应该放在 transcript 里：两边不是在比不同 task，而是在比同一个 replay 下两种 execution style。",
            "我把大部分低价值细节从 slide 移掉了，比如更长的 surrounding code、无关 helper、以及更多行的 control flow。",
        ],
    },
    {
        "kind": "table",
        "title": "Result P1: A1 Is Still 3.30x Slower Than B0",
        "note": "Same `rope_double_hand` replay. No render. RTX 4090.",
        "columns": ["Config", "Controller / Launch", "ms/substep", "RTF", "Takeaway"],
        "rows": [
            ["Newton A0", "baseline write", _fmt(A0_ROW, "ms_per_substep_mean", ".6f"), _fmt(A0_ROW, "rtf_mean", ".3f"), "bridge tax on"],
            ["Newton A1", "precomputed write", _fmt(A1_ROW, "ms_per_substep_mean", ".6f"), _fmt(A1_ROW, "rtf_mean", ".3f"), "same replay, tax reduced"],
            ["PhysTwin B0", "graph headless replay", _fmt(B0_ROW, "ms_per_substep_mean", ".6f"), _fmt(B0_ROW, "rtf_mean", ".3f"), "same replay, graph-enabled"],
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
        "kind": "image",
        "title": "Result P2: Bridge Tax Is Only Part Of The Gap",
        "path": PERF_ATTRIBUTION_PNG,
        "note": "A0→A1 proves bridge tax. A3/B1 still show the clean rope gap is not collision-dominated.",
        "transcript": [
            "这一页现在不再是一堵字墙，而是改成一个 attribution chart。",
            f"首先 H1 还是一样硬：A0 到 A1 是 `{A0_ROW.get('ms_per_substep_mean', 0.0) / max(A1_ROW.get('ms_per_substep_mean', 1.0e-12), 1.0e-12):.3f}x` 的提升，所以 controller bridge tax 是真实存在的。",
            f"但 bridge tax 不是全部。Newton A3 的 precomputed attribution 里，bridge 是 `{A3_BRIDGE_MS:.3f} ms/substep`，internal force `{A3_INTERNAL_MS:.3f}`，integration `{A3_INTEGRATION_MS:.3f}`，collision 只有 `{A3_COLLISION_MS:.3f}`，还剩 `{A3_UNEXPLAINED_MS:.3f}` 的 runtime overhead。",
            f"右边的 PhysTwin B1 frame-level attribution 则说明它的大头基本就是 simulator launch，本身大约 `{B1_SIM_LAUNCH_MS:.3f} ms/frame`；controller target `{B1_CONTROLLER_FRAME_MS:.3f}` 和 state reset `{B1_STATE_RESET_MS:.3f}` 都是小头。",
            "所以这一页的真正 point 还是结构：bridge tax 确实存在，但 clean rope replay 的 remaining gap 不是 collision story。",
        ],
    },
    {
        "kind": "image",
        "title": "Result P3: Nsight Supports A Launch-Structure Explanation",
        "path": PERF_NSIGHT_PNG,
        "note": "Newton API time is launch-dominated; PhysTwin replay is graph-launch-dominated on the same rope case.",
        "transcript": [
            "这一页也从纯文字改成了 chart，因为这里的 point 本质上是一个 100% share comparison。",
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
        "kind": "code_twocol",
        "title": "Source Proof: The Diagnostic Really Splits Contact Forces And Renders A Global+Local Layout",
        "common_settings": "Left = the trigger substep explicitly stores `f_spring`, `f_internal_total`, and `f_external_total`. Right = the accepted renderer keeps the main global view, draws 3D world-space glyphs, adds a zoom panel, and renders force artifacts in a fresh helper process so the process-video path and force-video path do not contaminate each other.",
        "left_label": "Bridge diagnostic capture: external force is measured as the incremental particle-body contact contribution on top of the internal force path.",
        "left_path": FORCE_DIAG_CODE_PNG,
        "right_label": "Bridge render path: keep the manual global camera, draw 3D glyphs, then add the split zoom panel for the local patch.",
        "right_path": FORCE_LAYOUT_CODE_PNG,
        "transcript": [
            "这一页是新的 source proof。",
            "左边这段 bridge code 说明 trigger substep 不是黑盒截图，而是在同一个 substep 里把 `f_spring`、`f_internal_total` 和 `f_external_total` 明确分开。这里的 external force 不是猜的，而是 particle-body contact 之后相对于 internal path 的增量。",
            "右边这段 render code 说明 accepted 版本没有再把主画面换成一个 contact-only camera。它保留全局主相机，在 3D scene 里直接画 world-space glyph，再加右侧 zoom panel，所以 full cloth context 和 local readability 才能同时存在。",
            "另外 accepted 版本还把 force artifact render 单独放进 fresh helper process，所以 phenomenon video 和 force video 不会再互相污染成黑片。",
        ],
    },
    {
        "kind": "grid",
        "title": "Result F1: Accepted Global Phenomenon Videos Cover The Whole Penetration Story",
        "common_settings": "All four accepted cases now pass black-screen, motion, and temporal-density QA on the phenomenon video. The point of this page is WHAT happened over time.",
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
        "title": "Result F2: Accepted Force Videos Keep The Full Cloth And Still Explain The Local Contact Patch",
        "common_settings": "All four accepted force videos now pass black-screen, motion, temporal-density, subject-visibility, and contact-readability QA. Experiment setting for the bunny mechanism workpoint: cloth total mass = 0.1 kg, rigid target mass = 0.5 kg. The point of this page is WHY it happened.",
        "items": [
            ("Bunny baseline\nforce mechanism", ACCEPTED_FORCE_GIF["bunny_baseline"]),
            ("Box control\nforce mechanism", ACCEPTED_FORCE_GIF["box_control"]),
            ("Bunny low inertia\nforce mechanism", ACCEPTED_FORCE_GIF["bunny_low_inertia"]),
            ("Bunny larger scale\nforce mechanism", ACCEPTED_FORCE_GIF["bunny_larger_scale"]),
        ],
        "transcript": [
            "这一页专门讲 force mechanism。",
            "这里也把实验设定说清楚：cloth total mass 是 0.1 kg，rigid target mass 是 0.5 kg。",
            "现在 accepted 的 force video 已经满足一个很关键的视觉要求：左侧主面板仍然能看到 full cloth 和 bunny，右侧 zoom panel 才负责讲 local force patch。",
            "所以我们不再在 global story 和 local readability 之间二选一。",
            "从这四个 case 可以直接看出，主要问题不是 outward direction 错了，而是 contact support 太弱，尤其是 bunny baseline、low inertia 和 larger scale 这三条 still point to insufficient contact magnitude。",
        ],
    },
    {
        "kind": "image",
        "title": "Result F3: The New 2x2 Board Makes The Box-vs-Bunny Comparison Immediate",
        "note": "Current promoted meeting artifact: TL box penalty, TR box total, BL bunny penalty, BR bunny total. Experiment setting: self-collision OFF, cloth total mass = 0.1 kg, rigid target mass = 0.5 kg. The board uses all rigid force-active cloth nodes from rollout start to one second after first collision.",
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
        "title": "Result F4: The Historical 4-Case Summary Board Still Compresses The Older Mechanism Story",
        "note": "Historical 4-case sync-safe summary board: one representative phenomenon frame + one representative force frame per case, together with compact metrics and one-sentence takeaway.",
        "path": ACCEPTED_BUNNY_BOARD_PNG,
        "transcript": [
            "这一页保留历史的 4-case summary board，作用更像一张 mechanism summary appendix。",
            "每个 case 都只保留一张 phenomenon frame、一张 force frame、几项关键指标和一句 takeaway，所以它仍然适合快速回顾旧的四 case mechanism package。",
            "但和上一页相比，这一页现在不再是主要视频页；真正更适合 meeting 现场播放的是新的 `2 x 2` board。",
        ],
    },
    {
        "kind": "image",
        "title": "Question, Claim, And Constraint: Final Self-Collision Campaign",
        "note": "Campaign summary slide: promoted mode, no-core-change constraint, and current gate status.",
        "path": SLIDE_QUESTION_CLAIM_PNG,
        "transcript": [
            "这里开始进入第四段 self-collision, Newton way。",
            "这一章展开成 6 页 self-collision campaign 证据块。",
            "这一页先把 claim 说死：最终 promoted mode 是 bridge-side phystwin，而且整个 campaign 没有改 Newton core。",
            "同时我也把当前 gate 状态讲清楚：exactness 已经过，final cloth-box demo 已经过 QC，但 strict self-collision parity 仍然被 blocker 卡住。",
        ],
    },
    {
        "kind": "image",
        "title": "Source Evidence: Native Newton Semantics Are Not PhysTwin Exact",
        "note": "Use the campaign code-evidence summary board directly: IR radius mapping, off/native/custom/phystwin mode split, and bridge-side PhysTwin operator.",
        "path": SLIDE_SOURCE_EVIDENCE_PNG,
        "transcript": [
            "这一页是源码证据，不是实验结果。",
            "第一段代码说明 bridge 会把 PhysTwin pairwise collision distance 映射成 Newton particle radius 语义，所以 native path 一开始就不是原封不动的 PhysTwin collision law。",
            "第二段代码说明 cloth-box ON 场景里，off、native、custom、phystwin 四条路径是明确分开的；第三段代码说明 exact PhysTwin-style velocity correction 是 bridge-side 引入，而不是改 Newton core。",
            "同时这里也要把边界说清楚：PhysTwin 这条 cloth spring-mass 源码原生只定义了 pairwise object_collision 和 implicit z=0 ground collision，没有 generic box-support contact。",
        ],
    },
    {
        "kind": "image",
        "title": "Scene-Level Decision Matrix: Native Is Not Enough",
        "note": "Controlled cloth-box matrix plus bunny-diagnostic conclusion. Use this page to separate scene-level evidence from source-level evidence.",
        "path": SLIDE_NATIVE_FAILURE_PNG,
        "transcript": [
            "这一页是 controlled scene-level evidence。",
            "cloth-box matrix 的作用不是证明 phystwin 已经完美，而是证明 native 不足以直接被当成最终 claim。",
            "所以 box scene 在这里是 scene evidence，不是 strict phystwin parity scene。",
            "这里我只保留 cloth-box scope，不再把 bunny 或其他 scene 混进最终结论里。",
        ],
    },
    {
        "kind": "image",
        "title": "Bridge-Side PhysTwin Exactness",
        "note": "Operator-level exactness result from the campaign verifier.",
        "path": SLIDE_EXACTNESS_PNG,
        "transcript": [
            "这一页只回答一个问题：bridge-side phystwin operator 本身是不是 exact。",
            "现在 verifier 的 strict gate 已经过：max_abs_dv 在 1e-6 量级，median_rel_dv 在 1e-8 量级。",
            "所以我们可以把 exactness claim 说得很窄但很硬：operator-level PhysTwin collision equivalence 已经验证通过。",
        ],
    },
    {
        "kind": "image",
        "title": "Final Demo: Cloth + Box + Self-Collision ON",
        "note": "QC-passing hero demo contact sheet from the final top-down `phystwin` presentation render.",
        "path": SLIDE_FINAL_DEMO_PNG,
        "transcript": [
            "这一页放最终 cloth-box phystwin hero demo。",
            "我最后选的是 top-down presentation 视角，因为它同时保住了 cloth、box、接触区和后续 settle 过程。",
            "但这个视频的作用是 demo evidence，不是 strict parity 的 claim scope。",
            "这条视频已经通过 black/blank、motion 和 scene-visibility 的 QC gate，所以它是当前可以直接汇报的 self-collision ON 最终 demo。",
        ],
    },
    {
        "kind": "image",
        "title": "Strict Self-Collision Parity Is Blocked By Rollout Mismatch",
        "note": "Final blocker page: the in-scope cloth self-collision reference exists, but the current Newton bridge rollout semantics do not reach the required strict parity gate.",
        "path": SLIDE_STRICT_PARITY_PNG,
        "transcript": [
            "最后这一页专门讲最终 blocker，不粉饰。",
            "现在 blocker 不是缺 reference，因为 cloth self-collision reference case 已经明确存在，而且我们就是拿它做的 strict parity。",
            "这里的 strict scope 也收紧得很明确：只覆盖 PhysTwin 原生的 object_collision 加 implicit z=0 ground，不把 box scene 混进去。",
            "真正的问题是：在当前 PhysTwin 到 Newton 的 rollout 语义下，这个 cloth case 连 self-collision off baseline 都远离 PhysTwin，所以 bridge-side phystwin operator 虽然 operator-level exact，整条 rollout 仍然达不到 1e-5 gate。",
        ],
    },
    {
        "kind": "twocol",
        "title": "Robotic With Deformable Objects: Current Defendable Sub-Conclusion",
        "common_settings": "Chapter-5 claim for today: the defendable robot-deformable evidence is a native Franka release/drop baseline with visible support, settle-before-release, gravity-dominated fall, and real ground contact at 1:1 time. This is not yet full manipulation.",
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
    (MEETING_DIR / "gif").mkdir(parents=True, exist_ok=True)
    _ensure_resized_gif(RECALL_ROPE_GIF, PERF_ROPE_CASE_GIF, width=720, fps=8)
    _code_excerpt_image(
        VIEWER_CODE_PATH,
        "rope_benchmark_modes",
        _extract_code_segments(
            VIEWER_CODE_PATH,
            [(185, 193), (202, 208)],
            highlight_lines={185, 191, 202, 206, 207},
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
    _render_perf_attribution_png(PERF_ATTRIBUTION_PNG)
    _render_perf_nsight_png(PERF_NSIGHT_PNG)
    bunny_force_code = ROOT / "Newton" / "phystwin_bridge" / "demos" / "demo_cloth_bunny_drop_without_self_contact.py"
    _code_excerpt_image(
        bunny_force_code,
        "force_diag_capture",
        _extract_code_segments(
            bunny_force_code,
            [(2825, 2830), (3441, 3458)],
            highlight_lines={2830, 3443, 3454, 3455},
        ),
        FORCE_DIAG_CODE_PNG,
    )
    _code_excerpt_image(
        bunny_force_code,
        "force_diag_layout",
        _extract_code_segments(
            bunny_force_code,
            [(1583, 1598), (1600, 1614)],
            highlight_lines={1583, 1595, 1602, 1611},
        ),
        FORCE_LAYOUT_CODE_PNG,
    )
    for name, src in ACCEPTED_PHENO_MP4.items():
        _ensure_gif(src, ACCEPTED_PHENO_GIF[name], width=640, fps=8, max_colors=96)
    for name, src in ACCEPTED_FORCE_MP4.items():
        _ensure_gif(src, ACCEPTED_FORCE_GIF[name], width=640, fps=8, max_colors=96)
    if CURRENT_BUNNY_BOARD_MP4.exists():
        _ensure_gif(CURRENT_BUNNY_BOARD_MP4, CURRENT_BUNNY_BOARD_GIF, width=960, fps=8, max_colors=128)
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
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
        ]
        if bold
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        ]
    )
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def _render_code_png(out_path: Path, header: str, lines: list[str], font_size: int = 18, max_chars: int = 86) -> Path:
    mx, my = 28, 22
    font = _load_mono_font(font_size)
    font_bold = _load_mono_font(font_size, bold=True)
    bg, panel = (246, 248, 251), (255, 255, 255)
    txt_c, hdr_c = (34, 34, 34), (48, 87, 138)
    gutter_c = (120, 128, 138)
    line_hl_fill = (255, 219, 77, 92)
    token_colors = {
        Comment: txt_c,
        Keyword: txt_c,
        Keyword.Constant: txt_c,
        Name.Builtin: txt_c,
        Name.Function: txt_c,
        Name.Class: txt_c,
        String: txt_c,
        Number: txt_c,
        Operator: txt_c,
        Punctuation: txt_c,
        Token.Error: (176, 32, 32),
        Text: txt_c,
    }

    all_lines = [header, ""] + [ln[:max_chars] for ln in lines]
    probe = Image.new("RGB", (100, 100))
    d = ImageDraw.Draw(probe)
    bbox = d.textbbox((0, 0), "M", font=font)
    cw = max(8, bbox[2] - bbox[0])
    lh = max(14, bbox[3] - bbox[1] + 4)
    width = min(max(mx * 2 + max_chars * cw, 980), 1500)
    height = min(max(my * 2 + len(all_lines) * lh, 340), 980)
    img = Image.new("RGBA", (width, height), bg + (255,))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle(
        [8, 8, width - 8, height - 8],
        radius=14,
        fill=panel + (255,),
        outline=(204, 212, 220, 255),
        width=2,
    )

    def _color_for_token(tok):
        for ttype, color in token_colors.items():
            if tok in ttype:
                return color
        return txt_c

    lexer = PythonLexer(stripnl=False)
    y = my + 4
    for row_idx, raw_line in enumerate(all_lines):
        if row_idx == 0:
            draw.text((mx, y), raw_line, font=font_bold, fill=hdr_c)
            y += lh
            continue
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

        x = mx
        x_code_start = x
        if line_no:
            draw.text((x, y), f"{line_no:>4}", font=font_bold if highlight else font, fill=gutter_c)
            x += int(cw * 6.2)
            x_code_start = x

        rendered = []
        x_probe = x
        for tok, value in lex(code, lexer):
            clean = value.replace("\n", "")
            if not clean:
                continue
            rendered.append((clean, _color_for_token(tok)))
            x_probe += int(draw.textlength(clean, font=font))

        if highlight and x_probe > x_code_start:
            stroke_y = y + int(lh * 0.62)
            draw.line([(x_code_start - 2, stroke_y), (x_probe + 4, stroke_y)], fill=line_hl_fill, width=10)

        for clean, color in rendered:
            draw.text((x, y), clean, font=font, fill=color)
            x += int(draw.textlength(clean, font=font))
        y += lh

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
    header = f"# {rel_path}"
    return _render_code_png(out_path, header, lines)


def _ensure_gif(mp4_path: Path, gif_path: Path, *, width: int = 640, fps: int = 8, max_colors: int = 96) -> Path:
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    if gif_path.exists() and gif_path.stat().st_mtime >= mp4_path.stat().st_mtime:
        return gif_path
    script = ROOT / "scripts" / "render_gif.sh"
    subprocess.run(
        [
            str(script),
            str(mp4_path),
            str(gif_path),
            str(width),
            str(fps),
            str(max_colors),
        ],
        check=True,
    )
    return gif_path


def _ensure_resized_gif(src_path: Path, out_path: Path, *, width: int = 720, fps: int = 8) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_mtime >= src_path.stat().st_mtime:
        return out_path
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src_path),
            "-vf",
            f"fps={fps},scale={width}:-1:flags=lanczos",
            str(out_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return out_path


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
            font_size=12,
            bold=False,
        )
    label_positions = [
        (REF_GRID_TL_LABEL_LEFT, REF_GRID_TOP_LABEL_TOP),
        (REF_GRID_TR_LABEL_LEFT, REF_GRID_TOP_LABEL_TOP),
        (REF_GRID_TL_LABEL_LEFT, REF_GRID_BOT_LABEL_TOP),
        (REF_GRID_TR_LABEL_LEFT, REF_GRID_BOT_LABEL_TOP),
    ]
    pic_positions = [
        (REF_GRID_TL_PIC_LEFT, REF_GRID_TOP_PIC_TOP),
        (REF_GRID_TR_PIC_LEFT, REF_GRID_TOP_PIC_TOP),
        (REF_GRID_TL_PIC_LEFT, REF_GRID_BOT_PIC_TOP),
        (REF_GRID_TR_PIC_LEFT, REF_GRID_BOT_PIC_TOP),
    ]
    for idx, (label, path) in enumerate(items[:4]):
        lx, ly = label_positions[idx]
        px, py = pic_positions[idx]
        _add_label(slide, lx, ly, REF_GRID_LABEL_W, REF_GRID_LABEL_H, label, font_size=11, bold=False)
        _add_pic(slide, path, px, py, REF_GRID_PIC_W, REF_GRID_PIC_H)


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
            font_size=12,
            bold=False,
        )
    _add_label(
        slide,
        REF_GRID_TL_LABEL_LEFT,
        REF_GRID_TOP_LABEL_TOP,
        REF_GRID_LABEL_W,
        REF_GRID_LABEL_H,
        left_label,
        font_size=11,
        bold=False,
    )
    _add_pic(
        slide,
        left_path,
        REF_GRID_TL_PIC_LEFT,
        REF_GRID_TOP_PIC_TOP,
        REF_GRID_PIC_W,
        REF_GRID_PIC_H,
    )
    _add_label(
        slide,
        REF_GRID_TR_LABEL_LEFT,
        REF_GRID_TOP_LABEL_TOP,
        REF_GRID_LABEL_W,
        REF_GRID_LABEL_H,
        right_label,
        font_size=11,
        bold=False,
    )
    _add_pic(
        slide,
        right_path,
        REF_GRID_TR_PIC_LEFT,
        REF_GRID_TOP_PIC_TOP,
        REF_GRID_PIC_W,
        REF_GRID_PIC_H,
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
    _set_title_textbox(title_box, title, size_pt=26)
    if note:
        _add_label(
            slide,
            REF_GRID_COMMON_LEFT,
            REF_GRID_COMMON_TOP,
            REF_GRID_COMMON_W,
            REF_GRID_COMMON_H,
            note,
            font_size=11,
            bold=False,
        )
    left_x = 520000
    right_x = 4760000
    label_y = 1580000
    pic_y = 1860000
    pic_w = 3520000
    pic_h = 2480000
    _add_label(slide, left_x, label_y, pic_w, 220000, left_label, font_size=10, bold=False)
    _add_pic(slide, left_path, left_x, pic_y, pic_w, pic_h)
    _add_label(slide, right_x, label_y, pic_w, 220000, right_label, font_size=10, bold=False)
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
            _gif_twocol(
                prs,
                slide["title"],
                slide["left_label"],
                slide["left_path"],
                slide["right_label"],
                slide["right_path"],
                common_settings=slide.get("common_settings"),
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

    print(f"PPTX: {out_pptx}")
    print(f"Transcript MD: {transcript_md}")
    print(f"Transcript PDF: {transcript_pdf}")
    print(f"Slides: {len(prs.slides)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
