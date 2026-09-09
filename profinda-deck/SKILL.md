---
name: profinda-deck
description: Build ProFinda presentation decks from content, not markup. A content-driven engine turns a Python list of slide dicts into a single self-contained HTML deck in the ProFinda design language — 17 layouts (title, section, statement, quote, bullets, two-column, media, gallery, charts, stats, big-number, cards, table, timeline, compare, feature, closing), inline SVG charts, embedded media, a 3D star-cloud flythrough, speaker notes, keyboard/click/swipe nav, and per-slide Horizon accent theming (H1 brand / H2 amber / H3 orange-red). Use when the user wants a ProFinda slide deck, roadmap/pitch/QBR/review presentation, or to add slides to one. Builds on profinda-design.
---

# ProFinda Decks

Build a deck by writing **content** — a list of slide dicts — and letting the engine render a ProFinda-branded, self-contained HTML deck. You never hand-write HTML/CSS. Follows the **`profinda-design`** language (load that skill for palette/type/components).

## Quick start

```python
# my_deck.py
from build_deck import build   # assets/build_deck.py

SLIDES = [
    {"layout": "cover", "title": 'Q3 <span class="accent">Business Review</span>',
     "subtitle": "Where we are, where we're going.",
     "notes": "Open warm; set the agenda."},
    {"layout": "bullets", "title": "Agenda",
     "items": ["Results", "What worked", "Next quarter"]},
    {"layout": "chart", "title": "Revenue", "eyebrow": "Results",
     "chart": {"type": "bar", "data": [["Q1", 120], ["Q2", 210], ["Q3", 340]]}},
    {"layout": "closing", "title": 'Thank you.', "subtitle": "Questions?"},
]
build(SLIDES, title="Q3 Business Review", out="Q3-Review.html")
```

```bash
python3 my_deck.py                       # writes ./Q3-Review.html
PF_DECK_OUT=~/Desktop python3 my_deck.py # choose output dir
python3 assets/build_deck.py --demo      # build the full layout showcase
```

The **layout showcase** (`assets/demo_content.py`) renders every layout and the Horizon themes — read it as living documentation and copy slides from it.

## The slide model

Every slide is a dict: `{"layout": <name>, ...fields}`. On **any** slide:
- `notes` — speaker notes (toggle with the on-cover control or `N`).
- `horizon` — `"h1"` (default, brand teal/green), `"h2"` (amber), `"h3"` (orange→red). Sets the accent for that slide; the **whole deck eases** to it as you arrive. Phasing only — not decoration, not status.
- `section` — the label shown top-right.
- Text fields accept inline HTML, so `<span class="accent">word</span>`, `<br>`, `&rarr;` etc. all work.

## Layout catalog

| layout | key fields |
|---|---|
| `cover` | `title`, `subtitle?`, `eyebrow?`, `stats?[{kicker,value,label,horizon}]`, `logo?` |
| `section` | `title`, `kicker?`, `body?` |
| `statement` | `title`, `body?`, `eyebrow?` |
| `quote` | `quote`, `attribution?`, `eyebrow?` |
| `bullets` | `title`, `items[str \| {text,icon}]`, `body?`, `eyebrow?` |
| `two-col` | `left`, `right` (each: `{heading,body}` / `{bullets}` / `{chart}` / `{media}` / `{glyph}`), `title?` |
| `media` | `media` (path / URL / data-URI), `caption?`, `title?`, `body?` |
| `gallery` | `items[{media,caption?}]`, `title?` |
| `chart` | `chart{type:bar\|line\|donut, data:[[label,value]], legend?}`, `title?`, `body?` |
| `stats` | `stats[{value,label,kicker?,horizon?}]`, `title?` |
| `big-number` | `value`, `label`, `body?` |
| `cards` | `cards[{heading,body,icon?}]`, `title?` |
| `table` | `columns[]`, `rows[[]]`, `title?` |
| `timeline` | `items[{when,heading,body}]`, `title?` |
| `compare` | `left{heading,items[]}`, `right{heading,items[]}` (right = the "pro" side), `title?` |
| `feature` | `title`, `body?`, `tag?`, `aka?`, `why?`, `why_label?`, `chips?[]`, `chips_label?`, `glyph?`, `index?`, `of?` — the hero-glyph "one big thing" slide |
| `closing` | `title`, `subtitle?`, `points?[]`, `logo?` |

**Icons** (bullets/cards/feature glyph): `spark chart list globe gear loop coin doc sparkle future grid rocket target shield users check cross clock bolt layers star`. Add more in `ICONS` in `build_deck.py` (keep the stroked-line style).

**Charts** are rendered as inline SVG at build time from your data — self-contained, and they adopt the slide's Horizon accent.

**Media**: local file paths are embedded as base64 (deck stays standalone); URLs and `data:` URIs pass through. `.mp4/.webm/.mov` render as autoplay-muted-loop video.

## Files

- `assets/build_deck.py` — the engine + `build()`. Import it, or run with `--demo`.
- `assets/demo_content.py` — the layout showcase (every layout + H2/H3).
- `assets/pf_logo.txt` — base64 logo, embedded into every deck.
- `assets/fonts/` — **Mulish** (the brand font) as base64 `.woff2` (latin + latin-ext), embedded into every deck via `@font-face` so it renders in the real brand font on any machine, with no font CDN. It's a variable font, so one file per subset covers weights 500–900. `OFL.txt` is the license (Mulish is SIL OFL — redistribution requires shipping it). To restyle the font, replace these files or edit `_font_face()`.
- `examples/roadmap/` — a real, hand-authored deck kept as a reference build (origin of the 3D flythrough + Horizon theming). New decks should use the engine, not copy this.

Env: `PF_DECK_OUT` (output dir), `PF_DECK_LOGO` (alternate logo).

## Guardrails

- Self-contained always: no external fonts/scripts/images. The brand font (Mulish) and local media are embedded as base64; verify no `src=`/`href=`/`@import` `http(s)` refs (including `fonts.googleapis.com`) remain.
- Write **content**; don't hand-author slide HTML. If a layout is missing, add a renderer to `LAYOUTS` in `build_deck.py` rather than injecting raw markup.
- Match `profinda-design`: brand teal/green, Mulish, glass, glow + star cloud, staggered entrances. Horizon amber/orange/red is phasing only.
- Honour `prefers-reduced-motion` (the engine already falls back to static/fade).

## Definition of done

- `build()` runs, writes one HTML file that opens standalone by double-click.
- Self-contained (only base64 assets, 0 external resource refs).
- Nav + speaker-notes (`N`) work; Horizon 2/3 slides retheme the whole deck.
- Content lives in a slide list; no bespoke HTML per slide.
