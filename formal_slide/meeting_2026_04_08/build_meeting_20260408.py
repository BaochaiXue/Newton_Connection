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

ROBOT_ONEWAY_SUMMARY = json.loads((ROBOT_ONEWAY_ROOT / "summary.json").read_text(encoding="utf-8"))
ROBOT_TOOL_SUMMARY = json.loads((ROBOT_TOOL_ROOT / "summary.json").read_text(encoding="utf-8"))
ROBOT_ONEWAY_MULTIMODAL_REVIEW = ROBOT_ONEWAY_ROOT / "multimodal_review.md"
ROBOT_TOOL_CONTACT_ONSET = json.loads((ROBOT_TOOL_ROOT / "tool_contact_onset_report.json").read_text(encoding="utf-8"))

ROBOT_ONEWAY_DEFORMATION_TIME_S = _extract_number_from_markdown(ROBOT_ONEWAY_MULTIMODAL_REVIEW, "rope deformation time")
ROBOT_ONEWAY_LATERAL_TIME_S = _extract_number_from_markdown(ROBOT_ONEWAY_MULTIMODAL_REVIEW, "rope lateral motion time")
ROBOT_TOOL_DEFORMATION_TIME_S = float(ROBOT_TOOL_CONTACT_ONSET["first_rope_deformation_time_s"])
ROBOT_TOOL_LATERAL_TIME_S = float(ROBOT_TOOL_CONTACT_ONSET["first_rope_lateral_motion_time_s"])

ROBOT_ONEWAY_HERO_MP4 = ROBOT_ONEWAY_ROOT / "hero_presentation.mp4"
ROBOT_ONEWAY_VALIDATION_MP4 = ROBOT_ONEWAY_ROOT / "validation_camera.mp4"
ROBOT_TOOL_HERO_MP4 = ROBOT_TOOL_ROOT / "hero_presentation.mp4"
ROBOT_TOOL_VALIDATION_MP4 = ROBOT_TOOL_ROOT / "validation_camera.mp4"

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
        "title": "Xinjie Zhang",
        "subtitle": [
            "April 8 meeting opening.",
            "Working deck: recall + stable self-collision + robot SemiImplicit baseline.",
            "Goal: preserve conservative claims while showing the cleanest current robot->rope visual result.",
        ],
        "transcript": [
            "这一页是 `2026-04-08` meeting 的 opening page。",
            "当前 bundle 不再只是 recall scaffold。",
            "这次 opening 要把三件事一次说清楚：baseline recall、stable self-collision diagnosis、以及这周最值得拿上会的 robot SemiImplicit visual result。",
            "所以我的 opening 目标不是 overclaim，而是把已经成立的部分和还没有成立的部分彻底分开。",
        ],
    },
    {
        "kind": "grid",
        "title": "Recall R1: The Bridge Baseline Was Already Established",
        "common_settings": "Recall only. These baseline bridge cases were already established before the new weekly discussion.",
        "items": [
            ("Cloth baseline already worked", RECALL_CLOTH_GIF),
            ("Zebra baseline already worked", RECALL_ZEBRA_GIF),
            ("Sloth baseline already worked", RECALL_SLOTH_GIF),
            ("Rope baseline already worked", RECALL_ROPE_GIF),
        ],
        "transcript": [
            "第一页 recall 只做 baseline reminder。",
            "cloth、zebra、sloth、rope 这四条 bridge baseline 不是这周才第一次成立，它们已经是之前 meeting 里站住的内容。",
            "所以这一页的作用不是重新证明 bridge 能 import，而是提醒听众：后面的新问题建立在一个已经存在的 baseline 上。",
        ],
    },
    {
        "kind": "grid",
        "title": "Recall R2: The Baseline Already Matched The Reference Motion",
        "common_settings": "Recall only. Motion-overlay comparison was already available for the established baseline cases.",
        "items": [
            ("Cloth overlay recall", RECALL_CLOTH_OVERLAY_GIF),
            ("Zebra overlay recall", RECALL_ZEBRA_OVERLAY_GIF),
            ("Sloth overlay recall", RECALL_SLOTH_OVERLAY_GIF),
            ("Rope overlay recall", RECALL_ROPE_OVERLAY_GIF),
        ],
        "transcript": [
            "第二页 recall 继续只做 visual reminder。",
            "之前不只是说 bridge case 看起来差不多，而是已经有 direct motion overlay 去对照 reference 和 Newton。",
            "这意味着当前讨论的起点不是『baseline 还没对齐』，而是 baseline 对齐之后还剩下哪些更窄的问题。",
        ],
    },
    {
        "kind": "twocol",
        "title": "Recall R3: Deformable-Rigid Interaction Already Existed",
        "common_settings": "Recall only. Rigid interaction was already visible before the new weekly question narrowed to failure mode and geometry.",
        "left_label": "Rope + bunny recall\nbunny mass = 5 kg",
        "left_path": RECALL_BUNNY_M5_GIF,
        "right_label": "Rope + bunny recall\nbunny mass = 500 kg",
        "right_path": RECALL_BUNNY_M500_GIF,
        "transcript": [
            "这一页回忆的是 interaction 本身已经存在。",
            "也就是说，deformable-rigid 不是这周才第一次出现的效果；之前 rope 和 bunny 的 interaction 就已经是可见的。",
            "所以后面如果继续讨论 bunny 或别的 rigid target，问题不应该再退回成『到底有没有 interaction』，而应该继续讲 interaction 之后暴露出来的 failure mode。",
        ],
    },
    {
        "kind": "twocol",
        "title": "Recall R4: Bunny Was Harder Than Thick Box",
        "common_settings": "Recall only. The support/contact problem was geometry-dependent rather than a missing bridge baseline.",
        "left_label": "Same cloth + bunny support",
        "left_path": RECALL_BUNNY_SUPPORT_GIF,
        "right_label": "Same cloth + thick-box support",
        "right_path": RECALL_BOX_SUPPORT_GIF,
        "transcript": [
            "这一页 recall 的 point 很直接。",
            "同样是 rigid support，换成 thick box 以后现象就明显更稳定，所以问题不是 bridge 连 contact baseline 都没有。",
            "这个对比把问题收窄到 geometry-sensitive support behavior，而不是把所有 rigid interaction 都打成失败。",
        ],
    },
    {
        "kind": "twocol",
        "title": "Recall R5: Weight Change Did Not Remove Interaction",
        "common_settings": "Recall only. Changing total rope weight changed behavior, but it did not erase deformable-rigid interaction itself.",
        "left_label": "Rope total mass = 1 kg",
        "left_path": RECALL_ROPE_WEIGHT_1KG_GIF,
        "right_label": "Rope total mass = 5 kg",
        "right_path": RECALL_ROPE_WEIGHT_5KG_GIF,
        "transcript": [
            "这一页 recall weight compare。",
            "它的作用不是重新讲参数调优，而是提醒听众：weight 改了以后，interaction 仍然存在。",
            "所以后面的 failure analysis 不能被讲成『只要 weight 一变，interaction 就没了』，更准确的是 behavior 变了，但 interaction baseline 没被抹掉。",
        ],
    },
    {
        "kind": "twocol",
        "title": "Recall R6: Radius Helped, But Thin Geometry Still Survived",
        "common_settings": "Recall only. Larger radius helped, but thin geometry still preserved a hard penetration counterexample.",
        "left_label": "Thin-ear close-up\n5x radius",
        "left_path": RECALL_THIN_EAR_5X_GIF,
        "right_label": "Thin-ear close-up\n10x radius",
        "right_path": RECALL_THIN_EAR_10X_GIF,
        "transcript": [
            "最后一页 recall 只保留最难反驳的 visual counterexample。",
            "radius 变大确实会帮忙，但 thin geometry 还是能把 penetration 问题保留下来。",
            "这页的作用是把后续讨论重新固定在一个更窄的问题上：不是 bridge baseline 缺失，而是 thin geometry 和 local contact behavior 仍然需要新的解释或修复。",
        ],
    },
]

