---
name: profinda-design
description: Build anything visual in ProFinda's design language — product UI, prototypes, presentations, marketing pages, documents, exports. Covers the official brand palette (blue/teal/green/carbon/grays), Light and Dark themes, Mulish typography, glass surfaces, line icons, the constellation background, components and motion. Use when creating or styling any ProFinda-branded HTML/CSS, slide deck, prototype, landing page, CV/report export, or when the user mentions brand colors, look & feel, design system, or "make it look like ProFinda".
---

# ProFinda Design Language

Build to the ProFinda look: AI-first, skills-led, enterprise-grade — confident, precise, quietly alive. One brand palette, applied in two co-equal themes.

**Read [REFERENCE.md](REFERENCE.md) for the full spec** (canonical hexes, CSS tokens, components, motion). This file is the quick start.

## Themes

- **Light** → platform / product UI. White + light-gray neutrals, Carbon navy text, brand accents for emphasis.
- **Dark** → presentations & prototypes. Deep Carbon navy canvas, glass surfaces, glowing accents.
- **profinda.com** mixes both section-by-section.

Pick by medium (see REFERENCE "Applying it by medium"). Never invent hero colours — derive from the tokens.

## Brand palette (canonical — do not guess)

```
Blue 1 #01338B   Blue 2 #1072EB   Blue 3 #0094FF
Teal   #0EAD9A   Green  #8CC63F
Carbon 1 #131E2D   Carbon 2 #1D2D3D   Carbon 3 #203142   (deep navy)
Steel  1 #354556   Steel  2 #405466   Steel  3 #A6B9BF   (cool slate)
White  #FFFFFF   Gray 1 #EEEEEE   Gray 2 #DDDDDD
Brand gradient:  linear-gradient(92deg,#0094FF,#0EAD9A,#8CC63F)
Carbon gradient: linear-gradient(180deg,#203142,#131E2D)
```

Copy the full `:root` + `.theme-light` + `.theme-dark` token blocks from REFERENCE.md — don't hand-type hexes into components.

## Non-negotiables

- **Type:** Mulish (fallback Inter/system). Headings `font-weight:900; letter-spacing:-.02em; line-height:1.06`. Fluid sizes via `clamp()`. For self-contained files, embed Mulish as a base64 `@font-face` (it's SIL OFL) — `assets/profinda-background.html` does this; the `profinda-deck` skill bundles the `.woff2` under `assets/fonts/`. A bare `font-family` alone falls back to Inter/system where Mulish isn't installed.
- **Accents on text/lines/dots/borders/glows only** — never flood large fills with teal/green/blue.
- **Emphasis** = brand gradient on key words (`background-clip:text`), not a colour swap.
- **Icons:** stroked line set, 24×24, `stroke-width:1.9`, round caps/joins, `fill:none`, `stroke:currentColor`. Don't mix styles.
- **Surfaces:** cards `border-radius:14–18px`, hairline `--line` borders; on dark add `backdrop-filter:blur`.
- **Motion:** entrance = fade+rise+de-blur, `~.62s cubic-bezier(.2,.7,.2,1)`, staggered. Always guard ambient motion with `@media (prefers-reduced-motion: reduce)`.
- **Self-contained deliverables:** no external fonts/scripts/images.

## Quick start (dark, self-contained)

Drop [assets/profinda-background.html](assets/profinda-background.html) in as the base: it ships the `:root` tokens, glow field, living constellation (reduced-motion safe), and a `.accent` helper. Add your content on top.

## Workflow

1. Decide the **medium → theme** (product=Light, deck/prototype=Dark, marketing=both).
2. Paste the token blocks from REFERENCE.md; reference tokens, never raw hexes.
3. Compose with the documented components (pill, stat card, chip, accent callout, hero glyph).
4. Add entrance motion + (dark) the background system.
5. Check the guardrails list in REFERENCE.md before shipping.

## Reference build

The `profinda-deck` skill's `examples/sample.html` is the canonical dark-theme build; profinda.com is the light+dark reference.
