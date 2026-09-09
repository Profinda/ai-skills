---
name: profinda-jira
description: ProFinda Jira workflow for agents and devs. Epic = living PRD (problem, goals, risk, high-level architecture); Story = user-facing feature; Task = internal technical work; Sub-task = optional executable step. Covers the question-when-missing spec workflow, plan-lives-in-Jira rule, dependencies as issue links, and dual sign-off. Use when a Jira ticket ID (SP-XXXX) is given, when starting work on a ticket, when creating Epics/Stories/Tasks, or when writing a PRD (the PRD is the Epic — this supersedes profinda-prd).
---

# ProFinda Jira Workflow

Use `mcp-atlassian` MCP tools for all Jira operations (`jira_get_issue`,
`jira_create_issue`, `jira_update_issue`, `jira_transition_issue`,
`jira_add_comment`, `jira_get_transitions`, `jira_create_issue_link`). Always call
`jira_get_transitions` before transitioning — IDs vary by current state.

## The model — write once, per level

| Level | Is | Holds |
|---|---|---|
| **Epic** | the living PRD | problem, goals, personas, success metrics, scope, **high-level architecture**, **risk (once)**, PRD approval |
| **Story** | user-facing feature (UI, public APIs, MCPs) | user value, requirements, UX, acceptance criteria, detailed design, plan, test approach |
| **Task** | internal technical work (devops, non-breaking refactors) | technical end-state, DoD, detailed design, plan, rollout/rollback, monitoring, release-notes gate |
| **Sub-task** | *optional* one executable step | objective, spec/thinking, files, verification |

Non-negotiable rules:
- **Risk and high-level architecture live on the Epic only.** Stories/Tasks
  inherit them. If a Story/Task uncovers a new risk, **update the Epic** and note
  the change — the Epic is a living document.
- **The plan lives in the Story/Task description.** It may be drafted as a local
  `PLAN.md` in the loop, but it MUST end up in Jira so it survives independent of
  any machine (holiday, handoff, dead laptop).
- **Steps are sub-tasks OR a checklist** in the parent — the dev/agent chooses.
  Recommended: sub-tasks for multi-session/parallel work; checklist for small
  atomic work. Never mandate sub-tasks.
- **Dependencies are Jira issue links** (`blocks` / `is blocked by`) via
  `jira_create_issue_link`, never a free-text section.
- **Sign-off is recorded in the description table AND via the status transition.**
  SOC-2 / ISO 27001 auditors do not accept a status change alone as approval.
- **Fields, not prose.** T-shirt, estimate, PM, Pod, Customer, Source, AI Service,
  release notes, fix version are Jira fields — never duplicated in the description.

Templates live in `templates/` (Markdown = source of truth; `templates/adf/` =
generated Jira ADF). Load the relevant template before writing a description.

## Question-when-missing (before writing a spec)

The goal is useful specs, not boilerplate. **Synthesise first, then ask only for
genuine gaps** — do not run a full interview.

1. Read the ticket + parent + linked docs, and explore the codebase for context.
2. Draft the spec from what you know.
3. Ask targeted questions ONLY where information is genuinely missing and material
   (e.g. no acceptance criteria, unclear scope, unknown personas, missing risk
   inputs on an Epic). Batch the questions; don't drip-feed.
4. Do not invent requirements. Mark unknowns explicitly or `N/A` with a reason.

Per level, the fields most often missing and worth asking about:
- **Epic:** the problem & why now, success metric, risk inputs, high-level approach.
- **Story:** acceptance criteria, UX/Figma, scope boundaries.
- **Task:** definition of done, rollback, customer-impact (release-notes gate).

## Risk assessment (Epic only)

The Epic template's risk table lists **every risk type** to evaluate: Data,
Customisation, UX, InfoSec, Performance, Business, Political, Resource,
Commercial, Cost, AI. Treat it as a checklist, not free text:

1. Go type by type. For each, either **score it** (Critical 8 / High 5 / Medium 3
   / Low 1) with a one-line description + mitigation, or mark **N/A (0)** with a
   brief reason. Never leave a row blank — blank means "not yet assessed".
2. **Flag what the conversation hasn't covered.** If a risk type has no signal
   from the discussion or codebase, say so and ask — don't guess a score.
3. For the **AI** row, also assess bias, privacy, misinformation and societal
   harm at individual / group / societal level.
4. Compute the **total**; if it's ≥ 17 or any single risk is Critical, mark it
   **escalated**. Set **InfoSec reviewed** if any InfoSec risk is Medium+.
5. Risk is assessed **once, on the Epic**. If a Story/Task later surfaces a new
   risk, add the row to the Epic and note the change in its change log.

Full definitions live in Notion: *Risk Management / Risk Assessment Framework*.

