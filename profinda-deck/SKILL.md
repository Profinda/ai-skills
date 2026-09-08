---
name: profinda-deck
description: Build ProFinda presentation decks — self-contained single-file HTML slide decks in the ProFinda design language, with keyboard/click navigation, speaker notes, a living-constellation background, hero glyphs and (optionally) a 3D flythrough between slides plus Horizon accent theming. Use when the user wants a ProFinda slide deck, roadmap presentation, pitch deck, or asks to build/update the Product Roadmap deck. Builds on the profinda-design skill.
---

# ProFinda Decks

Build slide decks that look and feel like ProFinda: a single self-contained HTML file (base64 assets, no external resources), navigable by arrows/click/swipe, with toggleable speaker notes, the constellation background, hero glyphs, chips/pills/stat cards, and staggered entrance motion.

Follows the **`profinda-design`** language — load that skill for the palette, tokens, typography, components and motion. This skill is the deck-specific builder on top of it.

## Two reference builds (bundled)

Both are Python scripts that assemble one HTML file. **Edit the script and re-run it — never hand-edit the generated HTML** (it gets overwritten).

| Script | Output | Use |
|---|---|---|
| [assets/build_deck.py](assets/build_deck.py) | `ProFinda-Product-Roadmap.html` | The flat deck: 2D cross-fade slide transitions. Simpler, lighter. |
| [assets/build_deck_3d.py](assets/build_deck_3d.py) | `ProFinda-Product-Roadmap-3D.html` | The 3D deck: camera flies through a star volume, slides arrive from the new angle. Adds **Horizon accent theming**. |

The bundled `ProFinda-Product-Roadmap-3D.html` reference (open the version in `~/Downloads/` or rebuild) is the canonical look:
`file:///Users/kikorb/Downloads/ProFinda-Product-Roadmap-3D.html`

### Assets
- `assets/pf_logo.txt` — base64 ProFinda logo, embedded into the deck. Bundled so the scripts are portable.

## Build

```bash
# writes the .html next to the script by default
python3 assets/build_deck_3d.py
# or choose an output directory:
PF_DECK_OUT=~/Downloads python3 assets/build_deck_3d.py
```

Env overrides: `PF_DECK_OUT` (output dir), `PF_DECK_LOGO` (alternate logo txt).

## Structure of a deck script

- `INITIATIVES` (or your content list) — the data that drives the repeated slides (title, summary, "why", keyword chips, clients, speaker `notes`).
- Inline `add(html, section, note)` calls build the framing slides (cover, philosophy, part band, close).
- One `<style>` block carries the full design language (copied from `profinda-design`).
- A small nav engine handles keys (← → ↑ ↓ PageUp/Down, Home/End, F fullscreen, N notes), click-to-advance, dots, swipe.

To change content: edit the data list / `add()` calls and rebuild. To restyle: edit the `:root` tokens and component CSS — keep them aligned with `profinda-design`.

## Horizon accent theming (the 3D deck)

ProFinda's colours are **blue, teal, green**. For roadmap **horizons** the 3D deck extends the accent palette with a warm ramp so the phase reads instantly. These are contextual accents for phasing, **not** new brand colours or status colours.

| Horizon | Meaning | A → B |
|---|---|---|
| Horizon 1 | Core / near-term (brand) | Teal `#0EAD9A` → Green `#8CC63F` |
| Horizon 2 | Next bets | Amber `#F6C445` → Gold `#E8A317` |
| Horizon 3 | Future / exploratory | Orange `#F97316` → Red `#E23B2E` |

Implemented as themeable accent variables that every accent surface eases between:

```css
:root{ --accA:var(--teal); --accB:var(--lime); /* Horizon 1 = default */
  --h2a:#F6C445; --h2b:#E8A317; --h2-dark:#B77C0C;
  --h3a:#F97316; --h3b:#E23B2E; --h3-dark:#B4231A; }
body.h2{ --accA:var(--h2a); --accB:var(--h2b); /* + glows */ }
body.h3{ --accA:var(--h3a); --accB:var(--h3b); /* + glows */ }
```

Add `h2` / `h3` to `<body>` (or per-`.stat` card the `h2`/`h3` class) for the horizon being shown; leave off for Horizon 1. All accent surfaces transition smoothly (0.9s ease) as horizons switch.

## Guardrails

- Keep the deck **fully self-contained**: no external fonts/scripts/images. Verify: `grep -c 'data:image/png;base64'` stays `2`, and there are **no** `src=`/`href=` `http(s)` refs.
- Don't break navigation (arrows, click, dots, swipe, F, Home/End, N notes).
- Edit the **script**, regenerate; don't hand-patch the HTML.
- Match `profinda-design`: navy canvas, teal/green brand accents, Mulish, glass cards, glow + constellation, staggered entrances.
- Horizon amber/orange/red is for phasing only — default to brand teal→green.
- Honour `prefers-reduced-motion` (both scripts already fall back to static/fade).

## Definition of done

- Script runs, writes one HTML file, opens standalone by double-click.
- Self-contained (2 base64 images, 0 external resource refs).
- Navigation + speaker-notes toggle (and `N`) work across all slides.
- Any Horizon 2/3 content uses the warm accents; everything else stays brand.