SELF_COLLISION_SLIDES: list[dict] = [
    {
        "kind": "image",
        "title": "Self-Collision S1: Stable 2x2 Matrix And Mechanism Board",
        "path": SELF_COLLISION_BOARD_PNG,
        "note": (
            "Sources: stable matrix root "
            "`Newton/phystwin_bridge/results/ground_contact_self_collision_repro_fix_20260404_200830_aa5e607` "
            "and stable follow-up root "
            "`Newton/phystwin_bridge/results/self_collision_transfer_case3_vs_case4_followup_20260404_210334_ac9ec33`."
        ),
        "transcript": [
            "这一页是本周 self-collision 章节最重要的可视化成果。",
            "左上角是稳定的 `2 x 2` matrix，最优 full-rollout 组合仍然是 case 3，也就是 PhysTwin-style self-collision 加 native Newton ground-contact。",
            "右上角是 case 3 和 case 4 的 per-frame RMSE 曲线。这里最关键的不是谁最后均值更小，而是 case 4 在 early rollout 其实更好，它是在 frame 40 首次翻符号、并在 frame 107 开始进入持续更差区间。",
            "下排把机制证据压在一张图里：左边是 frame 40、107、137 的 active ground particle 对比，右边是 self-contact active nodes 加 controller mismatch reminder。",
            "这张图想传达的主句只有一句：case 4 不是因为 local self-collision law 错了才输，而是因为 fully PhysTwin-style branch 暴露了 bridge 里剩余的 whole-step mismatch。",
        ],
    },
    {
        "kind": "body",
        "title": "Self-Collision S2: Current Conclusion And Recommendation",
        "bullets": [
            "Stable conclusion: `case_3 > case_4` is now reproducible, so this is a real bridge behavior rather than a drifting ranking artifact.",
            "Mechanism reading: native Newton ground-contact currently behaves like a stabilizing compensator for a broader whole-step mismatch; the strongest remaining mismatch is still controller-spring semantics.",
            "What this does NOT mean: native Newton self-collision or native Newton ground-contact is the final PhysTwin-faithful semantic target.",
            "Recommendation stays `C`: bridge-side PhysTwin-style self-collision is still necessary; the remaining blocker sits outside the isolated self-collision operator itself.",
        ],
        "transcript": [
            "这一页只做 decision close，不再堆图。",
            "第一，stable matrix 已经证明 case 3 比 case 4 更好这个排序是真的，不是之前那种不稳定 ranking artifact。",
            "第二，但这个 stable result 不能被误读成 native Newton ground-contact 更 PhysTwin-faithful。我们现在更支持的解释是，native ground 在当前 bridge 里起到了一个 stabilizing compensation 的作用，而 fully PhysTwin-style pair 反而把剩下的 whole-step mismatch 暴露出来了。",
            "第三，所以 recommendation 不变，仍然是 C，也就是 bridge-side PhysTwin-style self-collision is necessary。",
            "现在没有被解决掉的，不是 isolated self-collision operator，而是更上层的 rollout interaction，尤其 controller-spring semantics。",
        ],
    },
]

