# ProFinda Design Language

The visual and interaction language for anything we put in front of a human under the ProFinda name: product UI, prototypes, presentations, marketing pages, documents, exports. It is AI-first, skills-led, enterprise-grade, and it should feel distinctly ProFinda: confident, precise, quietly alive.

This document is the source of truth. It is mirrored into Notion (SDLC → Development, referenced from Refinement for prototypes) and into the `profinda-design` skill in `ai-skills`, so both people and agents build to the same spec.

## Two themes, one palette

Everything is drawn from one brand palette. We apply it in two co-equal themes:

- **Light** — the default for the **platform / product UI**. White and light-gray neutrals, Carbon navy for text and structure, brand accents for emphasis and actions.
- **Dark** — the default for **presentations and prototypes**. A deep Carbon navy canvas with softly-lit glass surfaces, brand accents that glow against the dark.
- **profinda.com uses both**, section by section, which is the reference for mixing them.

Pick the theme by medium (see "Applying it by medium"), but never invent new hero colours: both themes come from the same tokens below.

## Brand palette (source of truth)

This is the official ProFinda palette. Confirmed in live use on profinda.com (`#0EAD9A`, `#8CC63F`, `#0094FF`). Treat these hexes as canonical.

### Primary — Blue

| Token | Hex | Role |
|---|---|---|
| Blue 1 | `#01338B` | Deep primary blue, strong emphasis, deep gradient stop |
| Blue 2 | `#1072EB` | Mid primary blue, links, interactive |
| Blue 3 | `#0094FF` | Bright primary blue, highlights, accents |

### Secondary — Teal & Green

| Token | Hex | Role |
|---|---|---|
| Teal | `#0EAD9A` | The signature ProFinda accent |
| Green | `#8CC63F` | Secondary accent, highlights, positive / "on" state |

### Secondary Dark — Carbon

Two ramps share the "Carbon" name in the brand sheet. To disambiguate we call them **Carbon** (deep navy) and **Carbon Steel** (cool slate). Watch the collision: both label their steps 1/2/3.

Carbon (deep navy — canvas, text, structure):

| Token | Hex | Role |
|---|---|---|
| Carbon 1 | `#131E2D` | Darkest navy: dark-theme canvas, light-theme headings/text |
| Carbon 2 | `#1D2D3D` | Mid navy: raised dark surfaces |
| Carbon 3 | `#203142` | Lighter navy: glyph cores, hovered dark surfaces |

Carbon Steel (cool slate — secondary text, borders, muted UI):

| Token | Hex | Role |
|---|---|---|
| Carbon Steel 1 | `#354556` | Strong slate: secondary text on light, borders on dark |
| Carbon Steel 2 | `#405466` | Mid slate: muted text, dividers |
| Carbon Steel 3 | `#A6B9BF` | Light slate: captions, disabled, hairlines on light |

### Grayscale — neutrals

| Token | Hex | Role |
|---|---|---|
| White | `#FFFFFF` | Light-theme canvas, text on dark |
| Gray 1 | `#EEEEEE` | Light surface / card fill |
| Gray 2 | `#DDDDDD` | Light borders, dividers |

### Gradients

Two canonical gradients (per the brand sheet):

- **Carbon** — deep navy vertical block, `linear-gradient(180deg, #203142, #131E2D)`. Dark canvases, glyph cores, deep panels.
- **Brand** — blue → teal → green, `linear-gradient(180deg, #0094FF, #0EAD9A, #8CC63F)`. The signature accent gradient: on emphasised words (via `background-clip:text`), rules, active indicators, primary affordances. Rotate the angle to taste (the deck uses ~92deg for inline text).

Never fill large flat areas with a brand accent. Accents live as gradients on text, thin rules, small dots, borders, and glows.

### Horizon accents (roadmap phasing)

ProFinda's colours are **blue, teal and green**. That is the brand, and it is the default for everything. But when we document **roadmap horizons** — near-term vs. later bets — we extend the accent palette with a warm ramp so the phase reads at a glance. These are **contextual accents, not new brand colours**: only use them to distinguish Horizon 2 / Horizon 3 initiatives or projects.

| Horizon | Meaning | Accent A | Accent B | Dark |
|---|---|---|---|---|
| **Horizon 1** | Core / near-term (the brand) | Teal `#0EAD9A` | Green `#8CC63F` | `#0A8377` |
| **Horizon 2** | Next bets (warm amber / gold) | `#F6C445` | `#E8A317` | `#B77C0C` |
| **Horizon 3** | Future / exploratory (orange → red) | `#F97316` | `#E23B2E` | `#B4231A` |

Applied exactly like the brand accent (gradient A→B on text/rules/indicators, glows from an rgba of A). Horizon 1 stays teal→green, so anything not explicitly a Horizon 2/3 item uses the normal brand accent.

```css
:root{
  /* Horizon 1 = brand (teal→green). */
  --h2a:#F6C445; --h2b:#E8A317; --h2-dark:#B77C0C;   /* Horizon 2: warm amber/gold */
  --h3a:#F97316; --h3b:#E23B2E; --h3-dark:#B4231A;   /* Horizon 3: orange→red      */
}
```

