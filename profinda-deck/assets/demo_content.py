"""
Layout showcase for the ProFinda deck engine.

Every slide is a dict with a "layout" and its fields. `notes` (speaker notes) and
`horizon` ("h1" default, "h2", "h3") are optional on any slide. This file is both a
test fixture and living documentation of what the engine can render — copy any
slide as a starting point.

Build it:  python3 build_deck.py --demo    ->  ProFinda-Deck-Demo.html
"""

SLIDES = [
    # 1. COVER — hero + optional stat/horizon row
    {
        "layout": "cover",
        "eyebrow": "Deck engine · Layout showcase",
        "title": 'Build decks in<br><span class="accent">minutes, not days.</span>',
        "subtitle": "One content list, every ProFinda layout. This deck is generated from a Python list of dicts — no HTML hand-authoring.",
        "stats": [
            {"kicker": "Horizon 1", "value": "17 layouts", "label": "Content-driven slide types", "horizon": "h1"},
            {"kicker": "Horizon 2", "value": "Charts + media", "label": "Inline SVG, embedded images", "horizon": "h2"},
            {"kicker": "Horizon 3", "value": "0 HTML", "label": "You write content, not markup", "horizon": "h3"},
        ],
        "section": "Overview",
        "notes": "This is the cover. Notice the speaker-notes toggle got added here automatically, and the three stat cards each show a different Horizon accent — teal, amber, orange — without changing the brand.",
    },

    # 2. SECTION divider
    {
        "layout": "section",
        "kicker": "Part One",
        "title": 'Text &<br><span class="accent">structure.</span>',
        "body": "Section bands break a deck into acts. Named for the idea, with a single accent rule underneath.",
        "section": "Text & structure",
        "notes": "Use section slides to signal a gear change to the audience.",
    },

    # 3. STATEMENT — one big idea
    {
        "layout": "statement",
        "eyebrow": "The big idea",
        "title": 'Every visual choice should <span class="accent">earn its place.</span>',
        "body": "A statement slide is a single sentence the room should remember. Emphasise the words that matter with the accent gradient.",
        "section": "Statement",
    },

    # 4. QUOTE
    {
        "layout": "quote",
        "eyebrow": "What clients tell us",
        "quote": 'This is the first roadmap that actually felt like <span class="accent">it was built for us.</span>',
        "attribution": "Head of Resourcing, Global Advisory Firm",
        "section": "Quote",
    },

    # 5. BULLETS — iconed list
    {
        "layout": "bullets",
        "eyebrow": "How it works",
        "title": "Content in, deck out",
        "body": "Each bullet can carry its own icon.",
        "items": [
            {"icon": "list", "text": "Write a <b>list of slide dicts</b> — layout + fields."},
            {"icon": "bolt", "text": "The engine renders ProFinda-styled HTML with entrance motion."},
            {"icon": "shield", "text": "Output is <b>one self-contained file</b> — no external assets."},
            {"icon": "check", "text": "Navigation, notes, 3D flythrough and Horizon theming for free."},
        ],
        "section": "Bullets",
        "notes": "Bullets take an icon per item; default is a check.",
    },

    # 6. TWO-COL — flexible split (text + glyph here)
    {
        "layout": "two-col",
        "eyebrow": "Two column",
        "title": "Pair anything, side by side",
        "left": {"heading": "Left is text", "body": "A column can be a heading + body, a bullet list, a chart, a media block, or a hero glyph — mix and match."},
        "right": {"glyph": "layers"},
        "section": "Two column",
    },

    # 7. TWO-COL — text + bullets
    {
        "layout": "two-col",
        "title": "Text and a list together",
        "left": {"heading": "The problem", "body": "Decks used to mean hand-writing HTML or fighting a WYSIWYG. Both are slow and drift off-brand."},
        "right": {"bullets": [
            {"icon": "cross", "text": "No consistent design language"},
            {"icon": "cross", "text": "Slow to produce"},
            {"icon": "check", "text": "Now: content-only, always on-brand"},
        ]},
        "section": "Two column",
    },

    # 8. SECTION — data
    {
        "layout": "section",
        "kicker": "Part Two",
        "title": 'Data &<br><span class="accent">evidence.</span>',
        "section": "Data & evidence",
    },

    # 9. CHART — bar
    {
        "layout": "chart",
        "eyebrow": "Adoption",
        "title": "Weekly active resource managers",
        "chart": {"type": "bar", "legend": False, "data": [["Q1", 120], ["Q2", 210], ["Q3", 340], ["Q4", 520]]},
        "section": "Chart · bar",
        "notes": "Charts are inline SVG rendered at build time from your data — fully self-contained, and they pick up the current Horizon accent.",
    },

    # 10. CHART — line
    {
        "layout": "chart",
        "eyebrow": "Trend",
        "title": "Time to resource a role (days)",
        "chart": {"type": "line", "data": [["Jan", 21], ["Feb", 16], ["Mar", 11], ["Apr", 6], ["May", 3], ["Jun", 0.3]]},
        "section": "Chart · line",
    },

    # 11. CHART — donut with legend
    {
        "layout": "chart",
        "eyebrow": "Mix",
        "title": "Where demand comes from",
        "chart": {"type": "donut", "legend": True, "data": [["Advisory", 42], ["Audit", 31], ["Tax", 18], ["Other", 9]]},
        "section": "Chart · donut",
    },

    # 12. STATS — metric row
    {
        "layout": "stats",
        "eyebrow": "By the numbers",
        "title": "What good looks like",
        "stats": [
            {"value": "2.7m", "label": "Ontology interconnections"},
            {"value": "4 min", "label": "To resource a role"},
            {"value": "98%", "label": "Match acceptance"},
            {"value": "14", "label": "Enterprise clients"},
        ],
        "section": "Stats",
    },

    # 13. BIG NUMBER
    {
        "layout": "big-number",
        "eyebrow": "One number to remember",
        "value": '3 wks &rarr; <span class="accent">4 min</span>',
        "label": "Time to resource a role",
        "body": "The single stat that reframes the whole conversation.",
        "section": "Big number",
    },

    # 14. TABLE
    {
        "layout": "table",
        "eyebrow": "At a glance",
        "title": "Plan comparison",
        "columns": ["Capability", "Core", "Enterprise"],
        "rows": [
            ["Search &amp; match", "<b>&#10003;</b>", "<b>&#10003;</b>"],
            ["Custom calculated fields", "&mdash;", "<b>&#10003;</b>"],
            ["Looker analytics", "&mdash;", "<b>&#10003;</b>"],
            ["MCP open endpoints", "&mdash;", "<b>&#10003;</b>"],
        ],
        "section": "Table",
    },

    # 15. TIMELINE
    {
        "layout": "timeline",
        "eyebrow": "Roadmap",
        "title": "Where we're heading",
        "items": [
            {"when": "Now", "heading": "Deepen the core", "body": "Booking, skills, reporting."},
            {"when": "Next", "heading": "New products", "body": "Alumni & events."},
            {"when": "Later", "heading": "Blended workforce", "body": "Human + AI agents."},
        ],
        "section": "Timeline",
    },

    # 16. COMPARE
    {
        "layout": "compare",
        "eyebrow": "Why us",
        "title": "Point solutions vs. ProFinda",
        "left": {"heading": "Point solutions", "items": ["Single practice", "Manual re-planning", "No skills ontology"]},
        "right": {"heading": "ProFinda", "items": ["Whole business", "Automated optimisation", "2.7m-edge ontology"]},
        "section": "Compare",
    },

    # 17. CARDS grid
    {
        "layout": "cards",
        "eyebrow": "Principles",
        "title": "ProFinda's DNA",
        "cards": [
            {"icon": "users", "heading": "Client-driven", "body": "Grounded in real change-requests, not a wish-list."},
            {"icon": "layers", "heading": "Deepen &amp; extend", "body": "Strengthen what works, open new markets."},
            {"icon": "sparkle", "heading": "Distinctly ProFinda", "body": "AI-native, skills-led, enterprise-grade."},
        ],
        "section": "Cards",
    },

    # 18. MEDIA — inline generated SVG image (self-contained placeholder)
    {
        "layout": "media",
        "eyebrow": "Media",
        "title": "Drop in an image or video",
        "body": "Point at a local file, a URL, or a data URI — local files get embedded as base64 so the deck stays self-contained.",
        "media": "data:image/svg+xml;base64,"
                 "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMjAwIiBoZWlnaHQ9IjYwMCI+"
                 "PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJnIiB4MT0iMCIgeTE9IjAiIHgyPSIxIiB5Mj0iMSI+PHN0b3Ag"
                 "b2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzBFQUQ5QSIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xv"
                 "cj0iIzhDQzYzRiIvPjwvbGluZWFyR3JhZGllbnQ+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMjAwIiBoZWlnaHQ9"
                 "IjYwMCIgZmlsbD0iIzEzMUUyRCIvPjxjaXJjbGUgY3g9IjYwMCIgY3k9IjMwMCIgcj0iMTgwIiBmaWxsPSJ1"
                 "cmwoI2cpIi8+PHRleHQgeD0iNjAwIiB5PSIzMTUiIGZvbnQtZmFtaWx5PSJzYW5zLXNlcmlmIiBmb250LXNp"
                 "emU9IjQ4IiBmb250LXdlaWdodD0iOTAwIiBmaWxsPSIjMEMxNjIyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5Q"
                 "cm9GaW5kYTwvdGV4dD48L3N2Zz4=",
        "caption": "Example embedded media (an inline SVG here).",
        "section": "Media",
    },

    # 19. HORIZON 2 — feature slide, amber theme (whole palette eases)
    {
        "layout": "feature",
        "horizon": "h2",
        "index": "H2",
        "of": "/ next bets",
        "title": "Alumni & Events",
        "aka": "Horizon 2 — new products",
        "tag": "Two new products beyond the core",
        "body": "Community and events products that extend ProFinda past resourcing into the wider talent lifecycle.",
        "why": "Opens new buying centres inside the same clients and a new revenue line.",
        "why_label": "Why now —",
        "chips": ["Alumni communities", "Event management", "Talent re-engagement", "Marketplace"],
        "glyph": "rocket",
        "section": "Horizon 2",
        "notes": "Watch the whole deck retheme to amber as we enter Horizon 2 — the accent gradient, glyph, chips, progress bar and dots all ease to the warm palette. This is phasing colour, not a new brand colour.",
    },

    # 20. HORIZON 2 — stats in amber
    {
        "layout": "stats",
        "horizon": "h2",
        "eyebrow": "Horizon 2 · opportunity",
        "title": "The prize",
        "stats": [
            {"value": "2", "label": "New products"},
            {"value": "+30%", "label": "Account expansion potential"},
            {"value": "6", "label": "Design-partner clients"},
        ],
        "section": "Horizon 2",
    },

    # 21. HORIZON 3 — feature slide, orange/red theme
    {
        "layout": "feature",
        "horizon": "h3",
        "index": "H3",
        "of": "/ exploratory",
        "title": "Strategic Workforce Planning",
        "aka": "Horizon 3 — Human & AI agents",
        "tag": "Budget human + digital workforce together",
        "body": "Forward-looking capacity planning across human talent and synthetic AI agents in one platform.",
        "why": "Positions ProFinda as the home for the blended human-and-AI workforce. Vision-stage.",
        "why_label": "The bet —",
        "chips": ["Skill-gap forecasting", "Human + AI modelling", "MCP-connected agents", "Long-term capacity"],
        "glyph": "future",
        "section": "Horizon 3",
        "notes": "Horizon 3 eases everything to the orange-to-red palette. Frame these as where we're pointing, not committed near-term builds.",
    },

    # 22. STATEMENT back on brand (H1) to show it eases back
    {
        "layout": "statement",
        "eyebrow": "Back to now",
        "title": 'One roadmap. <span class="accent">Every horizon.</span>',
        "body": "Move between horizons and the whole deck recolours — but the brand blue/teal/green is always home.",
        "section": "Synthesis",
    },

    # 23. CLOSING
    {
        "layout": "closing",
        "title": 'Content in.<br><span class="accent">Deck out.</span>',
        "subtitle": "Every layout you just saw came from one list of dicts. Building a ProFinda deck is now about the story, not the markup.",
        "points": [
            "17 content-driven layouts",
            "Charts, media, tables, timelines",
            "Horizon theming, 3D flythrough, notes",
        ],
        "section": "Close",
        "notes": "Close by handing them the one-liner: content in, deck out.",
    },
]
