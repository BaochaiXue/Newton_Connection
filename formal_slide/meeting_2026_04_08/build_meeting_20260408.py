#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pptx import Presentation

MEETING_DIR = Path(__file__).resolve().parent
ROOT = MEETING_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from formal_slide.meeting_2026_04_01 import build_meeting_20260401 as shared

TEMPLATE_PPTX = ROOT / "formal_slide" / "meeting_2026_04_01" / "templates" / "My Adjust.pptx"
OUT_PPTX = MEETING_DIR / "bridge_meeting_20260408_recall_initial.pptx"
DECK_GIF_DIR = MEETING_DIR / "gif"
IMAGE_DIR = MEETING_DIR / "images"
DEFAULT_MAX_PPTX_MB = 100.0
DEFAULT_MAX_GIF_MB = 40.0

STABLE_MATRIX_ROOT = (
    ROOT
    / "Newton"
    / "phystwin_bridge"
    / "results"
    / "ground_contact_self_collision_repro_fix_20260404_200830_aa5e607"
    / "per_run"
    / "run_01"
    / "matrix"
)
STABLE_FOLLOWUP_ROOT = (
    ROOT
    / "Newton"
    / "phystwin_bridge"
    / "results"
    / "self_collision_transfer_case3_vs_case4_followup_20260404_210334_ac9ec33"
)
SELF_COLLISION_BOARD_PNG = IMAGE_DIR / "self_collision_stable_mechanism_board.png"
CODE_GROUND_NATIVE_PNG = IMAGE_DIR / "code_ground_native_order.png"
CODE_GROUND_PHYSTWIN_PNG = IMAGE_DIR / "code_ground_phystwin_order.png"
CODE_CONTROLLER_PHYSTWIN_PNG = IMAGE_DIR / "code_controller_phystwin.png"
CODE_CONTROLLER_BRIDGE_PNG = IMAGE_DIR / "code_controller_bridge.png"


def _require_promoted_root(task_slug: str) -> Path:
    root = shared._meta_local_root(task_slug)
    if root is None or not root.exists():
        raise FileNotFoundError(f"Missing promoted local artifact root for task `{task_slug}`.")
    return root.resolve()


def _extract_number_from_markdown(path: Path, label: str) -> float:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"{re.escape(label)}:\s+`([^`]+)`", text)
    if not match:
        raise ValueError(f"Could not find `{label}` in {path}")
    return float(match.group(1))


ROBOT_ONEWAY_ROOT = _require_promoted_root("robot_rope_franka_semiimplicit_oneway")
ROBOT_TOOL_ROOT = _require_promoted_root("robot_visible_rigid_tool_baseline")
ROBOT_ONEWAY_EXPORT_ROOT = MEETING_DIR / "robot_direct_finger_three_views"
ROBOT_TOOL_EXPORT_ROOT = MEETING_DIR / "robot_visible_tool_three_views"

ROBOT_ONEWAY_SUMMARY = json.loads((ROBOT_ONEWAY_ROOT / "summary.json").read_text(encoding="utf-8"))
ROBOT_TOOL_SUMMARY = json.loads((ROBOT_TOOL_ROOT / "summary.json").read_text(encoding="utf-8"))
ROBOT_ONEWAY_MULTIMODAL_REVIEW = ROBOT_ONEWAY_ROOT / "multimodal_review.md"
ROBOT_TOOL_CONTACT_ONSET = json.loads((ROBOT_TOOL_ROOT / "tool_contact_onset_report.json").read_text(encoding="utf-8"))

ROBOT_ONEWAY_DEFORMATION_TIME_S = _extract_number_from_markdown(ROBOT_ONEWAY_MULTIMODAL_REVIEW, "rope deformation time")
ROBOT_ONEWAY_LATERAL_TIME_S = _extract_number_from_markdown(ROBOT_ONEWAY_MULTIMODAL_REVIEW, "rope lateral motion time")
ROBOT_TOOL_DEFORMATION_TIME_S = float(ROBOT_TOOL_CONTACT_ONSET["first_rope_deformation_time_s"])
ROBOT_TOOL_LATERAL_TIME_S = float(ROBOT_TOOL_CONTACT_ONSET["first_rope_lateral_motion_time_s"])

ROBOT_ONEWAY_HERO_MP4 = (
    (ROBOT_ONEWAY_EXPORT_ROOT / "hero_presentation.mp4")
    if (ROBOT_ONEWAY_EXPORT_ROOT / "hero_presentation.mp4").exists()
    else (ROBOT_ONEWAY_ROOT / "hero_presentation.mp4")
)
ROBOT_ONEWAY_VALIDATION_MP4 = (
    (ROBOT_ONEWAY_EXPORT_ROOT / "validation_camera.mp4")
    if (ROBOT_ONEWAY_EXPORT_ROOT / "validation_camera.mp4").exists()
    else (ROBOT_ONEWAY_ROOT / "validation_camera.mp4")
)
ROBOT_TOOL_HERO_MP4 = (
    (ROBOT_TOOL_EXPORT_ROOT / "hero_presentation.mp4")
    if (ROBOT_TOOL_EXPORT_ROOT / "hero_presentation.mp4").exists()
    else (ROBOT_TOOL_ROOT / "hero_presentation.mp4")
)
ROBOT_TOOL_VALIDATION_MP4 = (
    (ROBOT_TOOL_EXPORT_ROOT / "validation_camera.mp4")
    if (ROBOT_TOOL_EXPORT_ROOT / "validation_camera.mp4").exists()
    else (ROBOT_TOOL_ROOT / "validation_camera.mp4")
)

