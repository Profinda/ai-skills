#!/usr/bin/env python3
"""EXAMPLE: the ProFinda Product Roadmap deck (self-contained single HTML file).

This is a real deck kept as a worked example / reference build. It predates the
generic engine in ../../assets/build_deck.py and hand-authors its own slides;
new decks should use that engine with a content list instead. Retained because
it's the origin of the 3D flythrough + Horizon theming and a useful reference.

Note: newer engine features (per-Horizon star-cloud recolouring and the opt-in
in-browser Edit mode, build(edit=True)) live in the engine, not this snapshot.
"""
import json, os, pathlib

HERE = pathlib.Path(__file__).resolve().parent
# Shared logo lives in the skill's assets/; output dir overridable via PF_DECK_OUT.
LOGO = pathlib.Path(os.environ.get("PF_DECK_LOGO", HERE.parent.parent / "assets" / "pf_logo.txt")).read_text().strip()
OUT_DIR = pathlib.Path(os.environ.get("PF_DECK_OUT", HERE))
FONT_DIR = HERE.parent.parent / "assets" / "fonts"

def _font_face():
    import base64
    subsets = {
        "mulish-latin.woff2":
            "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,"
            "U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD",
        "mulish-latin-ext.woff2":
            "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,"
            "U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF",
    }
    faces = []
    for fn, ur in subsets.items():
        p = FONT_DIR / fn
        if not p.exists():
            continue
        b64 = base64.b64encode(p.read_bytes()).decode()
        faces.append("@font-face{font-family:'Mulish';font-style:normal;font-weight:500 900;font-display:swap;"
                     f"src:url(data:font/woff2;base64,{b64}) format('woff2');unicode-range:{ur};}}")
    return "\n".join(faces)