Guardrails: don't use amber/orange/red decoratively or for status (success/warning/error) — that's a separate concern. They mean "later horizon" and nothing else. The reference build (`ProFinda-Product-Roadmap-3D.html`) swaps the whole accent palette per horizon via `body.h2` / `body.h3`; see the `profinda-deck` skill.

## CSS tokens

Copy this as the canonical token set. Theme-specific roles are split into Light and Dark blocks that both reference the same brand values.

```css
:root{
  /* ---- Brand palette (theme-agnostic) ---- */
  --blue-1:#01338B; --blue-2:#1072EB; --blue-3:#0094FF;
  --teal:#0EAD9A;   --green:#8CC63F;
  --carbon-1:#131E2D; --carbon-2:#1D2D3D; --carbon-3:#203142;
  --steel-1:#354556;  --steel-2:#405466;  --steel-3:#A6B9BF;
  --white:#FFFFFF; --gray-1:#EEEEEE; --gray-2:#DDDDDD;

  --grad-brand:linear-gradient(92deg,var(--blue-3),var(--teal),var(--green));
  --grad-carbon:linear-gradient(180deg,var(--carbon-3),var(--carbon-1));
}

/* ---- Light theme (platform / product) ---- */
:root, .theme-light{
  --canvas:var(--white);
  --surface:var(--gray-1);
  --line:var(--gray-2);
  --ink:var(--carbon-1);      /* primary text  */
  --muted:var(--steel-1);     /* secondary text */
  --muted2:var(--steel-3);    /* captions       */
  --accent:var(--teal);
  --accent-2:var(--green);
  --link:var(--blue-2);
}

/* ---- Dark theme (decks / prototypes) ---- */
.theme-dark{
  --canvas:var(--carbon-1);
  --surface:rgba(255,255,255,.045);   /* glass */
  --line:rgba(255,255,255,.09);
  --ink:#EAF1F8;              /* near-white text */
  --muted:#C7D2DE;           /* slate body      */
  --muted2:#8FA1B3;          /* captions        */
  --accent:var(--teal);
  --accent-2:var(--green);
  --link:var(--blue-3);
}
```

> Dark-theme-only helper shades (`#EAF1F8`, `#C7D2DE`, `#8FA1B3`, glass alphas) are **derived, not brand tokens** — they exist to place near-white/slate text on the Carbon canvas. Don't introduce equivalents on light; use the Carbon/Steel ramps instead.

## Typography

- **Family:** `'Mulish','Inter',system-ui,-apple-system,sans-serif`. Mulish is the ProFinda face; Inter/system are fallbacks. For self-contained deliverables, either embed Mulish or accept the fallback — don't pull external font CDNs into files that must stand alone.
- **Headings:** `font-weight:900; line-height:1.06; letter-spacing:-.02em`. Big and tight. Use `clamp()` for fluid sizing (hero e.g. `clamp(44px,7.4vw,116px)`).
- **Body:** `--ink`/`--muted`, `font-weight:500`, `line-height:1.4–1.55`, measure ~`60ch`.
- **Eyebrow / kicker:** uppercase, `font-weight:800`, `letter-spacing:.22em`, colored `--accent`, usually preceded by a small dot or short gradient line.
- **Emphasis in prose:** wrap key words in the brand gradient rather than switching colour.
- **Selection:** `::selection{background:rgba(14,173,154,.35)}`.

```css
h1,h2,h3,h4{line-height:1.06;font-weight:900;letter-spacing:-.02em}
.accent{background:var(--grad-brand);
  -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.eyebrow{display:inline-flex;align-items:center;gap:11px;font-size:13px;font-weight:800;
  letter-spacing:.22em;text-transform:uppercase;color:var(--accent)}
```

## Surfaces, spacing, radius

- **Card (light):** `background:var(--surface); border:1px solid var(--line); border-radius:18px`. Padding ~`22–26px`.
- **Card (dark / glass):** `background:var(--surface); border:1px solid var(--line); border-radius:18px; backdrop-filter:blur(8px)`.
- **Radius scale:** pills `100px`; cards `14–18px`; icon tiles `12–13px`; chips `12px`.
- **Elevation:** avoid hard shadows in light UI; on dark, floating panels use soft, wide, dark shadows plus a 1px inset top highlight: `box-shadow:0 24px 70px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.05)`.
- **Rhythm:** generous whitespace, fluid gaps via `clamp()` (e.g. `clamp(20px,2.4vw,34px)`).

## Background system (dark theme)

Two layers give dark surfaces their signature depth. Both are `pointer-events:none`, sit behind content, and are expected on hero / marketing / presentation surfaces (optional for dense product UI).

1. **Glow field** — stacked low-alpha radial gradients in teal/blue/green over a Carbon linear base:

```css
background:
  radial-gradient(1100px 620px at 82% -8%, rgba(14,173,154,.20), transparent 60%),
  radial-gradient(900px 520px at 6% 116%, rgba(0,148,255,.16), transparent 55%),
  radial-gradient(700px 500px at 50% 120%, rgba(140,198,63,.10), transparent 60%),
  linear-gradient(160deg, var(--carbon-1) 0%, #0C1622 100%);
```

