#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from pptx import Presentation

MEETING_DIR = Path(__file__).resolve().parent
ROOT = MEETING_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from formal_slide.meeting_2026_04_01 import build_meeting_20260401 as shared

TEMPLATE_PPTX = ROOT / "formal_slide" / "meeting_2026_04_01" / "templates" / "My Adjust.pptx"
OUT_PPTX = MEETING_DIR / "bridge_meeting_20260408_recall_initial.pptx"
DECK_GIF_DIR = MEETING_DIR / "gif"
DEFAULT_MAX_PPTX_MB = 100.0

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
            "Initial recall-only scaffold.",
            "Goal: re-establish the baseline before this week's new results.",
        ],
        "transcript": [
            "这一页是 `2026-04-08` meeting 的 opening page。",
            "当前 bundle 只先建立 recall part，不提前假装后面的新结果已经定稿。",
            "所以 opening 要做的只有一件事：把这次 recall 的边界讲清楚，也就是先把已经建立的 baseline 和已经收窄的问题重新摆稳。",
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


def _prepare_generated_assets() -> None:
    DECK_GIF_DIR.mkdir(parents=True, exist_ok=True)
    for src, out, width, fps, max_colors in RECALL_DIRECT_GIF_SPECS:
        shared._ensure_resized_gif(src, out, width=width, fps=fps, max_colors=max_colors)


def _build_transcript_md(slides: list[dict] | None = None) -> str:
    lines = [
        "# Meeting Transcript — PhysTwin -> Newton Bridge",
        "",
        "语言：中文主讲 + English terminology  ",
        "形式：opening + recall-only initial draft  ",
        "结构：1. opening  2. recall  ",
        "目标：给 `2026-04-08` meeting 建立第一版 recall scaffold  ",
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


def _parse_slide_range(spec: str | None) -> list[dict]:
    if not spec:
        return list(RECALL_SLIDES)
    match = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", spec)
    if not match:
        raise ValueError(f"Unsupported --slide-range format: {spec!r}. Expected START-END.")
    start = int(match.group(1))
    end = int(match.group(2))
    if start < 1 or end < start or end > len(RECALL_SLIDES):
        raise ValueError(f"Slide range {spec!r} is out of bounds for a {len(RECALL_SLIDES)}-slide deck.")
    return list(RECALL_SLIDES[start - 1 : end])


def build_meeting_deck(prs: Presentation, slides: list[dict] | None = None) -> None:
    shared._delete_all_slides(prs)
    active_slides = slides or list(RECALL_SLIDES)
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
        else:
            raise ValueError(f"Unsupported slide kind for 2026-04-08 recall bundle: {kind}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the 2026-04-08 recall-only meeting bundle.")
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