ROBOT_ONEWAY_HERO_VALIDATION_GIF = DECK_GIF_DIR / "robot_rope_franka_semiimplicit_oneway_hero_validation_deck.gif"
ROBOT_TOOL_HERO_VALIDATION_GIF = DECK_GIF_DIR / "robot_visible_rigid_tool_baseline_hero_validation_deck.gif"

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
RECALL_ROPE_WEIGHT_1KG_GIF = DECK_GIF_DIR / "rope_bunny_total1kg_m5_v1.gif"
RECALL_ROPE_WEIGHT_5KG_GIF = DECK_GIF_DIR / "rope_bunny_total5kg_m5_v1.gif"
RECALL_BUNNY_SUPPORT_GIF = DECK_GIF_DIR / "cloth_rigid_compare_bunny_m5_v1.gif"
RECALL_BOX_SUPPORT_GIF = DECK_GIF_DIR / "cloth_rigid_compare_box_m5_v1.gif"
RECALL_THIN_EAR_5X_GIF = DECK_GIF_DIR / "thin_ear_ccd5x_v3.gif"
RECALL_THIN_EAR_10X_GIF = DECK_GIF_DIR / "thin_ear_ccd10x_v3.gif"

RECALL_DIRECT_GIF_SPECS = [
    (shared.RECALL_CLOTH_GIF_SRC, RECALL_CLOTH_GIF, 800, 6, 80),
    (shared.RECALL_ZEBRA_GIF_SRC, RECALL_ZEBRA_GIF, 800, 6, 80),
    (shared.RECALL_SLOTH_GIF_SRC, RECALL_SLOTH_GIF, 800, 6, 80),
    (shared.RECALL_ROPE_GIF_SRC, RECALL_ROPE_GIF, 800, 6, 80),
    (shared.RECALL_CLOTH_OVERLAY_GIF_SRC, RECALL_CLOTH_OVERLAY_GIF, 800, 6, 80),
    (shared.RECALL_ZEBRA_OVERLAY_GIF_SRC, RECALL_ZEBRA_OVERLAY_GIF, 800, 6, 80),
    (shared.RECALL_SLOTH_OVERLAY_GIF_SRC, RECALL_SLOTH_OVERLAY_GIF, 800, 6, 80),
    (shared.RECALL_ROPE_OVERLAY_GIF_SRC, RECALL_ROPE_OVERLAY_GIF, 800, 6, 80),
    (shared.RECALL_BUNNY_M5_GIF_SRC, RECALL_BUNNY_M5_GIF, 800, 8, 96),
    (shared.RECALL_BUNNY_M500_GIF_SRC, RECALL_BUNNY_M500_GIF, 800, 8, 96),
    (shared.RECALL_ROPE_WEIGHT_1KG_GIF, RECALL_ROPE_WEIGHT_1KG_GIF, 800, 8, 96),
    (shared.RECALL_ROPE_WEIGHT_5KG_GIF, RECALL_ROPE_WEIGHT_5KG_GIF, 800, 8, 96),
    (shared.RECALL_BUNNY_SUPPORT_GIF, RECALL_BUNNY_SUPPORT_GIF, 800, 8, 96),
    (shared.RECALL_BOX_SUPPORT_GIF, RECALL_BOX_SUPPORT_GIF, 800, 8, 96),
    (shared.RECALL_THIN_EAR_5X_GIF, RECALL_THIN_EAR_5X_GIF, 800, 8, 96),
    (shared.RECALL_THIN_EAR_10X_GIF, RECALL_THIN_EAR_10X_GIF, 800, 8, 96),
]


