#!/usr/bin/env python3
"""
ProFinda deck engine — content-driven, single-file, self-contained HTML decks.

You write CONTENT (a list of slide dicts); this renders a ProFinda-branded deck
with the 3D star-cloud flythrough, speaker notes, keyboard/click/swipe nav,
progress + dots, fullscreen, and per-slide Horizon accent theming.

QUICK START
-----------
Define SLIDES (see the demo at the bottom, or examples/roadmap.py), then:

    python3 build_deck.py                     # writes ./ProFinda-Deck.html
    PF_DECK_OUT=~/Desktop python3 build_deck.py
    python3 build_deck.py --demo              # build the layout showcase deck

Or import and drive it from your own script:

    from build_deck import build
    build(SLIDES, title="Q3 Business Review", out="QBR.html")

SLIDE MODEL
-----------
Every slide is a dict: {"layout": <name>, ...fields, "notes": "...", "horizon": "h1|h2|h3"}
`notes` (speaker notes) and `horizon` (accent theme, default h1) are optional on ALL layouts.
See LAYOUTS below and the SKILL.md for the full field reference per layout.
"""
import base64, html as _html, json, os, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
LOGO = pathlib.Path(os.environ.get("PF_DECK_LOGO", HERE / "pf_logo.txt")).read_text().strip()
OUT_DIR = pathlib.Path(os.environ.get("PF_DECK_OUT", HERE))
FONT_DIR = HERE / "fonts"

def _font_face():
    """Embed Mulish (OFL) as base64 @font-face so the deck renders in the real
    brand font on any machine, staying fully self-contained (no font CDN).
    Mulish here is a variable font, so one file covers weights 500-900."""
    subsets = {
        "mulish-latin.woff2":
            "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,"
            "U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,"
            "U+2212,U+2215,U+FEFF,U+FFFD",
        "mulish-latin-ext.woff2":
            "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,"
            "U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,"
            "U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF",
    }
    faces = []
    for fname, urange in subsets.items():
        p = FONT_DIR / fname
        if not p.exists():
            continue
        b64 = base64.b64encode(p.read_bytes()).decode()
        faces.append(
            "@font-face{font-family:'Mulish';font-style:normal;font-weight:500 900;"
            "font-display:swap;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');"
            f"unicode-range:{urange};}}")
    return "\n".join(faces)

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def esc(s):
    return _html.escape(str(s), quote=True) if s is not None else ""

def rich(s):
    """Content text may contain **bold** and *accent* markers and literal HTML
    is passed through (so you can drop <br>, <span class=accent>, etc.)."""
    return "" if s is None else str(s)

def cls(*names):
    return " ".join(n for n in names if n)

def anim(d=0):
    return "anim" + (f" d{d}" if d else "")

# Icon set (stroked line icons, 24x24). Extend freely; keep the visual style.
ICONS = {
    "spark":'<path d="M12 2v6M12 16v6M2 12h6M16 12h6M5.6 5.6l4.2 4.2M14.2 14.2l4.2 4.2M18.4 5.6l-4.2 4.2M9.8 14.2l-4.2 4.2"/><circle cx="12" cy="12" r="3"/>',
    "chart":'<path d="M3 3v18h18"/><path d="M7 15l3-4 3 2 4-6"/>',
    "list":'<path d="M8 6h13M8 12h13M8 18h13"/><circle cx="3.6" cy="6" r="1.3" fill="currentColor" stroke="none"/><circle cx="3.6" cy="12" r="1.3" fill="currentColor" stroke="none"/><circle cx="3.6" cy="18" r="1.3" fill="currentColor" stroke="none"/>',
    "globe":'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/>',
    "gear":'<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9 17 7M7 17l-2.1 2.1"/>',
    "loop":'<path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 3v5h-5"/>',
    "coin":'<circle cx="12" cy="12" r="9"/><path d="M12 7v10M9.5 9.2a2.4 2.4 0 0 1 4.6.6M14.5 14.8a2.4 2.4 0 0 1-4.6-.6"/>',
    "doc":'<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>',
    "sparkle":'<path d="m12 3 2 5 5 2-5 2-2 5-2-5-5-2 5-2z"/>',
    "future":'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/><path d="M3 12h2M19 12h2"/>',
    "grid":'<rect x="3" y="3" width="7" height="7" rx="1.4"/><rect x="14" y="3" width="7" height="7" rx="1.4"/><rect x="3" y="14" width="7" height="7" rx="1.4"/><rect x="14" y="14" width="7" height="7" rx="1.4"/>',
    "rocket":'<path d="M5 15c-1.5 1-2 4-2 4s3-.5 4-2M9 12l6-6a6 6 0 0 1 5-2 6 6 0 0 1-2 5l-6 6zM9 12l3 3"/><circle cx="15" cy="9" r="1"/>',
    "target":'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none"/>',
    "shield":'<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "users":'<circle cx="9" cy="8" r="3"/><circle cx="17" cy="10" r="2.4"/><path d="M3 20a6 6 0 0 1 12 0M14 20a5 5 0 0 1 7-2.5"/>',
    "check":'<path d="M20 7 9 18l-5-5"/>',
    "cross":'<path d="M6 6l12 12M18 6 6 18"/>',
    "clock":'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "bolt":'<path d="M13 2 3 14h7l-1 8 10-12h-7z"/>',
    "layers":'<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5M3 18l9 5 9-5" opacity=".6"/>',
    "star":'<path d="m12 3 2.6 6.3 6.8.5-5.2 4.4 1.7 6.6L12 17.8 6.3 21.3l1.7-6.6L2.8 10.3l6.8-.5z"/>',
}
def icon_svg(name, extra=""):
    p = ICONS.get(name, ICONS["spark"])
    return (f'<svg class="ic {extra}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{p}</svg>')

def logo_src():
    return LOGO if LOGO.startswith("data:") else "data:image/png;base64," + LOGO

def media_src(m):
    """Accept a data: URI, an http(s) URL, or a local file path (embedded as base64)."""
    if not m:
        return ""
    if m.startswith("data:") or m.startswith("http"):
        return m
    p = pathlib.Path(m).expanduser()
    if p.exists():
        ext = p.suffix.lower().lstrip(".")
        mime = {"jpg":"jpeg","jpeg":"jpeg","png":"png","gif":"gif","webp":"webp","svg":"svg+xml",
                "mp4":"mp4","webm":"webm","mov":"quicktime"}.get(ext, ext)
        kind = "video" if ext in ("mp4","webm","mov") else "image"
        return f"data:{kind}/{mime};base64," + base64.b64encode(p.read_bytes()).decode()
    return m  # leave as-is; author's problem if it 404s

def eyebrow(text, d=0):
    if not text:
        return ""
    return f'<div class="eyebrow {anim(d)}"><span class="dot"></span>{esc(text)}</div>'

def chips(items, d=3):
    if not items:
        return ""
    inner = "".join(f'<span class="chip">{rich(c)}</span>' for c in items)
    return f'<div class="kw {anim(d)}">{inner}</div>'

