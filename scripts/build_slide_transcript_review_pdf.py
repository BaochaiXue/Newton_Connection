#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

import fitz
from weasyprint import HTML


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class TranscriptSection:
    slide_number: int
    title: str
    lines: list[str]


@dataclass(frozen=True)
class LayoutCandidate:
    slug: str
    page_width_in: float
    page_height_in: float
    slide_column_ratio: float
    transcript_font_pt: float
    transcript_line_height: float
    header_font_pt: float


LAYOUT_CANDIDATES = [
    LayoutCandidate(
        slug="review_legal_landscape",
        page_width_in=14.0,
        page_height_in=8.5,
        slide_column_ratio=0.60,
        transcript_font_pt=8.3,
        transcript_line_height=1.16,
        header_font_pt=16.0,
    ),
    LayoutCandidate(
        slug="review_wide_landscape",
        page_width_in=15.0,
        page_height_in=9.5,
        slide_column_ratio=0.59,
        transcript_font_pt=8.6,
        transcript_line_height=1.18,
        header_font_pt=17.0,
    ),
    LayoutCandidate(
        slug="review_large_landscape",
        page_width_in=16.0,
        page_height_in=10.0,
        slide_column_ratio=0.58,
        transcript_font_pt=8.8,
        transcript_line_height=1.20,
        header_font_pt=18.0,
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a review PDF where each slide is paired with its matching transcript."
    )
    parser.add_argument("--pptx", type=Path, required=True, help="Input meeting PPTX.")
    parser.add_argument("--transcript-md", type=Path, required=True, help="Input transcript markdown.")
    parser.add_argument("--out-pdf", type=Path, required=True, help="Output review PDF.")
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=ROOT / "tmp_vis" / "slide_transcript_review",
        help="Scratch directory for rendered slide images and debug HTML.",
    )
    parser.add_argument(
        "--deck-title",
        type=str,
        default="Slide Transcript Review",
        help="Short label shown in the review PDF header.",
    )
    return parser.parse_args()


def _parse_transcript_sections(path: Path) -> list[TranscriptSection]:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"^## Slide\s+(\d+)\s+[—-]\s+(.*)$", flags=re.M)
    matches = list(pattern.finditer(text))
    if not matches:
        raise ValueError(f"No slide transcript sections found in {path}")

    sections: list[TranscriptSection] = []
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        sections.append(
            TranscriptSection(
                slide_number=int(match.group(1)),
                title=match.group(2).strip(),
                lines=lines,
            )
        )
    return sections