RECALL_SLIDES: list[dict] = [
    {
        "kind": "title",
        "title": "PhysTwin -> Newton Bridge",
        "subtitle": [
            "April 8 update",
            "Recall -> Stable self-collision diagnosis -> Conservative robot baseline",
            "Goal: one clear claim per slide; no overclaim",
        ],
        "transcript": [
            "这一页是 opening slide。",
            "我会把这次 meeting 强行压成三段：recall，stable self-collision diagnosis，和 conservative robot baseline。",
            "这样做的目的是避免所有结果混在一起，导致听众既抓不到当前最强结论，也分不清哪些事情仍然没有做到。",
        ],
    },
    {
        "kind": "body",
        "title": "Agenda: Keep Four Claims Separate",
        "bullets": [
            "Bridge baseline already exists.",
            "Self-collision issue is now a stable mechanism question.",
            "Robot result is a conservative SemiImplicit one-way baseline.",
            "Out of scope today: physical blocking, full two-way coupling, self-collision parity.",
        ],
        "transcript": [
            "这一页是全场最重要的 scope slide。",
            "我先把四件事拆开：第一，bridge baseline 已经存在；第二，self-collision 现在是 mechanism question；第三，robot 结果现在只讲 conservative one-way baseline；第四，physical blocking、full two-way coupling 和 self-collision parity 今天都不 claim。",
            "如果这一页不先说清楚，后面所有 visual 都会被误读得更强。",
        ],
    },
    {
        "kind": "grid",
        "title": "Recall: The Bridge Baseline Already Exists",
        "common_settings": "These four imports were already established before this week's narrower questions.",
        "items": [
            ("Cloth baseline", RECALL_CLOTH_GIF),
            ("Zebra baseline", RECALL_ZEBRA_GIF),
            ("Sloth baseline", RECALL_SLOTH_GIF),
            ("Rope baseline", RECALL_ROPE_GIF),
        ],
        "transcript": [
            "这一页只做一件事：提醒听众 bridge baseline 不是本周才第一次成立。",
            "cloth、zebra、sloth、rope 这四个 import 都已经是 earlier meeting 的 established baseline。",
            "所以从这里开始，我们讨论的不是『能不能 import deformable』，而是 import 之后剩下哪些 narrower failure modes。",
        ],
    },
    {
        "kind": "twocol",
        "title": "Recall: The Remaining Issue Is Contact Behavior, Not Import",
        "common_settings": "Same cloth scene. Geometry-sensitive support behavior remained the harder part.",
        "left_label": "Same cloth + bunny support",
        "left_path": RECALL_BUNNY_SUPPORT_GIF,
        "right_label": "Same cloth + thick-box support",
        "right_path": RECALL_BOX_SUPPORT_GIF,
        "transcript": [
            "同样是 rigid support，换成 thick box 以后现象就明显更稳定，所以问题不是 bridge 连 contact baseline 都没有。",
            "这个对比把问题收窄到 geometry-sensitive contact behavior。",
            "所以 recall 的作用已经够了：后面不再需要继续证明 import，而是直接进入本周的 narrowed diagnosis。",
        ],
    },
]

SELF_COLLISION_SLIDES: list[dict] = [
    {
        "kind": "image",
        "title": "Self-Collision: The Case-3-Over-Case-4 Ranking Is Now Stable",
        "path": SELF_COLLISION_BOARD_PNG,
        "note": (
            "Top-left: stable 2x2 matrix. Top-right: per-frame RMSE. Bottom: mechanism evidence around frames 40 / 107 / 137."
        ),
        "transcript": [
            "这一页是本周 self-collision 章节的核心证据页。",
            "左上角是稳定的 `2 x 2` matrix，最优 full-rollout 组合仍然是 case 3，也就是 PhysTwin-style self-collision 加 native Newton ground-contact。",
            "右上角是 case 3 和 case 4 的 per-frame RMSE 曲线。这里最关键的不是谁最后均值更小，而是 case 4 在 early rollout 其实更好，它是在 frame 40 首次翻符号、并在 frame 107 开始进入持续更差区间。",
            "下排把机制证据压在一张图里：左边是 frame 40、107、137 的 active ground particle 对比，右边是 self-contact active nodes 加 controller mismatch reminder。",
            "所以这页只想传达一句话：case 4 不是因为 local self-collision law 错了才输，而是因为 fully PhysTwin-style branch 暴露了 bridge 里剩余的 whole-step mismatch。",
        ],
    },
    {
        "kind": "code_twocol_large",
        "title": "Self-Collision: Native Newton Ground And PhysTwin-Style Ground Are Different Update Laws",
        "left_label": "Native Newton ground-contact\ncontact force then integrate",
        "left_path": CODE_GROUND_NATIVE_PNG,
        "right_label": "Bridge PhysTwin-style ground path\nvelocity update -> self-collision -> TOI ground",
        "right_path": CODE_GROUND_PHYSTWIN_PNG,
        "note": "Short reading: native Newton is force-space contact; the PhysTwin-style branch is velocity-level ordering.",
        "transcript": [
            "这一页的目标是把 ground law 的源码差异直接摆出来，而且一眼能看懂。",
            "左边 Newton native path 在 solver 里先累计 contact force，然后再 integrate particles，所以它是 force-space spring-damper contact。",
            "右边 bridge strict PhysTwin-style path则是先 `update_vel_from_force_phystwin`，再做 PhysTwin-style self-collision，最后做 `integrate_ground_collision_phystwin`，也就是 velocity-level TOI update。",
            "所以 case 3 和 case 4 的差异从源码上就不是一个小参数差异，而是整个 update law 不同。",
        ],
    },
    {
        "kind": "code_twocol_large",
        "title": "Self-Collision: Controller Semantics Are Still Not PhysTwin-Native",
        "left_label": "PhysTwin source\nsprings read `control_x / control_v`",
        "left_path": CODE_CONTROLLER_PHYSTWIN_PNG,
        "right_label": "Current bridge rollout\ncontrollers are embedded into `particle_q / particle_qd`",
        "right_path": CODE_CONTROLLER_BRIDGE_PNG,
        "note": "This is the strongest remaining mismatch outside the isolated self-collision operator.",
        "transcript": [
            "这一页讲 current strongest mismatch。",
            "PhysTwin 原版 spring law 会区分 object state 和 controller channel：如果弹簧端点连到 controller，它直接读 `control_x` 和 `control_v`。",
            "但我们当前 bridge rollout 是先把 controller target 写进 `state_in.particle_q` 和 `state_in.particle_qd`，再让 spring path继续往下跑。",
            "这两个 runtime semantics 不同，所以即使 isolated self-collision operator 已经很强，whole-step rollout 里仍然会留下 controller-spring mismatch。",
        ],
    },
    {
        "kind": "body",
        "title": "Self-Collision: What We Can Say Today",
        "bullets": [
            "`case_3 > case_4` is now reproducible.",
            "The blocker is whole-step interaction, not the isolated self-collision operator.",
            "Native ground currently behaves like a stabilizing compensator.",
            "Recommendation stays `C`: keep bridge-side PhysTwin-style self-collision.",
        ],
        "transcript": [
            "这一页只做结论收口。",
            "第一，stable matrix 已经证明 case 3 比 case 4 更好这个排序是真的。",
            "第二，但这个 stable result 不能被误读成 native Newton ground-contact 更 PhysTwin-faithful。我们现在更支持的解释是 native ground 在当前 bridge 里起到了 stabilizing compensation 的作用，而 fully PhysTwin-style pair 暴露了更上层的 mismatch。",
            "第三，所以 recommendation 不变，仍然是 C：bridge-side PhysTwin-style self-collision 还是必要的。",
            "真正没解决掉的，是 rollout-level whole-step interaction，尤其 controller-spring semantics。",
        ],
    },
]

