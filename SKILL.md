---
name: compact-reference-pdf
description: >
  Converts one or more Markdown (.md) reference guides into compact, print-ready
  A4 PDF files with consistent two-column layout, colour-coded headings, styled
  code blocks, zebra-stripe tables, and strict page-break control so no logical
  block (heading + its content, code snippet, table, blockquote) is ever split
  across pages. Use this skill whenever the user asks to:
  - "turn this into a PDF"
  - "make it printable / print-ready"
  - "save as PDF for printing"
  - "create a reference card / cheatsheet PDF"
  - "make all my guides look the same"
  Always apply this skill for any .md → PDF conversion where visual quality and
  print economy matter.
---

# Compact Reference PDF Skill

Transforms Markdown reference guides into **compact, print-ready A4 PDFs**.

## What the output looks like

| Property | Value |
|---|---|
| Page size | A4 |
| Margins | 10 mm all sides |
| Columns | 2 (maximises density) |
| Base font | IBM Plex Sans 8 pt |
| Code font | IBM Plex Mono 6.8 pt |
| Page numbers | Bottom-right |
| Logical blocks | Never split across pages |

Visual hierarchy:
- **H1** — full-width title, red underline
- **H2** — full-width dark-blue banner (spans both columns)
- **H3** — blue left-border pill inside a column
- **Code blocks** — dark (#1a1a2e) background, blue left accent
- **Tables** — dark-blue header row, alternating row shading
- **Blockquotes / tips** — amber left-border highlight box

---

## How to use

1. Make sure the Markdown file(s) exist (already created or uploaded).
2. Run `compact_reference_pdf.py`, passing the input/output paths.
3. Present the resulting PDF(s) to the user.

---

## Dependencies

Install once if not already present:

```bash
pip install markdown weasyprint beautifulsoup4 --break-system-packages
```

---

## The script

Save as `compact_reference_pdf.py` and edit the `FILES` dict at the top.

```python
# compact_reference_pdf.py
# Usage: edit FILES dict, then  python compact_reference_pdf.py

import markdown
from bs4 import BeautifulSoup
import warnings

# ── EDIT THIS ────────────────────────────────────────────────
FILES = {
    "output-name": "/path/to/input.md",
    # add more pairs as needed
}
OUTPUT_DIR = "/mnt/user-data/outputs"
# ─────────────────────────────────────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap');

@page {
    size: A4;
    margin: 10mm 11mm 10mm 11mm;
    @bottom-right {
        content: counter(page);
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 7pt;
        color: #aaa;
    }
}

* { box-sizing: border-box; }

body {
    font-family: 'IBM Plex Sans', 'DejaVu Sans', sans-serif;
    font-size: 8pt;
    line-height: 1.35;
    color: #1a1a2e;
    background: white;
    column-count: 2;
    column-gap: 5mm;
    column-fill: auto;
}

/* H1 and its subtitle span both columns */
h1 {
    column-span: all;
    font-size: 13pt;
    font-weight: 700;
    color: #0f3460;
    border-bottom: 2px solid #e94560;
    padding-bottom: 3px;
    margin: 0 0 2px 0;
    break-after: avoid;
    page-break-after: avoid;
}
h1 + p {
    column-span: all;
    font-style: italic;
    color: #555;
    font-size: 7.5pt;
    margin: 0 0 6px 0;
}

/* H2 spans both columns — acts as a section divider */
h2 {
    column-span: all;
    font-size: 9pt;
    font-weight: 700;
    color: white;
    background: #0f3460;
    padding: 3px 7px;
    margin: 7px 0 3px 0;
    break-after: avoid;
    page-break-after: avoid;
    border-radius: 2px;
}

/* H3 stays inside one column */
h3 {
    font-size: 8pt;
    font-weight: 700;
    color: #0f3460;
    background: #e8f0fe;
    border-left: 3px solid #4361ee;
    padding: 2px 6px;
    margin: 5px 0 2px 0;
    break-after: avoid;
    page-break-after: avoid;
    border-radius: 0 2px 2px 0;
}

h4 {
    font-size: 7.5pt;
    font-weight: 700;
    color: #333;
    margin: 4px 0 1px 0;
    break-after: avoid;
    page-break-after: avoid;
}

/* Section wrappers injected by Python */
.section-h3 {
    break-inside: avoid;
    page-break-inside: avoid;
}
.section-h2 > h2,
.section-h2 > h2 + * {
    break-after: avoid;
    page-break-after: avoid;
}
.section-h3 > h3,
.section-h3 > h3 + * {
    break-after: avoid;
    page-break-after: avoid;
}

p {
    margin: 0 0 3px 0;
    orphans: 2;
    widows: 2;
}

pre {
    background: #1a1a2e;
    color: #e2e8f8;
    border-radius: 3px;
    padding: 4px 7px;
    font-family: 'IBM Plex Mono', 'DejaVu Sans Mono', monospace;
    font-size: 6.8pt;
    line-height: 1.3;
    margin: 2px 0 4px 0;
    break-inside: avoid;
    page-break-inside: avoid;
    border-left: 2px solid #4361ee;
    white-space: pre-wrap;
    word-break: break-all;
}

code {
    font-family: 'IBM Plex Mono', 'DejaVu Sans Mono', monospace;
    background: #e8f0fe;
    color: #0f3460;
    padding: 0 3px;
    border-radius: 2px;
    font-size: 6.8pt;
}
pre code { background: none; color: inherit; padding: 0; font-size: inherit; }

table {
    width: 100%;
    border-collapse: collapse;
    margin: 2px 0 4px 0;
    font-size: 7pt;
    break-inside: avoid;
    page-break-inside: avoid;
}
thead tr { background: #0f3460; color: white; }
thead th { padding: 3px 5px; text-align: left; font-weight: 600; font-size: 7pt; }
tbody tr { break-inside: avoid; page-break-inside: avoid; }
tbody tr:nth-child(even) { background: #f0f4ff; }
tbody tr:nth-child(odd)  { background: white; }
tbody td { padding: 2px 5px; border-bottom: 1px solid #dde4f5; vertical-align: top; }

blockquote {
    background: #fff8e7;
    border-left: 3px solid #f4a261;
    margin: 2px 0 3px 0;
    padding: 3px 7px;
    border-radius: 0 3px 3px 0;
    font-size: 7.5pt;
    color: #4a3800;
    break-inside: avoid;
    page-break-inside: avoid;
}
blockquote p { margin: 0; }

ul, ol { margin: 1px 0 3px 0; padding-left: 14px; }
li { margin-bottom: 1px; line-height: 1.3; break-inside: avoid; page-break-inside: avoid; }

strong { font-weight: 700; color: #0f3460; }
em     { color: #555; }

hr {
    column-span: all;
    border: none;
    border-top: 1px solid #dde4f5;
    margin: 4px 0;
}

a { color: #4361ee; }
"""

TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{css}</style></head>
<body>{body}</body></html>"""


def wrap_sections(html_body):
    """Wrap h2/h3 blocks in divs so page-break-inside:avoid works per section."""
    soup = BeautifulSoup(html_body, "html.parser")

    def group_by(elements, tag_name, div_class):
        groups, current, has_h = [], [], False
        for el in elements:
            if getattr(el, "name", None) == tag_name:
                if current:
                    groups.append((has_h, current))
                current, has_h = [el], True
            else:
                current.append(el)
        if current:
            groups.append((has_h, current))
        result = []
        for has_h, bucket in groups:
            if not has_h:
                result.extend(bucket)
            else:
                div = soup.new_tag("div", attrs={"class": div_class})
                for el in bucket:
                    div.append(el.extract() if hasattr(el, "extract") else el)
                result.append(div)
        return result

    h2_sections = group_by(list(soup.contents), "h2", "section-h2")
    final = []
    for el in h2_sections:
        if "section-h2" in (el.get("class", []) if hasattr(el, "get") else []):
            h3_grouped = group_by(list(el.contents), "h3", "section-h3")
            el.clear()
            for child in h3_grouped:
                el.append(child)
        final.append(el)

    wrapper = BeautifulSoup("", "html.parser")
    for el in final:
        wrapper.append(el)
    return str(wrapper)


def convert(files, output_dir):
    import os
    from weasyprint import HTML
    warnings.filterwarnings("ignore")

    md_parser = markdown.Markdown(extensions=["tables", "fenced_code", "nl2br"])

    for name, src_path in files.items():
        print(f"  Processing: {name}")
        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()

        raw_html = md_parser.convert(content)
        md_parser.reset()
        wrapped  = wrap_sections(raw_html)
        full_html = TEMPLATE.format(css=CSS, body=wrapped)

        html_path = f"/tmp/{name}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(full_html)

        pdf_path = os.path.join(output_dir, f"{name}.pdf")
        HTML(filename=html_path).write_pdf(pdf_path)
        print(f"  Saved:  {pdf_path}")


if __name__ == "__main__":
    convert(FILES, OUTPUT_DIR)
    print("Done.")
```

---

## Key design decisions (for future tweaks)

### Two-column layout
`column-count: 2` on `<body>` — the single most effective space-saver.
H1 and H2 use `column-span: all` to act as full-width dividers.

### Page-break control — two layers
1. **CSS**: `break-inside: avoid` / `page-break-inside: avoid` on `pre`, `table`,
   `blockquote`, `li`, and `.section-h3`.
2. **Python `wrap_sections()`**: parses the flat HTML with BeautifulSoup and
   re-wraps every `h2`+content and `h3`+content in a `<div class="section-h*">`.
   This is necessary because CSS cannot select "a heading and all siblings until
   the next heading of the same level" — only explicit wrappers work reliably.

### Typography scale
All sizes are intentionally small (8 pt body, 6.8 pt code) because the target
is a **printed cheatsheet**, not a screen document. On paper at A4 these sizes
are perfectly legible.

### Margins
10 mm all sides — tight but within the safe print area of all common printers
(most have a hardware minimum of ~5 mm).

---

## Checklist when invoking this skill

- [ ] Markdown source file(s) exist and are accessible
- [ ] `FILES` dict set correctly (name → path)
- [ ] `OUTPUT_DIR` points to `/mnt/user-data/outputs`
- [ ] Dependencies installed (`markdown`, `weasyprint`, `beautifulsoup4`)
- [ ] Present final PDF(s) with `present_files`