## When the developer provides a Jira ID

1. **Read the ticket** — `jira_get_issue` with `comment_limit: 10`. Check for a
   `[AGENT HANDOFF]` comment; if present, resume from it.
2. **Restate the acceptance criteria / DoD** in your own words (read-only). If
   they are missing or thin, say so and ask — do not silently invent them.
3. **AC CONFIRMATION GATE — STOP HERE.** End the turn with exactly:
   **Is this understanding correct? (yes / correct me)** — no tool calls in the
   same turn. Until confirmed, do not plan, transition, or change the codebase.
   Allowed: read the ticket + linked docs, create a worktree. Escape hatch: "skip
   the gate" / "just go".
4. **Move to In Progress** — `jira_transition_issue`.
5. **Write the plan into the description** — load the template, fill it via
   question-when-missing. This is the durable plan the work follows.
6. **Choose steps** — sub-tasks (create + link) or a checklist in the description.
7. **Build** — update step status / tick boxes as you go; refine the plan as
   understanding evolves.

## When no Jira ticket exists

Before non-trivial work, offer to create one:
> "No Jira ticket found. Should I create one in SP?
> - **Story** — user-facing feature or behaviour change
> - **Task** — technical work, refactor, or infrastructure
> Which fits, or proceed without one?"

For anything spanning multiple Stories/Tasks, offer to create an **Epic** first
and write the PRD into it (see below). Create via `jira_create_issue`, then follow
the flow above.

## The PRD is the Epic (supersedes profinda-prd)

Do not write PRD markdown files. The PRD lives in the **Epic description** using
`templates/epic.md`. The Epic starts light (Draft) and is enriched over time —
problem/goals first, then personas, scope, high-level architecture, and the risk
assessment as 3-amigos and sizing happen. It **must be complete before entering
development** (`In refinement → In Progress`); `N/A` with a brief reason is
acceptable on a field that does not apply.

## Dependencies

Create real links, don't type them:
```
jira_create_issue_link(type="Blocks", inward_issue_key="SP-A", outward_issue_key="SP-B")
```

## HANDOFF comment

Only when explicitly handing off or requested. Post on the Story/Task, not the Epic.
```
[AGENT HANDOFF]
Date: YYYY-MM-DD
Branch: feature/SP-XXXX-short-description
Completed: SP-XXXX sub-task / step
Next: what to do and why
Context: chose X over Y because Z (lib/foo.rb:42)
Blockers: none
```

## Closing a ticket (Done / Closed)

SP's "Closed (Any Status)" transition has a workflow validator that isn't
reflected in `jira_get_transitions` or `expand=transitions.fields` — that API
only reports `resolution` as required, but the actual transition screen also
enforces two custom fields. Skip the browser by setting them directly:

1. `jira_get_transitions(issue_key)` — find the "Closed (Any Status)" id (varies
   by current status).
2. `jira_update_issue(issue_key, fields={...})` to set, before transitioning:
   - `customfield_10690` ("FF Resolution Summary") — free text, non-empty. One
     or two sentences on what fixed it / why it's resolved.
   - `customfield_10599` ("Sum of Story Points") — number. Must be non-zero for
     **Bug** issue types (the validator's own error says "Enter 0 if it is not
     a BUG" — 0 is fine for other types). Nominally "automated" (summed from
     sub-tasks) but is a plain editable field when there are none.
3. `jira_transition_issue(issue_key, transition_id, fields={"resolution": {"name": "Done"}})`
   — `name` must be a value from `GET /rest/api/3/resolution` (`Done`, `Won't Do`,
   `Duplicate`, `Cannot Reproduce`, `Declined`, `Ready for production`,
   `Client resolved`, `Tested after Merge`, `Development finished`,
   `Workaround Provided`, ...). `"Fixed"` is **not** a valid name and will error.

Both custom fields are plain editable fields via `jira_update_issue` (not
gated to the transition screen), so steps 2 and 3 don't need to happen in the
same call — set them first, then transition.

If this starts failing again (workflow changes over time), the fastest way to
find the real required fields is the transition screen in the Jira UI itself
(click the status pill → pick the target status → read the form), since
Cloud's screen-based validators aren't fully exposed via the REST API.

## Commit discipline

```
Add rate limiter middleware [SP-1234]
```
No PRD files, no agent state files in the repo. Jira is the record.

## Session end checklist

- [ ] Plan written into the Story/Task before implementation started
- [ ] Steps tracked (sub-task status or checklist) and kept current
- [ ] New risks pushed up to the Epic
- [ ] Dependencies created as issue links
- [ ] Sign-off row filled when transitioning through an approval gate
- [ ] Description reflects final understanding (decisions, deviations)
- [ ] Ticket in the correct state