ROBOT_SLIDES: list[dict] = [
    {
        "kind": "body",
        "title": "Robot: This Week's Claim Is Intentionally Narrow",
        "bullets": [
            "Deformable interaction runs under `SolverSemiImplicit`.",
            "Native Franka + native tabletop + bridged rope stay in the scene.",
            "One-way robot -> rope is acceptable.",
            "We do NOT claim physical blocking or full two-way coupling.",
        ],
        "transcript": [
            "进入 robot section 之前，我先把 claim boundary 再说一遍。",
            "这周 robot 结果的目标不是 articulated physical blocking，也不是 full two-way coupling。",
            "我们现在只 claim 一件事：native Franka 在 native tabletop scene 里，通过 `SolverSemiImplicit` 下的 deformable rope interaction，给出一个 truthful one-way robot-to-rope baseline。",
            "这一页是为了避免后面所有 robot visual 被误听成更强的 physics claim。",
        ],
    },
    {
        "kind": "gif_bullets",
        "title": "Robot: Best Meeting Visual Is The Honest Visible-Tool Baseline",
        "gif_label": "Same rollout. Left: hero presentation. Right: validation camera.\nVisible rigid tool is the actual physical contactor.",
        "gif_path": ROBOT_TOOL_HERO_VALIDATION_GIF,
        "note": (
            "Visible short rod = actual physical contactor. Same rollout on both sides."
        ),
        "bullets": [
            "The visible tool is the real contactor.",
            f"Tool contact: `{ROBOT_TOOL_SUMMARY['actual_tool_first_contact_time_s']:.2f} s` -> rope lateral motion: `{ROBOT_TOOL_LATERAL_TIME_S:.2f} s` -> deformation: `{ROBOT_TOOL_DEFORMATION_TIME_S:.2f} s`.",
            "This is the clearest meeting-facing visual because geometry truth is easy to see.",
            "Claim: tool-mediated one-way robot -> rope only.",
        ],
        "transcript": [
            "这一页我先放这周最适合上会的 visual result。",
            "它不是 direct-finger claim，而是更保守、更直观的 visible-tool baseline：native Franka 挂一个可见 short rod，这根 rod 本身就是实际接触体。",
            "这里我把 hero 和 validation 放成同一条 rollout 的双视角，左边更适合 presentation，右边更适合确认 contact story。",
            f"这个结果的好处很直接：tool first contact 是清楚的，`{ROBOT_TOOL_SUMMARY['actual_tool_first_contact_time_s']:.2f}` 秒先接触，rope 的 lateral motion 和 deformation 都更晚，所以不会给人 remote push 的感觉。",
            "所以如果周三现场只需要一条最容易被接受的 robot visual，我会优先停这一页，而且我会明确说它是 tool-mediated one-way baseline，不是更强的 blocking physics claim。",
        ],
    },
    {
        "kind": "gif_bullets",
        "title": "Robot: The Promoted Direct-Finger Result Still Matters",
        "gif_label": "Same rollout. Left: hero presentation. Right: validation camera.\nActual finger-box contact remains the proof surface.",
        "gif_path": ROBOT_ONEWAY_HERO_VALIDATION_GIF,
        "note": (
            "Promoted conservative task: `robot_rope_franka_semiimplicit_oneway`."
        ),
        "bullets": [
            "This is the current conservative direct-finger authority.",
            f"Finger contact: `{ROBOT_ONEWAY_SUMMARY['actual_finger_box_first_contact_time_s']:.2f} s` -> deformation: `{ROBOT_ONEWAY_DEFORMATION_TIME_S:.2f} s` -> lateral motion: `{ROBOT_ONEWAY_LATERAL_TIME_S:.2f} s`.",
            "Proof surface stays actual finger-box contact, not proxy radii.",
            "Claim stays one-way only.",
        ],
        "transcript": [
            "这一页再把 currently promoted 的 direct-finger path 摆出来。",
            "我保留这页的原因不是因为它比 visible-tool 更好看，而是因为它对应的是当前被重新认证过的 conservative authority。",
            f"这里同样是 same-rollout 双视角，而且 proof surface 仍然是 actual finger-box contact。也就是说，`{ROBOT_ONEWAY_SUMMARY['actual_finger_box_first_contact_time_s']:.2f}` 秒才算真正接触，之后 rope deformation 和 lateral motion 才开始。",
            "这页要讲清楚两点：第一，deformable interaction 是 `SolverSemiImplicit`；第二，这不是 full two-way，也不是 physical blocking。",
            "所以周三如果老师追问当前 direct-finger claim 到底站到哪里，这页就是最安全的答案。",
        ],
    },
    {
        "kind": "body",
        "title": "Close: What Is Ready For Wednesday",
        "bullets": [
            "Recall: bridge baseline is not the open question.",
            "Self-collision: stable ranking, mechanism narrowed, recommendation unchanged.",
            "Robot: best meeting visual is the honest visible-tool baseline.",
            "Authority: direct-finger SemiImplicit one-way path is still the promoted conservative result.",
        ],
        "transcript": [
            "最后一页只做收尾，不加新信息。",
            "如果周三只记住四句话，我希望就是这四条：bridge baseline 不是 open question；self-collision 的 stable ranking 已经拿到了；最适合上会的 robot visual 是 honest visible-tool baseline；而 direct-finger 这条 conservative authority 也已经被重新认证。",
            "这样整场汇报的边界就很清楚：我们有真实进展，但没有 overclaim 到 physical blocking 或 full two-way coupling。",
        ],
    },
]