# 14 initiatives. keywords = decomposition chips (legacy names / head-of-product alt names / sub-themes).
# aka = head-of-product alternative title surfaced as subtitle. clients = list of company keys.
INITIATIVES = [
  {
    "n": 1, "title": "ProPilot — AI Roadmap", "icon": "spark",
    "aka": None,
    "tag": "The assistant layer + open endpoints",
    "summary": "An AI assistant layer across the whole platform \u2014 natural-language search, bulk actions, booking-conflict suggestions, chat-based reporting \u2014 plus the API endpoints (MCP) that let external AI agents and client co-pilots reach ProFinda's intelligence directly, not just through our own UI.",
    "why": "Cuts time-to-value for new users and sharpens our AI story \u2014 but the bigger bet is reach: by exposing ProFinda's intelligence as open endpoints, our AI agents and co-pilots don't have to live only inside our own UI. They can be infused across our clients' IT landscape, so people get ProFinda-quality answers from the other screens and flows they already work in every day.",
    "keywords": ["ProPilot (LLM assistant)", "MCP open endpoints", "RFP / unstructured text \u2192 role automation", "Self-service journeys"],
    "clients": ["afry"],
    "notes": "The problem we're solving is that a powerful platform is also a hard platform to learn \u2014 new users take too long to get value, and everything they want to do lives behind menus and screens they have to discover. ProPilot answers that with an assistant layer: instead of learning where things are, you just ask \u2014 search, booking suggestions, reporting, all in natural language. The deeper problem is bigger than our own UI. The world is moving to AI agents and co-pilots, and if the only way to reach ProFinda's intelligence is through screens we built, we get left outside that shift. So we're opening our capabilities as endpoints other AI systems can call directly. Be honest in the room: this second part is us getting ahead of demand, not responding to it \u2014 it's a bet on where work is going, and a new way for ProFinda to be present in an AI-first workflow."
  },
  {
    "n": 2, "title": "AI Planner Evolution", "icon": "planner",
    "aka": "Intelligent Schedule Optimization",
    "tag": "The holy grail of resourcing automation",
    "summary": "The algorithmic engine behind smart, automated staffing \u2014 grown from an Audit-only tool into a general-purpose planner \u2014 plus the continuity mechanics (roll forward, grade promotions, leaver/mover handling) it must reason about over time.",
    "why": "This is the core differentiator versus manual staffing and point solutions, and it's already a go-live requirement for at least one enterprise client.",
    "keywords": ["KPI-based optimisation", "Scenario comparison", "Normative models", "Continuity: roll-forward, promotions, leavers/movers", "Gap-fill suggestions (AIrene)"],
    "clients": ["kpmg", "ey", "cohnreznick"],
    "notes": "This is the one to slow down on. Staffing at scale is still largely manual \u2014 a skilled person solving a giant, shifting puzzle by hand, and redoing it every time someone is promoted, leaves, or moves. That's slow, it doesn't scale, and it's exactly where point-solution competitors try to beat us. (We'll cover the competitive landscape properly on its own slide later.) The problem we're solving is turning that manual puzzle into something the platform can reason about and largely automate: propose optimal plans, let you compare scenarios before committing, and handle the messy reality of people changing over time so plans don't silently rot. We're growing this from a tool that only served one practice into a general-purpose planner for the whole business. Frame it as the core of our product story \u2014 automated, intelligent staffing is the holy grail of resourcing, and for at least one major enterprise it's already a condition of going live, not a nice-to-have."
  },
  {
    "n": 3, "title": "Booking Flexibility", "icon": "grid",
    "aka": "In-Context Booking Workflow",
    "tag": "Where RMs spend most of their day",
    "summary": "Removing hard constraints and friction from the core booking engine \u2014 24-hour role caps, rigid approvals, manual named-resource lookups, no bulk actions \u2014 and bringing search, availability and approvals in-context, right inside the grid.",
    "why": "The highest-frequency workflow in the platform. Almost every client touches it daily, so friction here has outsized impact on adoption and satisfaction.",
    "keywords": ["Booking approvals", "Named-resource booking", "Team demands", "Bulk actions", "RM landing dashboard", "Kanban for Tax"],
    "clients": ["deloitte", "kpmg", "ey", "newton"],
    "notes": "Here's the problem: booking is where Resource Managers spend most of their day, and today it fights them. There are hard constraints baked into the engine \u2014 caps, rigid approval flows, no way to act in bulk \u2014 and to do a simple thing they're forced to jump out to another screen, look something up, and come back. Every one of those little frictions, multiplied across the whole day and nearly every client, quietly drags down adoption and satisfaction. So this initiative is about taking friction out of the highest-frequency workflow we have: relax the artificial constraints, allow bulk actions, and bring search, availability and approvals right into the grid where the work already happens, instead of scattering them across the app. The framing to land: this isn't glamorous, but it's the workflow people live in \u2014 making it fast and fluid is one of the highest-leverage things we can do for day-to-day happiness."
  },
  {
    "n": 4, "title": "Insight Platform", "icon": "chart",
    "aka": None,
    "tag": "Removes developer bottlenecks",
    "summary": "The strategic bet to replace PowerBI with Looker as ProFinda's productised, embeddable analytics engine \u2014 plus custom calculated fields so clients define their own metrics instead of relying on one fixed platform-wide formula.",
    "why": "This becomes a genuine, monetizable enterprise add-on \u2014 not a patch to old reporting. It lifts a long-standing ceiling on data volume and customization, and lets clients define their own metrics, so they can elevate how they see resourcing and work with their own data on their own terms rather than waiting on us to hard-code every formula.",
    "keywords": ["Looker migration", "Dashboard expansion", "Custom calculated fields", "Remove CSV limits", "Report scalability"],
    "clients": ["afry", "ey", "kpmg"],
    "notes": "The problem here is twofold. First, our current analytics stack has a ceiling \u2014 it caps how much data we can push through and how far clients can customise, and every bespoke metric becomes an engineering job. Second, and more strategic: reporting is treated as a cost of doing business rather than something we can sell. This initiative attacks both. We move to a properly productised, embeddable analytics engine that lifts the data and scale ceiling, and we let clients define their own calculated metrics instead of being stuck with one fixed formula we hard-coded. Why it matters: it turns reporting from a support burden into a genuine, monetizable enterprise add-on \u2014 a real upsell, not just a fix. Position this as a deliberate strategic bet: we're not patching the old reporting, we're changing what reporting is for the business."
  },
  {
    "n": 5, "title": "Report Quality of Life", "icon": "list",
    "aka": None,
    "tag": "Used more than almost anything else",
    "summary": "The everyday reporting fixes clients ask for constantly \u2014 filters, labels, scheduling, headers, group-by options \u2014 plus several single-client dashboard builds tracked here for visibility.",
    "why": "Reporting is one of the most-used surfaces in the whole platform \u2014 clients live in it every single day. That means every fix you ship here is felt immediately by real people: a filter that finally exists, a report that schedules itself, headers that make sense. It's the highest hit-rate work on the roadmap \u2014 small, shippable changes that visibly make clients' days better and quietly kill a whole class of support tickets.",
    "keywords": ["Scheduled & recurring reports", "Filters, headers, group-by", "EY Core & Reporting"],
    "clients": ["ey", "cohnreznick", "kpmg"],
    "notes": "The trap with reporting is dismissing it as small stuff. It isn't \u2014 it's one of the most-used parts of the platform, and precisely because it's used so heavily, the little annoyances hurt the most. When a filter is missing, a report can't be scheduled, headers aren't labelled properly, or you can't group data the way you think about it, that friction shows up every single day and turns into a steady stream of support tickets and quiet dissatisfaction. So the problem we're solving is death by a thousand paper-cuts in the area people touch most. The what is deliberately unglamorous: the everyday quality-of-life fixes clients ask for constantly, plus a few specific dashboards we're tracking openly. The message to land: we're giving this equal billing with the big strategic bets, because reliability in the workhorse features is what earns trust in the flashy ones."
  },
  {
    "n": 6, "title": "Skills", "icon": "skills",
    "aka": None,
    "tag": "Match quality is the core promise",
    "summary": "Improving the quality, structure and governance of the skills ontology that feeds search and match \u2014 skills discovery, domains, validation, quality detection, and interoperability with external and client-owned taxonomies and frameworks.",
    "why": "Great skills data is what makes ProFinda feel like magic \u2014 the right person surfaced instantly. Every improvement here directly sharpens the core promise clients buy us for: trustworthy skills, sensible relationships, and matching that speaks each client's own language. Get this right and every search, every match and every downstream feature gets better with it.",
    "keywords": ["Skills validation & certification", "Skills Discovery", "Skills Domains", "External Taxonomies", "Skill Frameworks 2.0", "Ontology alignment", "Skills recommender", "Experience in matches", "Exclusion filters"],
    "clients": ["ey", "kpmg", "newton", "afry"],
    "notes": "Everything ProFinda promises rests on one thing: putting the right person forward. And a match is only ever as good as the skills data underneath it. The problem is that skills data is messy \u2014 inconsistent, unstructured, sometimes plain wrong, and rarely lined up with the way a client already describes their own people. When that data is poor, the matches are poor, and we're failing at the exact thing clients pay us for. So this initiative is about the quality, structure and governance of the skills that feed search and matching: making skills trustworthy, giving them sensible relationships, catching bad data automatically, and speaking the client's own taxonomy instead of forcing ours. We renamed it from 'Smarter Matching' to simply 'Skills', and pulled it organizationally closer to Search, because better matching isn't a separate feature \u2014 it's a direct consequence of getting the skills right. This underpins the core product promise."
  },
  {
    "n": 7, "title": "Internationalization", "icon": "globe",
    "aka": None,
    "tag": "One platform, every market",
    "summary": "Multi-language UI, a multilingual ontology, and regional/locale handling (calendars, labels) so the platform works the same everywhere.",
    "why": "Unlocks non-English-speaking markets and removes a recurring blocker for global enterprise clients operating across regions.",
    "keywords": ["Multilingual product", "Multilingual ontology", "Additional languages", "Locale & calendars", "Client relabelling"],
    "clients": ["ey"],
    "notes": "The problem is simple to state and expensive to ignore: our clients are global, their people are not all English speakers, and today the platform quietly assumes they are. When the interface, the skills language, or even the calendar doesn't fit a region, it becomes a real blocker to rolling ProFinda out across a whole organisation \u2014 and in some markets it's the reason we can't win the deal at all. So this initiative is about making the platform feel native everywhere: the interface in the user's own language, matching that works across languages, and the local details \u2014 calendars, labels, regional differences \u2014 handled properly rather than bolted on. Frame it as an investment, not a single feature: it cuts across everything we build, and it's the groundwork that unlocks entire non-English markets and makes every future global rollout possible. It pays back far beyond any one client."
  },
  {
    "n": 8, "title": "Self-Service Configuration", "icon": "gear",
    "aka": "Configurable Notification Engine",
    "tag": "Soft-coded, event-driven admin control",
    "summary": "Giving client admins direct control over notifications, permissions, user groups and settings \u2014 instead of routing every change through a support ticket.",
    "why": "Reduces support and delivery load, speeds up client-side changes, and improves end-user response times on booking requests and approvals.",
    "keywords": ["Notifications engine", "User groups", "Client-editable settings", "Permissions rework", "In-product documentation"],
    "clients": ["ey", "kpmg"],
    "notes": "Here's a problem that costs us on both sides. Right now, when a client wants to change something simple \u2014 who gets notified, who has permission to do what, how a group is set up \u2014 they can't just do it. They raise a ticket, it lands with our team, and everyone waits. That's slow and frustrating for them, and it's a constant drain on our support and delivery capacity for changes that shouldn't need an engineer at all. So this initiative hands that control back to client admins: let them configure notifications, permissions, groups and settings themselves, safely, without coming through us. The value is on both sides of the table \u2014 clients move faster and feel in control, and we free up real capacity to work on the roadmap instead of fielding config requests. Worth noting: this is also something we've already publicly committed to, so we're delivering on a promise, not inventing scope."
  },
  {
    "n": 9, "title": "Actuals", "icon": "loop",
    "aka": None,
    "tag": "Closing the loop: plan vs. reality",
    "summary": "Ingesting real timesheet / actuals data so RMs can compare planned bookings against what actually happened \u2014 with consistent planning units across SAP and ProFinda.",
    "why": "A foundational requirement for any serious workforce-planning conversation with finance stakeholders, and a precondition for a credible ROI story.",
    "keywords": ["Ingest client actuals", "Forecast vs. actuals", "Actual Utilisation", "New KPIs", "Mid-Market", "Timesheet values in-platform", "SAP S/4 hours plugin"],
    "clients": ["ey", "kpmg"],
    "notes": "Today the platform knows the plan but not the reality. We can tell you what was booked, but not what actually happened \u2014 the real hours people worked. That gap is a genuine problem, because without it a Resource Manager can never learn whether their plans were any good, and more importantly we can never prove our own value. If a finance stakeholder asks 'did this actually save us anything?', 'the plan looked great' is not an answer. So this initiative brings real timesheet data into the platform and lines it up against the plan, using consistent units so the comparison is honest rather than apples-to-oranges. Why it matters: it closes the loop between forecast and reality. That's the foundation for any serious workforce-planning conversation, and it's what lets us tell a credible ROI story instead of asserting one. Small in scope, but genuinely foundational \u2014 a lot of the bigger vision depends on it."
  },
  {
    "n": 10, "title": "Pricing & Budgeting", "icon": "coin",
    "aka": "renamed from \u201cCommercial Control\u201d",
    "tag": "Financial visibility before staffing",
    "summary": "Letting RMs see the cost, margin and budget impact of a staffing decision before they commit \u2014 and, because we also do the resourcing, flagging early whether the client has the skills and availability to actually deliver what the budget assumes.",
    "why": "What sets us apart from standalone pricing tools: because we also do the resourcing, the budget can flag early whether the client actually has the right skills and availability to deliver what it assumes \u2014 not just whether the numbers add up. Named repeatedly as a competitive gap, and a strong upsell for clients doing this in spreadsheets outside the platform.",
    "keywords": ["Pricing plan / budget in-platform", "Skills & availability early indicators", "Salesforce pricing app", "Engagement economics", "Revenue calculations"],
    "clients": ["am", "cohnreznick", "kpmg"],
    "notes": "The problem is that staffing decisions are also financial decisions, but we treat them as if they aren't. Right now someone books a team without seeing what it costs, what it does to margin, or whether it fits the budget \u2014 and then that analysis happens later, offline, in a spreadsheet outside the platform. That's slow, error-prone, and it means the money conversation is disconnected from the decision that drives it. So this initiative brings the financials into the moment of the decision: let people see cost, margin and budget impact before they commit, not after. Why it earns a place on the roadmap: it's been called out repeatedly as a gap against competitors, and for the many clients doing this in spreadsheets today it's a clear reason to bring more of their process into ProFinda. And here's our real differentiator against standalone pricing tools \u2014 because we also do the resourcing, the budgeting tool can give early indicators of whether the client actually has the right skills and the availability to deliver what the budget assumes. A finance-only tool can tell you the numbers add up; only we can tell you whether the people behind those numbers exist and are free. We renamed it from 'Commercial Control' to match how people actually talk about it \u2014 pricing and budgeting."
  },
  {
    "n": 11, "title": "CV Studio", "icon": "doc",
    "aka": None,
    "tag": "A client-facing deliverable in every pitch",
    "summary": "Rebuilding the CV export / template experience with real-time editing and AI-assisted content tailoring, plus a new CV parser.",
    "why": "One of the strongest, most tangible ROIs we offer clients. It saves real time exporting and formatting CVs, presents each consultant in the best possible lens so clients can 'sell' them to their own customers, and turns that into a repeatable, on-brand model. And because it draws on live profile data, the CV is always up to date \u2014 unlike traditional CV systems where the document goes stale the moment it's saved.",
    "keywords": ["CV exporter & templates", "CV Versions", "Real-time editing", "AI-assisted tailoring", "New CV parser"],
    "clients": ["afry", "ey"],
    "notes": "This one is small in scope but punches above its weight, and it's one of the clearest, most tangible ROIs we can point to. Three angles to land. First, time: exporting and formatting CVs by hand is slow and repetitive \u2014 we take that work away and make it a repeatable, on-brand model. Second, selling: the CV is the client's shop window in a pitch, so presenting each consultant in the best possible lens directly helps them win the work in front of their own customers. Third, and this is the one traditional CV systems can't match \u2014 because our CVs draw on live profile data, they're always up to date. A saved Word CV is stale the moment it's created; ours reflects the person's latest skills and experience every time. Add AI that tailors the CV to the specific opportunity, and you've got a small build with a very visible payoff and a genuinely differentiated story."
  },
  {
    "n": 12, "title": "Demand Setup", "icon": "form",
    "aka": None,
    "tag": "Quality upstream, quality everywhere",
    "summary": "Making it faster and more accurate to create demand \u2014 smarter role forms, reusable engagement / role templates, and contractor & contingent-worker handling.",
    "why": "Demand quality upstream directly determines match quality downstream, so this is a leverage point that pays off everywhere else.",
    "keywords": ["Role form", "Engagement / role templates", "Demand uploader v2", "Contractor / contingent handling", "RFP / unstructured text \u2192 role automation"],
    "clients": ["ey", "newton", "cohnreznick"],
    "notes": "The key idea here is garbage in, garbage out. Everything downstream \u2014 the matches we suggest, the reports we produce, the plans we optimise \u2014 is only as good as the demand that was entered at the start. And today entering demand is slower and sloppier than it should be: forms that don't guide you, teams rebuilding the same roles from scratch every time, and no clean way to handle contractors or bulk-create demand. When that upstream step is weak, that weakness quietly propagates into every other part of the platform. So this initiative is about quality at the source: make it faster and more accurate to describe what's needed, with smarter forms and reusable templates so nobody starts from a blank page. The framing to land: this isn't the glamorous slide, but it's a leverage point \u2014 fix demand once, upstream, and the quality improvement is felt everywhere else for free."
  },
  {
    "n": 13, "title": "Next-Gen Experience & Platform Redesign", "icon": "sparkle",
    "aka": "absorbs \u201cEveryday UX Polish\u201d",
    "tag": "Elevates perceived value in every demo",
    "summary": "A comprehensive modernization of ProFinda's visual identity and core UI \u2014 a refreshed design system and a redesigned individual Profile experience.",
    "why": "Lifts perceived product value in enterprise demos, drives end-user engagement, and modernizes the profile hub to support skills self-reporting and talent mobility.",
    "keywords": ["Design system refresh", "Redesigned profile hub", "Persona-specific UX", "Responsive core modules", "Everyday UX papercuts"],
    "clients": [],
    "notes": "Be upfront that this one is forward-looking, not a committed near-term build. The problem it addresses is perception. In an enterprise demo, how the product looks and feels is doing a lot of the selling before anyone reads a feature list \u2014 and a capable platform that looks dated gets marked down for reasons that have nothing to do with what it can actually do. There's also a real user cost: a modern, engaging experience is what pulls people in to keep their own profiles and skills up to date, which feeds everything else. So this is a comprehensive modernization \u2014 a refreshed visual language and a redesigned profile experience \u2014 plus the long tail of small interface annoyances we track so they don't quietly pile up. Position it as where we're taking the platform: it lifts perceived value in every demo and drives the day-to-day engagement the rest of the roadmap depends on."
  },
  {
    "n": 14, "title": "Strategic Workforce Planning", "icon": "future",
    "aka": None,
    "tag": "Budget human + digital workforce together",
    "summary": "Forward-looking capacity planning that lets organizations model future demand, skill gaps and headcount across both human talent and synthetic AI agents \u2014 in one unified platform.",
    "why": "Positions ProFinda as a leader in next-generation workforce planning, letting enterprises budget and allocate human capital and digital workforce capacity together.",
    "keywords": ["Human & AI agents", "Long-term capacity vs. demand", "Skill-gap forecasting", "Human + AI-agent modeling", "MCP-connected digital workers"],
    "clients": [],
    "notes": "This is the vision slide, so say that plainly \u2014 it's where we're pointing, not something shipping next quarter. The problem it anticipates is the one every large organisation is about to face: how do you plan a workforce when part of that workforce is no longer human? Companies already need to look further ahead \u2014 modelling future demand, spotting skill gaps before they bite \u2014 and now they also have to fold AI agents into that same picture and budget for human and digital capacity together. Nobody has a real home for that yet. Our bet is that ProFinda should be it, because everything else on this roadmap builds toward it: knowing what actually happened, knowing people's real capabilities, and being able to connect AI agents into the platform. Leave them with the big idea \u2014 planning the blended human-and-AI workforce in one place \u2014 and let that be the note the whole presentation ends on."
  },
]