# ---------------------------------------------------------------------------
# Inline SVG charts (rendered at build time from data — fully self-contained)
# ---------------------------------------------------------------------------
def chart_bar(series, w=560, h=300, horizon="h1"):
    vals = [float(v) for _, v in series]
    mx = max(vals + [1]); pad = 40; bw = (w - pad*2) / (len(series) or 1)
    bars, labels = [], []
    for i,(lbl,v) in enumerate(series):
        bh = (float(v)/mx) * (h - pad*2)
        x = pad + i*bw + bw*0.18; y = h - pad - bh; rw = bw*0.64
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{rw:.1f}" height="{bh:.1f}" rx="6" fill="url(#gBar)"/>')
        bars.append(f'<text x="{x+rw/2:.1f}" y="{y-8:.1f}" text-anchor="middle" class="cval">{esc(v)}</text>')
        labels.append(f'<text x="{x+rw/2:.1f}" y="{h-pad+20:.1f}" text-anchor="middle" class="clab">{esc(lbl)}</text>')
    return f'''<svg class="chart" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet">
      <defs><linearGradient id="gBar" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="var(--accA)"/><stop offset="100%" stop-color="var(--accB)"/></linearGradient></defs>
      <line x1="{pad}" y1="{h-pad}" x2="{w-pad}" y2="{h-pad}" class="cax"/>
      {''.join(bars)}{''.join(labels)}</svg>'''

def chart_line(series, w=560, h=300, horizon="h1"):
    vals=[float(v) for _,v in series]; mx=max(vals+[1]); mn=min(vals+[0]); rng=(mx-mn) or 1
    pad=40; step=(w-pad*2)/((len(series)-1) or 1)
    pts=[]
    for i,(_,v) in enumerate(series):
        x=pad+i*step; y=h-pad-((float(v)-mn)/rng)*(h-pad*2); pts.append((x,y))
    path="M"+" L".join(f"{x:.1f} {y:.1f}" for x,y in pts)
    area=path+f" L{pts[-1][0]:.1f} {h-pad} L{pts[0][0]:.1f} {h-pad} Z"
    dots="".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="var(--accB)"/>' for x,y in pts)
    labs="".join(f'<text x="{pad+i*step:.1f}" y="{h-pad+20:.1f}" text-anchor="middle" class="clab">{esc(l)}</text>'
                 for i,(l,_) in enumerate(series))
    return f'''<svg class="chart" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet">
      <defs><linearGradient id="gArea" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="var(--accA)" stop-opacity=".28"/><stop offset="100%" stop-color="var(--accA)" stop-opacity="0"/></linearGradient></defs>
      <line x1="{pad}" y1="{h-pad}" x2="{w-pad}" y2="{h-pad}" class="cax"/>
      <path d="{area}" fill="url(#gArea)"/>
      <path d="{path}" fill="none" stroke="var(--accA)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      {dots}{labs}</svg>'''

def chart_donut(series, w=320, h=320, horizon="h1"):
    total=sum(float(v) for _,v in series) or 1; cx,cy,r,th=w/2,h/2,120,34
    import math
    segs=[]; ang=-90; palette=["var(--accA)","var(--accB)","var(--blue-3)","var(--steel-3)","var(--h2a)","var(--h3a)"]
    for i,(lbl,v) in enumerate(series):
        frac=float(v)/total; a2=ang+frac*360
        large=1 if frac>0.5 else 0
        x1=cx+r*math.cos(math.radians(ang)); y1=cy+r*math.sin(math.radians(ang))
        x2=cx+r*math.cos(math.radians(a2)); y2=cy+r*math.sin(math.radians(a2))
        segs.append(f'<path d="M{x1:.1f} {y1:.1f} A{r} {r} 0 {large} 1 {x2:.1f} {y2:.1f}" '
                    f'fill="none" stroke="{palette[i%len(palette)]}" stroke-width="{th}"/>')
        ang=a2
    return f'''<svg class="chart donut" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet">
      {''.join(segs)}
      <text x="{cx}" y="{cy-4}" text-anchor="middle" class="dnum">{esc(int(total))}</text>
      <text x="{cx}" y="{cy+20}" text-anchor="middle" class="dlab">total</text></svg>'''

def chart_legend(series):
    palette=["var(--accA)","var(--accB)","var(--blue-3)","var(--steel-3)","var(--h2a)","var(--h3a)"]
    items="".join(f'<span class="lg"><i style="background:{palette[i%len(palette)]}"></i>{esc(l)} '
                  f'<b>{esc(v)}</b></span>' for i,(l,v) in enumerate(series))
    return f'<div class="legend">{items}</div>'

def render_chart(spec, horizon="h1"):
    kind=spec.get("type","bar"); data=spec.get("data",[])
    data=[(d[0], d[1]) for d in data]
    if kind=="line": svg=chart_line(data,horizon=horizon)
    elif kind=="donut": svg=chart_donut(data,horizon=horizon)
    else: svg=chart_bar(data,horizon=horizon)
    leg=chart_legend(data) if spec.get("legend") else ""
    return f'<div class="chartwrap">{svg}{leg}</div>'

# ---------------------------------------------------------------------------
# Hero glyph (the signature rotating-ring intelligent-object motif)
# ---------------------------------------------------------------------------
def glyph(icon="spark", d=2):
    return f'''<div class="glyph-wrap {anim(d)}"><div class="glyph">
      <div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div>
      <div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div>
      <div class="core">{icon_svg(icon)}</div></div></div>'''

# ===========================================================================
# LAYOUT RENDERERS  — each takes a slide dict, returns inner HTML
# ===========================================================================
def L_cover(s):
    stats=""
    if s.get("stats"):
        cells="".join(
            f'<div class="stat {("h2" if st.get("horizon")=="h2" else "h3" if st.get("horizon")=="h3" else "")}">'
            f'{f"<div class=hz>{esc(st["kicker"])}</div>" if st.get("kicker") else ""}'
            f'<div class="n">{rich(st.get("value",""))}</div><div class="l">{esc(st.get("label",""))}</div></div>'
            for st in s["stats"])
        stats=f'<div class="statrow {anim(4)}">{cells}</div>'
    logo=f'<img class="cover-logo {anim(0)}" src="{logo_src()}" alt="ProFinda">' if s.get("logo",True) else ""
    sub=f'<p class="sub {anim(3)}">{rich(s["subtitle"])}</p>' if s.get("subtitle") else ""
    return f'''<div class="cover">
      {logo}
      {eyebrow(s.get("eyebrow"),1)}
      <h1 class="{anim(2)}">{rich(s["title"])}</h1>
      {sub}{stats}</div>'''

def L_section(s):
    rule='<div class="rule '+anim(2)+'"></div>'
    cnt=f'<p class="cnt {anim(3)}">{rich(s["body"])}</p>' if s.get("body") else ""
    kick=f'<div class="kick {anim(0)}">{esc(s["kicker"])}</div>' if s.get("kicker") else ""
    return f'<div class="part">{kick}<h2 class="{anim(1)}">{rich(s["title"])}</h2>{rule}{cnt}</div>'

def L_statement(s):
    sub=f'<p class="lead {anim(2)}">{rich(s["body"])}</p>' if s.get("body") else ""
    return f'''<div class="statement">{eyebrow(s.get("eyebrow"),0)}
      <h2 class="{anim(1)}">{rich(s["title"])}</h2>{sub}</div>'''

def L_quote(s):
    who=f'<div class="qby {anim(2)}">{rich(s.get("attribution",""))}</div>' if s.get("attribution") else ""
    return f'''<div class="quote">{eyebrow(s.get("eyebrow"),0)}
      <blockquote class="{anim(1)}"><span class="qm">&ldquo;</span>{rich(s["quote"])}</blockquote>{who}</div>'''

def L_bullets(s):
    items="".join(
        f'<li class="{anim(3+min(i,3))}">'
        f'{icon_svg(b.get("icon","check")) if isinstance(b,dict) else icon_svg("check")}'
        f'<span>{rich(b["text"] if isinstance(b,dict) else b)}</span></li>'
        for i,b in enumerate(s["items"]))
    lead=f'<p class="lead {anim(2)}">{rich(s["body"])}</p>' if s.get("body") else ""
    return f'''<div class="bullets">{eyebrow(s.get("eyebrow"),0)}
      <h2 class="{anim(1)}">{rich(s.get("title",""))}</h2>{lead}
      <ul class="blist">{items}</ul></div>'''

def _column(col):
    if col.get("chart"): return render_chart(col["chart"], col.get("horizon","h1"))
    if col.get("media"): return _media_block(col)
    if col.get("glyph"): return glyph(col.get("glyph","spark"),2)
    if col.get("bullets"):
        items="".join(f'<li>{icon_svg(b.get("icon","check")) if isinstance(b,dict) else icon_svg("check")}'
                      f'<span>{rich(b["text"] if isinstance(b,dict) else b)}</span></li>'
                      for b in col["bullets"])
        return f'<ul class="blist">{items}</ul>'
    parts=[]
    if col.get("heading"): parts.append(f'<h3>{rich(col["heading"])}</h3>')
    if col.get("body"): parts.append(f'<p class="lead">{rich(col["body"])}</p>')
    return "".join(parts)

def L_two_col(s):
    left=s["left"]; right=s["right"]
    return f'''<div class="twocol-wrap">{eyebrow(s.get("eyebrow"),0)}
      {f'<h2 class="{anim(1)}">{rich(s["title"])}</h2>' if s.get("title") else ""}
      <div class="twocol {anim(2)}">
        <div class="tc-col">{_column(left)}</div>
        <div class="tc-col">{_column(right)}</div></div></div>'''

def _media_block(s):
    src=media_src(s.get("media"))
    is_vid = src.startswith("data:video") or any(src.split("?")[0].endswith(e) for e in (".mp4",".webm",".mov"))
    if is_vid:
        el=f'<video src="{src}" muted playsinline loop autoplay></video>'
    else:
        el=f'<img src="{src}" alt="{esc(s.get("alt",""))}">'
    cap=f'<figcaption>{rich(s["caption"])}</figcaption>' if s.get("caption") else ""
    return f'<figure class="media">{el}{cap}</figure>'

def L_media(s):
    body=f'<p class="lead {anim(2)}">{rich(s["body"])}</p>' if s.get("body") else ""
    head=""
    if s.get("title") or s.get("eyebrow"):
        head=f'{eyebrow(s.get("eyebrow"),0)}<h2 class="{anim(1)}">{rich(s.get("title",""))}</h2>{body}'
    return f'<div class="mediaslide">{head}<div class="{anim(3 if head else 1)}">{_media_block(s)}</div></div>'

def L_gallery(s):
    cells="".join(f'<div class="gcell {anim(2+min(i,4))}">{_media_block(m)}</div>'
                  for i,m in enumerate(s["items"]))
    return f'''<div class="gallery-wrap">{eyebrow(s.get("eyebrow"),0)}
      {f'<h2 class="{anim(1)}">{rich(s["title"])}</h2>' if s.get("title") else ""}
      <div class="gallery">{cells}</div></div>'''

def L_chart(s):
    body=f'<p class="lead {anim(2)}">{rich(s["body"])}</p>' if s.get("body") else ""
    return f'''<div class="chartslide">{eyebrow(s.get("eyebrow"),0)}
      <h2 class="{anim(1)}">{rich(s.get("title",""))}</h2>{body}
      <div class="{anim(3)}">{render_chart(s["chart"], s.get("horizon","h1"))}</div></div>'''

def L_stats(s):
    cells="".join(
        f'<div class="stat {anim(2+min(i,4))} {("h2" if st.get("horizon")=="h2" else "h3" if st.get("horizon")=="h3" else "")}">'
        f'{f"<div class=hz>{esc(st["kicker"])}</div>" if st.get("kicker") else ""}'
        f'<div class="n">{rich(st.get("value",""))}</div><div class="l">{esc(st.get("label",""))}</div></div>'
        for i,st in enumerate(s["stats"]))
    return f'''<div class="statsslide">{eyebrow(s.get("eyebrow"),0)}
      <h2 class="{anim(1)}">{rich(s.get("title",""))}</h2>
      <div class="statrow big">{cells}</div></div>'''

def L_bignumber(s):
    return f'''<div class="bignum">{eyebrow(s.get("eyebrow"),0)}
      <div class="bn {anim(1)}">{rich(s["value"])}</div>
      <div class="bnlab {anim(2)}">{rich(s["label"])}</div>
      {f'<p class="lead {anim(3)}">{rich(s["body"])}</p>' if s.get("body") else ""}</div>'''

def L_cards(s):
    n=len(s["cards"]); colcls="c3" if n%3==0 or n>4 else "c2" if n%2==0 else "c3"
    cells=[]
    for i,c in enumerate(s["cards"]):
        ic=f'<div class="ci">{icon_svg(c.get("icon","spark"))}</div>' if c.get("icon") else ""
        cells.append(f'<div class="card {anim(2+min(i,4))}">{ic}'
                     f'<h4>{rich(c.get("heading",""))}</h4>'
                     f'<p>{rich(c.get("body",""))}</p></div>')
    return f'''<div class="cards-wrap">{eyebrow(s.get("eyebrow"),0)}
      <h2 class="{anim(1)}">{rich(s.get("title",""))}</h2>
      <div class="cards {colcls}">{''.join(cells)}</div></div>'''

def L_table(s):
    head="".join(f"<th>{rich(h)}</th>" for h in s["columns"])
    rows="".join("<tr>"+"".join(f"<td>{rich(c)}</td>" for c in r)+"</tr>" for r in s["rows"])
    return f'''<div class="table-wrap">{eyebrow(s.get("eyebrow"),0)}
      <h2 class="{anim(1)}">{rich(s.get("title",""))}</h2>
      <table class="{anim(2)}"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'''

def L_timeline(s):
    steps=[]
    for i,it in enumerate(s["items"]):
        steps.append(f'<div class="tl-step {anim(2+min(i,4))}">'
                     f'<div class="tl-dot"></div>'
                     f'<div class="tl-when">{rich(it.get("when",""))}</div>'
                     f'<div class="tl-what"><h4>{rich(it.get("heading",""))}</h4>'
                     f'<p>{rich(it.get("body",""))}</p></div></div>')
    return f'''<div class="timeline-wrap">{eyebrow(s.get("eyebrow"),0)}
      <h2 class="{anim(1)}">{rich(s.get("title",""))}</h2>
      <div class="timeline">{''.join(steps)}</div></div>'''

def L_compare(s):
    def side(col, kind):
        items="".join(f'<li>{icon_svg("check" if kind=="pro" else "cross")}<span>{rich(x)}</span></li>'
                      for x in col.get("items",[]))
        return (f'<div class="cmp {kind}"><div class="cmp-h">{rich(col.get("heading",""))}</div>'
                f'<ul>{items}</ul></div>')
    return f'''<div class="compare-wrap">{eyebrow(s.get("eyebrow"),0)}
      <h2 class="{anim(1)}">{rich(s.get("title",""))}</h2>
      <div class="compare {anim(2)}">{side(s["left"],"con")}{side(s["right"],"pro")}</div></div>'''

def L_feature(s):
    """Big hero glyph + intro + why box + decomposition chips (the roadmap-initiative layout, generalised)."""
    aka=f'<div class="aka {anim(1)}"><span class="ic">&#8627;</span>{rich(s["aka"])}</div>' if s.get("aka") else ""
    tag=f'<div class="tag {anim(2)}">{rich(s["tag"])}</div>' if s.get("tag") else ""
    num=""
    if s.get("index"):
        num=f'<div class="init-num {anim(0)}">{esc(s["index"])} <span class="of">{esc(s.get("of",""))}</span><span class="bar"></span></div>'
    why=""
    if s.get("why"):
        wl=s.get("why_label","Why it matters —")
        why=f'<div class="col-why"><p class="why {anim(4)}"><b>{esc(wl)}</b> {rich(s["why"])}</p></div>'
    kw=""
    if s.get("chips"):
        kw=(f'<div class="col-kw"><div class="kw-wrap {anim(3)}">'
            f'<div class="kw-head">{esc(s.get("chips_label","What it includes"))}</div>'
            f'{chips(s["chips"],0)}</div></div>')
    return f'''<div class="init">{num}
      <div class="init-grid">
        <div class="col-intro"><h2 class="{anim(1)}">{rich(s["title"])}</h2>{aka}{tag}
          {f'<p class="summary {anim(3)}">{rich(s["body"])}</p>' if s.get("body") else ""}</div>
        <div class="col-glyph">{glyph(s.get("glyph","spark"),2)}</div>
        {why}{kw}</div></div>'''

def L_closing(s):
    logo=f'<img class="cover-logo {anim(0)}" src="{logo_src()}" alt="ProFinda" style="margin-bottom:34px">' if s.get("logo",True) else ""
    sub=f'<p class="sub {anim(2)}">{rich(s["subtitle"])}</p>' if s.get("subtitle") else ""
    pts=""
    if s.get("points"):
        cells="".join(f'<div class="b"><span>{i+1}</span>{rich(p)}</div>' for i,p in enumerate(s["points"]))
        pts=f'<div class="three {anim(3)}">{cells}</div>'
    return f'''<div class="closing" style="text-align:center;display:flex;flex-direction:column;align-items:center">
      {logo}<h2 class="{anim(1)}">{rich(s["title"])}</h2>{sub}{pts}</div>'''

LAYOUTS = {
    "cover": L_cover, "section": L_section, "statement": L_statement, "quote": L_quote,
    "bullets": L_bullets, "two-col": L_two_col, "media": L_media, "gallery": L_gallery,
    "chart": L_chart, "stats": L_stats, "big-number": L_bignumber, "cards": L_cards,
    "table": L_table, "timeline": L_timeline, "compare": L_compare, "feature": L_feature,
    "closing": L_closing,
}

def render_slide(s):
    layout=s.get("layout","statement")
    fn=LAYOUTS.get(layout)
    if not fn:
        raise ValueError(f"Unknown layout '{layout}'. Available: {', '.join(sorted(LAYOUTS))}")
    return fn(s)

# ---------------------------------------------------------------------------
# Assemble the deck
# ---------------------------------------------------------------------------
def build(slides, title="ProFinda Deck", out="ProFinda-Deck.html", edit=False, subtitle_counter=True):
    """Render a deck. Set edit=True to include presenter Edit mode (press E):
    in-place editing of text/chips/notes, a Save/Export/Reset bar, edits
    persisted to localStorage and exportable to a fresh baked-in .html.
    Leave edit=False for clean audience-only decks."""
    payload=[]
    for i,s in enumerate(slides):
        inner=render_slide(s)
        section=s.get("section", s.get("layout","").title())
        payload.append({"html":inner,"section":section,"note":s.get("notes",""),"horizon":s.get("horizon","h1")})
    data_json=json.dumps({"slides":payload}, ensure_ascii=False)
    doc=(TEMPLATE
         .replace("/*__FONTS__*/", _font_face())
         .replace("/*__EDIT_CSS__*/", EDIT_CSS if edit else "")
         .replace("<!--__EDIT_BAR__-->", EDIT_BAR if edit else "")
         .replace("<!--__EDIT_HINT__-->", EDIT_HINT if edit else "")
         .replace("/*__EDIT_JS__*/", EDIT_JS if edit else "")
         .replace("__TITLE__", esc(title))
         .replace("__LOGO__", logo_src())
         .replace("__DATA__", data_json))
    outp = (OUT_DIR / out) if not os.path.isabs(out) else pathlib.Path(out)
    outp.write_text(doc, encoding="utf-8")
    print("Wrote", outp, len(doc), "bytes,", len(slides), "slides", "(edit mode)" if edit else "")
    return outp

# ---------------------------------------------------------------------------
# Edit mode (opt-in via build(edit=True)) — injected into the template when on.
# ---------------------------------------------------------------------------
EDIT_CSS = r"""
/* ---------- Edit mode (presenter-only; toggle with E) ---------- */
body.editing [data-edit]{outline:1.5px dashed rgba(255,255,255,.22);outline-offset:4px;border-radius:6px;cursor:text;transition:outline-color .15s ease,background .15s ease}
body.editing [data-edit]:hover{outline-color:var(--accA);background:rgba(255,255,255,.03)}
body.editing [data-edit]:focus{outline:2px solid var(--accA);background:rgba(255,255,255,.05)}
body.editing .slide.active .anim{opacity:1 !important;transform:none !important;filter:none !important;transition:none !important}
body.editing .slide.active .chip{opacity:1 !important;transform:none !important}
body.editing .kw .chip{position:relative;cursor:text}
body.editing .kw .chip .chip-x{display:inline-grid;place-items:center;margin-left:8px;width:16px;height:16px;border-radius:50%;background:rgba(226,59,46,.9);color:#fff;font-size:12px;font-weight:900;line-height:1;cursor:pointer;vertical-align:middle}
body.editing .kw .chip .chip-x::before{content:"\00d7"}
.chip .chip-x{display:none}
body.editing .kw .chip-add{cursor:pointer;border-style:dashed;color:var(--accA);opacity:1 !important}
.chip-add{display:none}
body.editing .chip-add{display:inline-flex;align-items:center}
#editBar{position:fixed;top:16px;left:50%;transform:translateX(-50%) translateY(-14px);z-index:60;display:none;align-items:center;gap:12px;padding:9px 14px;border-radius:999px;background:rgba(12,22,34,.92);border:1px solid var(--line);backdrop-filter:blur(14px);box-shadow:0 10px 40px rgba(0,0,0,.5);opacity:0;transition:opacity .25s ease,transform .25s ease;font-size:13px;color:var(--slate)}
body.editing #editBar{display:flex;opacity:1;transform:translateX(-50%) translateY(0)}
#editBar .eb-tag{font-weight:800;letter-spacing:.14em;text-transform:uppercase;font-size:10.5px;color:var(--accA)}
#editBar .eb-dirty{color:var(--h2a);font-weight:700}
#editBar button{font:inherit;font-weight:800;cursor:pointer;border-radius:999px;padding:7px 16px;border:1px solid var(--line);background:transparent;color:var(--ink);transition:all .15s ease}
#editBar .eb-save{border-color:var(--accA);color:var(--accA)}
#editBar .eb-save:hover{background:var(--accA);color:#06121b}
#editBar .eb-save:disabled{opacity:.4;cursor:default;border-color:var(--line);color:var(--muted2);background:transparent}
#editBar .eb-export:hover{border-color:var(--green);color:var(--green)}
#editBar .eb-reset:hover{border-color:var(--h3b);color:var(--h3b)}
body.editing #notesPanel{outline:1.5px dashed rgba(255,255,255,.22);outline-offset:4px}
body.editing #notesPanel .np-body[contenteditable]{cursor:text;min-height:1.4em}
"""

EDIT_BAR = r"""
<div id="editBar" aria-hidden="true">
  <span class="eb-tag">Edit mode</span>
  <span class="eb-status" id="ebStatus">No changes</span>
  <button class="eb-save" id="ebSave" disabled>Save slide</button>
  <button class="eb-export" id="ebExport" title="Download a copy of the deck with all edits baked in">Export .html</button>
  <button class="eb-reset" id="ebReset" title="Discard all saved edits">Reset edits</button>
</div>
"""

EDIT_HINT = r""" &middot; <span class="key">E</span> edit"""

EDIT_JS = r"""
/* ---------- Edit mode (presenter-only; toggle with E) ----------
   In-place editing of slide text, chips and speaker notes. Edits are held in an
   overrides buffer (localStorage) replayed onto each slide, and can be exported
   to a fresh self-contained .html with the changes baked in. */
const EDIT_KEY='pf_overrides_v1';
let editMode=false;
let overrides={};
try{ overrides = JSON.parse(localStorage.getItem(EDIT_KEY)||'{}') || {}; }catch(e){ overrides={}; }

// Text nodes made directly editable, keyed to the engine's own layout classes.
const EDIT_SEL = [
  '.cover h1','.cover .sub','.statement h2','.statement .lead',
  '.part h2','.part .cnt','.part .kick','.quote blockquote','.quote .qby',
  '.bullets h2','.bullets .lead','.blist li span','.twocol-wrap h2','.tc-col h3','.tc-col .lead',
  '.mediaslide h2','.mediaslide .lead','.media figcaption','.gallery-wrap h2',
  '.chartslide h2','.chartslide .lead','.statsslide h2','.stat .n','.stat .l','.stat .hz',
  '.bignum .bn','.bignum .bnlab','.bignum .lead','.cards-wrap h2','.card h4','.card p',
  '.table-wrap h2','.table-wrap td','.timeline-wrap h2','.tl-when','.tl-what h4','.tl-what p',
  '.compare-wrap h2','.cmp-h','.cmp li span',
  '.init h2','.aka','.tag','.summary','.why','.kw-head',
  '.closing h2','.closing .sub','.closing .three .b'
].join(',');

function persistOverrides(){ try{ localStorage.setItem(EDIT_KEY, JSON.stringify(overrides)); }catch(e){} }
function captureSlide(i){
  const inner = slides[i].el.querySelector('.slide-inner');
  const clone = inner.cloneNode(true);
  clone.querySelectorAll('[contenteditable]').forEach(el=>el.removeAttribute('contenteditable'));
  clone.querySelectorAll('[data-edit]').forEach(el=>el.removeAttribute('data-edit'));
  clone.querySelectorAll('.chip-x,.chip-add').forEach(el=>el.remove());
  overrides[i] = { html: clone.innerHTML, note: slides[i].note };
  persistOverrides();
}
function applyOverrides(){
  Object.keys(overrides).forEach(k=>{
    const i=+k, o=overrides[k]; if(!slides[i]||!o) return;
    if(o.html!=null) slides[i].el.querySelector('.slide-inner').innerHTML=o.html;
    if(o.note!=null) slides[i].note=o.note;
  });
}
let slideDirty=false;
function markDirty(){ if(!editMode) return; slideDirty=true; updateEditBar(); }
function makeChipControls(kw){
  if(!kw) return;
  kw.querySelectorAll('.chip-add').forEach(el=>el.remove());
  kw.querySelectorAll('.chip .chip-x').forEach(el=>el.remove());
  kw.querySelectorAll('.chip').forEach(chip=>{
    const x=document.createElement('span'); x.className='chip-x'; x.title='Remove pill';
    x.addEventListener('click',e=>{ e.stopPropagation(); chip.remove(); markDirty(); });
    chip.appendChild(x);
  });
  const add=document.createElement('span'); add.className='chip chip-add'; add.textContent='+ add';
  add.addEventListener('click',e=>{
    e.stopPropagation();
    const chip=document.createElement('span'); chip.className='chip'; chip.textContent='New item';
    kw.insertBefore(chip,add); enableChip(chip); markDirty();
    chip.setAttribute('contenteditable','true'); chip.focus(); document.getSelection().selectAllChildren(chip);
  });
  kw.appendChild(add);
}
function enableChip(chip){
  chip.setAttribute('contenteditable','true');
  const x=document.createElement('span'); x.className='chip-x'; x.title='Remove pill';
  x.addEventListener('click',e=>{ e.stopPropagation(); chip.remove(); markDirty(); });
  chip.appendChild(x);
}
function enterEditOnSlide(i){
  const el=slides[i].el;
  el.querySelectorAll(EDIT_SEL).forEach(node=>{
    node.setAttribute('data-edit',''); node.setAttribute('contenteditable','true'); node.setAttribute('spellcheck','false');
  });
  el.querySelectorAll('.kw').forEach(makeChipControls);
  notesBody.setAttribute('contenteditable','true'); notesBody.setAttribute('data-edit','');
}
function leaveEditOnSlide(i){
  const el=slides[i].el;
  el.querySelectorAll('[contenteditable]').forEach(n=>n.removeAttribute('contenteditable'));
  el.querySelectorAll('[data-edit]').forEach(n=>n.removeAttribute('data-edit'));
  el.querySelectorAll('.chip-add').forEach(n=>n.remove());
  el.querySelectorAll('.chip .chip-x').forEach(n=>n.remove());
  notesBody.removeAttribute('contenteditable'); notesBody.removeAttribute('data-edit');
}
const editBar=document.getElementById('editBar');
const ebSave=document.getElementById('ebSave');
const ebStatus=document.getElementById('ebStatus');
function updateEditBar(){
  if(!editMode) return;
  ebSave.disabled=!slideDirty;
  ebStatus.textContent = slideDirty ? 'Unsaved changes' : (overrides[cur]?'Saved (edited)':'No changes');
  ebStatus.className = 'eb-status'+(slideDirty?' eb-dirty':'');
}
function saveCurrent(){ captureSlide(cur); slideDirty=false; updateEditBar(); }
function refreshEditUIForSlide(){
  if(!editMode) return;
  slides.forEach((s,i)=>leaveEditOnSlide(i));
  enterEditOnSlide(cur); slideDirty=false; updateEditBar();
}
function setEdit(on){
  editMode=on;
  document.body.classList.toggle('editing',on);
  if(on){ notesPanel.classList.add('show'); enterEditOnSlide(cur); slideDirty=false; updateEditBar(); }
  else{ slides.forEach((s,i)=>leaveEditOnSlide(i)); renderNotes(); }
}
document.getElementById('slides').addEventListener('input',e=>{ if(editMode) markDirty(); });
notesBody.addEventListener('input',e=>{ if(editMode){ slides[cur].note=notesBody.textContent; markDirty(); } });
if(ebSave) ebSave.addEventListener('click',e=>{e.stopPropagation();saveCurrent();});
const ebExportBtn=document.getElementById('ebExport');
if(ebExportBtn) ebExportBtn.addEventListener('click',e=>{e.stopPropagation();exportDeck();});
const ebResetBtn=document.getElementById('ebReset');
if(ebResetBtn) ebResetBtn.addEventListener('click',e=>{
  e.stopPropagation();
  if(!confirm('Discard ALL saved edits and reload the original deck?')) return;
  overrides={}; persistOverrides(); location.reload();
});
function exportDeck(){
  if(slideDirty) saveCurrent();
  const doc=document.documentElement.cloneNode(true);
  const docHead=doc.querySelector('head'), docBody=doc.querySelector('body');
  const slidesHost=doc.querySelector('#slides'); if(slidesHost) slidesHost.innerHTML='';
  doc.querySelectorAll('.dots').forEach(d=>d.innerHTML='');
  if(docBody) docBody.classList.remove('editing');
  doc.querySelectorAll('[contenteditable]').forEach(n=>n.removeAttribute('contenteditable'));
  doc.querySelectorAll('[data-edit]').forEach(n=>n.removeAttribute('data-edit'));
  doc.querySelectorAll('.chip-x,.chip-add').forEach(n=>n.remove());
  let inject=doc.querySelector('#pfBakedOverrides');
  if(!inject){ inject=document.createElement('script'); inject.id='pfBakedOverrides'; if(docHead) docHead.insertBefore(inject, docHead.firstChild); }
  inject.textContent='window.__PF_BAKED_OVERRIDES='+JSON.stringify(overrides)+';';
  const html='<!DOCTYPE html>\n'+doc.outerHTML;
  const blob=new Blob([html],{type:'text/html'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='ProFinda-Deck.html';
  document.body.appendChild(a); a.click();
  setTimeout(()=>{ URL.revokeObjectURL(a.href); a.remove(); }, 1000);
}
if(window.__PF_BAKED_OVERRIDES){
  try{ const baked=window.__PF_BAKED_OVERRIDES; if(!Object.keys(overrides).length){ overrides=baked; persistOverrides(); } }catch(e){}
}
applyOverrides();
window.addEventListener('keydown',e=>{
  const typing = e.target && (e.target.isContentEditable || /^(INPUT|TEXTAREA)$/.test(e.target.tagName));
  if(typing){ if(e.key==='Escape'){ e.target.blur(); } return; }
  if(e.key==='e'||e.key==='E'){ e.preventDefault(); setEdit(!editMode); }
});
"""

# The HTML shell (CSS design system + JS engine). __DATA__ is the slide payload.
TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<style>
/*__FONTS__*/
/*__EDIT_CSS__*/
:root{
  --navy:#131E2D; --navy2:#203142; --navy3:#0C1622; --navy-soft:#1B2A3B;
  --teal:#0EAD9A; --teal-dark:#0A8377; --lime:#8CC63F; --lime-dark:#6fa02f;
  --blue-1:#01338B; --blue-2:#1072EB; --blue-3:#0094FF;
  --steel-1:#354556; --steel-2:#405466; --steel-3:#A6B9BF;
  /* Horizon accents. H1 = brand (teal->lime). H2 = amber/gold. H3 = orange->red. */
  --h2a:#F6C445; --h2b:#E8A317; --h2-dark:#B77C0C;
  --h3a:#F97316; --h3b:#E23B2E; --h3-dark:#B4231A;
  --slate:#C7D2DE; --muted:#8FA1B3; --muted2:#6B7C8E;
  --ink:#EAF1F8; --line:rgba(255,255,255,.09);
  /* Themeable accents; body.h2/.h3 swap them and every accent surface eases over. */
  --accA:var(--teal); --accB:var(--lime); --accDark:var(--teal-dark);
  --accGlow:rgba(14,173,154,.6); --accGlowSoft:rgba(14,173,154,.18); --accGlow2:rgba(140,198,63,.6);
}
body.h2{ --accA:var(--h2a); --accB:var(--h2b); --accDark:var(--h2-dark);
  --accGlow:rgba(246,196,69,.6); --accGlowSoft:rgba(246,196,69,.20); --accGlow2:rgba(232,163,23,.6); }
body.h3{ --accA:var(--h3a); --accB:var(--h3b); --accDark:var(--h3-dark);
  --accGlow:rgba(249,115,22,.6); --accGlowSoft:rgba(249,115,22,.20); --accGlow2:rgba(226,59,46,.62); }
/* Smoothly ease every accent surface as the horizon changes. */
.progress,.dots i,.accent,.eyebrow .dot,.eyebrow .ln,.eyebrow,.init-num,.tag,.why b,
.chip::before,.glyph .core svg,.glyph .orb,.glyph .r2,.glyph .r3,.part .kick,.part .rule,
.counter b,.na,.notes-toggle b,.three .b span,.kick,.stat::before,.stat .hz,.stat .n,
.blist svg,.card .ci,.tl-dot,.cmp.pro .cmp-h,.bn,.qm,.chart{
  transition:color .9s ease, background .9s ease, background-color .9s ease,
    border-color .9s ease, box-shadow .9s ease, fill .9s ease, filter .9s ease,
    stroke .9s ease, -webkit-text-fill-color .9s ease;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{font-family:'Mulish','Inter',system-ui,-apple-system,sans-serif;
  background:var(--navy3); color:var(--ink); -webkit-font-smoothing:antialiased; cursor:default;}
h1,h2,h3,h4{line-height:1.06;font-weight:900;letter-spacing:-.02em}
::selection{background:rgba(14,173,154,.35)}

/* ---------- Stage / background ---------- */
#stage{position:fixed;inset:0;overflow:hidden}
.bg-net{position:absolute;inset:0;z-index:0;opacity:.9;pointer-events:none;width:100%;height:100%}
#slides{position:absolute;inset:0;perspective:1400px;perspective-origin:50% 50%;transform-style:preserve-3d}
.bg-glow{position:absolute;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(1100px 620px at 82% -8%,rgba(14,173,154,.20),transparent 60%),
    radial-gradient(900px 520px at 6% 116%,rgba(0,148,255,.16),transparent 55%),
    radial-gradient(700px 500px at 50% 120%,rgba(140,198,63,.10),transparent 60%),
    linear-gradient(160deg,var(--navy) 0%,var(--navy3) 100%);}
.grain{position:absolute;inset:0;z-index:1;pointer-events:none;opacity:.05;
  background-image:radial-gradient(rgba(255,255,255,.6) .5px,transparent .5px);background-size:3px 3px;}

.slide{position:absolute;inset:0;z-index:2;display:flex;align-items:center;justify-content:center;
  padding:clamp(28px,4.4vw,84px);opacity:0;visibility:hidden;pointer-events:none;
  transform-style:preserve-3d;transform-origin:50% 50%;
  transform:translate3d(var(--sx,0px),var(--sy,0px),var(--sz,-620px)) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg));
  transition:opacity .7s ease, transform 1.35s cubic-bezier(.19,.72,.16,1);}