MEETING_SLIDES: list[dict] = RECALL_SLIDES + SELF_COLLISION_SLIDES + ROBOT_SLIDES


def _ensure_hstack_gif(left_src: Path, right_src: Path, out_gif: Path, *, fps: int = 8, height: int = 360, max_colors: int = 128) -> Path:
    out_gif.parent.mkdir(parents=True, exist_ok=True)
    inputs = [left_src, right_src]
    newest_input_mtime = max(path.stat().st_mtime for path in inputs)
    if out_gif.exists() and out_gif.stat().st_mtime >= newest_input_mtime:
        return out_gif

    tmp_gif = out_gif.with_suffix(".tmp.gif")
    filter_complex = (
        f"[0:v]fps={int(fps)},scale=-2:{int(height)}:flags=lanczos[left];"
        f"[1:v]fps={int(fps)},scale=-2:{int(height)}:flags=lanczos[right];"
        "[left][right]hstack=inputs=2,split[s0][s1];"
        f"[s0]palettegen=max_colors={int(max_colors)}:stats_mode=full[p];"
        "[s1][p]paletteuse=dither=sierra2_4a"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(left_src),
            "-i",
            str(right_src),
            "-filter_complex",
            filter_complex,
            "-loop",
            "0",
            str(tmp_gif),
        ],
        check=True,
    )
    tmp_gif.replace(out_gif)
    return out_gif