# Client label map (for the floating logo chips / legend)
CLIENTS = {
  "ey": "EY", "kpmg": "KPMG", "deloitte": "Deloitte", "afry": "AFRY",
  "cohnreznick": "Cohn Reznick", "newton": "Newton", "am": "Alvarez & Marsal",
}

data_json = json.dumps({"initiatives": INITIATIVES, "clients": CLIENTS}, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ProFinda \u00b7 Product Roadmap</title>
<style>
/*__FONTS__*/
:root{
  --navy:#131E2D; --navy2:#203142; --navy3:#0C1622; --navy-soft:#1B2A3B;
  --teal:#0EAD9A; --teal-dark:#0A8377; --lime:#8CC63F; --lime-dark:#6fa02f;
  --blue:#1B9AF0; --blue-deep:#0A52C0; --purple:#8E9BC4; --purple-deep:#5A6aa0;
  /* Horizon 1 = teal/lime (existing). Horizon 2 = yellow-ish. Horizon 3 = orange->red. */
  --h2a:#F6C445; --h2b:#E8A317; --h2-dark:#B77C0C;
  --h3a:#F97316; --h3b:#E23B2E; --h3-dark:#B4231A;
  --slate:#C7D2DE; --muted:#8FA1B3; --muted2:#6B7C8E;
  --ink:#EAF1F8; --line:rgba(255,255,255,.09);
  /* Themeable accents. Horizon 1 (default) = teal -> lime.
     go() swaps these (via body.h2 / body.h3) and every accent surface eases to the new palette.
     --accA/--accB drive gradients & text; --accGlow is the rgba used for shadows/glows. */
  --accA:var(--teal); --accB:var(--lime); --accDark:var(--teal-dark);
  --accGlow:rgba(14,173,154,.6); --accGlowSoft:rgba(14,173,154,.18); --accGlow2:rgba(140,198,63,.6);
}
/* Horizon 2 = warm amber / gold */
body.h2{
  --accA:var(--h2a); --accB:var(--h2b); --accDark:var(--h2-dark);
  --accGlow:rgba(246,196,69,.6); --accGlowSoft:rgba(246,196,69,.20); --accGlow2:rgba(232,163,23,.6);
}
/* Horizon 3 = orange -> red */
body.h3{
  --accA:var(--h3a); --accB:var(--h3b); --accDark:var(--h3-dark);
  --accGlow:rgba(249,115,22,.6); --accGlowSoft:rgba(249,115,22,.20); --accGlow2:rgba(226,59,46,.62);
}
/* Smooth the palette change on every accent surface as horizons switch. */
.progress,.dots i,.accent,.eyebrow .dot,.eyebrow .ln,.eyebrow,.init-num,.init .tag,
.init .why b,.chip::before,.glyph .core svg,.glyph .orb,.glyph .r2,.glyph .r3,
.part .kick,.part .rule,.counter b,.na,.notes-toggle b,.closing .three .b span,
.kick,.h-lead .accent{
  transition:color .9s ease, background .9s ease, background-color .9s ease,
    border-color .9s ease, box-shadow .9s ease, fill .9s ease, filter .9s ease,
    -webkit-text-fill-color .9s ease;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{
  font-family:'Mulish','Inter',system-ui,-apple-system,sans-serif;
  background:var(--navy3); color:var(--ink);
  -webkit-font-smoothing:antialiased;
  cursor:default;
}
h1,h2,h3,h4{line-height:1.06;font-weight:900;letter-spacing:-.02em}
::selection{background:rgba(14,173,154,.35)}

/* ---------- Stage ---------- */
#stage{position:fixed;inset:0;overflow:hidden}
.bg-net{position:absolute;inset:0;z-index:0;opacity:.9;pointer-events:none;width:100%;height:100%}
/* 3D scene: slides live in a perspective volume and arrive from the camera's new angle */
#slides{position:absolute;inset:0;perspective:1400px;perspective-origin:50% 50%;transform-style:preserve-3d}
.bg-glow{position:absolute;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(1100px 620px at 82% -8%,rgba(14,173,154,.20),transparent 60%),
    radial-gradient(900px 520px at 6% 116%,rgba(27,154,240,.16),transparent 55%),
    radial-gradient(700px 500px at 50% 120%,rgba(140,198,63,.10),transparent 60%),
    linear-gradient(160deg,var(--navy) 0%,var(--navy3) 100%);
}
.grain{position:absolute;inset:0;z-index:1;pointer-events:none;opacity:.05;
  background-image:radial-gradient(rgba(255,255,255,.6) .5px,transparent .5px);
  background-size:3px 3px;}

.slide{position:absolute;inset:0;z-index:2;display:flex;align-items:center;justify-content:center;
  padding:clamp(28px,4.4vw,84px);opacity:0;visibility:hidden;pointer-events:none;
  transform-style:preserve-3d;transform-origin:50% 50%;
  /* incoming 3D offset (set per-transition by JS); eases to 0 when active */
  transform:translate3d(var(--sx,0px),var(--sy,0px),var(--sz,-620px)) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg));
  transition:opacity .7s ease, transform 1.35s cubic-bezier(.19,.72,.16,1);}
.slide.active{opacity:1;visibility:visible;pointer-events:auto;
  transform:translate3d(0,0,0) rotateX(0) rotateY(0)}
.slide-inner{width:100%;max-width:1500px;position:relative}

/* fly-in animation building blocks */
.anim{opacity:0;transform:translateY(26px);filter:blur(6px);
  transition:opacity .62s cubic-bezier(.2,.7,.2,1),transform .62s cubic-bezier(.2,.7,.2,1),filter .62s ease;}
.slide.active .anim{opacity:1;transform:none;filter:none}
.slide.active .anim.d1{transition-delay:.10s}
.slide.active .anim.d2{transition-delay:.20s}
.slide.active .anim.d3{transition-delay:.30s}
.slide.active .anim.d4{transition-delay:.40s}
.slide.active .anim.d5{transition-delay:.50s}
.slide.active .anim.d6{transition-delay:.60s}

/* ---------- Shared ---------- */
.eyebrow{display:inline-flex;align-items:center;gap:11px;font-size:clamp(11px,1vw,13.5px);font-weight:800;
  letter-spacing:.22em;text-transform:uppercase;color:var(--accA);margin-bottom:20px}
