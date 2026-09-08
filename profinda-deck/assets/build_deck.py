#!/usr/bin/env python3
"""Build the self-contained ProFinda Product Roadmap presentation (single HTML file, base64 assets)."""
import json, os, pathlib

HERE = pathlib.Path(__file__).resolve().parent
# Logo asset resolves next to this script; output dir overridable via PF_DECK_OUT.
LOGO = pathlib.Path(os.environ.get("PF_DECK_LOGO", HERE / "pf_logo.txt")).read_text().strip()
OUT_DIR = pathlib.Path(os.environ.get("PF_DECK_OUT", HERE))

# 14 initiatives. keywords = decomposition chips (legacy names / head-of-product alt names / sub-themes).
# aka = head-of-product alternative title surfaced as subtitle. clients = list of company keys.
INITIATIVES = [
  {
    "n": 1, "title": "ProPilot — AI Roadmap", "icon": "spark",
    "aka": None,
    "tag": "The assistant layer + open endpoints",
    "summary": "An AI assistant layer across the whole platform \u2014 natural-language search, bulk actions, booking-conflict suggestions, chat-based reporting \u2014 plus the API endpoints (MCP) that let external AI agents and client co-pilots reach ProFinda's intelligence directly, not just through our own UI.",
    "why": "Cuts time-to-value for new users, sharpens the AI narrative against competitors, and opens a brand-new distribution channel through partner and client AI ecosystems.",
    "keywords": ["ProPilot (LLM assistant)", "MCP open endpoints", "RFP \u2192 role automation", "Self-service journeys"],
    "clients": ["afry"],
    "notes": "The problem we're solving is that a powerful platform is also a hard platform to learn \u2014 new users take too long to get value, and everything they want to do lives behind menus and screens they have to discover. ProPilot answers that with an assistant layer: instead of learning where things are, you just ask \u2014 search, booking suggestions, reporting, all in natural language. The deeper problem is bigger than our own UI. The world is moving to AI agents and co-pilots, and if the only way to reach ProFinda's intelligence is through screens we built, we get left outside that shift. So we're opening our capabilities as endpoints other AI systems can call directly. Be honest in the room: this second part is us getting ahead of demand, not responding to it \u2014 it's a bet on where work is going, and a new way for ProFinda to be present in an AI-first workflow."
  },
  {
    "n": 2, "title": "AI Planner Evolution", "icon": "planner",
    "aka": "Intelligent Schedule Optimization",
    "tag": "The holy grail of resourcing automation",
    "summary": "The algorithmic engine behind smart, automated staffing \u2014 grown from an Audit-only tool into a general-purpose planner \u2014 plus the continuity mechanics (roll forward, grade promotions, leaver/mover handling) it must reason about over time.",
    "why": "This is the core differentiator versus manual staffing and point solutions like Dayshape, and it's already a go-live requirement for at least one enterprise client.",
    "keywords": ["KPI-based optimisation", "Scenario comparison", "Normative models", "Continuity: roll-forward, promotions, leavers/movers", "Gap-fill suggestions (AIrene)"],
    "clients": ["kpmg", "ey", "cohnreznick"],
    "notes": "This is the one to slow down on. Staffing at scale is still largely manual \u2014 a skilled person solving a giant, shifting puzzle by hand, and redoing it every time someone is promoted, leaves, or moves. That's slow, it doesn't scale, and it's exactly where point-solution competitors try to beat us. The problem we're solving is turning that manual puzzle into something the platform can reason about and largely automate: propose optimal plans, let you compare scenarios before committing, and handle the messy reality of people changing over time so plans don't silently rot. We're growing this from a tool that only served one practice into a general-purpose planner for the whole business. Frame it as the core of our product story \u2014 automated, intelligent staffing is the holy grail of resourcing, and for at least one major enterprise it's already a condition of going live, not a nice-to-have."
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
    "aka": "Custom Calculated Fields Framework",
    "tag": "Removes developer bottlenecks",
    "summary": "The strategic bet to replace PowerBI with Looker as ProFinda's productised, embeddable analytics engine \u2014 plus custom calculated fields so clients define their own metrics instead of relying on one fixed platform-wide formula.",
    "why": "Turns reporting from a cost center into a monetizable Enterprise add-on, and lifts a long-standing ceiling on data volume and customization.",
    "keywords": ["Looker migration", "Dashboard expansion", "Custom calculated fields", "Remove CSV limits", "Report scalability"],
    "clients": ["afry", "ey", "kpmg"],
    "notes": "The problem here is twofold. First, our current analytics stack has a ceiling \u2014 it caps how much data we can push through and how far clients can customise, and every bespoke metric becomes an engineering job. Second, and more strategic: reporting is treated as a cost of doing business rather than something we can sell. This initiative attacks both. We move to a properly productised, embeddable analytics engine that lifts the data and scale ceiling, and we let clients define their own calculated metrics instead of being stuck with one fixed formula we hard-coded. Why it matters: it turns reporting from a support burden into a genuine, monetizable enterprise add-on \u2014 a real upsell, not just a fix. Position this as a deliberate strategic bet: we're not patching the old reporting, we're changing what reporting is for the business."
  },
  {
    "n": 5, "title": "Report Quality of Life", "icon": "list",
    "aka": None,
    "tag": "Used more than almost anything else",
    "summary": "The everyday reporting fixes clients ask for constantly \u2014 filters, labels, scheduling, headers, group-by options \u2014 plus several single-client dashboard builds tracked here for visibility. It earns equal billing with the bigger strategic bets, not a lesser tier.",
    "why": "One of the most-used areas of the platform, so small friction here is a disproportionately common source of support tickets and dissatisfaction.",
    "keywords": ["Real-time booking fields", "Scheduled & recurring reports", "Filters, headers, group-by", "KPMG UK Stagegate dashboards", "EY Core & Reporting"],
    "clients": ["ey", "cohnreznick", "kpmg"],
    "notes": "The trap with reporting is dismissing it as small stuff. It isn't \u2014 it's one of the most-used parts of the platform, and precisely because it's used so heavily, the little annoyances hurt the most. When a filter is missing, a report can't be scheduled, headers aren't labelled properly, or you can't group data the way you think about it, that friction shows up every single day and turns into a steady stream of support tickets and quiet dissatisfaction. So the problem we're solving is death by a thousand paper-cuts in the area people touch most. The what is deliberately unglamorous: the everyday quality-of-life fixes clients ask for constantly, plus a few specific dashboards we're tracking openly. The message to land: we're giving this equal billing with the big strategic bets, because reliability in the workhorse features is what earns trust in the flashy ones."
  },
  {
    "n": 6, "title": "Skills", "icon": "skills",
    "aka": "renamed from \u201cSmarter Matching\u201d",
    "tag": "Match quality is the core promise",
    "summary": "Improving the quality, structure and governance of the skills ontology that feeds search and match \u2014 validation, parent-child relationships, quality detection, and interoperability with client-owned taxonomies. This is Skills folded organizationally closer to Search.",
    "why": "Match quality is what clients pay for; bad skills data directly degrades the product's core promise.",
    "keywords": ["Skills validation & certification", "Parent-child skills", "Ontology alignment", "Skills recommender", "Experience in matches", "Exclusion filters"],
    "clients": ["ey", "kpmg", "newton", "afry"],
    "notes": "Everything ProFinda promises rests on one thing: putting the right person forward. And a match is only ever as good as the skills data underneath it. The problem is that skills data is messy \u2014 inconsistent, unstructured, sometimes plain wrong, and rarely lined up with the way a client already describes their own people. When that data is poor, the matches are poor, and we're failing at the exact thing clients pay us for. So this initiative is about the quality, structure and governance of the skills that feed search and matching: making skills trustworthy, giving them sensible relationships, catching bad data automatically, and speaking the client's own taxonomy instead of forcing ours. We renamed it from 'Smarter Matching' to simply 'Skills', and pulled it organizationally closer to Search, because better matching isn't a separate feature \u2014 it's a direct consequence of getting the skills right. This underpins the core product promise."
  },
  {
    "n": 7, "title": "Internationalization", "icon": "globe",
    "aka": None,
    "tag": "One platform, every market",
    "summary": "Multi-language UI, a multilingual ontology, and regional/locale handling (calendars, labels) so the platform works the same everywhere. It cuts across every pod \u2014 Booking, Search, Skills and Reporting all need it.",
    "why": "Unlocks non-English-speaking markets and removes a recurring blocker for global enterprise clients operating across regions.",
    "keywords": ["Multilingual product", "Multilingual ontology", "Additional languages", "Locale & calendars", "Client relabelling", "Regional segmentation"],
    "clients": ["ey"],
    "notes": "The problem is simple to state and expensive to ignore: our clients are global, their people are not all English speakers, and today the platform quietly assumes they are. When the interface, the skills language, or even the calendar doesn't fit a region, it becomes a real blocker to rolling ProFinda out across a whole organisation \u2014 and in some markets it's the reason we can't win the deal at all. So this initiative is about making the platform feel native everywhere: the interface in the user's own language, matching that works across languages, and the local details \u2014 calendars, labels, regional differences \u2014 handled properly rather than bolted on. Frame it as an investment, not a single feature: it cuts across everything we build, and it's the groundwork that unlocks entire non-English markets and makes every future global rollout possible. It pays back far beyond any one client."
  },
  {
    "n": 8, "title": "Self-Service Configuration", "icon": "gear",
    "aka": "Configurable Notification Engine",
    "tag": "Soft-coded, event-driven admin control",
    "summary": "Giving client admins direct control over notifications, permissions, user groups and settings \u2014 instead of routing every change through a support ticket. This is exactly what the public roadmap promises under \u201cAdmin Panel.\u201d",
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
    "keywords": ["Ingest client actuals", "Forecast vs. actuals", "Timesheet values in-platform", "SAP S/4 hours plugin"],
    "clients": ["ey", "kpmg"],
    "notes": "Today the platform knows the plan but not the reality. We can tell you what was booked, but not what actually happened \u2014 the real hours people worked. That gap is a genuine problem, because without it a Resource Manager can never learn whether their plans were any good, and more importantly we can never prove our own value. If a finance stakeholder asks 'did this actually save us anything?', 'the plan looked great' is not an answer. So this initiative brings real timesheet data into the platform and lines it up against the plan, using consistent units so the comparison is honest rather than apples-to-oranges. Why it matters: it closes the loop between forecast and reality. That's the foundation for any serious workforce-planning conversation, and it's what lets us tell a credible ROI story instead of asserting one. Small in scope, but genuinely foundational \u2014 a lot of the bigger vision depends on it."
  },
  {
    "n": 10, "title": "Pricing & Budgeting", "icon": "coin",
    "aka": "renamed from \u201cCommercial Control\u201d",
    "tag": "Financial visibility before staffing",
    "summary": "Letting RMs see the cost, margin and budget impact of a staffing decision before they commit \u2014 including a dedicated Salesforce-native pricing app.",
    "why": "Named repeatedly as a competitive gap versus Dayshape, and a strong upsell for clients doing this in spreadsheets outside the platform.",
    "keywords": ["Pricing plan / budget in-platform", "Salesforce pricing app", "Engagement economics", "Revenue calculations"],
    "clients": ["am", "cohnreznick", "kpmg"],
    "notes": "The problem is that staffing decisions are also financial decisions, but we treat them as if they aren't. Right now someone books a team without seeing what it costs, what it does to margin, or whether it fits the budget \u2014 and then that analysis happens later, offline, in a spreadsheet outside the platform. That's slow, error-prone, and it means the money conversation is disconnected from the decision that drives it. So this initiative brings the financials into the moment of the decision: let people see cost, margin and budget impact before they commit, not after. Why it earns a place on the roadmap: it's been called out repeatedly as a gap against competitors, and for the many clients doing this in spreadsheets today it's a clear reason to bring more of their process into ProFinda. We renamed it from 'Commercial Control' to match how people actually talk about it \u2014 pricing and budgeting."
  },
  {
    "n": 11, "title": "CV Studio", "icon": "doc",
    "aka": None,
    "tag": "A client-facing deliverable in every pitch",
    "summary": "Rebuilding the CV export / template experience with real-time editing and AI-assisted content tailoring, plus a new CV parser.",
    "why": "CVs are used in every staffing pitch; quality here reflects directly on the client's own brand, not just ProFinda's.",
    "keywords": ["CV exporter & templates", "Real-time editing", "AI-assisted tailoring", "New CV parser"],
    "clients": ["afry", "ey"],
    "notes": "This one is small in scope but punches above its weight, and the why is about brand. The CV is what actually goes in front of the end customer in a pitch \u2014 it's the client's shop window. When our CV output looks dated or is painful to tailor, that reflects on the client's own brand, not just on us, and it shows up at the single highest-stakes moment: trying to win the work. Today that experience is clunky and manual. So this initiative rebuilds it \u2014 real-time editing, better templates, and cleaner data coming in \u2014 with the genuinely differentiating piece being AI that helps tailor a CV to the specific opportunity being pitched. That ties straight back to our AI-first story: not AI for its own sake, but AI making a consultant look their best in front of a prospective client. It's a small build with a very visible payoff."
  },
  {
    "n": 12, "title": "Demand Setup", "icon": "form",
    "aka": None,
    "tag": "Quality upstream, quality everywhere",
    "summary": "Making it faster and more accurate to create demand \u2014 smarter role forms, reusable engagement / role templates, and contractor & contingent-worker handling.",
    "why": "Demand quality upstream directly determines match quality downstream, so this is a leverage point that pays off everywhere else.",
    "keywords": ["Role form", "Engagement / role templates", "Demand uploader v2", "Contractor / contingent handling"],
    "clients": ["ey", "newton", "cohnreznick"],
    "notes": "The key idea here is garbage in, garbage out. Everything downstream \u2014 the matches we suggest, the reports we produce, the plans we optimise \u2014 is only as good as the demand that was entered at the start. And today entering demand is slower and sloppier than it should be: forms that don't guide you, teams rebuilding the same roles from scratch every time, and no clean way to handle contractors or bulk-create demand. When that upstream step is weak, that weakness quietly propagates into every other part of the platform. So this initiative is about quality at the source: make it faster and more accurate to describe what's needed, with smarter forms and reusable templates so nobody starts from a blank page. The framing to land: this isn't the glamorous slide, but it's a leverage point \u2014 fix demand once, upstream, and the quality improvement is felt everywhere else for free."
  },
  {
    "n": 13, "title": "Next-Gen Experience & Platform Redesign", "icon": "sparkle",
    "aka": "absorbs \u201cEveryday UX Polish\u201d",
    "tag": "Elevates perceived value in every demo",
    "summary": "A comprehensive modernization of ProFinda's visual identity and core UI \u2014 a refreshed design system and a redesigned individual Profile experience \u2014 alongside the long tail of everyday interface fixes.",
    "why": "Lifts perceived product value in enterprise demos, drives end-user engagement, and modernizes the profile hub to support skills self-reporting and talent mobility.",
    "keywords": ["Design system refresh", "Redesigned profile hub", "Responsive core modules", "Everyday UX papercuts"],
    "clients": [],
    "notes": "Be upfront that this one is forward-looking, not a committed near-term build. The problem it addresses is perception. In an enterprise demo, how the product looks and feels is doing a lot of the selling before anyone reads a feature list \u2014 and a capable platform that looks dated gets marked down for reasons that have nothing to do with what it can actually do. There's also a real user cost: a modern, engaging experience is what pulls people in to keep their own profiles and skills up to date, which feeds everything else. So this is a comprehensive modernization \u2014 a refreshed visual language and a redesigned profile experience \u2014 plus the long tail of small interface annoyances we track so they don't quietly pile up. Position it as where we're taking the platform: it lifts perceived value in every demo and drives the day-to-day engagement the rest of the roadmap depends on."
  },
  {
    "n": 14, "title": "Strategic Workforce Planning", "icon": "future",
    "aka": "Human & AI Agents",
    "tag": "Budget human + digital workforce together",
    "summary": "Forward-looking capacity planning that lets organizations model future demand, skill gaps and headcount across both human talent and synthetic AI agents \u2014 in one unified platform.",
    "why": "Positions ProFinda as a leader in next-generation workforce planning, letting enterprises budget and allocate human capital and digital workforce capacity together. (Vision-stage: no Discovery ticket yet.)",
    "keywords": ["Long-term capacity vs. demand", "Skill-gap forecasting", "Human + AI-agent modeling", "MCP-connected digital workers"],
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
:root{
  --navy:#131E2D; --navy2:#203142; --navy3:#0C1622; --navy-soft:#1B2A3B;
  --teal:#0EAD9A; --teal-dark:#0A8377; --lime:#8CC63F; --lime-dark:#6fa02f;
  --blue:#1B9AF0; --blue-deep:#0A52C0; --purple:#8E9BC4; --purple-deep:#5A6aa0;
  --slate:#C7D2DE; --muted:#8FA1B3; --muted2:#6B7C8E;
  --ink:#EAF1F8; --line:rgba(255,255,255,.09);
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
.bg-net{position:absolute;inset:0;z-index:0;opacity:.45;pointer-events:none}
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
  transition:opacity .5s ease;}
.slide.active{opacity:1;visibility:visible;pointer-events:auto}
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
  letter-spacing:.22em;text-transform:uppercase;color:var(--teal);margin-bottom:20px}
.eyebrow .ln{width:38px;height:2px;background:linear-gradient(90deg,var(--teal),transparent)}
.eyebrow .dot{width:8px;height:8px;border-radius:50%;background:var(--teal);box-shadow:0 0 0 5px rgba(14,173,154,.18)}
.accent{background:linear-gradient(92deg,var(--teal),var(--lime));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.accent-blue{background:linear-gradient(92deg,var(--blue),var(--teal));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}

/* ---------- Cover ---------- */
.cover h1{font-size:clamp(44px,7.4vw,116px);line-height:.98}
.cover .sub{font-size:clamp(17px,2vw,27px);color:var(--slate);max-width:30ch;margin-top:26px;font-weight:500;line-height:1.4}
.cover .foot{margin-top:44px;display:flex;gap:14px;flex-wrap:wrap}
.pill{display:inline-flex;align-items:center;gap:9px;background:rgba(255,255,255,.05);border:1px solid var(--line);
  border-radius:100px;padding:11px 20px;font-size:14px;font-weight:700;color:#dfe9f2;backdrop-filter:blur(6px)}
.pill b{color:#fff}
.cover-logo{height:34px;margin-bottom:40px;filter:drop-shadow(0 4px 20px rgba(0,0,0,.4))}

/* stats row */
.statrow{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:44px;max-width:820px}
.stat{background:rgba(255,255,255,.045);border:1px solid var(--line);border-radius:18px;padding:22px 20px;backdrop-filter:blur(8px)}
.stat .n{font-size:clamp(26px,3.3vw,42px);font-weight:900;letter-spacing:-.02em;
  background:linear-gradient(90deg,#fff,var(--teal));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.stat .l{font-size:13px;color:var(--slate);font-weight:600;margin-top:4px}

/* ---------- Philosophy slide ---------- */
.philo h2{font-size:clamp(30px,4.6vw,68px)}
.philo .lead{font-size:clamp(16px,1.7vw,23px);color:var(--slate);max-width:62ch;margin-top:22px;line-height:1.5;font-weight:500}
.philo .lead em{color:#fff;font-style:normal;font-weight:800}
.audience{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-top:42px}
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
.part .kick{font-size:clamp(13px,1.3vw,17px);font-weight:800;letter-spacing:.24em;text-transform:uppercase;color:var(--teal);margin-bottom:18px}
.part h2{font-size:clamp(36px,6vw,92px)}
.part .rule{height:5px;width:120px;background:linear-gradient(90deg,var(--teal),var(--lime));border-radius:3px;margin-top:26px;box-shadow:0 0 30px rgba(14,173,154,.5)}
.part .cnt{margin-top:26px;font-size:clamp(15px,1.6vw,20px);color:var(--slate);max-width:56ch;line-height:1.5}

/* ---------- Initiative slide ---------- */
.init-grid{display:grid;grid-template-columns:1.15fr .85fr;
  grid-template-areas:"intro glyph" "why kw";
  grid-template-rows:auto auto;
  column-gap:clamp(30px,4vw,72px);row-gap:clamp(20px,2.4vw,34px);align-items:center}
.init-grid .col-intro{grid-area:intro;align-self:end}
.init-grid .col-glyph{grid-area:glyph;align-self:center}
.init-grid .col-why{grid-area:why;align-self:start}
.init-grid .col-kw{grid-area:kw;align-self:start}
.init-num{font-size:clamp(15px,1.4vw,19px);font-weight:900;color:var(--teal);letter-spacing:.08em;display:flex;align-items:center;gap:14px;margin-bottom:16px}
.init-num .of{color:var(--muted2);font-weight:700}
.init-num .bar{flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}
.init h2{font-size:clamp(32px,4.7vw,66px);color:#fff}
.init .aka{margin-top:14px;font-size:clamp(13px,1.25vw,17px);color:var(--muted);font-style:italic;font-weight:600;display:flex;align-items:center;gap:9px}
.init .aka .ic{font-style:normal}
.init .tag{margin-top:22px;display:inline-block;font-size:clamp(13px,1.3vw,16.5px);font-weight:800;color:var(--lime);
  border-left:3px solid var(--lime);padding:5px 0 5px 16px;background:linear-gradient(90deg,rgba(140,198,63,.09),transparent);border-radius:0 8px 8px 0}
.init .summary{margin-top:26px;font-size:clamp(15px,1.55vw,21px);color:var(--slate);line-height:1.52;max-width:60ch}
.init .why{margin-top:0;font-size:clamp(13.5px,1.35vw,17px);color:#cdd9e5;line-height:1.5;max-width:60ch;
  background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
/* nudge the why box down so its top lines up with the first pill row (past the kw header) */
.init-grid .col-why{padding-top:43px}
.init .why b{color:var(--teal)}

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
.chip:nth-child(2){transition-delay:.55s}
.chip:nth-child(3){transition-delay:.65s}
.chip:nth-child(4){transition-delay:.75s}
.chip:nth-child(5){transition-delay:.85s}
.chip:nth-child(6){transition-delay:.95s}
.chip::before{content:"";display:inline-block;width:7px;height:7px;border-radius:2px;margin-right:9px;vertical-align:middle;
  background:linear-gradient(135deg,var(--teal),var(--lime))}

/* big glyph */
.glyph{position:relative;display:grid;place-items:center;aspect-ratio:1;max-width:340px;margin:0 auto;width:100%}
.glyph .ring{position:absolute;border:1px solid var(--line);border-radius:50%}
.glyph .r1{inset:0;animation:spin 34s linear infinite}
.glyph .r2{inset:14%;border-style:dashed;border-color:rgba(14,173,154,.28);animation:spin 26s linear infinite reverse}
.glyph .r3{inset:30%;border-color:rgba(140,198,63,.22);animation:spin 20s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.glyph .core{width:44%;height:44%;border-radius:26px;display:grid;place-items:center;
  background:linear-gradient(150deg,var(--navy2),var(--navy-soft));border:1px solid var(--line);
  box-shadow:0 20px 60px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.06)}
.glyph .core svg{width:52%;height:52%;color:var(--teal);filter:drop-shadow(0 0 14px rgba(14,173,154,.5))}
.glyph .orb{position:absolute;width:12px;height:12px;border-radius:50%;background:radial-gradient(circle,var(--lime),var(--teal));box-shadow:0 0 14px rgba(140,198,63,.6)}
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
.closing .three .b span{width:26px;height:26px;flex:none;border-radius:50%;background:linear-gradient(135deg,var(--teal),var(--lime));color:var(--navy3);font-weight:900;font-size:13px;display:grid;place-items:center}

/* ---------- Chrome (nav / progress / hint) ---------- */
.topbar{position:fixed;top:0;left:0;right:0;height:64px;z-index:40;display:flex;align-items:center;justify-content:space-between;
  padding:0 clamp(22px,4vw,54px);pointer-events:none}
.topbar img{height:22px;opacity:.92}
.tb-right{display:flex;align-items:center;gap:16px;pointer-events:auto}
.section-label{font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);}
.counter{font-size:13px;font-weight:800;color:#fff;background:rgba(255,255,255,.06);border:1px solid var(--line);border-radius:100px;padding:7px 14px}
.counter b{color:var(--teal)}

.progress{position:fixed;bottom:0;left:0;height:4px;z-index:40;background:linear-gradient(90deg,var(--teal),var(--lime));width:0;transition:width .5s cubic-bezier(.2,.7,.2,1);box-shadow:0 0 16px rgba(14,173,154,.6)}
.progress-track{position:fixed;bottom:0;left:0;right:0;height:4px;z-index:39;background:rgba(255,255,255,.06)}

.dots{position:fixed;right:clamp(14px,2vw,26px);top:50%;transform:translateY(-50%);z-index:40;display:flex;flex-direction:column;gap:9px}
.dots i{width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,.18);cursor:pointer;transition:all .25s}
.dots i.on{background:linear-gradient(135deg,var(--teal),var(--lime));transform:scale(1.5);box-shadow:0 0 10px rgba(14,173,154,.6)}
.dots i:hover{background:rgba(255,255,255,.4)}

.nav-arrows{position:fixed;bottom:20px;right:clamp(20px,3vw,40px);z-index:40;display:flex;gap:10px}
.na{width:46px;height:46px;border-radius:50%;border:1px solid var(--line);background:rgba(255,255,255,.06);color:#fff;
  display:grid;place-items:center;cursor:pointer;transition:all .2s;backdrop-filter:blur(8px)}
.na:hover{background:var(--teal);border-color:var(--teal);transform:translateY(-2px)}
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
  <svg class="bg-net" id="bgNet" viewBox="0 0 1440 810" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs><radialGradient id="ng"><stop offset="0%" stop-color="#0EAD9A"/><stop offset="100%" stop-color="#8CC63F"/></radialGradient></defs>
    <g id="netLines" stroke="rgba(255,255,255,.10)" stroke-width="1" fill="none"></g>
    <g id="netNodes"></g>
  </svg>
  <div class="grain"></div>
  <div id="slides"></div>
</div>

<div class="topbar">
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
function add(html, section, note){ const d=document.createElement('div'); d.className='slide'; d.innerHTML='<div class="slide-inner">'+html+'</div>'; slidesEl.appendChild(d); slides.push({el:d,section,note:note||''}); }

/* Cover */
add(`
  <div class="cover">
    <img class="cover-logo anim" src="${LOGO}" alt="ProFinda">
    <div class="eyebrow anim d1"><span class="ln"></span>Product Roadmap \u00b7 Next 12\u201318 Months</div>
    <h1 class="anim d2">The Future of<br><span class="accent">Resourcing.</span></h1>
    <p class="sub anim d3">An AI-first roadmap \u2014 14 initiatives, carefully calculated to deepen the product our clients already rely on, and to win the ones we want next.</p>
    <div class="statrow anim d4">
      <div class="stat"><div class="n">14</div><div class="l">Strategic initiatives</div></div>
      <div class="stat"><div class="n">2.7m</div><div class="l">Ontology interconnections</div></div>
      <div class="stat"><div class="n">3 wks &rarr; 4 min</div><div class="l">Time to resource a role</div></div>
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
      <div class="aud"><div class="ai">${svg(ICON.aud_sp)}</div><h4>Senior Partners</h4><p>Margin & compliance in view</p></div>
      <div class="aud"><div class="ai">${svg(ICON.aud_c)}</div><h4>C-Suite</h4><p>Strategic workforce planning</p></div>
      <div class="aud"><div class="ai">${svg(ICON.aud_wf)}</div><h4>The Workforce</h4><p>Visibility, mobility, growth</p></div>
    </div>
  </div>`, 'Overview',
  "Here's the strategic shift. ProFinda has always served the Resource Manager first, and this roadmap absolutely keeps that promise \u2014 RMs stay our primary user, and they benefit from almost every initiative you'll see. But AI lets us extend the platform's intelligence to everyone with a stake in how work gets staffed. Walk left to right: Resource Managers get faster, smarter staffing every day \u2014 that's the core. Engagement Managers get demand created right the first time. Senior Partners get margin and compliance in view. The C-Suite gets genuine strategic workforce planning. And the workforce itself gets visibility, mobility and growth. The reason this matters commercially: every new audience is a new buying centre inside the same client. We're not walking away from the RM \u2014 we're growing outward from a position of strength. Keep that RM-to-C-Suite arc in mind, because the closing slide comes right back to it.")

/* Philosophy 2 - DNA / discipline */
add(`
  <div class="philo">
    <div class="eyebrow anim"><span class="dot"></span>How we build</div>
    <h2 class="anim d1">Not features for the sake of it.</h2>
    <p class="lead anim d2">Every item on this roadmap is <em>carefully calculated</em> to enhance the existing product and make it more relevant \u2014 for our current client base, and to win prospects. We add what feels like <em>ProFinda's DNA</em>, blending client change-requests with our own thinking.</p>
    <div class="dna anim d3">
      <div class="card"><div class="ci">${svg(ICON.dna_client)}</div><h4>Client-driven</h4><p>Grounded in real change-requests from EY, KPMG, Deloitte and more \u2014 not a wish-list built in a vacuum.</p></div>
      <div class="card"><div class="ci">${svg(ICON.dna_bal)}</div><h4>Deepen &amp; extend</h4><p>Each initiative strengthens what already works and opens a door to a market we don't yet own.</p></div>
      <div class="card"><div class="ci">${svg(ICON.dna_ai)}</div><h4>Distinctly ProFinda</h4><p>AI-native, skills-led, enterprise-grade. We blend client asks with our own product thinking.</p></div>
    </div>
  </div>`, 'Overview',
  "One slide on discipline, because it pre-empts the obvious question: is this just a wish-list? No. Every item is carefully calculated to enhance the existing product and make it more relevant \u2014 both for the clients we have and the prospects we want. Three principles. First, it's client-driven: grounded in real change-requests from the firms we work with, not invented in a vacuum. Second, deepen and extend: each initiative strengthens something that already works and opens a door to a market we don't yet own. Third, it's distinctly ProFinda: AI-native, skills-led, enterprise-grade. The phrase I'd land is 'ProFinda's DNA' \u2014 we take the client ask and blend it with our own product thinking, rather than just building tickets to order. That blend is what stops the roadmap being a backlog and makes it a strategy. With that lens set, let's look at the fourteen initiatives themselves.")

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

/* Closing */
add(`
  <div class="closing" style="text-align:center;display:flex;flex-direction:column;align-items:center">
    <img class="cover-logo anim" src="${LOGO}" alt="ProFinda" style="margin-bottom:34px">
    <h2 class="anim d1">One roadmap.<br><span class="accent">Every stakeholder, ahead.</span></h2>
    <p class="sub anim d2">14 initiatives that deepen the product our clients trust today \u2014 and pull ProFinda into the agentic, AI-first future of work.</p>
    <div class="three anim d3">
      <div class="b"><span>1</span>Client CRs, blended with our thinking</div>
      <div class="b"><span>2</span>AI-first, skills-led, enterprise-grade</div>
      <div class="b"><span>3</span>Relevant from the RM to the C-Suite</div>
    </div>
  </div>`, 'Close',
  "Let me bring it together. Fourteen initiatives, but one roadmap and one direction. Everything you've seen deepens the product our clients trust today \u2014 booking, skills, reporting, demand \u2014 while pulling ProFinda into the agentic, AI-first future of work. Three things to remember. One: this is client change-requests blended with our own thinking \u2014 real asks, shaped by product strategy, not a backlog dump. Two: it's distinctly ProFinda \u2014 AI-first, skills-led, enterprise-grade. And three: it's relevant from the Resource Manager all the way up to the C-Suite, which is how the same platform grows into new buying centres inside the same organisation. The single sentence I'd leave you with is the one on the slide: one roadmap, every stakeholder, ahead. Thank you \u2014 and I'm happy to go as deep as you like on any one of these initiatives.")

/* ---------- Navigation engine ---------- */
let cur=0; const total=slides.length;
let reseedNet=()=>{}; // reassigned once the background constellation initialises
document.getElementById('totNum').textContent=total;
const prog=document.getElementById('prog');
const dotsEl=document.getElementById('dots');
slides.forEach((s,i)=>{const d=document.createElement('i');d.addEventListener('click',()=>go(i));dotsEl.appendChild(d);});
const dotEls=[...dotsEl.children];

function go(i){
  if(i<0||i>=total||i===cur) { if(i<0||i>=total) return; }
  cur=Math.max(0,Math.min(total-1,i));
  slides.forEach((s,idx)=>s.el.classList.toggle('active',idx===cur));
  dotEls.forEach((d,idx)=>d.classList.toggle('on',idx===cur));
  prog.style.width=((cur)/(total-1)*100)+'%';
  document.getElementById('curNum').textContent=cur+1;
  document.getElementById('secLabel').textContent=slides[cur].section;
  renderNotes();
  reseedNet();
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

/* ---------- background network (living constellation) ---------- */
(function(){
  const SVGNS='http://www.w3.org/2000/svg';
  const W=1440,H=810,N=30,LINK=210;
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const nodes=[];
  for(let i=0;i<N;i++){
    const x=Math.random()*W, y=Math.random()*H;
    nodes.push({
      x, y, tx:x, ty:y,           // current + target (home) position
      r:1.4+Math.random()*3.2,
      // gentle persistent drift so it's alive even mid-slide
      vx:(Math.random()-.5)*0.05, vy:(Math.random()-.5)*0.05,
      ph:Math.random()*Math.PI*2, sp:0.15+Math.random()*0.25 // breathing offset/speed
    });
  }
  // build reusable SVG elements once (no per-frame innerHTML)
  const gLines=document.getElementById('netLines');
  const gNodes=document.getElementById('netNodes');
  const circles=nodes.map(n=>{const c=document.createElementNS(SVGNS,'circle');c.setAttribute('r',n.r.toFixed(1));c.setAttribute('fill','url(#ng)');gNodes.appendChild(c);return c;});
  const pairs=[]; const lineEls=[];
  for(let i=0;i<N;i++)for(let j=i+1;j<N;j++){pairs.push([i,j]);const ln=document.createElementNS(SVGNS,'line');gLines.appendChild(ln);lineEls.push(ln);}

  function draw(){
    for(let i=0;i<N;i++){const n=nodes[i];circles[i].setAttribute('cx',n.x.toFixed(1));circles[i].setAttribute('cy',n.y.toFixed(1));}
    for(let k=0;k<pairs.length;k++){
      const [i,j]=pairs[k], a=nodes[i], b=nodes[j];
      const d=Math.hypot(a.x-b.x,a.y-b.y), ln=lineEls[k];
      if(d<LINK){ln.setAttribute('x1',a.x.toFixed(1));ln.setAttribute('y1',a.y.toFixed(1));ln.setAttribute('x2',b.x.toFixed(1));ln.setAttribute('y2',b.y.toFixed(1));ln.setAttribute('stroke-opacity',(1-d/LINK).toFixed(2));ln.style.display='';}
      else ln.style.display='none';
    }
  }

  // give every node a fresh home target -> triggers the reposition-on-slide-change ease
  reseedNet=function(){ for(const n of nodes){ n.tx=40+Math.random()*(W-80); n.ty=40+Math.random()*(H-80); } };

  if(reduce){ draw(); return; }  // honor reduced-motion: static render, no loop

  let t=0;
  function tick(){
    t+=0.016;
    for(const n of nodes){
      // slow ease toward home target (this is what "repositions" on slide change)
      n.x+=(n.tx-n.x)*0.012; n.y+=(n.ty-n.y)*0.012;
      // constant faint drift + tiny breathing so it never looks frozen while talking
      n.tx+=n.vx; n.ty+=n.vy;
      if(n.tx<20||n.tx>W-20)n.vx*=-1; if(n.ty<20||n.ty>H-20)n.vy*=-1;
      n.x+=Math.cos(t*n.sp+n.ph)*0.06; n.y+=Math.sin(t*n.sp+n.ph)*0.06;
    }
    draw();
    requestAnimationFrame(tick);
  }
  draw();
  requestAnimationFrame(tick);
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

HTML = HTML.replace("__DATA__", data_json).replace("__LOGO__", LOGO)
out = OUT_DIR / "ProFinda-Product-Roadmap.html"
out.write_text(HTML, encoding="utf-8")
print("Wrote", out, len(HTML), "bytes")
