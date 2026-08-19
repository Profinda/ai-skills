#!/usr/bin/env python3
"""Generate Jira ADF JSON from the Markdown description templates.

Markdown is the source of truth (../*.md). This script regenerates the matching
../adf/*.adf.json. Do NOT edit the ADF by hand.

Supports the subset of Markdown used by the templates:
- Headings (#..######)
- Coloured section banners: a heading prefixed with a colour token becomes a
  full-width coloured header bar (bold text), matching the original Jira
  template. Syntax:  ## {green} 6. Risk assessment
  Dark colours (white text): green, teal, navy, red, orange.
  Light colours (dark text): light-green, light-orange, light-grey.
  See PALETTE.
- Paragraphs
- Bullet lists (- ) and task lists (- [ ] / - [x])
- Tables (| ... |) with a header separator row
- Blockquotes (> )
- HTML comments <!-- ... --> are dropped (guidance not stored in Jira)

Usage:
    python3 generate.py            # regenerate all
    python3 generate.py --check    # exit 1 if any ADF is out of sync
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_DIR = HERE.parent
TEMPLATES = ["epic", "story", "task", "subtask"]

# Named section-banner colours. Each maps to a (background, text) pair.
# Dark shades (white text) match the original SP-10376 template palette; light
# shades (dark text) are for softer intro/meta banners like the change log.
PALETTE = {
    "green": ("#1d7a4e", "#ffffff"),
    "teal": ("#0f7b8c", "#ffffff"),
    "navy": ("#1b2a4a", "#ffffff"),
    "red": ("#b91c1c", "#ffffff"),
    "orange": ("#c96a00", "#ffffff"),
    "light-green": ("#dcfff1", "#1b2a4a"),
    "light-orange": ("#fff0db", "#1b2a4a"),
    "light-grey": ("#f4f6f8", "#1b2a4a"),
}

BANNER_RE = re.compile(r"^\{(" + "|".join(PALETTE) + r")\}\s*(.*)")


def text_node(s, marks=None):
    node = {"type": "text", "text": s}
    if marks:
        node["marks"] = marks
    return node


def paragraph(s):
    content = [text_node(s)] if s else []
    node = {"type": "paragraph"}
    if content:
        node["content"] = content
    return node


def heading(level, s):
    return {
        "type": "heading",
        "attrs": {"level": level},
        "content": [text_node(s)],
    }


def banner(color_name, s):
    """A full-width coloured header bar: single-cell table row, bold text."""
    bg, fg = PALETTE[color_name]
    marks = [{"type": "strong"}, {"type": "textColor", "attrs": {"color": fg}}]
    cell = {
        "type": "tableCell",
        "attrs": {"colspan": 1, "background": bg},
        "content": [{"type": "paragraph", "content": [text_node(s, marks)]}],
    }
    return {
        "type": "table",
        "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
        "content": [{"type": "tableRow", "content": [cell]}],
    }


def strip_comments(md):
    return re.sub(r"<!--.*?-->", "", md, flags=re.DOTALL)


def parse_table(lines, i):
    rows = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        rows.append(lines[i].strip())
        i += 1

    def cells(row):
        parts = [c.strip() for c in row.strip().strip("|").split("|")]
        return parts

    parsed = [cells(r) for r in rows]
    # drop the separator row (---|---)
    body = [r for r in parsed if not all(set(c) <= set("-: ") and c for c in r)]

    table_rows = []
    for idx, row in enumerate(body):
        is_header = idx == 0
        cell_type = "tableHeader" if is_header else "tableCell"
        cell_nodes = [
            {"type": cell_type, "attrs": {}, "content": [paragraph(c)]}
            for c in row
        ]
        table_rows.append({"type": "tableRow", "content": cell_nodes})

    return {
        "type": "table",
        "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
        "content": table_rows,
    }, i


def parse_list(lines, i):
    items = []
    is_task = bool(re.match(r"\s*- \[[ xX]\]", lines[i]))
    while i < len(lines):
        m = re.match(r"\s*- (?:\[([ xX])\] )?(.*)", lines[i])
        if not m:
            break
        checked = m.group(1)
        text = m.group(2)
        if is_task:
            state = "DONE" if (checked or "").lower() == "x" else "TODO"
            items.append(
                {
                    "type": "taskItem",
                    "attrs": {"localId": str(len(items)), "state": state},
                    "content": [text_node(text)] if text else [],
                }
            )
        else:
            items.append(
                {"type": "listItem", "content": [paragraph(text)]}
            )
        i += 1
    if is_task:
        return {"type": "taskList", "attrs": {"localId": "tl"}, "content": items}, i
    return {"type": "bulletList", "content": items}, i


def md_to_adf(md):
    md = strip_comments(md)
    lines = md.split("\n")
    content = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        h = re.match(r"(#{1,6}) (.*)", line)
        if h:
            level = len(h.group(1))
            title = h.group(2).strip()
            b = BANNER_RE.match(title)
            if b:
                content.append(banner(b.group(1), b.group(2).strip()))
            else:
                content.append(heading(level, title))
            i += 1
            continue
        if line.strip().startswith("|"):
            node, i = parse_table(lines, i)
            content.append(node)
            continue
        if re.match(r"\s*- ", line):
            node, i = parse_list(lines, i)
            content.append(node)
            continue
        if line.strip().startswith(">"):
            quote = re.sub(r"^\s*> ?", "", line)
            content.append(
                {"type": "blockquote", "content": [paragraph(quote.strip())]}
            )
            i += 1
            continue
        content.append(paragraph(line.strip()))
        i += 1

    return {"type": "doc", "version": 1, "content": content}


def main():
    check = "--check" in sys.argv
    drift = False
    for name in TEMPLATES:
        src = SRC_DIR / f"{name}.md"
        out = HERE / f"{name}.adf.json"
        adf = md_to_adf(src.read_text())
        rendered = json.dumps(adf, indent=2, ensure_ascii=False) + "\n"
        if check:
            existing = out.read_text() if out.exists() else ""
            if existing != rendered:
                drift = True
                print(f"OUT OF SYNC: {out.name} — run generate.py")
        else:
            out.write_text(rendered)
            print(f"wrote {out.name}")
    if check and drift:
        sys.exit(1)
    if check:
        print("all ADF in sync")


if __name__ == "__main__":
    main()