.eyebrow .ln{width:38px;height:2px;background:linear-gradient(90deg,var(--accA),transparent)}
.eyebrow .dot{width:8px;height:8px;border-radius:50%;background:var(--accA);box-shadow:0 0 0 5px var(--accGlowSoft)}
.accent{background:linear-gradient(92deg,var(--accA),var(--accB));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.accent-blue{background:linear-gradient(92deg,var(--blue),var(--teal));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}

/* ---------- Cover ---------- */
.cover h1{font-size:clamp(44px,7.4vw,116px);line-height:.98}
.cover .sub{font-size:clamp(17px,2vw,27px);color:var(--slate);max-width:30ch;margin-top:26px;font-weight:500;line-height:1.4}
.cover .foot{margin-top:44px;display:flex;gap:14px;flex-wrap:wrap}
.pill{display:inline-flex;align-items:center;gap:9px;background:rgba(255,255,255,.05);border:1px solid var(--line);
  border-radius:100px;padding:11px 20px;font-size:14px;font-weight:700;color:#dfe9f2;backdrop-filter:blur(6px)}
.pill b{color:#fff}
.cover-logo{height:34px;margin-bottom:40px;filter:drop-shadow(0 4px 20px rgba(0,0,0,.4))}

/* horizon row (three phases of the roadmap) */
.statrow{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:44px;max-width:880px}
.stat{position:relative;overflow:hidden;background:rgba(255,255,255,.045);border:1px solid var(--line);
  border-radius:18px;padding:22px 20px;backdrop-filter:blur(8px)}
.stat::before{content:"";position:absolute;top:0;left:0;width:100%;height:4px;
  background:linear-gradient(90deg,var(--teal),var(--lime))}
.stat .hz{font-size:10.5px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;
  color:var(--teal);margin-bottom:9px}
.stat .n{font-size:clamp(20px,2.5vw,31px);font-weight:900;letter-spacing:-.02em;line-height:1.08;
  background:linear-gradient(90deg,#fff,var(--teal));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.stat .l{font-size:13px;color:var(--slate);font-weight:600;margin-top:6px;line-height:1.35}
/* Horizon 2 = yellow-ish */
.stat.h2::before{background:linear-gradient(90deg,var(--h2a),var(--h2b))}
.stat.h2 .hz{color:var(--h2a)}
.stat.h2 .n{background:linear-gradient(90deg,#fff,var(--h2a));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
/* Horizon 3 = orange -> red */
.stat.h3::before{background:linear-gradient(90deg,var(--h3a),var(--h3b))}
.stat.h3 .hz{color:var(--h3a)}
.stat.h3 .n{background:linear-gradient(90deg,#fff,var(--h3a));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}

/* ---------- Philosophy slide ---------- */
.philo h2{font-size:clamp(30px,4.6vw,68px)}
.philo .lead{font-size:clamp(16px,1.7vw,23px);color:var(--slate);max-width:62ch;margin-top:22px;line-height:1.5;font-weight:500}
.philo .lead em{color:#fff;font-style:normal;font-weight:800}
.audience{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:42px}
.aud{background:rgba(255,255,255,.045);border:1px solid var(--line);border-radius:16px;padding:20px 16px;text-align:center;position:relative;overflow:hidden}
.aud::before{content:"";position:absolute;top:0;left:0;width:100%;height:3px;background:linear-gradient(90deg,var(--teal),var(--lime))}
.aud .ai{width:46px;height:46px;margin:0 auto 12px;border-radius:13px;display:grid;place-items:center;
  background:linear-gradient(135deg,var(--navy2),var(--navy-soft));border:1px solid var(--line)}
.aud .ai svg{width:24px;height:24px;color:var(--teal)}
.aud h4{font-size:15px;color:#fff;margin-bottom:4px}
.aud p{font-size:12px;color:var(--muted);line-height:1.35}
.aud.primary::before{height:5px}
.aud.primary .ai{background:linear-gradient(135deg,var(--teal-dark),var(--teal))}
.aud.primary .ai svg{color:#fff}
.aud.primary h4{color:#fff}
.aud .badge{position:absolute;top:9px;right:10px;font-size:9px;font-weight:800;letter-spacing:.1em;color:var(--lime);text-transform:uppercase}

.dna{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:20px}
.dna .card{background:rgba(255,255,255,.045);border:1px solid var(--line);border-radius:18px;padding:26px 24px}
.dna .card .ci{width:44px;height:44px;border-radius:12px;display:grid;place-items:center;margin-bottom:15px;color:#fff}
.dna .card:nth-child(1) .ci{background:linear-gradient(135deg,var(--teal),var(--teal-dark))}
.dna .card:nth-child(2) .ci{background:linear-gradient(135deg,var(--blue),var(--blue-deep))}
.dna .card:nth-child(3) .ci{background:linear-gradient(135deg,var(--lime),var(--lime-dark))}
.dna .card .ci svg{width:23px;height:23px}
.dna .card h4{font-size:19px;color:#fff;margin-bottom:9px}
.dna .card p{font-size:14.5px;color:var(--slate);line-height:1.5}

/* ---------- Part band ---------- */
.part .kick{font-size:clamp(13px,1.3vw,17px);font-weight:800;letter-spacing:.24em;text-transform:uppercase;color:var(--accA);margin-bottom:18px}
.part h2{font-size:clamp(36px,6vw,92px)}
.part .rule{height:5px;width:120px;background:linear-gradient(90deg,var(--accA),var(--accB));border-radius:3px;margin-top:26px;box-shadow:0 0 30px var(--accGlow)}
.part .cnt{margin-top:26px;font-size:clamp(15px,1.6vw,20px);color:var(--slate);max-width:56ch;line-height:1.5}

/* ---------- Initiative slide ---------- */
.init-grid{display:grid;grid-template-columns:1.15fr .85fr;
  grid-template-areas:"intro glyph" "why kw";
  grid-template-rows:auto auto;
  column-gap:clamp(30px,4vw,72px);row-gap:clamp(20px,2.4vw,34px);align-items:center}
.init-grid .col-intro{grid-area:intro;align-self:end}
.init-grid .col-glyph{grid-area:glyph;align-self:center}
.init-grid .col-why{grid-area:why;align-self:start;padding-top:43px}
.init-grid .col-kw{grid-area:kw;align-self:start}
.init-num{font-size:clamp(15px,1.4vw,19px);font-weight:900;color:var(--accA);letter-spacing:.08em;display:flex;align-items:center;gap:14px;margin-bottom:16px}
.init-num .of{color:var(--muted2);font-weight:700}
.init-num .bar{flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}
.init h2{font-size:clamp(32px,4.7vw,66px);color:#fff}
.init .aka{margin-top:14px;font-size:clamp(13px,1.25vw,17px);color:var(--muted);font-style:italic;font-weight:600;display:flex;align-items:center;gap:9px}
.init .aka .ic{font-style:normal}
.init .tag{margin-top:22px;display:inline-block;font-size:clamp(13px,1.3vw,16.5px);font-weight:800;color:var(--accB);
  border-left:3px solid var(--accB);padding:5px 0 5px 16px;background:linear-gradient(90deg,var(--accGlowSoft),transparent);border-radius:0 8px 8px 0}
.init .summary{margin-top:26px;font-size:clamp(15px,1.55vw,21px);color:var(--slate);line-height:1.52;max-width:60ch}
.init .why{margin-top:0;font-size:clamp(13.5px,1.35vw,17px);color:#cdd9e5;line-height:1.5;max-width:60ch;
  background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
.init .why b{color:var(--accA)}
.init .why.big{font-size:clamp(15px,1.55vw,20px);padding:24px 26px;line-height:1.58;
  background:linear-gradient(120deg,var(--accGlowSoft),rgba(255,255,255,.03));
  border-color:var(--accGlowSoft);box-shadow:0 14px 44px rgba(0,0,0,.35)}

/* keyword chips (the decomposition of the initiative) */
.kw-wrap{display:flex;flex-direction:column;gap:14px}
.kw-head{font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--muted2)}
.kw{display:flex;flex-wrap:wrap;gap:11px}
.chip{font-size:clamp(13px,1.35vw,16px);font-weight:700;color:#eaf3fb;
  background:rgba(255,255,255,.05);border:1px solid var(--line);border-radius:12px;padding:11px 16px;
  opacity:0;transform:translateY(14px) scale(.96);
  transition:opacity .5s ease,transform .5s cubic-bezier(.2,.7,.2,1),border-color .3s,background .3s}
.slide.active .chip{opacity:1;transform:none}
.chip:nth-child(1){transition-delay:.45s}
.chip:nth-child(2){transition-delay:.52s}
.chip:nth-child(3){transition-delay:.59s}
.chip:nth-child(4){transition-delay:.66s}
.chip:nth-child(5){transition-delay:.73s}
.chip:nth-child(6){transition-delay:.80s}
.chip:nth-child(7){transition-delay:.87s}
.chip:nth-child(8){transition-delay:.94s}
.chip:nth-child(9){transition-delay:1.01s}
.chip::before{content:"";display:inline-block;width:7px;height:7px;border-radius:2px;margin-right:9px;vertical-align:middle;
  background:linear-gradient(135deg,var(--accA),var(--accB))}

/* big glyph */
.glyph{position:relative;display:grid;place-items:center;aspect-ratio:1;max-width:340px;margin:0 auto;width:100%}
.glyph .ring{position:absolute;border:1px solid var(--line);border-radius:50%}
.glyph .r1{inset:0;animation:spin 34s linear infinite}
.glyph .r2{inset:14%;border-style:dashed;border-color:var(--accGlowSoft);animation:spin 26s linear infinite reverse}
.glyph .r3{inset:30%;border-color:var(--accGlowSoft);animation:spin 20s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.glyph .core{width:44%;height:44%;border-radius:26px;display:grid;place-items:center;
  background:linear-gradient(150deg,var(--navy2),var(--navy-soft));border:1px solid var(--line);
  box-shadow:0 20px 60px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.06)}
.glyph .core svg{width:52%;height:52%;color:var(--accA);filter:drop-shadow(0 0 14px var(--accGlow))}
.glyph .orb{position:absolute;width:12px;height:12px;border-radius:50%;background:radial-gradient(circle,var(--accB),var(--accA));box-shadow:0 0 14px var(--accGlow2)}
.glyph .o1{top:2%;left:48%}
.glyph .o2{bottom:8%;right:6%;background:radial-gradient(circle,var(--blue),var(--teal))}
.glyph .o3{bottom:12%;left:4%}

/* clients as small, faint ghost names arranged in a ring around the glyph icon */
.glyph-wrap{position:relative;width:100%;max-width:360px;margin:0 auto;aspect-ratio:1}
.glyph-wrap .glyph{max-width:none}
.cl-orbit{position:absolute;top:50%;left:50%;width:0;height:0;
  /* sit on an invisible ring at angle --a, radius --r (px); place at the ring point, then
     recentre the label on that point and counter-rotate so text stays upright */
  transform:rotate(var(--a)) translate(var(--r,128px)) rotate(calc(-1 * var(--a)));
  transform-origin:0 0;white-space:nowrap;
  font-size:clamp(12px,1.15vw,15px);font-weight:900;letter-spacing:-.01em;
  color:rgba(255,255,255,.32);text-shadow:0 1px 8px rgba(9,15,23,.85);
  opacity:0;transition:opacity .6s ease}
.cl-orbit>span{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);display:block}
.slide.active .cl-orbit{opacity:1}
.slide.active .cl-orbit:nth-child(1){transition-delay:.5s}
.slide.active .cl-orbit:nth-child(2){transition-delay:.62s}
.slide.active .cl-orbit:nth-child(3){transition-delay:.74s}
.slide.active .cl-orbit:nth-child(4){transition-delay:.86s}
.slide.active .cl-orbit:nth-child(5){transition-delay:.98s}
.cl-orbit.none{transform:translate(-50%,-50%);left:50%;top:118%;
  font-size:12px;font-weight:700;font-style:italic;color:rgba(255,255,255,.14)}
.cl-orbit-label{position:absolute;left:50%;top:calc(100% + 10px);transform:translateX(-50%);
  font-size:10px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:var(--muted2);white-space:nowrap}

/* floating faint client glyphs in background of init slides */
.floaters{position:absolute;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.floaters span{position:absolute;font-size:clamp(30px,5vw,72px);font-weight:900;color:rgba(255,255,255,.03);
  letter-spacing:-.03em;white-space:nowrap;animation:drift 24s ease-in-out infinite}
@keyframes drift{0%,100%{transform:translateY(0)}50%{transform:translateY(-22px)}}

/* ---------- Closing ---------- */
.closing h2{font-size:clamp(36px,5.6vw,84px)}
.closing .sub{font-size:clamp(16px,1.8vw,24px);color:var(--slate);max-width:52ch;margin-top:24px;line-height:1.45;font-weight:500}
.closing .three{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:44px;max-width:940px}
.closing .three .b{display:flex;align-items:center;gap:13px;background:rgba(255,255,255,.05);border:1px solid var(--line);border-radius:100px;padding:14px 22px;font-weight:700;font-size:15px;color:#fff}
.closing .three .b span{width:26px;height:26px;flex:none;border-radius:50%;background:linear-gradient(135deg,var(--accA),var(--accB));color:var(--navy3);font-weight:900;font-size:13px;display:grid;place-items:center}

/* ---------- Chrome (nav / progress / hint) ---------- */
.topbar{position:fixed;top:0;left:0;right:0;height:64px;z-index:40;display:flex;align-items:center;justify-content:space-between;
  padding:0 clamp(22px,4vw,54px);pointer-events:none}
.topbar img{height:22px;opacity:.92;transition:opacity .4s ease}
/* hide the small top-bar logo on slides that carry their own big centred logo
   (cover + closing), so the two wordmarks don't overlap at top-left */
#topbar.logo-hidden img{opacity:0}
.tb-right{display:flex;align-items:center;gap:16px;pointer-events:auto}
.section-label{font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);}
.counter{font-size:13px;font-weight:800;color:#fff;background:rgba(255,255,255,.06);border:1px solid var(--line);border-radius:100px;padding:7px 14px}
.counter b{color:var(--accA)}

.progress{position:fixed;bottom:0;left:0;height:4px;z-index:40;background:linear-gradient(90deg,var(--accA),var(--accB));width:0;transition:width .5s cubic-bezier(.2,.7,.2,1),background .9s ease,box-shadow .9s ease;box-shadow:0 0 16px var(--accGlow)}
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
.notes-toggle:hover{border-color:var(--teal);color:#fff}
.notes-toggle b{color:var(--teal);font-weight:800}
.notes-toggle.on{background:rgba(14,173,154,.14);border-color:var(--teal)}
.notes-toggle.on b{color:var(--lime)}
.notes-toggle .nt-dot{width:9px;height:9px;border-radius:50%;background:var(--muted2);transition:all .2s}
.notes-toggle.on .nt-dot{background:var(--lime);box-shadow:0 0 0 4px rgba(140,198,63,.2)}
.notes-toggle .nt-key{display:inline-grid;place-items:center;min-width:20px;height:20px;padding:0 6px;margin-left:3px;
  border-radius:5px;background:rgba(255,255,255,.08);border:1px solid var(--line);font-size:11px;font-weight:800;color:#dfe9f2}

#notesPanel{position:fixed;left:50%;transform:translateX(-50%) translateY(14px);bottom:26px;z-index:45;
  width:min(1040px,86vw);max-height:30vh;overflow-y:auto;
  background:rgba(12,22,34,.86);border:1px solid var(--line);border-radius:16px;
  padding:18px 24px 20px;backdrop-filter:blur(14px);
  box-shadow:0 24px 70px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.05);
  opacity:0;visibility:hidden;pointer-events:none;transition:opacity .3s ease,transform .3s cubic-bezier(.2,.7,.2,1)}
#notesPanel.show{opacity:1;visibility:visible;pointer-events:auto;transform:translateX(-50%) translateY(0)}
#notesPanel .np-head{display:flex;align-items:center;gap:9px;font-size:10.5px;font-weight:800;letter-spacing:.18em;
  text-transform:uppercase;color:var(--teal);margin-bottom:9px}
#notesPanel .np-head::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--lime);box-shadow:0 0 0 4px rgba(140,198,63,.18)}
#notesPanel .np-body{font-size:clamp(14px,1.15vw,15.5px);line-height:1.55;color:#e7eef6;font-weight:500}
#notesPanel::-webkit-scrollbar{width:8px}
#notesPanel::-webkit-scrollbar-thumb{background:rgba(255,255,255,.14);border-radius:8px}

@media (max-width:960px){
  .init-grid{grid-template-columns:1fr;grid-template-areas:"intro" "glyph" "why" "kw";gap:26px}
  .init-grid .col-why{padding-top:0}
  .glyph{max-width:220px}
  .audience,.statrow,.closing .three,.dna{grid-template-columns:1fr 1fr}
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
<div class="hint" id="hint"><span class="key">\u2190</span><span class="key">\u2192</span> arrows or click to navigate \u00b7 <span class="key">F</span> fullscreen \u00b7 <span class="key">N</span> speaker notes</div>

<div id="notesPanel" aria-live="polite">
  <div class="np-head">Speaker notes</div>
  <div class="np-body" id="notesBody"></div>
</div>

<script>
const DATA = __DATA__;
const LOGO = "__LOGO__";

/* ---------- SVG icon set ---------- */
const ICON = {
  spark:'<path d="M12 2v6M12 16v6M2 12h6M16 12h6M5.6 5.6l4.2 4.2M14.2 14.2l4.2 4.2M18.4 5.6l-4.2 4.2M9.8 14.2l-4.2 4.2"/><circle cx="12" cy="12" r="3"/>',
  planner:'<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5z"/>',
  grid:'<rect x="3" y="3" width="7" height="7" rx="1.4"/><rect x="14" y="3" width="7" height="7" rx="1.4"/><rect x="3" y="14" width="7" height="7" rx="1.4"/><path d="M17.5 14v3.4M14 17.5h7"/>',
  chart:'<path d="M3 3v18h18"/><path d="M7 15l3-4 3 2 4-6"/>',
  list:'<path d="M8 6h13M8 12h13M8 18h13"/><circle cx="3.6" cy="6" r="1.3" fill="currentColor" stroke="none"/><circle cx="3.6" cy="12" r="1.3" fill="currentColor" stroke="none"/><circle cx="3.6" cy="18" r="1.3" fill="currentColor" stroke="none"/>',
  skills:'<circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="M6.7 7.4 10.6 16M17.3 7.4 13.4 16M7 6h10"/>',
  globe:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/>',
  gear:'<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9 17 7M7 17l-2.1 2.1"/>',
  loop:'<path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 3v5h-5"/>',
  coin:'<circle cx="12" cy="12" r="9"/><path d="M12 7v10M9.5 9.2a2.4 2.4 0 0 1 4.6.6M14.5 14.8a2.4 2.4 0 0 1-4.6-.6"/>',
  doc:'<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>',
  form:'<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/>',
  sparkle:'<path d="m12 3 2 5 5 2-5 2-2 5-2-5-5-2 5-2z"/>',
  future:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/><path d="M3 12h2M19 12h2"/>',
  aud_rm:'<rect x="3" y="3" width="7" height="7" rx="1.4"/><rect x="14" y="3" width="7" height="7" rx="1.4"/><rect x="3" y="14" width="7" height="7" rx="1.4"/><path d="M17.5 14v3.4M14 17.5h7"/>',
  aud_em:'<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
  aud_sp:'<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
  aud_c:'<path d="M3 21h18"/><path d="M5 21V7l7-4 7 4v14"/><path d="M9 21v-6h6v6"/>',
  aud_wf:'<circle cx="9" cy="8" r="3"/><circle cx="17" cy="10" r="2.4"/><path d="M3 20a6 6 0 0 1 12 0M14 20a5 5 0 0 1 7-2.5"/>',
  dna_client:'<path d="M20 7 9 18l-5-5"/>',
  dna_bal:'<path d="M12 3v18M7 8H4l3-4 3 4H7v8M17 8h-3l3-4 3 4h-3v8"/>',
  dna_ai:'<circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/><circle cx="12" cy="2" r="1" fill="currentColor" stroke="none"/><circle cx="12" cy="22" r="1" fill="currentColor" stroke="none"/><circle cx="2" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="22" cy="12" r="1" fill="currentColor" stroke="none"/>',
};
const svg=(p,cls)=>`<svg class="${cls||''}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">${p}</svg>`;

/* ---------- Build slides ---------- */
const slidesEl=document.getElementById('slides');
const slides=[]; // {section,note}
function add(html, section, note, theme){ const d=document.createElement('div'); d.className='slide'; if(theme){ d.dataset.theme=theme; } d.innerHTML='<div class="slide-inner">'+html+'</div>'; slidesEl.appendChild(d); slides.push({el:d,section,note:note||'',theme:theme||''}); }

/* Cover */
add(`
  <div class="cover">
    <img class="cover-logo anim" src="${LOGO}" alt="ProFinda">
    <div class="eyebrow anim d1"><span class="ln"></span>Product Roadmap \u00b7 Next 18 Months</div>
    <h1 class="anim d2">The Future of<br><span class="accent">Resourcing.</span></h1>
    <p class="sub anim d3">An AI-first roadmap \u2014 14 initiatives, carefully selected to deepen the product our clients already rely on, and to win the ones we want next.</p>
    <div class="statrow anim d4">
      <div class="stat"><div class="hz">Horizon 1</div><div class="n">14 Initiatives</div><div class="l">The core resourcing platform, deepened</div></div>
      <div class="stat h2"><div class="hz">Horizon 2</div><div class="n">Alumni &amp; Events</div><div class="l">Two new products \u2014 communities &amp; events</div></div>
      <div class="stat h3"><div class="hz">Horizon 3</div><div class="n">&lt;Placeholder&gt;</div><div class="l">Where we go next</div></div>
    </div>
    <div class="notes-toggle anim d5" id="notesToggle" role="button" tabindex="0" aria-pressed="false">
      <span class="nt-dot"></span>Speaker notes: <b id="ntState">Off</b><span class="nt-key">N</span>
    </div>
  </div>`, 'Overview',
  "Welcome, and thanks for the time. What you're about to see is our product roadmap for the next twelve to eighteen months \u2014 and the one-line version is right here: this is an AI-first roadmap. Fourteen initiatives, each carefully calculated to deepen the product our clients already rely on and to win the ones we want next. I'll pause on the numbers because they frame everything: fourteen strategic initiatives; an ontology with roughly 2.7 million interconnections powering our matching; and time-to-resource-a-role going from three weeks down to about four minutes. That last one is the promise in a nutshell. One practical note for me as I present \u2014 I've got speaker notes I can toggle with this control or the N key; you won't see them, they just keep me honest on the detail. Let's get into where we're heading.")

/* Philosophy 1 - AI-first + audiences */
add(`
  <div class="philo">
    <div class="eyebrow anim"><span class="dot"></span>Where we're heading</div>
    <h2 class="anim d1">An <span class="accent">AI-first</span> platform \u2014<br>relevant far beyond the RM.</h2>
    <p class="lead anim d2">ProFinda has always served the <em>Resource Manager</em> first. This roadmap keeps that promise \u2014 and extends the platform's intelligence to <em>everyone</em> with a stake in how work gets staffed.</p>
    <div class="audience anim d3">
      <div class="aud primary"><span class="badge">First</span><div class="ai">${svg(ICON.aud_rm)}</div><h4>Resource Managers</h4><p>Faster, smarter staffing every day</p></div>
      <div class="aud"><div class="ai">${svg(ICON.aud_em)}</div><h4>Engagement Managers</h4><p>Demand created right, first time</p></div>
      <div class="aud"><div class="ai">${svg(ICON.aud_c)}</div><h4>C-Suite</h4><p>Strategic workforce planning</p></div>
      <div class="aud"><div class="ai">${svg(ICON.aud_wf)}</div><h4>The Workforce</h4><p>Visibility, mobility, growth</p></div>
    </div>
  </div>`, 'Overview',
  "Here's the strategic shift. ProFinda has always served the Resource Manager first, and this roadmap absolutely keeps that promise \u2014 RMs stay our primary user, and they benefit from almost every initiative you'll see. But AI lets us extend the platform's intelligence to everyone with a stake in how work gets staffed. Walk left to right: Resource Managers get faster, smarter staffing every day \u2014 that's the core. Engagement Managers get demand created right the first time \u2014 and the margin-and-compliance view Senior Partners care about now sits naturally between the EM and the C-Suite rather than as its own audience. The C-Suite gets genuine strategic workforce planning. And the workforce itself gets visibility, mobility and growth. The reason this matters commercially: every new audience is a new buying centre inside the same client. We're not walking away from the RM \u2014 we're growing outward from a position of strength. Keep that RM-to-C-Suite arc in mind, because the closing slide comes right back to it.")

/* Philosophy 2 - DNA / discipline */
add(`
  <div class="philo">
    <div class="eyebrow anim"><span class="dot"></span>How we build</div>
    <h2 class="anim d1">Not features for the sake of it.</h2>
    <p class="lead anim d2">Every item on this roadmap is <em>carefully selected</em> to enhance the existing product and make it more relevant \u2014 for our current client base, and to win prospects. We add what feels like <em>ProFinda's DNA</em>, blending client change-requests with our own thinking.</p>
    <div class="dna anim d3">
      <div class="card"><div class="ci">${svg(ICON.dna_client)}</div><h4>Client-driven</h4><p>Grounded in real change-requests from EY, KPMG, AFRY, Alvarez &amp; Marsal and more \u2014 not a wish-list built in a vacuum.</p></div>
      <div class="card"><div class="ci">${svg(ICON.dna_bal)}</div><h4>Deepen &amp; extend</h4><p>Each initiative strengthens what already works and opens the door to clients we don't yet own.</p></div>
      <div class="card"><div class="ci">${svg(ICON.dna_ai)}</div><h4>Distinctly ProFinda</h4><p>AI-native, skills-led, enterprise-grade. We blend client asks with our own product thinking.</p></div>
    </div>
  </div>`, 'Overview',
  "One slide on discipline, because it pre-empts the obvious question: is this just a wish-list? No. Every item is carefully selected to enhance the existing product and make it more relevant \u2014 both for the clients we have and the prospects we want. Three principles. First, it's client-driven: grounded in real change-requests from the firms we work with, not invented in a vacuum. Second, deepen and extend: each initiative strengthens something that already works and opens the door to clients we don't yet own. Third, it's distinctly ProFinda: AI-native, skills-led, enterprise-grade. The phrase I'd land is 'ProFinda's DNA' \u2014 we take the client ask and blend it with our own product thinking, rather than just building tickets to order. That blend is what stops the roadmap being a backlog and makes it a strategy. With that lens set, let's look at the fourteen initiatives themselves.")

/* Part band */
add(`
  <div class="part">
    <div class="kick anim">The Roadmap</div>
    <h2 class="anim d1">14 Initiatives,<br><span class="accent">one direction.</span></h2>
    <div class="rule anim d2"></div>
    <p class="cnt anim d3">Named for the improvement they deliver \u2014 not the team that builds them. Each decomposes into the concrete work behind it, and the clients waiting on it.</p>
  </div>`, 'The Roadmap',
  "Quick framing before the detail, and it's an important one. We deliberately regrouped a messy legacy backlog into fourteen equally-weighted initiatives, and we named each one after the improvement it delivers \u2014 not the pod or the team that happens to build it. That's why you'll see 'Booking Flexibility' rather than a team name. Two things to watch for as we go: each initiative decomposes into concrete, real tickets \u2014 you'll see the actual work behind it \u2014 and each carries the clients currently waiting on it. A few also show an 'aka' subtitle: that's the alternative name our Head of Product proposed for the same thing, and part of this whole exercise was reconciling that naming so we're all pointing the same direction. Fourteen initiatives, one direction. Let's take them in order.")

/* Initiative slides */
// clients rendered as faint ghost names on an invisible ring around the glyph
const clientOrbit = (keys)=>{
  if(!keys || !keys.length)
    return `<span class="cl-orbit none">Vision-stage \u00b7 no client attached yet</span>`;
  const n=keys.length;
  return keys.map((k,i)=>{
    const a = -90 + i*(360/n);           // start at top, spread evenly
    const r = n<=4 ? 132 : 148;          // px radius, sits outside the icon core on the ring
    return `<span class="cl-orbit" style="--a:${a}deg;--r:${r}px"><span>${DATA.clients[k]||k}</span></span>`;
  }).join('');
};

const floaters = (keys)=>{
  const pool = (keys&&keys.length? keys.map(k=>DATA.clients[k]||k):['ProFinda']);
  const pos=[['6%','9%'],['70%','16%'],['16%','72%'],['78%','68%'],['44%','84%']];
  let h=''; pool.slice(0,5).forEach((c,i)=>{const p=pos[i%pos.length]; h+=`<span style="top:${p[1]};left:${p[0]};animation-delay:${i*1.6}s">${c}</span>`;});
  return `<div class="floaters">${h}</div>`;
};

DATA.initiatives.forEach(it=>{
  add(`
    <div class="init">
      <div class="init-num anim">${String(it.n).padStart(2,'0')} <span class="of">/ 14</span><span class="bar"></span></div>
      <div class="init-grid">
        <div class="col-intro">
          <h2 class="anim d1">${it.title}</h2>
          ${it.aka?`<div class="aka anim d1"><span class="ic">\u21b3</span>${it.aka}</div>`:''}
          <div class="tag anim d2">${it.tag}</div>
          <p class="summary anim d3">${it.summary}</p>
        </div>
        <div class="col-glyph">
          <div class="glyph-wrap anim d2">
            <div class="glyph">
              <div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div>
              <div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div>
              <div class="core">${svg(ICON[it.icon]||ICON.spark)}</div>
            </div>
            ${clientOrbit(it.clients)}
          </div>
        </div>
        <div class="col-why">
          <p class="why anim d4"><b>Why we're building it \u2014</b> ${it.why}</p>
        </div>
        <div class="col-kw">
          <div class="kw-wrap anim d3">
            <div class="kw-head">What it decomposes into</div>
            <div class="kw">${it.keywords.map(k=>`<span class="chip">${k}</span>`).join('')}</div>
          </div>
        </div>
      </div>
    </div>`, `Initiative ${String(it.n).padStart(2,'0')}`, it.notes||'');
});

/* ---- Horizon placeholder slides (theme-switching) ---- */
const LIPSUM_A = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.";
const LIPSUM_B = "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.";
function horizonSlide(o){
  const chips = o.chips.map(c=>`<span class="chip">${c}</span>`).join('');
  return `
    <div class="init horizon">
      <div class="init-num anim">${o.kicker} <span class="of">/ placeholder</span><span class="bar"></span></div>
      <div class="init-grid">
        <div class="col-intro">
          <div class="eyebrow anim"><span class="dot"></span>${o.eyebrow}</div>
          <h2 class="anim d1">${o.title}</h2>
          <div class="tag anim d2">${o.tag}</div>
          <p class="summary anim d3">${o.summary}</p>
        </div>
        <div class="col-glyph">
          <div class="glyph-wrap anim d2">
            <div class="glyph">
              <div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div>
              <div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div>
              <div class="core">${svg(ICON.future)}</div>
            </div>
          </div>
        </div>
        <div class="col-why">
          <p class="why big anim d4"><b>Why we're building it \u2014</b> ${o.why}</p>
        </div>
        <div class="col-kw">
          <div class="kw-wrap anim d3">
            <div class="kw-head">What it decomposes into</div>
            <div class="kw">${chips}</div>
          </div>
        </div>
      </div>
    </div>`;
}
add(horizonSlide({
  kicker:"H2", eyebrow:"Horizon 2 \u00b7 placeholder", title:"Horizon 2 \u2014 Placeholder",
  tag:"Placeholder tag line goes here",
  summary:LIPSUM_A+" "+LIPSUM_B,
  why:LIPSUM_A+" "+LIPSUM_B+" "+LIPSUM_A,
  chips:["Placeholder one","Placeholder two","Placeholder three","Placeholder four","Placeholder five"]
}), 'Horizon 2', "Placeholder speaker note for the Horizon 2 slide. Lorem ipsum dolor sit amet, consectetur adipiscing elit \u2014 swap this out with the real Horizon 2 narrative once the content is ready.", 'h2');
add(horizonSlide({
  kicker:"H3", eyebrow:"Horizon 3 \u00b7 placeholder", title:"Horizon 3 \u2014 Placeholder",
  tag:"Placeholder tag line goes here",
  summary:LIPSUM_B+" "+LIPSUM_A,
  why:LIPSUM_B+" "+LIPSUM_A+" "+LIPSUM_B,
  chips:["Placeholder one","Placeholder two","Placeholder three","Placeholder four","Placeholder five"]
}), 'Horizon 3', "Placeholder speaker note for the Horizon 3 slide. Lorem ipsum dolor sit amet \u2014 replace with the real Horizon 3 story when ready.", 'h3');

/* Closing */
add(`
  <div class="closing" style="text-align:center;display:flex;flex-direction:column;align-items:center">
    <img class="cover-logo anim" src="${LOGO}" alt="ProFinda" style="margin-bottom:34px">
    <h2 class="anim d1">One roadmap.<br><span class="accent">Carefully curated. Built for our clients.</span></h2>
    <p class="sub anim d2">14 initiatives that deepen the product our clients trust today \u2014 and pull ProFinda into the agentic, AI-first future of work.</p>
    <div class="three anim d3">
      <div class="b"><span>1</span>Client CRs, blended with our thinking</div>
      <div class="b"><span>2</span>AI-first, skills-led, enterprise-grade</div>
      <div class="b"><span>3</span>Relevant from the RM to the C-Suite</div>
    </div>
  </div>`, 'Close',
  "Let me bring it together. Fourteen initiatives, but one roadmap and one direction. Everything you've seen deepens the product our clients trust today \u2014 booking, skills, reporting, demand \u2014 while pulling ProFinda into the agentic, AI-first future of work. Three things to remember. One: this is client change-requests blended with our own thinking \u2014 real asks, shaped by product strategy, not a backlog dump. Two: it's distinctly ProFinda \u2014 AI-first, skills-led, enterprise-grade. And three: it's relevant from the Resource Manager all the way up to the C-Suite, which is how the same platform grows into new buying centres inside the same organisation. The single sentence I'd leave you with is the one on the slide: one roadmap, carefully curated and built for our clients. Thank you \u2014 and I'm happy to go as deep as you like on any one of these initiatives.")

/* ---------- Navigation engine ---------- */
let cur=0; const total=slides.length;
let stepCamera=(dir,el)=>{}; // reassigned once the 3D star cloud initialises
document.getElementById('totNum').textContent=total;
const prog=document.getElementById('prog');
const dotsEl=document.getElementById('dots');
slides.forEach((s,i)=>{const d=document.createElement('i');d.addEventListener('click',()=>go(i));dotsEl.appendChild(d);});
const dotEls=[...dotsEl.children];

function go(i){
  if(i<0||i>=total||i===cur) { if(i<0||i>=total) return; }
  const dir = i>cur ? 1 : -1;
  const prevIdx = cur;
  cur=Math.max(0,Math.min(total-1,i));
  const incoming = slides[cur].el;
  // move the 3D camera to a new viewpoint; it returns the direction the new
  // slide should fly in FROM, so content appears to already sit there in space.
  stepCamera(dir, incoming);
  slides.forEach((s,idx)=>s.el.classList.toggle('active',idx===cur));
  dotEls.forEach((d,idx)=>d.classList.toggle('on',idx===cur));
  prog.style.width=((cur)/(total-1)*100)+'%';
  document.getElementById('curNum').textContent=cur+1;
  document.getElementById('secLabel').textContent=slides[cur].section;
  document.getElementById('topbar').classList.toggle('logo-hidden', !!incoming.querySelector('.cover-logo'));
  renderNotes();
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
  const visible=notesOn && !!note;
  notesPanel.classList.toggle('show',visible);
}
function syncToggle(){
  ntState.textContent=notesOn?'On':'Off';
  notesToggle.classList.toggle('on',notesOn);
  notesToggle.setAttribute('aria-pressed',notesOn?'true':'false');
}
function setNotes(on){
  notesOn=on;
  try{ localStorage.setItem('pf_notes',on?'1':'0'); }catch(e){}
  syncToggle(); renderNotes();
}
notesToggle.addEventListener('click',e=>{e.stopPropagation();setNotes(!notesOn);});
notesToggle.addEventListener('keydown',e=>{ if(e.key==='Enter'||e.key===' '){e.preventDefault();e.stopPropagation();setNotes(!notesOn);} });
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
// swipe
let tx=0; window.addEventListener('touchstart',e=>tx=e.touches[0].clientX,{passive:true});
window.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-tx; if(Math.abs(dx)>50){dx<0?next():prev();}},{passive:true});

setTimeout(()=>document.getElementById('hint').classList.add('fade'),4200);
go(0);

/* ---------- 3D star cloud: a volume you fly INTO ----------
   Real x/y/z stars in a box. A camera has a position and an orientation
   (yaw/pitch/roll). Each frame we transform every star into camera space and
   project it with perspective, so near stars are big & bright, far ones fade,
   and turning the camera reveals other faces of the same cloud. On each slide
   step the camera rotates to a new viewpoint (yaw left, pitch down, up...) and
   dollies forward; the slide content is told to fly in from that same
   direction, as if it was already sitting there in space. */
(function(){
  const canvas=document.getElementById('bgCanvas');
  const ctx=canvas.getContext('2d');
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let W=0,H=0,DPR=Math.min(window.devicePixelRatio||1,2);
  function resize(){ W=canvas.clientWidth; H=canvas.clientHeight;
    canvas.width=Math.round(W*DPR); canvas.height=Math.round(H*DPR);
    ctx.setTransform(DPR,0,0,DPR,0,0); }
  resize(); window.addEventListener('resize',resize);

  // Infinite star field: stars live in a repeating cell of size CELL. Each frame
  // every star is wrapped into the cell CENTRED ON THE CAMERA, so no matter how
  // far the camera flies or where it looks, it's always surrounded by stars at a
  // constant density. This is what fixes the "fly out into emptiness" problem.
  const N=200, CELL=2200, HALF=CELL/2;
  const LINK=360, LINK2=LINK*LINK;      // link distance in wrapped 3D space
  const DRAW=1700;                       // only draw stars within this range (fog)
  const stars=[];
  for(let i=0;i<N;i++){
    stars.push({ x:Math.random()*CELL, y:Math.random()*CELL, z:Math.random()*CELL,
                 r:0.7+Math.random()*1.9, tw:Math.random()*Math.PI*2 });
  }

  const F=820; // focal length (perspective strength)
  // camera: position + orientation. cam = live values, tgt = eased-to targets.
  const cam={ x:0,y:0,z:0, yaw:0,pitch:0,roll:0 };
  const tgt={ x:0,y:0,z:0, yaw:0,pitch:0,roll:0 };
  let t=0;

  // wrap a coordinate so it lands within [-HALF,HALF) of the camera on that axis
  function wrap(v, camv){ let d=(v-camv)%CELL; if(d<-HALF)d+=CELL; else if(d>=HALF)d-=CELL; return d; }

  // rotate a camera-relative point (already wrapped) into view space + project
  const cs={cy:1,sy:0,cp:1,sp:0,cr:1,sr:0};
  function project(dx,dy,dz){
    // yaw (around Y)
    let x1= cs.cy*dx + cs.sy*dz, z1=-cs.sy*dx + cs.cy*dz, y1=dy;
    // pitch (around X)
    let y2= cs.cp*y1 - cs.sp*z1, z2= cs.sp*y1 + cs.cp*z1, x2=x1;
    // roll (around Z)
    let x3= cs.cr*x2 - cs.sr*y2, y3= cs.sr*x2 + cs.cr*y2, z3=z2;
    if(z3<=1) return null;              // behind camera
    const s=F/z3;
    return { px:W/2 + x3*s, py:H/2 + y3*s, scale:s, z:z3 };
  }

  function frame(){
    t+=0.016;
    const k=0.045;
    cam.x   += (tgt.x-cam.x)*k;     cam.y   += (tgt.y-cam.y)*k;   cam.z   += (tgt.z-cam.z)*k;
    cam.yaw += (tgt.yaw-cam.yaw)*k; cam.pitch+=(tgt.pitch-cam.pitch)*k; cam.roll+=(tgt.roll-cam.roll)*k;
    // gentle continuous drift so it never looks frozen while talking
    cam.yaw   += Math.sin(t*0.05)*0.00020;
    cam.pitch += Math.cos(t*0.043)*0.00016;
    // slow perpetual forward creep so there's always subtle motion into the field
    cam.z += 0.25;

    // refresh rotation cache
    cs.cy=Math.cos(cam.yaw);  cs.sy=Math.sin(cam.yaw);
    cs.cp=Math.cos(cam.pitch);cs.sp=Math.sin(cam.pitch);
    cs.cr=Math.cos(cam.roll); cs.sr=Math.sin(cam.roll);

    ctx.clearRect(0,0,W,H);

    // wrap + project every star relative to the camera
    const wx=new Float64Array(N), wy=new Float64Array(N), wz=new Float64Array(N);
    const proj=new Array(N);
    for(let i=0;i<N;i++){
      const dx=wrap(stars[i].x,cam.x), dy=wrap(stars[i].y,cam.y), dz=wrap(stars[i].z,cam.z);
      wx[i]=dx; wy[i]=dy; wz[i]=dz;
      proj[i]=project(dx,dy,dz);
    }

    // constellation lines: rebuild each frame from wrapped neighbours (stable & always present)
    ctx.lineWidth=1;
    for(let i=0;i<N;i++){
      const a=proj[i]; if(!a||a.z>DRAW) continue;
      for(let j=i+1;j<N;j++){
        const b=proj[j]; if(!b||b.z>DRAW) continue;
        const ddx=wx[i]-wx[j], ddy=wy[i]-wy[j], ddz=wz[i]-wz[j];
        const d2=ddx*ddx+ddy*ddy+ddz*ddz; if(d2>LINK2) continue;
        const zAvg=(a.z+b.z)/2;
        const al=Math.max(0,Math.min(.22,(1-d2/LINK2)*(1-zAvg/DRAW)*.22));
        if(al<=0.012) continue;
        ctx.strokeStyle='rgba(150,200,220,'+al.toFixed(3)+')';
        ctx.beginPath(); ctx.moveTo(a.px,a.py); ctx.lineTo(b.px,b.py); ctx.stroke();
      }
    }

    // stars
    for(let i=0;i<N;i++){
      const pr=proj[i]; if(!pr||pr.z>DRAW) continue;
      if(pr.px<-40||pr.px>W+40||pr.py<-40||pr.py>H+40) continue;
      const s=stars[i];
      const rad=Math.max(.5, s.r*pr.scale*140);
      const tw=0.6+0.4*Math.sin(t*1.2+s.tw);         // twinkle
      const al=Math.max(0,Math.min(.95,(1 - pr.z/DRAW)))*tw;
      if(al<=0.02) continue;
      const near=Math.max(0,Math.min(1,1-pr.z/(DRAW*0.8)));
      const g=Math.round(173+ (198-173)*(1-near));
      ctx.fillStyle='rgba('+Math.round(14+(140-14)*(1-near))+','+g+','+Math.round(154+ (63-154)*(1-near))+','+al.toFixed(3)+')';
      ctx.beginPath(); ctx.arc(pr.px,pr.py,Math.min(rad,5),0,6.283); ctx.fill();
    }
    requestAnimationFrame(frame);
  }

  // sequence of viewpoint changes: yaw left, pitch down, yaw right, pitch up...
  // each step also dollies the camera forward along its facing so we move deeper.
  let step=0;
  const YAWS=[ -0.42, 0.38, -0.30, 0.46, -0.50, 0.34 ];
  const PITCHES=[ 0.10, -0.26, 0.24, -0.14, 0.28, -0.20 ];
  stepCamera=function(dir, el){
    step += (dir||1);
    const yaw   = YAWS[((step%YAWS.length)+YAWS.length)%YAWS.length];
    const pitch = PITCHES[((step%PITCHES.length)+PITCHES.length)%PITCHES.length];
    tgt.yaw   += yaw;
    tgt.pitch += pitch;
    tgt.roll   = (Math.random()-.5)*0.05;             // whisper of roll
    // dolly forward along the NEW facing so each step takes us deeper into space.
    // The field is infinite (wrapped per-frame), so we can fly forever and always
    // have stars in front of us.
    const fwd=520;
    tgt.x += Math.sin(tgt.yaw)*Math.cos(tgt.pitch)*fwd;
    tgt.z += Math.cos(tgt.yaw)*Math.cos(tgt.pitch)*fwd;
    tgt.y += -Math.sin(tgt.pitch)*fwd;

    // tell the incoming slide to fly in FROM this camera direction
    if(el){
      const sx=Math.round(-Math.sin(yaw)*520);   // horizontal entry
      const sy=Math.round(Math.sin(pitch)*360);  // vertical entry
      const ry=Math.round(yaw*22);               // yaw -> rotateY
      const rx=Math.round(-pitch*20);            // pitch -> rotateX
      el.style.setProperty('--sx', sx+'px');
      el.style.setProperty('--sy', sy+'px');
      el.style.setProperty('--sz', '-680px');
      el.style.setProperty('--ry', ry+'deg');
      el.style.setProperty('--rx', rx+'deg');
      void el.offsetWidth; // reflow so the offset is the transition's start point
    }
  };

  if(reduce){
    // static: draw one frame, no loop; slides just fade (no 3D entry)
    document.querySelectorAll('.slide').forEach(s=>{
      s.style.setProperty('--sx','0px');s.style.setProperty('--sy','0px');
      s.style.setProperty('--sz','0px');s.style.setProperty('--rx','0deg');s.style.setProperty('--ry','0deg');
    });
    stepCamera=function(){};
    // one static projection of the wrapped field around the (still) camera
    cs.cy=1;cs.sy=0;cs.cp=1;cs.sp=0;cs.cr=1;cs.sr=0;
    ctx.clearRect(0,0,W,H);
    for(let i=0;i<N;i++){
      const dx=wrap(stars[i].x,cam.x),dy=wrap(stars[i].y,cam.y),dz=wrap(stars[i].z,cam.z);
      const pr=project(dx,dy,dz); if(!pr||pr.z>DRAW) continue;
      ctx.fillStyle='rgba(14,173,154,'+Math.max(.1,1-pr.z/DRAW).toFixed(2)+')';
      ctx.beginPath();ctx.arc(pr.px,pr.py,Math.min(3,1.2*pr.scale*120),0,6.283);ctx.fill();
    }
    return;
  }
  requestAnimationFrame(frame);
})();
</script>
</body>
</html>"""

# decode the literal unicode escapes used in the raw HTML template (raw string keeps them literal)
_ESC = {
  "\\u00b7":"\u00b7", "\\u2192":"\u2192", "\\u2190":"\u2190", "\\u21b3":"\u21b3",
  "\\u2014":"\u2014", "\\u2013":"\u2013", "\\u2019":"\u2019", "\\u201c":"\u201c",
  "\\u201d":"\u201d", "\\u2022":"\u2022",
}
for a,b in _ESC.items():
    HTML = HTML.replace(a,b)

HTML = HTML.replace("/*__FONTS__*/", _font_face()).replace("__DATA__", data_json).replace("__LOGO__", LOGO)
out = OUT_DIR / "ProFinda-Product-Roadmap-3D.html"
out.write_text(HTML, encoding="utf-8")
print("Wrote", out, len(HTML), "bytes")