def _build_self_collision_mechanism_board() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    matrix_summary = json.loads((STABLE_MATRIX_ROOT / "rmse_matrix_summary.json").read_text(encoding="utf-8"))
    followup_summary = json.loads((STABLE_FOLLOWUP_ROOT / "diagnostics_summary.json").read_text(encoding="utf-8"))
    step_diag = json.loads((STABLE_FOLLOWUP_ROOT / "step_diag_stable" / "step_diagnostics.json").read_text(encoding="utf-8"))
    controller_diag = json.loads(
        (STABLE_FOLLOWUP_ROOT / "controller_spring_rerun" / "controller_spring_diagnostic.json").read_text(
            encoding="utf-8"
        )
    )

    row_map = {row["case_label"]: row for row in matrix_summary["rows"]}
    values = np.array(
        [
            [
                float(row_map["case_1_self_off_ground_native"]["rmse_mean"]),
                float(row_map["case_2_self_off_ground_phystwin"]["rmse_mean"]),
            ],
            [
                float(row_map["case_3_self_phystwin_ground_native"]["rmse_mean"]),
                float(row_map["case_4_self_phystwin_ground_phystwin"]["rmse_mean"]),
            ],
        ],
        dtype=np.float64,
    )

    case3_curve = np.load(
        STABLE_MATRIX_ROOT / "case_3_self_phystwin_ground_native" / "case_3_self_phystwin_ground_native.npz"
    )["rmse_per_frame"]
    case4_curve = np.load(
        STABLE_MATRIX_ROOT / "case_4_self_phystwin_ground_phystwin" / "case_4_self_phystwin_ground_phystwin.npz"
    )["rmse_per_frame"]

    records = step_diag["records"]
    target_frames = [40, 107, 137]
    frame_means: dict[int, dict[str, float]] = {}
    for frame in target_frames:
        subset = [r for r in records if int(r["frame"]) == frame]
        frame_means[frame] = {
            "case3_ground_active_particles": float(np.mean([r["case3_ground_active_particles"] for r in subset])),
            "case4_ground_active_particles": float(np.mean([r["case4_ground_active_particles"] for r in subset])),
            "case3_self_active_nodes": float(np.mean([r["case3_self_active_nodes"] for r in subset])),
            "case4_self_active_nodes": float(np.mean([r["case4_self_active_nodes"] for r in subset])),
            "post_step_qd_diff_abs_max": float(np.mean([r["post_step_qd_diff"]["abs_max"] for r in subset])),
        }

    fig = plt.figure(figsize=(16, 9), dpi=220)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.0, 1.3, 1.0], height_ratios=[1.0, 1.0], wspace=0.28, hspace=0.28)
    fig.suptitle(
        "Stable 2x2 Matrix: Case 4 Fails Late, Not Early\n"
        "PhysTwin-style self-collision is still necessary; the remaining gap is whole-step interaction",
        fontsize=20,
        fontweight="bold",
        y=0.98,
    )

    ax_heat = fig.add_subplot(gs[0, 0])
    im = ax_heat.imshow(values, cmap="YlGnBu_r")
    ax_heat.set_xticks([0, 1], ["native ground", "PhysTwin-style ground"])
    ax_heat.set_yticks([0, 1], ["self off", "self PhysTwin-style"])
    ax_heat.set_title("Stable 2x2 rmse_mean", fontsize=15, fontweight="bold")
    for i in range(2):
        for j in range(2):
            val = values[i, j]
            label = f"{val:.6f}"
            extra = ""
            if (i, j) == (1, 0):
                extra = "\nBEST"
            if (i, j) == (1, 1):
                extra = "\nfully PhysTwin-style"
            ax_heat.text(j, i, label + extra, ha="center", va="center", fontsize=12, fontweight="bold")
    plt.colorbar(im, ax=ax_heat, fraction=0.046, pad=0.04)

    ax_curve = fig.add_subplot(gs[0, 1:])
    x = np.arange(len(case3_curve))
    ax_curve.plot(x, case3_curve, label="case 3: self PhysTwin-style + ground native", linewidth=2.4, color="#1f77b4")
    ax_curve.plot(x, case4_curve, label="case 4: self PhysTwin-style + ground PhysTwin-style", linewidth=2.4, color="#d62728")
    ax_curve.axvspan(0, 107, color="#cfe8cf", alpha=0.35, label="case 4 better or mixed early")
    ax_curve.axvspan(107, 180, color="#f7d7d7", alpha=0.4, label="persistent case 4 disadvantage")
    for frame, color in [(40, "#555555"), (107, "#2c7c2c"), (137, "#8b0000")]:
        ax_curve.axvline(frame, color=color, linestyle="--", linewidth=1.6)
    ax_curve.text(40 + 2, max(case4_curve) * 0.88, "first sign flip\nframe 40", color="#555555", fontsize=10)
    ax_curve.text(107 + 2, max(case4_curve) * 0.72, "persistent gap begins\nframe 107", color="#2c7c2c", fontsize=10)
    ax_curve.text(137 + 2, max(case4_curve) * 0.92, "peak delta\nframe 137", color="#8b0000", fontsize=10)
    ax_curve.set_title("Per-frame RMSE against PhysTwin reference", fontsize=15, fontweight="bold")
    ax_curve.set_xlabel("frame")
    ax_curve.set_ylabel("RMSE")
    ax_curve.legend(loc="upper left", fontsize=9)
    ax_curve.grid(alpha=0.25)

    ax_ground = fig.add_subplot(gs[1, 0])
    xx = np.arange(len(target_frames))
    w = 0.36
    ax_ground.bar(xx - w / 2, [frame_means[f]["case3_ground_active_particles"] for f in target_frames], width=w, label="case 3", color="#1f77b4")
    ax_ground.bar(xx + w / 2, [frame_means[f]["case4_ground_active_particles"] for f in target_frames], width=w, label="case 4", color="#d62728")
    ax_ground.set_xticks(xx, [str(f) for f in target_frames])
    ax_ground.set_title("Mean active ground particles\n(native ground persists longer)", fontsize=14, fontweight="bold")
    ax_ground.set_xlabel("frame")
    ax_ground.set_ylabel("active ground particles")
    ax_ground.legend(fontsize=9)
    ax_ground.grid(axis="y", alpha=0.25)

    ax_self = fig.add_subplot(gs[1, 1])
    ax_self.bar(xx - w / 2, [frame_means[f]["case3_self_active_nodes"] for f in target_frames], width=w, label="case 3", color="#1f77b4")
    ax_self.bar(xx + w / 2, [frame_means[f]["case4_self_active_nodes"] for f in target_frames], width=w, label="case 4", color="#d62728")
    ax_self.set_xticks(xx, [str(f) for f in target_frames])
    ax_self.set_title("Mean self-contact active nodes\n(similar by the peak-error window)", fontsize=14, fontweight="bold")
    ax_self.set_xlabel("frame")
    ax_self.set_ylabel("active self-contact nodes")
    ax_self.legend(fontsize=9)
    ax_self.grid(axis="y", alpha=0.25)

    ax_txt = fig.add_subplot(gs[1, 2])
    ax_txt.axis("off")
    explanation_lines = [
        "Stable reading",
        "",
        f"- first positive frame: {followup_summary['first_divergence']['first_positive_frame']}",
        f"- first persistent positive frame: {followup_summary['first_divergence']['first_persistent_positive_frame']}",
        "",
        "Why case 3 still wins",
        "- case 4 is better early, so the local PhysTwin-style operator is not the problem",
        "- case 3 keeps a much larger native-ground contact response through the mid-rollout transition",
        "- by the peak-error window, both branches have zero active ground nodes and similar self-contact activity",
        "- the remaining gap is carried rollout history",
        "",
        "Controller mismatch remains large",
        f"- one-step force_abs_max = {controller_diag['one_step']['force_abs_max']:.4g}",
        f"- short-rollout force_abs_max = {controller_diag['short_rollout']['force_abs_max']:.4g}",
        "",
        "Recommendation",
        "- C: bridge-side PhysTwin-style self-collision is still necessary",
        "- remaining blocker is whole-step interaction, not isolated self-collision law",
    ]
    ax_txt.text(0.0, 1.0, "\n".join(explanation_lines), va="top", ha="left", fontsize=11.2)

    fig.text(
        0.015,
        0.01,
        "Evidence roots: ground_contact_self_collision_repro_fix_20260404_200830_aa5e607 "
        "| self_collision_transfer_case3_vs_case4_followup_20260404_210334_ac9ec33",
        fontsize=9,
        color="#444444",
    )
    fig.savefig(SELF_COLLISION_BOARD_PNG, bbox_inches="tight")
    plt.close(fig)