.slide.active{opacity:1;visibility:visible;pointer-events:auto;transform:translate3d(0,0,0) rotateX(0) rotateY(0)}
.slide-inner{width:100%;max-width:1500px;position:relative}

.anim{opacity:0;transform:translateY(26px);filter:blur(6px);
  transition:opacity .62s cubic-bezier(.2,.7,.2,1),transform .62s cubic-bezier(.2,.7,.2,1),filter .62s ease;}
.slide.active .anim{opacity:1;transform:none;filter:none}
.slide.active .anim.d1{transition-delay:.10s}.slide.active .anim.d2{transition-delay:.20s}
.slide.active .anim.d3{transition-delay:.30s}.slide.active .anim.d4{transition-delay:.40s}
.slide.active .anim.d5{transition-delay:.50s}.slide.active .anim.d6{transition-delay:.60s}

/* ---------- Shared type ---------- */
.eyebrow{display:inline-flex;align-items:center;gap:11px;font-size:clamp(11px,1vw,13.5px);font-weight:800;
  letter-spacing:.22em;text-transform:uppercase;color:var(--accA);margin-bottom:20px}
.eyebrow .ln{width:38px;height:2px;background:linear-gradient(90deg,var(--accA),transparent)}
.eyebrow .dot{width:8px;height:8px;border-radius:50%;background:var(--accA);box-shadow:0 0 0 5px var(--accGlowSoft)}
.accent{background:linear-gradient(92deg,var(--accA),var(--accB));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.lead{font-size:clamp(16px,1.7vw,23px);color:var(--slate);max-width:64ch;margin-top:20px;line-height:1.5;font-weight:500}
.lead em{color:#fff;font-style:normal;font-weight:800}
.ic{width:24px;height:24px;color:var(--accA)}

/* ---------- Cover ---------- */
.cover h1{font-size:clamp(44px,7.4vw,112px);line-height:.98}
.cover .sub{font-size:clamp(17px,2vw,27px);color:var(--slate);max-width:34ch;margin-top:26px;font-weight:500;line-height:1.4}
.cover-logo{height:34px;margin-bottom:40px;filter:drop-shadow(0 4px 20px rgba(0,0,0,.4))}
.statrow{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:44px;max-width:900px}
.statrow.big{max-width:1100px}
.stat{position:relative;overflow:hidden;background:rgba(255,255,255,.045);border:1px solid var(--line);
  border-radius:18px;padding:22px 20px;backdrop-filter:blur(8px)}
.stat::before{content:"";position:absolute;top:0;left:0;width:100%;height:4px;background:linear-gradient(90deg,var(--accA),var(--accB))}
.stat .hz{font-size:10.5px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:var(--accA);margin-bottom:9px}
.stat .n{font-size:clamp(22px,2.7vw,38px);font-weight:900;letter-spacing:-.02em;line-height:1.08;
  background:linear-gradient(90deg,#fff,var(--accA));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.stat .l{font-size:13px;color:var(--slate);font-weight:600;margin-top:6px;line-height:1.35}
.stat.h2::before{background:linear-gradient(90deg,var(--h2a),var(--h2b))}
.stat.h2 .hz{color:var(--h2a)}.stat.h2 .n{background:linear-gradient(90deg,#fff,var(--h2a));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.stat.h3::before{background:linear-gradient(90deg,var(--h3a),var(--h3b))}
.stat.h3 .hz{color:var(--h3a)}.stat.h3 .n{background:linear-gradient(90deg,#fff,var(--h3a));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}

/* ---------- Section band ---------- */
.part .kick{font-size:clamp(13px,1.3vw,17px);font-weight:800;letter-spacing:.24em;text-transform:uppercase;color:var(--accA);margin-bottom:18px}
.part h2{font-size:clamp(36px,6vw,92px)}
.part .rule{height:5px;width:120px;background:linear-gradient(90deg,var(--accA),var(--accB));border-radius:3px;margin-top:26px;box-shadow:0 0 30px var(--accGlow)}
.part .cnt{margin-top:26px;font-size:clamp(15px,1.6vw,20px);color:var(--slate);max-width:56ch;line-height:1.5}

/* ---------- Statement ---------- */
.statement h2{font-size:clamp(30px,4.8vw,72px);max-width:20ch}
.statement .lead{max-width:60ch}

/* ---------- Quote ---------- */
.quote blockquote{font-size:clamp(26px,3.8vw,56px);font-weight:900;letter-spacing:-.02em;line-height:1.12;max-width:22ch;position:relative}
.quote .qm{color:var(--accA);font-size:1.2em;margin-right:.06em}
.quote .qby{margin-top:28px;font-size:clamp(14px,1.4vw,18px);color:var(--muted);font-weight:700}

/* ---------- Bullets ---------- */
.bullets h2{font-size:clamp(28px,4vw,58px)}
.blist{list-style:none;margin-top:34px;display:flex;flex-direction:column;gap:16px;max-width:70ch}
.blist li{display:flex;align-items:flex-start;gap:15px;font-size:clamp(15px,1.6vw,21px);color:var(--slate);font-weight:500;line-height:1.4}
.blist svg{width:26px;height:26px;flex:none;color:var(--accA);margin-top:1px}
.blist span b{color:#fff}

/* ---------- Two column ---------- */
.twocol-wrap h2{font-size:clamp(28px,4vw,56px)}
.twocol{display:grid;grid-template-columns:1fr 1fr;gap:clamp(28px,4vw,64px);margin-top:34px;align-items:center}
.tc-col h3{font-size:clamp(19px,2vw,27px);color:#fff;margin-bottom:12px}
.tc-col .lead{margin-top:0}
.tc-col .blist{margin-top:0}

/* ---------- Media ---------- */
.mediaslide h2,.gallery-wrap h2,.chartslide h2,.statsslide h2,.cards-wrap h2,.table-wrap h2,.timeline-wrap h2,.compare-wrap h2{font-size:clamp(26px,3.6vw,52px)}
.media{border:1px solid var(--line);border-radius:20px;overflow:hidden;background:rgba(255,255,255,.03);
  box-shadow:0 30px 80px rgba(0,0,0,.5)}
.media img,.media video{display:block;width:100%;height:auto;max-height:66vh;object-fit:cover}
.media figcaption{padding:12px 18px;font-size:13.5px;color:var(--muted);font-weight:600;border-top:1px solid var(--line)}
.mediaslide{display:flex;flex-direction:column;align-items:center;text-align:center}
.mediaslide>div{width:100%;max-width:1100px;margin-top:24px}

/* ---------- Gallery ---------- */
.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px;margin-top:30px}
.gcell .media img,.gcell .media video{height:240px}

/* ---------- Chart ---------- */
.chartwrap{margin-top:16px;display:flex;flex-direction:column;align-items:center;gap:16px}
.chart{width:100%;max-width:760px;max-height:56vh}
.chart .cax{stroke:var(--line);stroke-width:1.5}
.chart .clab{fill:var(--muted);font-size:13px;font-weight:700}
.chart .cval{fill:#fff;font-size:14px;font-weight:800}
.chart .dnum{fill:#fff;font-size:38px;font-weight:900}
.chart .dlab{fill:var(--muted);font-size:14px;font-weight:700;text-transform:uppercase;letter-spacing:.12em}
.legend{display:flex;flex-wrap:wrap;gap:16px;justify-content:center}
.legend .lg{display:inline-flex;align-items:center;gap:8px;font-size:14px;color:var(--slate);font-weight:600}
.legend .lg i{width:12px;height:12px;border-radius:3px;display:inline-block}
.legend .lg b{color:#fff}
.chartslide{display:flex;flex-direction:column;align-items:center;text-align:center}

/* ---------- Stats slide ---------- */
.statsslide{text-align:center;display:flex;flex-direction:column;align-items:center}
.statsslide .statrow{margin-top:34px}

/* ---------- Big number ---------- */
.bignum{text-align:center;display:flex;flex-direction:column;align-items:center}
.bn{font-size:clamp(80px,18vw,260px);font-weight:900;letter-spacing:-.04em;line-height:.9;
  background:linear-gradient(180deg,#fff,var(--accA));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.bnlab{margin-top:10px;font-size:clamp(18px,2.4vw,34px);font-weight:800;color:#fff}
.bignum .lead{text-align:center;max-width:52ch}

/* ---------- Cards ---------- */
.cards-wrap{text-align:center;display:flex;flex-direction:column;align-items:center}
.cards{display:grid;gap:18px;margin-top:34px;width:100%;max-width:1160px}
.cards.c3{grid-template-columns:repeat(3,1fr)}
.cards.c2{grid-template-columns:repeat(2,1fr)}
.card{background:rgba(255,255,255,.045);border:1px solid var(--line);border-radius:18px;padding:26px 24px;text-align:left}
.card .ci{width:46px;height:46px;border-radius:13px;display:grid;place-items:center;margin-bottom:15px;color:#fff;
  background:linear-gradient(135deg,var(--accA),var(--accDark))}
.card .ci svg{width:24px;height:24px}
.card h4{font-size:19px;color:#fff;margin-bottom:9px}
.card p{font-size:14.5px;color:var(--slate);line-height:1.5}

/* ---------- Table ---------- */
.table-wrap{display:flex;flex-direction:column;align-items:center}
.table-wrap table{margin-top:30px;border-collapse:collapse;width:100%;max-width:1100px;font-size:clamp(13px,1.4vw,17px)}
.table-wrap th{text-align:left;padding:14px 18px;color:var(--accA);font-weight:800;font-size:12.5px;
  text-transform:uppercase;letter-spacing:.1em;border-bottom:2px solid var(--line)}
.table-wrap td{padding:14px 18px;color:var(--slate);border-bottom:1px solid var(--line);font-weight:500}
.table-wrap tr:hover td{background:rgba(255,255,255,.02)}
.table-wrap td b{color:#fff}

/* ---------- Timeline ---------- */
.timeline-wrap{display:flex;flex-direction:column;align-items:center}
.timeline{margin-top:36px;position:relative;width:100%;max-width:1080px;
  display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:24px}
.tl-step{position:relative;padding-top:30px}
.timeline::before{content:"";position:absolute;top:6px;left:6px;right:6px;height:2px;background:var(--line)}
.tl-dot{position:absolute;top:0;left:0;width:14px;height:14px;border-radius:50%;
  background:linear-gradient(135deg,var(--accA),var(--accB));box-shadow:0 0 0 5px var(--accGlowSoft)}
.tl-when{font-size:12.5px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--accA);margin-bottom:8px}
.tl-what h4{font-size:18px;color:#fff;margin-bottom:6px}
.tl-what p{font-size:14px;color:var(--slate);line-height:1.45}

/* ---------- Compare ---------- */
.compare-wrap{display:flex;flex-direction:column;align-items:center}
.compare{margin-top:34px;display:grid;grid-template-columns:1fr 1fr;gap:20px;width:100%;max-width:1000px}
.cmp{border:1px solid var(--line);border-radius:18px;padding:26px;background:rgba(255,255,255,.03)}
.cmp-h{font-size:20px;font-weight:900;color:#fff;margin-bottom:18px}
.cmp ul{list-style:none;display:flex;flex-direction:column;gap:13px}
.cmp li{display:flex;gap:12px;align-items:flex-start;font-size:15.5px;color:var(--slate);line-height:1.4;font-weight:500}
.cmp li svg{width:22px;height:22px;flex:none;margin-top:1px}
.cmp.con li svg{color:var(--muted2)}
.cmp.pro{border-color:var(--accGlowSoft);box-shadow:0 0 40px var(--accGlowSoft) inset}
.cmp.pro .cmp-h{color:var(--accA)}
.cmp.pro li svg{color:var(--accA)}

/* ---------- Feature (generalised initiative layout) ---------- */
.init-num{font-size:clamp(15px,1.4vw,19px);font-weight:900;color:var(--accA);letter-spacing:.08em;display:flex;align-items:center;gap:14px;margin-bottom:16px}
.init-num .of{color:var(--muted2);font-weight:700}
.init-num .bar{flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}
.init-grid{display:grid;grid-template-columns:1.15fr .85fr;grid-template-areas:"intro glyph" "why kw";
  grid-template-rows:auto auto;column-gap:clamp(30px,4vw,72px);row-gap:clamp(20px,2.4vw,34px);align-items:center}
.col-intro{grid-area:intro;align-self:end}.col-glyph{grid-area:glyph;align-self:center}
.col-why{grid-area:why;align-self:start;padding-top:43px}.col-kw{grid-area:kw;align-self:start}
.init h2{font-size:clamp(32px,4.7vw,64px);color:#fff}
.aka{margin-top:14px;font-size:clamp(13px,1.25vw,17px);color:var(--muted);font-style:italic;font-weight:600;display:flex;align-items:center;gap:9px}
.aka .ic{font-style:normal;width:auto;height:auto;color:var(--muted)}
.tag{margin-top:22px;display:inline-block;font-size:clamp(13px,1.3vw,16.5px);font-weight:800;color:var(--accB);
  border-left:3px solid var(--accB);padding:5px 0 5px 16px;background:linear-gradient(90deg,var(--accGlowSoft),transparent);border-radius:0 8px 8px 0}
.summary{margin-top:26px;font-size:clamp(15px,1.55vw,21px);color:var(--slate);line-height:1.52;max-width:60ch}
.why{font-size:clamp(13.5px,1.35vw,17px);color:#cdd9e5;line-height:1.5;max-width:60ch;
  background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
.why b{color:var(--accA)}
.kw-wrap{display:flex;flex-direction:column;gap:14px}
.kw-head{font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--muted2)}
.kw{display:flex;flex-wrap:wrap;gap:11px}
.chip{font-size:clamp(13px,1.35vw,16px);font-weight:700;color:#eaf3fb;background:rgba(255,255,255,.05);
  border:1px solid var(--line);border-radius:12px;padding:11px 16px}
.chip::before{content:"";display:inline-block;width:7px;height:7px;border-radius:2px;margin-right:9px;vertical-align:middle;
  background:linear-gradient(135deg,var(--accA),var(--accB))}

/* glyph */
.glyph-wrap{position:relative;width:100%;max-width:340px;margin:0 auto;aspect-ratio:1}
.glyph{position:relative;display:grid;place-items:center;width:100%;height:100%}
.glyph .ring{position:absolute;border:1px solid var(--line);border-radius:50%}
.glyph .r1{inset:0;animation:spin 34s linear infinite}
.glyph .r2{inset:14%;border-style:dashed;border-color:var(--accGlowSoft);animation:spin 26s linear infinite reverse}
.glyph .r3{inset:30%;border-color:var(--accGlow2);opacity:.4;animation:spin 20s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.glyph .core{width:44%;height:44%;border-radius:26px;display:grid;place-items:center;
  background:linear-gradient(150deg,var(--navy2),var(--navy-soft));border:1px solid var(--line);
  box-shadow:0 20px 60px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.06)}
.glyph .core svg{width:52%;height:52%;color:var(--accA);filter:drop-shadow(0 0 14px var(--accGlow))}
.glyph .orb{position:absolute;width:12px;height:12px;border-radius:50%;background:radial-gradient(circle,var(--accB),var(--accA));box-shadow:0 0 14px var(--accGlow2)}
.glyph .o1{top:2%;left:48%}.glyph .o2{bottom:8%;right:6%}.glyph .o3{bottom:12%;left:4%}

/* ---------- Closing ---------- */
.closing h2{font-size:clamp(36px,5.6vw,84px)}
.closing .sub{font-size:clamp(16px,1.8vw,24px);color:var(--slate);max-width:52ch;margin-top:24px;line-height:1.45;font-weight:500}
.closing .three{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:44px;max-width:940px}
.closing .three .b{display:flex;align-items:center;gap:13px;background:rgba(255,255,255,.05);border:1px solid var(--line);border-radius:100px;padding:14px 22px;font-weight:700;font-size:15px;color:#fff}
.closing .three .b span{width:26px;height:26px;flex:none;border-radius:50%;background:linear-gradient(135deg,var(--accA),var(--accB));color:var(--navy3);font-weight:900;font-size:13px;display:grid;place-items:center}

/* ---------- Chrome ---------- */
.topbar{position:fixed;top:0;left:0;right:0;height:64px;z-index:40;display:flex;align-items:center;justify-content:space-between;
  padding:0 clamp(22px,4vw,54px);pointer-events:none;transition:opacity .5s ease}
.topbar.logo-hidden img{opacity:0}
.topbar img{height:22px;opacity:.92;transition:opacity .5s ease}
.tb-right{display:flex;align-items:center;gap:16px;pointer-events:auto}
.section-label{font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.counter{font-size:13px;font-weight:800;color:#fff;background:rgba(255,255,255,.06);border:1px solid var(--line);border-radius:100px;padding:7px 14px}
.counter b{color:var(--accA)}
.progress{position:fixed;bottom:0;left:0;height:4px;z-index:40;background:linear-gradient(90deg,var(--accA),var(--accB));width:0;transition:width .5s cubic-bezier(.2,.7,.2,1),background .9s ease;box-shadow:0 0 16px var(--accGlow)}
.progress-track{position:fixed;bottom:0;left:0;right:0;height:4px;z-index:39;background:rgba(255,255,255,.06)}
.dots{position:fixed;right:clamp(14px,2vw,26px);top:50%;transform:translateY(-50%);z-index:40;display:flex;flex-direction:column;gap:9px}
.dots i{width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,.18);cursor:pointer;transition:all .25s}
.dots i.on{background:linear-gradient(135deg,var(--accA),var(--accB));transform:scale(1.5);box-shadow:0 0 10px var(--accGlow)}
.dots i:hover{background:rgba(255,255,255,.4)}
.nav-arrows{position:fixed;bottom:20px;right:clamp(20px,3vw,40px);z-index:40;display:flex;gap:10px}
.na{width:46px;height:46px;border-radius:50%;border:1px solid var(--line);background:rgba(255,255,255,.06);color:#fff;
  display:grid;place-items:center;cursor:pointer;transition:all .2s;backdrop-filter:blur(8px)}
.na:hover{background:var(--accA);border-color:var(--accA);transform:translateY(-2px)}
.na svg{width:20px;height:20px}
.hint{position:fixed;bottom:20px;left:clamp(20px,3vw,40px);z-index:40;font-size:12.5px;color:var(--muted);display:flex;align-items:center;gap:10px}
.key{display:inline-grid;place-items:center;min-width:24px;height:24px;padding:0 7px;border-radius:6px;background:rgba(255,255,255,.07);border:1px solid var(--line);font-size:12px;font-weight:800;color:#dfe9f2}
.hint.fade{opacity:0;transition:opacity 1s ease .5s}

/* ---------- Speaker notes ---------- */
.notes-toggle{margin-top:34px;display:inline-flex;align-items:center;gap:9px;cursor:pointer;
  background:rgba(255,255,255,.05);border:1px solid var(--line);border-radius:100px;padding:10px 16px;
  font-size:13px;font-weight:700;color:var(--slate);backdrop-filter:blur(6px);transition:all .2s;user-select:none}
.notes-toggle:hover{border-color:var(--accA);color:#fff}
.notes-toggle b{color:var(--accA);font-weight:800}
.notes-toggle.on{background:var(--accGlowSoft);border-color:var(--accA)}
.notes-toggle .nt-dot{width:9px;height:9px;border-radius:50%;background:var(--muted2);transition:all .2s}
.notes-toggle.on .nt-dot{background:var(--accB);box-shadow:0 0 0 4px var(--accGlowSoft)}
.notes-toggle .nt-key{display:inline-grid;place-items:center;min-width:20px;height:20px;padding:0 6px;margin-left:3px;
  border-radius:5px;background:rgba(255,255,255,.08);border:1px solid var(--line);font-size:11px;font-weight:800;color:#dfe9f2}
#notesPanel{position:fixed;left:50%;transform:translateX(-50%) translateY(14px);bottom:26px;z-index:45;
  width:min(1040px,86vw);max-height:30vh;overflow-y:auto;background:rgba(12,22,34,.86);border:1px solid var(--line);
  border-radius:16px;padding:18px 24px 20px;backdrop-filter:blur(14px);
  box-shadow:0 24px 70px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.05);
  opacity:0;visibility:hidden;pointer-events:none;transition:opacity .3s ease,transform .3s cubic-bezier(.2,.7,.2,1)}
#notesPanel.show{opacity:1;visibility:visible;pointer-events:auto;transform:translateX(-50%) translateY(0)}
#notesPanel .np-head{display:flex;align-items:center;gap:9px;font-size:10.5px;font-weight:800;letter-spacing:.18em;text-transform:uppercase;color:var(--accA);margin-bottom:9px}
#notesPanel .np-head::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--accB);box-shadow:0 0 0 4px var(--accGlowSoft)}
#notesPanel .np-body{font-size:clamp(14px,1.15vw,15.5px);line-height:1.55;color:#e7eef6;font-weight:500}
#notesPanel::-webkit-scrollbar{width:8px}
#notesPanel::-webkit-scrollbar-thumb{background:rgba(255,255,255,.14);border-radius:8px}

@media (max-width:960px){
  .init-grid{grid-template-columns:1fr;grid-template-areas:"intro" "glyph" "why" "kw";gap:26px}
  .col-why{padding-top:0}.glyph-wrap{max-width:220px}
  .statrow,.twocol,.cards.c3,.cards.c2,.compare,.closing .three{grid-template-columns:1fr 1fr}
  .part h2,.cover h1{font-size:12vw}
}
</style>
</head>
<body>
<div id="stage">
  <div class="bg-glow"></div>
  <canvas class="bg-net" id="bgCanvas" aria-hidden="true"></canvas>
  <div class="grain"></div>
  <div id="slides"></div>
</div>

<div class="topbar" id="topbar">
  <img src="__LOGO__" alt="ProFinda">
  <div class="tb-right">
    <span class="section-label" id="secLabel"></span>
    <span class="counter"><b id="curNum">1</b> / <span id="totNum">1</span></span>
  </div>
</div>

<div class="progress-track"></div>
<div class="progress" id="prog"></div>
<div class="dots" id="dots"></div>
<div class="nav-arrows">
  <div class="na" id="prevBtn" aria-label="Previous"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg></div>
  <div class="na" id="nextBtn" aria-label="Next"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg></div>
</div>
<div class="hint" id="hint"><span class="key">&#8592;</span><span class="key">&#8594;</span> arrows or click &#183; <span class="key">F</span> fullscreen &#183; <span class="key">N</span> speaker notes<!--__EDIT_HINT__--></div>

<div id="notesPanel" aria-live="polite">
  <div class="np-head">Speaker notes</div>
  <div class="np-body" id="notesBody"></div>
</div>
<!--__EDIT_BAR__-->

<script>
const DATA = __DATA__;

/* ---------- Build slides from payload ---------- */
const slidesEl=document.getElementById('slides');
const slides=[];
DATA.slides.forEach(sp=>{
  const d=document.createElement('div'); d.className='slide';
  d.innerHTML='<div class="slide-inner">'+sp.html+'</div>';
  slidesEl.appendChild(d);
  slides.push({el:d,section:sp.section||'',note:sp.note||'',horizon:sp.horizon||'h1'});
});

/* Add the speaker-notes toggle onto the first slide (usually the cover). */
(function(){
  const first=slides[0]; if(!first) return;
  const t=document.createElement('div');
  t.className='notes-toggle anim d5'; t.id='notesToggle'; t.setAttribute('role','button');
  t.tabIndex=0; t.setAttribute('aria-pressed','false');
  t.innerHTML='<span class="nt-dot"></span>Speaker notes: <b id="ntState">Off</b><span class="nt-key">N</span>';
  const host=first.el.querySelector('.cover, .statement, .part, .slide-inner')||first.el.querySelector('.slide-inner');
  host.appendChild(t);
})();

/* ---------- Navigation engine ---------- */
let cur=0; const total=slides.length;
let stepCamera=(dir,el)=>{};
document.getElementById('totNum').textContent=total;
const prog=document.getElementById('prog');
const dotsEl=document.getElementById('dots');
slides.forEach((s,i)=>{const d=document.createElement('i');d.addEventListener('click',()=>go(i));dotsEl.appendChild(d);});
const dotEls=[...dotsEl.children];

function go(i){
  if(i<0||i>=total) return;
  const dir = i>cur ? 1 : -1;
  cur=Math.max(0,Math.min(total-1,i));
  const incoming = slides[cur].el;
  stepCamera(dir, incoming);
  slides.forEach((s,idx)=>s.el.classList.toggle('active',idx===cur));
  dotEls.forEach((d,idx)=>d.classList.toggle('on',idx===cur));
  prog.style.width=((total>1?cur/(total-1):1)*100)+'%';
  document.getElementById('curNum').textContent=cur+1;
  document.getElementById('secLabel').textContent=slides[cur].section;
  document.getElementById('topbar').classList.toggle('logo-hidden', !!incoming.querySelector('.cover-logo'));
  // per-slide Horizon theme: swap the whole accent palette; every accent surface eases over.
  applyTheme(slides[cur].horizon||'h1');
  renderNotes();
  if(typeof editMode!=='undefined' && editMode){ notesPanel.classList.add('show'); refreshEditUIForSlide(); }
}

/* ---------- Horizon theming ---------- */
// Star-cloud palette targets the background eases toward, matched to the CSS accents.
const THEME_STARS = {
  'h1':{ near:[140,198,63], far:[14,173,154], link:[150,200,220] },   // teal -> lime
  'h2':{ near:[246,196,69], far:[232,163,23], link:[224,196,120] },   // amber / gold
  'h3':{ near:[249,115,22], far:[226,59,46],  link:[236,150,110] },   // orange -> red
};
window.__starTargetTheme = THEME_STARS['h1'];
function applyTheme(hz){
  document.body.classList.toggle('h2', hz==='h2');
  document.body.classList.toggle('h3', hz==='h3');
  window.__starTargetTheme = THEME_STARS[hz] || THEME_STARS['h1'];
}

/* ---------- Speaker notes ---------- */
let notesOn=false;
const notesPanel=document.getElementById('notesPanel');
const notesBody=document.getElementById('notesBody');
const notesToggle=document.getElementById('notesToggle');
const ntState=document.getElementById('ntState');
try{ notesOn = localStorage.getItem('pf_notes')==='1'; }catch(e){}
function renderNotes(){
  const note=(slides[cur]&&slides[cur].note)||'';
  notesBody.textContent=note;
  notesPanel.classList.toggle('show', notesOn && !!note);
}
function syncToggle(){
  if(!ntState) return;
  ntState.textContent=notesOn?'On':'Off';
  notesToggle.classList.toggle('on',notesOn);
  notesToggle.setAttribute('aria-pressed',notesOn?'true':'false');
}
function setNotes(on){ notesOn=on; try{localStorage.setItem('pf_notes',on?'1':'0');}catch(e){} syncToggle(); renderNotes(); }
if(notesToggle){
  notesToggle.addEventListener('click',e=>{e.stopPropagation();setNotes(!notesOn);});
  notesToggle.addEventListener('keydown',e=>{ if(e.key==='Enter'||e.key===' '){e.preventDefault();e.stopPropagation();setNotes(!notesOn);} });
}
notesPanel.addEventListener('click',e=>e.stopPropagation());
syncToggle();

function next(){ if(cur<total-1) go(cur+1); }
function prev(){ if(cur>0) go(cur-1); }
document.getElementById('nextBtn').addEventListener('click',e=>{e.stopPropagation();next();});
document.getElementById('prevBtn').addEventListener('click',e=>{e.stopPropagation();prev();});
document.getElementById('stage').addEventListener('click',e=>{
  if(e.target.closest('.na')||e.target.closest('.dots')||e.target.closest('#notesToggle')||e.target.closest('#notesPanel')) return;
  const x=e.clientX/window.innerWidth; if(x<0.28) prev(); else next();
});
window.addEventListener('keydown',e=>{
  if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)){e.preventDefault();next();}
  else if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();prev();}
  else if(e.key==='Home'){go(0);} else if(e.key==='End'){go(total-1);}
  else if(e.key==='f'||e.key==='F'){ if(!document.fullscreenElement) document.documentElement.requestFullscreen(); else document.exitFullscreen(); }
  else if(e.key==='n'||e.key==='N'){ e.preventDefault(); setNotes(!notesOn); }
});
let tx=0; window.addEventListener('touchstart',e=>tx=e.touches[0].clientX,{passive:true});
window.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-tx; if(Math.abs(dx)>50){dx<0?next():prev();}},{passive:true});
/*__EDIT_JS__*/
setTimeout(()=>document.getElementById('hint').classList.add('fade'),4200);
go(0);

/* ---------- 3D star cloud (fly-through background) ---------- */
(function(){
  const canvas=document.getElementById('bgCanvas'); const ctx=canvas.getContext('2d');
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let W=0,H=0,DPR=Math.min(window.devicePixelRatio||1,2);
  function resize(){ W=canvas.clientWidth; H=canvas.clientHeight; canvas.width=Math.round(W*DPR); canvas.height=Math.round(H*DPR); ctx.setTransform(DPR,0,0,DPR,0,0); }
  resize(); window.addEventListener('resize',resize);
  const N=200, CELL=2200, HALF=CELL/2, LINK=360, LINK2=LINK*LINK, DRAW=1700;
  const stars=[]; for(let i=0;i<N;i++){ stars.push({x:Math.random()*CELL,y:Math.random()*CELL,z:Math.random()*CELL,r:0.7+Math.random()*1.9,tw:Math.random()*Math.PI*2}); }
  const F=820; const cam={x:0,y:0,z:0,yaw:0,pitch:0,roll:0}; const tgt={x:0,y:0,z:0,yaw:0,pitch:0,roll:0}; let t=0;
  // live (eased) star palette; eases toward window.__starTargetTheme each frame.
  const H1={near:[140,198,63],far:[14,173,154],link:[150,200,220]};
  const col={near:[...H1.near],far:[...H1.far],link:[...H1.link]};
  function wrap(v,camv){ let d=(v-camv)%CELL; if(d<-HALF)d+=CELL; else if(d>=HALF)d-=CELL; return d; }
  const cs={cy:1,sy:0,cp:1,sp:0,cr:1,sr:0};
  function project(dx,dy,dz){
    let x1=cs.cy*dx+cs.sy*dz, z1=-cs.sy*dx+cs.cy*dz, y1=dy;
    let y2=cs.cp*y1-cs.sp*z1, z2=cs.sp*y1+cs.cp*z1, x2=x1;
    let x3=cs.cr*x2-cs.sr*y2, y3=cs.sr*x2+cs.cr*y2, z3=z2;
    if(z3<=1) return null; const s=F/z3; return {px:W/2+x3*s,py:H/2+y3*s,scale:s,z:z3};
  }
  function frame(){
    t+=0.016; const k=0.045;
    cam.x+=(tgt.x-cam.x)*k; cam.y+=(tgt.y-cam.y)*k; cam.z+=(tgt.z-cam.z)*k;
    cam.yaw+=(tgt.yaw-cam.yaw)*k; cam.pitch+=(tgt.pitch-cam.pitch)*k; cam.roll+=(tgt.roll-cam.roll)*k;
    cam.yaw+=Math.sin(t*0.05)*0.00020; cam.pitch+=Math.cos(t*0.043)*0.00016; cam.z+=0.25;
    cs.cy=Math.cos(cam.yaw);cs.sy=Math.sin(cam.yaw);cs.cp=Math.cos(cam.pitch);cs.sp=Math.sin(cam.pitch);cs.cr=Math.cos(cam.roll);cs.sr=Math.sin(cam.roll);
    // ease star palette toward the current horizon target
    const tg=(window.__starTargetTheme)||H1, ck=0.06;
    for(let c=0;c<3;c++){ col.near[c]+=(tg.near[c]-col.near[c])*ck; col.far[c]+=(tg.far[c]-col.far[c])*ck; col.link[c]+=(tg.link[c]-col.link[c])*ck; }
    ctx.clearRect(0,0,W,H);
    const wx=new Float64Array(N),wy=new Float64Array(N),wz=new Float64Array(N); const proj=new Array(N);
    for(let i=0;i<N;i++){ const dx=wrap(stars[i].x,cam.x),dy=wrap(stars[i].y,cam.y),dz=wrap(stars[i].z,cam.z); wx[i]=dx;wy[i]=dy;wz[i]=dz; proj[i]=project(dx,dy,dz); }
    ctx.lineWidth=1;
    for(let i=0;i<N;i++){ const a=proj[i]; if(!a||a.z>DRAW) continue;
      for(let j=i+1;j<N;j++){ const b=proj[j]; if(!b||b.z>DRAW) continue;
        const ddx=wx[i]-wx[j],ddy=wy[i]-wy[j],ddz=wz[i]-wz[j]; const d2=ddx*ddx+ddy*ddy+ddz*ddz; if(d2>LINK2) continue;
        const zAvg=(a.z+b.z)/2; const al=Math.max(0,Math.min(.22,(1-d2/LINK2)*(1-zAvg/DRAW)*.22)); if(al<=0.012) continue;
        ctx.strokeStyle='rgba('+(col.link[0]|0)+','+(col.link[1]|0)+','+(col.link[2]|0)+','+al.toFixed(3)+')'; ctx.beginPath(); ctx.moveTo(a.px,a.py); ctx.lineTo(b.px,b.py); ctx.stroke();
      } }
    for(let i=0;i<N;i++){ const pr=proj[i]; if(!pr||pr.z>DRAW) continue;
      if(pr.px<-40||pr.px>W+40||pr.py<-40||pr.py>H+40) continue; const s=stars[i];
      const rad=Math.max(.5,s.r*pr.scale*140); const tw=0.6+0.4*Math.sin(t*1.2+s.tw); const al=Math.max(0,Math.min(.95,(1-pr.z/DRAW)))*tw; if(al<=0.02) continue;
      const near=Math.max(0,Math.min(1,1-pr.z/(DRAW*0.8)));
      const cr=Math.round(col.far[0]+(col.near[0]-col.far[0])*near);
      const cg=Math.round(col.far[1]+(col.near[1]-col.far[1])*near);
      const cb=Math.round(col.far[2]+(col.near[2]-col.far[2])*near);
      ctx.fillStyle='rgba('+cr+','+cg+','+cb+','+al.toFixed(3)+')';
      ctx.beginPath(); ctx.arc(pr.px,pr.py,Math.min(rad,5),0,6.283); ctx.fill();
    }
    requestAnimationFrame(frame);
  }
  let step=0; const YAWS=[-0.42,0.38,-0.30,0.46,-0.50,0.34]; const PITCHES=[0.10,-0.26,0.24,-0.14,0.28,-0.20];
  stepCamera=function(dir,el){
    step+=(dir||1);
    const yaw=YAWS[((step%YAWS.length)+YAWS.length)%YAWS.length]; const pitch=PITCHES[((step%PITCHES.length)+PITCHES.length)%PITCHES.length];
    tgt.yaw+=yaw; tgt.pitch+=pitch; tgt.roll=(Math.random()-.5)*0.05;
    const fwd=520; tgt.x+=Math.sin(tgt.yaw)*Math.cos(tgt.pitch)*fwd; tgt.z+=Math.cos(tgt.yaw)*Math.cos(tgt.pitch)*fwd; tgt.y+=-Math.sin(tgt.pitch)*fwd;
    if(el){ el.style.setProperty('--sx',Math.round(-Math.sin(yaw)*520)+'px'); el.style.setProperty('--sy',Math.round(Math.sin(pitch)*360)+'px');
      el.style.setProperty('--sz','-680px'); el.style.setProperty('--ry',Math.round(yaw*22)+'deg'); el.style.setProperty('--rx',Math.round(-pitch*20)+'deg'); void el.offsetWidth; }
  };
  if(reduce){
    document.querySelectorAll('.slide').forEach(s=>{ s.style.setProperty('--sx','0px');s.style.setProperty('--sy','0px');s.style.setProperty('--sz','0px');s.style.setProperty('--rx','0deg');s.style.setProperty('--ry','0deg'); });
    stepCamera=function(){}; cs.cy=1;cs.sy=0;cs.cp=1;cs.sp=0;cs.cr=1;cs.sr=0; ctx.clearRect(0,0,W,H);
    for(let i=0;i<N;i++){ const dx=wrap(stars[i].x,cam.x),dy=wrap(stars[i].y,cam.y),dz=wrap(stars[i].z,cam.z); const pr=project(dx,dy,dz); if(!pr||pr.z>DRAW) continue;
      ctx.fillStyle='rgba(14,173,154,'+Math.max(.1,1-pr.z/DRAW).toFixed(2)+')'; ctx.beginPath(); ctx.arc(pr.px,pr.py,Math.min(3,1.2*pr.scale*120),0,6.283); ctx.fill(); }
    return;
  }
  requestAnimationFrame(frame);
})();
</script>
</body>
</html>

"""

if __name__ == "__main__":
    if "--demo" in sys.argv:
        from demo_content import SLIDES as DEMO
        build(DEMO, title="ProFinda Deck Engine — Layout Showcase", out="ProFinda-Deck-Demo.html")
    else:
        try:
            from demo_content import SLIDES as DEMO
            build(DEMO, title="ProFinda Deck", out="ProFinda-Deck.html")
        except ImportError:
            print("No SLIDES provided. Run with --demo, or import build() and pass your own SLIDES.")