ROBOT_SLIDES: list[dict] = [
    {
        "kind": "gif_bullets",
        "title": "Robot R1: Best Meeting Visual Is The Honest Visible-Tool Baseline",
        "gif_label": "Same rollout. Left: hero presentation. Right: validation camera.\nVisible rigid tool is the actual physical contactor.",
        "gif_path": ROBOT_TOOL_HERO_VALIDATION_GIF,
        "note": (
            "Promoted control: `robot_visible_rigid_tool_baseline`. "
            "Native Franka + native tabletop + bridged rope, with the same visible short rod used for both render and contact."
        ),
        "bullets": [
            "Native Newton Franka, native tabletop, and bridged rope remain the scene stack; the deformable interaction still runs under `SolverSemiImplicit`.",
            f"Tool-first contact is explicit: tool contact starts at `{ROBOT_TOOL_SUMMARY['actual_tool_first_contact_time_s']:.2f} s`, rope lateral motion follows at `{ROBOT_TOOL_LATERAL_TIME_S:.2f} s`, and deformation follows at `{ROBOT_TOOL_DEFORMATION_TIME_S:.2f} s`.",
            "This is the cleanest meeting-facing visual because the rope is true-size and the visible short rod is the same geometry that actually does the pushing.",
            "Claim boundary stays conservative: tool-mediated one-way robot -> rope only; no direct-finger or physical-blocking claim.",
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
        "title": "Robot R2: The Promoted Direct-Finger Path Stays Conservative",
        "gif_label": "Same rollout. Left: hero presentation. Right: validation camera.\nActual finger-box contact remains the proof surface.",
        "gif_path": ROBOT_ONEWAY_HERO_VALIDATION_GIF,
        "note": (
            "Promoted conservative task: `robot_rope_franka_semiimplicit_oneway`. "
            "This is the direct-finger Path A bundle re-certified under a narrower one-way claim."
        ),
        "bullets": [
            "This is the current promoted direct-finger authority: `robot_rope_franka_semiimplicit_oneway`.",
            f"Finger-box first contact starts at `{ROBOT_ONEWAY_SUMMARY['actual_finger_box_first_contact_time_s']:.2f} s`; rope deformation follows at `{ROBOT_ONEWAY_DEFORMATION_TIME_S:.2f} s`; lateral rope motion follows at `{ROBOT_ONEWAY_LATERAL_TIME_S:.2f} s`.",
            "Deformable interaction is explicitly under `SolverSemiImplicit`, and the final proof surface stays actual finger-box contact rather than proxy radii.",
            "Claim boundary stays narrow: one-way robot -> rope only; no articulated physical-blocking, no full two-way coupling, no self-collision parity claim.",
        ],
        "transcript": [
            "这一页再把 currently promoted 的 direct-finger path 摆出来。",
            "我保留这页的原因不是因为它比 visible-tool 更好看，而是因为它对应的是当前被重新认证过的 conservative authority。",
            f"这里同样是 same-rollout 双视角，而且 proof surface 仍然是 actual finger-box contact。也就是说，`{ROBOT_ONEWAY_SUMMARY['actual_finger_box_first_contact_time_s']:.2f}` 秒才算真正接触，之后 rope deformation 和 lateral motion 才开始。",
            "这页要讲清楚两点：第一，deformable interaction 是 `SolverSemiImplicit`；第二，这不是 full two-way，也不是 physical blocking。",
            "所以周三如果老师追问当前 direct-finger claim 到底站到哪里，这页就是最安全的答案。",
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


def _prepare_generated_assets() -> None:
    DECK_GIF_DIR.mkdir(parents=True, exist_ok=True)
    _build_self_collision_mechanism_board()
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