def _build_self_collision_code_assets() -> None:
    newton_solver = ROOT / "Newton" / "newton" / "newton" / "_src" / "solvers" / "semi_implicit" / "solver_semi_implicit.py"
    bridge_stack = ROOT / "Newton" / "phystwin_bridge" / "tools" / "core" / "phystwin_contact_stack.py"
    phystwin_warp = ROOT / "PhysTwin" / "qqtt" / "model" / "diff_simulator" / "spring_mass_warp.py"
    bridge_import = ROOT / "Newton" / "phystwin_bridge" / "tools" / "core" / "newton_import_ir.py"

    shared._code_excerpt_image(
        newton_solver,
        "newton_native_ground_order",
        shared._extract_code_segments(
            newton_solver,
            [(160, 177)],
            highlight_lines={161, 168, 173, 177},
        ),
        CODE_GROUND_NATIVE_PNG,
    )
    shared._code_excerpt_image(
        bridge_stack,
        "bridge_phystwin_ground_order",
        shared._extract_code_segments(
            bridge_stack,
            [(452, 462), (467, 471), (507, 510)],
            highlight_lines={453, 461, 467, 471, 507},
        ),
        CODE_GROUND_PHYSTWIN_PNG,
    )
    shared._code_excerpt_image(
        phystwin_warp,
        "phystwin_controller_channel",
        shared._extract_code_segments(
            phystwin_warp,
            [(84, 86), (100, 111)],
            highlight_lines={84, 85, 103, 104, 110},
        ),
        CODE_CONTROLLER_PHYSTWIN_PNG,
    )
    shared._code_excerpt_image(
        bridge_import,
        "bridge_controller_embedding",
        shared._extract_code_segments(
            bridge_import,
            [(1714, 1730)],
            highlight_lines={1714, 1715, 1716, 1726, 1727},
        ),
        CODE_CONTROLLER_BRIDGE_PNG,
    )