2. **Living constellation** — ~30 nodes drifting slowly, hairline links when close, nodes filled with a teal→green radial gradient. Slow ambient motion; honors reduced-motion (static render, no loop). Optional grain overlay at `opacity:.05`.

See `assets/profinda-background.html` in the `profinda-design` skill for a drop-in, self-contained implementation.

## Iconography

- **Style:** stroked line icons, 24×24 viewBox, `stroke-width:1.9`, `stroke-linecap:round`, `stroke-linejoin:round`, `fill:none`, `stroke:currentColor`. Colour via `color` on the parent (usually `--accent` or `--ink`).
- **Presentation:** icons live in rounded tiles (`border-radius:12px`, subtle fill, `--line` border) or inside a hero-glyph "core".
- Keep to the linear system; don't mix in flat/filled emoji-style icons in product or marketing surfaces.

```css
.icon{width:24px;height:24px;color:var(--accent)}
/* <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">…</svg> */
```

## Components

**Pill:** `border-radius:100px; background:var(--surface); border:1px solid var(--line); padding:11px 20px; font-weight:700` (add `backdrop-filter:blur(6px)` on dark). Stats, tags, small facts, toggles.

**Stat card:** card with a big number in a brand-gradient (`font-weight:900`) over a small `--muted` label.

**Chip (decomposition tag):** card-styled, `border-radius:12px`, preceded by a tiny 7px brand-gradient square. Breaks a concept into parts.

**Tag / accent callout:** left border in `--green` with a fading wash: `border-left:3px solid var(--green); background:linear-gradient(90deg,rgba(140,198,63,.09),transparent); border-radius:0 8px 8px 0`.

**Hero glyph:** concentric rotating rings (`--line`, dashed teal, green) around a rounded "core" holding one line icon that glows teal. The signature "intelligent object".

**Primary action / active state:** the brand gradient (filled for buttons, or as text/indicator). Exactly one primary action per view; everything else is a ghost/glass control.

## Motion

- **Entrance:** fade + rise + slight de-blur. `opacity 0→1`, `translateY(26px)→0`, `filter:blur(6px)→none`, `~.62s cubic-bezier(.2,.7,.2,1)`, staggered ~.1s per element (`.d1…d6`).
- **Ambient:** constellation drift and ring spins (20–34s linear loops). Slow enough to never distract.
- **State changes:** ~.2–.3s ease.
- **Always** wrap ambient motion in `@media (prefers-reduced-motion: reduce)` with a static fallback.

```css
.anim{opacity:0;transform:translateY(26px);filter:blur(6px);
  transition:opacity .62s cubic-bezier(.2,.7,.2,1),
             transform .62s cubic-bezier(.2,.7,.2,1),filter .62s ease}
.is-in .anim{opacity:1;transform:none;filter:none}
.is-in .anim.d1{transition-delay:.10s} /* …d2 .20s, d3 .30s, etc. */
```

## Applying it by medium

- **Product / platform UI → Light.** Palette, cards, line icons, one primary action, tight heavy headings. Background system minimal; density and legibility first.
- **Prototypes → Dark (usually).** Full language incl. background + entrance motion so refinement decisions are made against the real, finished-looking bar. Self-contained where possible. Match the platform theme if the prototype is a platform feature.
- **Presentations → Dark.** The full experience: glow + constellation, hero glyphs, staggered entrances, brand-gradient key words, stat/pill rows. (The Product Roadmap deck is the reference build.)
- **Marketing → Both.** profinda.com mixes light and dark section-by-section; brand-gradient headline words, cards, generous space throughout.
- **Documents / exports (CVs, reports) → Light/print.** Restrained. Keep the brand accent gradient, Mulish headings, the line-icon system, and hairline dividers so it still reads as ProFinda.

## Guardrails

- Treat the **brand hexes as canonical**; derive theme roles from them, don't invent new hero colours.
- Don't tint large surfaces with brand accents; accents are for text, lines, dots, borders, glows.
- Two "Carbon" ramps exist (deep navy vs. steel slate) — name them explicitly to avoid mixing them up.
- Horizon amber/orange/red accents are for roadmap phasing only (H2/H3) — not decoration, not status colours. Default to the brand teal→green.
- Don't mix icon styles; the stroked line set is the system.
- Don't pull external fonts/scripts/images into deliverables that must be self-contained.
- Don't ship motion that ignores `prefers-reduced-motion`.
- Keep contrast enterprise-grade: `--ink` on `--canvas` for body, not muted-on-canvas.

## Reference build

`~/Downloads/ProFinda-Product-Roadmap.html` (built by `build_deck.py`) is the canonical self-contained reference for the **dark** theme: palette, glass cards, hero glyphs, constellation background, chips, pills, stat cards, and the entrance/ambient motion. **profinda.com** is the reference for mixing light and dark. For **presentations specifically**, the 3D flythrough deck `ProFinda-Product-Roadmap-3D.html` (built by `build_deck_3d.py`) adds the Horizon accent theming and the 3D slide transitions — see the `profinda-deck` skill.
