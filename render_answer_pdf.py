#!/usr/bin/env python3
"""
Render a Markdown file to PDF using WeasyPrint.

Why: this repo already ships `answer.md` + `answer.pdf`; the existing PDF
was produced by WeasyPrint, but we want a reproducible command to re-render
after edits.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import markdown
from weasyprint import CSS, HTML


DEFAULT_CSS = r"""
@page { size: A4; margin: 18mm 16mm; }

html, body {
  font-family: "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC",
               "Source Han Sans SC", "WenQuanYi Zen Hei", sans-serif;
  font-size: 11pt;
  line-height: 1.45;
  color: #111;
}

h1, h2, h3, h4 { line-height: 1.2; }
h1 { font-size: 20pt; margin: 0 0 10pt 0; }
h2 { font-size: 16pt; margin: 16pt 0 8pt 0; }
h3 { font-size: 13pt; margin: 14pt 0 6pt 0; }
h4 { font-size: 12pt; margin: 12pt 0 6pt 0; }

p { margin: 6pt 0; }
ul, ol { margin: 6pt 0 6pt 18pt; padding: 0; }
li { margin: 3pt 0; }

code, pre {
  font-family: "JetBrains Mono", "SFMono-Regular", "Consolas", "Menlo", monospace;
  font-size: 9.5pt;
}

pre {
  background: #f6f8fa;
  border: 1px solid #e5e7eb;
  padding: 8pt;
  white-space: pre-wrap;
}

table { border-collapse: collapse; width: 100%; margin: 10pt 0; }
th, td { border: 1px solid #d0d7de; padding: 6pt 6pt; vertical-align: top; }
th { background: #f6f8fa; }
"""


def render_md_to_pdf(md_path: Path, pdf_path: Path) -> None:
    md_text = md_path.read_text(encoding="utf-8")

    # Keep extensions minimal and stable.
    body = markdown.markdown(
        md_text,
        extensions=[
            "fenced_code",
            "tables",
            "sane_lists",
            "toc",
        ],
        output_format="xhtml",
    )

    html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>{md_path.stem}</title>
  </head>
  <body>
    {body}
  </body>
</html>
"""

    HTML(string=html, base_url=str(md_path.resolve().parent)).write_pdf(
        str(pdf_path),
        stylesheets=[CSS(string=DEFAULT_CSS)],
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Render markdown to PDF with WeasyPrint.")
    p.add_argument("--in", dest="inp", type=Path, default=Path("answer.md"))
    p.add_argument("--out", dest="out", type=Path, default=Path("answer.pdf"))
    args = p.parse_args()

    render_md_to_pdf(args.inp.resolve(), args.out.resolve())
    print(f"✅ PDF saved to {args.out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