def _convert_pptx_to_pdf(pptx_path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{pptx_path.stem}.pdf"
    if pdf_path.exists() and pdf_path.stat().st_mtime >= pptx_path.stat().st_mtime:
        return pdf_path

    subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(out_dir),
            str(pptx_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not pdf_path.exists():
        raise FileNotFoundError(f"LibreOffice did not produce expected PDF: {pdf_path}")
    return pdf_path


def _render_slide_previews(slides_pdf: Path, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(slides_pdf)
    image_paths: list[Path] = []
    try:
        for page_idx in range(doc.page_count):
            out_path = out_dir / f"slide_{page_idx + 1:02d}.png"
            if not out_path.exists() or out_path.stat().st_mtime < slides_pdf.stat().st_mtime:
                page = doc.load_page(page_idx)
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), alpha=False)
                pix.save(out_path)
            image_paths.append(out_path)
    finally:
        doc.close()
    return image_paths


def _pdf_page_count(pdf_path: Path) -> int:
    result = subprocess.run(
        ["pdfinfo", str(pdf_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, flags=re.M)
    if match is None:
        raise RuntimeError(f"Could not parse page count from pdfinfo output for {pdf_path}")
    return int(match.group(1))


def _line_class(line: str) -> str:
    if line.startswith("[") and line.endswith("]"):
        return "meta-line"
    return "body-line"


def _section_html(section: TranscriptSection, image_path: Path, deck_title: str) -> str:
    lines_html = "\n".join(
        f'<p class="{_line_class(line)}">{html.escape(line)}</p>' for line in section.lines
    )
    return f"""
    <section class="review-page">
      <div class="page-topline">
        <div class="deck-title">{html.escape(deck_title)}</div>
        <div class="page-label">Slide {section.slide_number}</div>
      </div>
      <div class="page-grid">
        <div class="slide-panel">
          <img src="{image_path.as_uri()}" alt="Slide {section.slide_number}" />
        </div>
        <div class="transcript-panel">
          <h1>Slide {section.slide_number}: {html.escape(section.title)}</h1>
          <div class="transcript-lines">
            {lines_html}
          </div>
        </div>
      </div>
    </section>
    """


def _build_html(
    *,
    sections: list[TranscriptSection],
    slide_images: list[Path],
    layout: LayoutCandidate,
    deck_title: str,
) -> str:
    if len(sections) != len(slide_images):
        raise ValueError(
            f"Slide/transcript mismatch: {len(slide_images)} slide pages vs {len(sections)} transcript sections"
        )

    pages = "\n".join(
        _section_html(section, slide_images[idx], deck_title)
        for idx, section in enumerate(sections)
    )
    slide_pct = layout.slide_column_ratio * 100.0
    text_pct = 100.0 - slide_pct
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <style>
    @page {{
      size: {layout.page_width_in:.2f}in {layout.page_height_in:.2f}in;
      margin: 0.35in;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      color: #17202a;
      font-family: "DejaVu Sans", sans-serif;
      background: #f6f2e8;
    }}
    .review-page {{
      break-after: page;
      page-break-after: always;
    }}
    .review-page:last-child {{
      break-after: auto;
      page-break-after: auto;
    }}
    .page-topline {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 0.16in;
      color: #6c7a89;
      font-size: 10pt;
      letter-spacing: 0.02em;
    }}
    .deck-title {{
      font-weight: 700;
      color: #34495e;
    }}
    .page-label {{
      font-weight: 600;
    }}
    .page-grid {{
      display: grid;
      grid-template-columns: {slide_pct:.2f}% {text_pct:.2f}%;
      column-gap: 0.28in;
      align-items: start;
    }}
    .slide-panel {{
      background: #ffffff;
      border: 1px solid #d7dee5;
      border-radius: 10px;
      padding: 0.10in;
      box-shadow: 0 4px 18px rgba(15, 35, 45, 0.08);
    }}
    .slide-panel img {{
      display: block;
      width: 100%;
      height: auto;
      border-radius: 6px;
    }}
    .transcript-panel {{
      background: rgba(255, 255, 255, 0.82);
      border: 1px solid #d7dee5;
      border-radius: 10px;
      padding: 0.18in 0.20in;
      box-shadow: 0 4px 18px rgba(15, 35, 45, 0.06);
      font-size: {layout.transcript_font_pt:.2f}pt;
      line-height: {layout.transcript_line_height:.3f};
    }}
    .transcript-panel h1 {{
      margin: 0 0 0.10in 0;
      color: #123b58;
      font-size: {layout.header_font_pt:.2f}pt;
      line-height: 1.08;
    }}
    .transcript-lines p {{
      margin: 0 0 0.07in 0;
    }}
    .transcript-lines p:last-child {{
      margin-bottom: 0;
    }}
    .meta-line {{
      color: #0b6178;
      font-family: "DejaVu Sans Mono", monospace;
      font-size: 0.93em;
    }}
    .body-line {{
      color: #17202a;
    }}
  </style>
</head>
<body>
{pages}
</body>
</html>
"""


def _render_review_pdf(
    *,
    html_text: str,
    html_path: Path,
    out_pdf: Path,
) -> None:
    html_path.write_text(html_text, encoding="utf-8")
    HTML(string=html_text, base_url=str(ROOT)).write_pdf(str(out_pdf))


def _pick_layout(
    *,
    sections: list[TranscriptSection],
    slide_images: list[Path],
    work_dir: Path,
    deck_title: str,
) -> tuple[LayoutCandidate, Path, Path]:
    attempts: list[dict[str, object]] = []
    for layout in LAYOUT_CANDIDATES:
        candidate_html = work_dir / f"review_{layout.slug}.html"
        candidate_pdf = work_dir / f"review_{layout.slug}.pdf"
        html_text = _build_html(
            sections=sections,
            slide_images=slide_images,
            layout=layout,
            deck_title=deck_title,
        )
        _render_review_pdf(html_text=html_text, html_path=candidate_html, out_pdf=candidate_pdf)
        page_count = _pdf_page_count(candidate_pdf)
        attempts.append(
            {
                "layout": asdict(layout),
                "pdf": str(candidate_pdf),
                "page_count": page_count,
            }
        )
        if page_count == len(sections):
            (work_dir / "review_layout_attempts.json").write_text(
                json.dumps(attempts, indent=2),
                encoding="utf-8",
            )
            return layout, candidate_html, candidate_pdf

    (work_dir / "review_layout_attempts.json").write_text(
        json.dumps(attempts, indent=2),
        encoding="utf-8",
    )
    raise RuntimeError(
        "Could not fit slide/transcript review pages into a 1:1 page mapping. "
        "See review_layout_attempts.json for the attempted layouts."
    )


def main() -> int:
    args = parse_args()
    pptx_path = args.pptx.expanduser().resolve()
    transcript_md = args.transcript_md.expanduser().resolve()
    out_pdf = args.out_pdf.expanduser().resolve()
    work_dir = args.work_dir.expanduser().resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    if not pptx_path.exists():
        raise FileNotFoundError(f"Missing PPTX: {pptx_path}")
    if not transcript_md.exists():
        raise FileNotFoundError(f"Missing transcript markdown: {transcript_md}")

    sections = _parse_transcript_sections(transcript_md)
    slides_pdf = _convert_pptx_to_pdf(pptx_path, work_dir / "slides_pdf")
    slide_images = _render_slide_previews(slides_pdf, work_dir / "slide_previews")
    if len(slide_images) != len(sections):
        raise RuntimeError(
            f"Slide/transcript mismatch: rendered {len(slide_images)} slide pages but found {len(sections)} transcript sections."
        )

    layout, html_path, candidate_pdf = _pick_layout(
        sections=sections,
        slide_images=slide_images,
        work_dir=work_dir,
        deck_title=args.deck_title,
    )

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    out_pdf.write_bytes(candidate_pdf.read_bytes())
    metadata = {
        "pptx": str(pptx_path),
        "transcript_md": str(transcript_md),
        "review_pdf": str(out_pdf),
        "slides_pdf": str(slides_pdf),
        "review_html": str(html_path),
        "work_dir": str(work_dir),
        "slide_count": len(slide_images),
        "selected_layout": asdict(layout),
    }
    (work_dir / "review_manifest.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"REVIEW_PDF={out_pdf}")
    print(f"SLIDE_COUNT={len(slide_images)}")
    print(f"LAYOUT={layout.slug}")
    print(f"WORK_DIR={work_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