def _prepare_generated_assets() -> None:
    DECK_GIF_DIR.mkdir(parents=True, exist_ok=True)
    _build_self_collision_mechanism_board()
    _build_self_collision_code_assets()
    _ensure_hstack_gif(ROBOT_TOOL_HERO_MP4, ROBOT_TOOL_VALIDATION_MP4, ROBOT_TOOL_HERO_VALIDATION_GIF)
    _ensure_hstack_gif(ROBOT_ONEWAY_HERO_MP4, ROBOT_ONEWAY_VALIDATION_MP4, ROBOT_ONEWAY_HERO_VALIDATION_GIF)
    for src, out, width, fps, max_colors in RECALL_DIRECT_GIF_SPECS:
        shared._ensure_resized_gif(src, out, width=width, fps=fps, max_colors=max_colors)


def _build_transcript_md(slides: list[dict] | None = None) -> str:
    lines = [
        "# Meeting Transcript — PhysTwin -> Newton Bridge",
        "",
        "语言：中文主讲 + English terminology  ",
        "形式：opening + recall + self-collision update + robot baseline  ",
        "结构：1. opening  2. recall  3. stable self-collision diagnosis  4. conservative robot SemiImplicit baseline  ",
        "目标：给 `2026-04-08` meeting 保留 recall baseline，并补上本周最稳妥的 robot visual result。  ",
        "",
        "---",
        "",
    ]
    active_slides = slides or list(MEETING_SLIDES)
    for idx, slide in enumerate(active_slides, start=1):
        lines.append(f"## Slide {idx} — {slide['title']}")
        for paragraph in slide["transcript"]:
            lines.append(paragraph)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _parse_slide_range(spec: str | None) -> list[dict]:
    if not spec:
        return list(MEETING_SLIDES)
    match = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", spec)
    if not match:
        raise ValueError(f"Unsupported --slide-range format: {spec!r}. Expected START-END.")
    start = int(match.group(1))
    end = int(match.group(2))
    if start < 1 or end < start or end > len(MEETING_SLIDES):
        raise ValueError(f"Slide range {spec!r} is out of bounds for a {len(MEETING_SLIDES)}-slide deck.")
    return list(MEETING_SLIDES[start - 1 : end])


def build_meeting_deck(prs: Presentation, slides: list[dict] | None = None) -> None:
    shared._delete_all_slides(prs)
    active_slides = slides or list(MEETING_SLIDES)
    for slide in active_slides:
        kind = slide["kind"]
        if kind == "title":
            shared._title_slide(prs, slide["title"], slide["subtitle"])
        elif kind == "grid":
            shared._gif_grid_2x2(
                prs,
                slide["title"],
                slide["items"],
                common_settings=slide.get("common_settings"),
            )
        elif kind == "twocol":
            shared._gif_twocol(
                prs,
                slide["title"],
                slide["left_label"],
                slide["left_path"],
                slide["right_label"],
                slide["right_path"],
                common_settings=slide.get("common_settings"),
            )
        elif kind == "code_twocol_large":
            shared._code_twocol_large(
                prs,
                slide["title"],
                slide["left_label"],
                slide["left_path"],
                slide["right_label"],
                slide["right_path"],
                note=slide.get("note"),
            )
        elif kind == "image":
            shared._image_slide(
                prs,
                slide["title"],
                slide["path"],
                note=slide.get("note"),
            )
        elif kind == "gif_bullets":
            shared._perf_gif_bullets(
                prs,
                slide["title"],
                slide["gif_label"],
                slide["gif_path"],
                slide["bullets"],
                note=slide.get("note"),
            )
        elif kind == "body":
            shared._body(prs, slide["title"], slide["bullets"])
        else:
            raise ValueError(f"Unsupported slide kind for 2026-04-08 meeting bundle: {kind}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the 2026-04-08 meeting bundle.")
    parser.add_argument("--out-dir", type=Path, default=MEETING_DIR)
    parser.add_argument("--out-pptx", type=Path, default=None)
    parser.add_argument("--slide-range", type=str, default=None)
    parser.add_argument("--max-pptx-mb", type=float, default=DEFAULT_MAX_PPTX_MB)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    _prepare_generated_assets()
    active_slides = _parse_slide_range(args.slide_range)

    if not TEMPLATE_PPTX.exists():
        raise FileNotFoundError(f"Missing shared template: {TEMPLATE_PPTX}")

    prs = Presentation(str(TEMPLATE_PPTX))
    build_meeting_deck(prs, slides=active_slides)
    out_pptx = args.out_pptx.resolve() if args.out_pptx else (out_dir / OUT_PPTX.name)
    out_pptx.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_pptx))
    shared._validate_pptx_size(out_pptx, max_pptx_mb=args.max_pptx_mb)

    transcript_text = _build_transcript_md(active_slides)
    transcript_md = out_dir / "transcript.md"
    transcript_md.write_text(transcript_text, encoding="utf-8")
    transcript_html = out_dir / "transcript.html"
    transcript_pdf = out_dir / "transcript.pdf"
    shared._markdown_to_pdf(transcript_text, transcript_html, transcript_pdf)

    print(f"PPTX: {out_pptx}")
    print(f"Transcript MD: {transcript_md}")
    print(f"Transcript PDF: {transcript_pdf}")
    print(f"Slides: {len(active_slides)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
