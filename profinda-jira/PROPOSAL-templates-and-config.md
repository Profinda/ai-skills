# ProFinda Jira — Template & Field-Config Proposal (Step 1)

Status: **DRAFT for team review**
Author: Product / Tech Architecture
Related template tickets: SP-10376 (Epic), SP-10377 (Story), SP-10378 (Task)

This document challenges the current Jira templates and field configuration, and
proposes a de-duplicated model where **each concept lives at exactly one level**
of the hierarchy: Epic → Story / Task → Sub-task.

---

## 1. Problems with the current templates

### 1.1 Story and Task templates are identical
SP-10377 (Story) and SP-10378 (Task) are byte-for-byte the same. There is no
differentiation between user-facing work and internal technical work.

### 1.2 The same spec is repeated at every level
Sections **C Requirements**, **D Technical Design**, **E Risk Assessment** and
**F Approval** appear on the Epic *and* the Story *and* the Task, near-verbatim.
Maintaining the same content in three places guarantees drift — the exact
failure mode we are trying to avoid by moving away from `PLAN.md`.

### 1.3 Duplication inside a single Story/Task template
Part 1 (DoR-to-Spec) and Part 2 (DoR-to-Build) restate the same concept:

| Concept | Part 1 field | Part 2 field | Verdict |
|---|---|---|---|
| Out of scope | "Out of scope / non-goals" | C "Out of scope" | Duplicate — keep one |
| Dependencies | "Known dependencies" | C "Dependencies" | Duplicate — use Jira links |
| Acceptance | "Acceptance intent" | C "Acceptance criteria" | Refinement — keep both, label clearly |
| Complexity | "Initial complexity view" | D "Estimated complexity" | Refinement — keep both |
| Problem/Outcome/Success | Problem & Outcome block | restated in Requirements | Duplicate — keep once |
| Feasibility | (under Problem in Epic) | D "Feasibility notes" | Inconsistent placement — put in D |

Roughly 40% of the Story/Task template is redundant.

### 1.4 Description text duplicates native Jira fields
Several things are captured both as a Jira field and as a table row in the
description. Anything Jira structures natively should NOT be re-typed in prose:

| Captured in description | Native Jira field | Action |
|---|---|---|
| Release notes | `customfield_10578` Release notes | Use the field |
| Estimated complexity / t-shirt | `customfield_10711` Tshirt size | Use the field |
| Story points / point breakdown | Story Points + point fields | Use the fields |
| Product contact / PM | `customfield_10602` Product Manager | Use the field |
| Dependencies / related tickets | Jira issue links | Use links |
| Fix version | `fixVersions` | Use the field |
| Requires documentation | `customfield_10694` | Use the field |

---

## 2. The de-duplicated model

Principle: **write it once, at the level where it belongs.**

```
EPIC   → the living PRD: problem, goals, personas, success metrics,
         scope, high-level architecture, RISK (once), t-shirt, sign-off (PRD approved)
STORY  → user-facing feature spec: user value, requirements, UX, acceptance
         criteria, detailed technical design, test approach, build sign-off
TASK   → internal technical spec: technical end-state, requirements, detailed
         design, rollout/rollback, monitoring, RELEASE-NOTES gate, build sign-off
SUB-TASK → the executable step: objective, dependencies, agent spec/thinking,
           files touched, verification. Status = progress signal.
```

Rules:
- **Risk assessment is done once, on the Epic.** If a Story/Task uncovers a new
  risk, the Epic is updated and the change is noted (the Epic is a living
  document, not dead on arrival).
- **Dependencies are Jira issue links**, not free text.
- **The description holds only narrative Jira cannot structure.** Points,
  t-shirt, PM, release notes, fix version, dependencies live in fields/links.
- **Sub-tasks replace `PLAN.md`.** An independent agent reading a Sub-task plus
  its parent Story/Task plus the Epic knows exactly where things are and what to
  do next.

---

## 3. The Epic lifecycle (living document)

The Epic starts light and is enriched as understanding grows. It **cannot enter
development until the spec is complete** (N/A is allowed on a field with a brief
reason). This maps onto the existing Epic workflow states:

| State | What the Epic must contain | Gate |
|---|---|---|
| **Backlog / Draft** | Item name, one-paragraph brief, goal | — |
| **In refinement** | Problem, goals, personas, success metrics, scope, high-level architecture, risk assessment, t-shirt size — filled or N/A-with-reason | 3-amigos + risk scored |
| **In Progress** | All of the above complete + PRD approved | **Cannot transition here until the spec is complete** |
| On Hold / Blocked | — | — |
| Closed / Won't do | Outcome recorded | — |

The important gate: **"In refinement" → "In Progress"** requires a complete
spec. This is the Definition of Ready to Build at the Epic level.

---

## 4. Proposed templates

### 4.1 EPIC (living PRD)

```md
# {Epic title}

## Lifecycle
- Stage: Draft | In refinement | Ready to build | In progress | Done
- PRD version: 1.0
- Last substantive change: {date} — {what changed and why}

## 1. Problem & why now
What problem are we solving? Why does it matter now? Evidence if available.

## 2. Goals & success metrics
- Goal:
- Success metric(s): user metric or technical measure. How we know it worked.

## 3. Who is affected (personas)
User persona(s), customer segment, or internal team. N/A for pure infra — say why.

## 4. Scope (intent) & non-goals
- In scope (intent): behaviours/capabilities this epic delivers.
- Non-goals: explicitly NOT included.

## 5. High-level solution & architecture
System-level approach. Services, data flows, contracts affected.
No implementation detail, no file paths. (Detailed design lives on Stories/Tasks.)

## 6. Risk assessment  ← DONE ONCE, HERE
Use the Risk Assessment Framework. Score each: Critical=8 High=5 Medium=3 Low=1.
Escalate before build if total ≥ 17.
| # | Type | Level (score) | Description | Mitigation |
|---|------|---------------|-------------|------------|
| 1 | Data/UX/InfoSec/Performance/Business/AI/… | | | |
- AI-specific risks: bias, privacy, misinformation, societal harm.
- Total risk score:
- InfoSec (SOG) reviewed? Yes / No / N/A

## 7. Sizing
- Epic t-shirt size: S / M / L / XL — justification. (Also set the Jira field.)

## 8. Stories & Tasks
Linked automatically via parent. List here only if extra context is useful.

## 9. Open questions
Outstanding decisions affecting scope or design.

## 10. PRD approval (gate to development)
| Role | Name & date | Approved / Rejected (notes) |
|------|-------------|-----------------------------|
| Product | | |
| Lead Engineer | | |
```

### 4.2 STORY (user-facing feature — UI, public APIs, MCPs)

```md
# {Story title}

## User value
As a {persona}, I want {capability}, so that {benefit}.

## Requirements (functional)
Numbered list of what the system must do for THIS story.

## UX / UI requirements
User-facing design requirements. Link Figma. N/A-with-reason if none.

## Acceptance criteria
- Given … When … Then … (specific, testable)

## Detailed technical design
Story-level design. Inherits the Epic architecture — do not repeat it.
- Approach:
- Architecture/data/API changes specific to this story:
- Feasibility notes:

## Test approach
What proves this works. Link test plan if applicable.

## Out of scope
Explicitly NOT included in this story.

## Risk
Inherits the Epic risk assessment. If this story introduces a NEW risk,
update the Epic risk table and note it here: "Added risk X to {Epic} on {date}."

## Dependencies
Use Jira issue links (blocks / is blocked by). Do not free-type here.

## Definition of Ready to Build
- [ ] Acceptance criteria clear and testable
- [ ] UX linked or N/A
- [ ] Technical design agreed
| Role | Name & date | Approved / Rejected |
|------|-------------|---------------------|
| Lead Engineer | | |
| Product (or delegate) | | |
```

### 4.3 TASK (internal technical — devops, non-breaking refactors)

```md
# {Task title}

## What & why (technical end-state)
What is being changed and the technical end state. Why it matters.

## Requirements / definition of done
Specific, testable conditions that define completion.

## Detailed technical design
Inherits the Epic architecture — do not repeat it.
- Approach:
- Architecture/data/API changes:
- Feasibility notes:

## Rollout & rollback plan
How this ships and how it is reverted if it goes wrong.

## Monitoring & observability
Metrics/logs to confirm health. What to watch after release.

## ⚠️ Customer impact check  (Release Notes gate)
Is this actually customer-visible after all?
- Breaking change? Yes / No
- UX change? Yes / No
- Public API / MCP change? Yes / No
If ANY = Yes → fill the **Release notes** field and set **Requires Documentation**.
If this is a large user-facing change, consider converting to a Story.

## Out of scope
Explicitly NOT included.

## Risk
Inherits the Epic risk assessment. New risk → update the Epic and note it here.

## Dependencies
Jira issue links only.

## Definition of Ready to Build
- [ ] Definition of done clear
- [ ] Rollback plan defined
- [ ] Customer impact check done
| Role | Name & date | Approved / Rejected |
|------|-------------|---------------------|
| Lead Engineer | | |
```

### 4.4 SUB-TASK (executable step — replaces PLAN.md)

```md
# {Sub-task title — one concrete step}

## Objective
The single step this delivers. What "done" means for this step.

## Depends on
- Blocked by: SP-XXXX (use Jira links too)
- Blocks: SP-XXXX

## Spec / thinking
The agent (or dev) writes the plan and reasoning for HOW to make the change.
This is where the thinking lives before code is written.

## Files / areas to touch
Modules, services, or areas affected.

## Verification
How to prove this step works (tests, manual check, command).
```

Sub-task **status** is the progress signal: To Do → In Progress → In Review → Done.
No separate progress doc.

A Sub-task carries **no estimation of its own** — no Story Points, no t-shirt, no
point-breakdown fields. The parent Task/Story holds the estimate. Its create
screen is stripped to the minimum (Summary, Description, Parent, Priority, Team).
See Jira config Change 2b / Change 6.

---

## 5. Proposed Jira field configuration

Goal: reduce the ~35-field create screens to what is genuinely needed at
creation, align required fields across issue types, and stop duplicating fields
that the description already covers (and vice versa).

### 5.1 Required-field inconsistencies today

| Field | Epic | Story | Task | Sub-task | Problem |
|---|---|---|---|---|---|
| Product Manager (10602) | required | (hidden) | optional | optional | Required on Epic only |
| Requires Documentation (10694) | required | required | required | required | OK |
| Source/category (11021) | required | required | required | optional | Inconsistent on sub-task |
| AI Service (11668) | required | (hidden) | (hidden) | (hidden) | Epic only — odd |
| Environment (10598) | (hidden) | required | required | optional | |
| Pod (10988) | optional | required | required | required | Inconsistent w/ Epic |
| Fix versions | optional | required | required | optional | |
| Priority | required | required | required | optional | |
| Parent | — | optional | optional | required | Correct |

### 5.2 Proposed create-screen fields (required / optional / remove)

Legend: **R** required · O optional · — hide from create screen (still usable later)

| Field | Epic | Story | Task | Sub-task | Notes |
|---|---|---|---|---|---|
| Summary | R | R | R | R | |
| Description (template) | R | R | R | R | |
| Priority | R | R | R | O | |
| Parent | — | R | R | R | Story/Task link to Epic; Sub-task to Story/Task |
| Product Manager (10602) | R | R | O | — | PM owns Story per Jira role split |
| Pod (10988) | R | R | R | O | Align: required everywhere except sub-task |
| Source/category (11021) | R | R | R | O | Align |
| Requires Documentation (10694) | O | R | R | O | Decided during refinement on Epic |
| AI Service (11668) | R | O | O | — | Keep on Epic; expose optional on Story/Task |
| Fix versions | O | R | R | O | Release train |
| Environment (10598) | — | R | R | O | |
| Tshirt size (10711) | R | O | O | — | Epic sizing; Story/Task use Story Points |
| Story Points (10022/10529) | — | R | R | — | **Required on Story/Task; removed from Sub-task** — the parent carries the estimate |
| Release notes (10578) | — | O | R-if-customer-facing | — | Task gate (see 4.3) |
| Customer (10548) | O | O | O | — | |
| Team (10300) | O | O | O | O | |

### 5.3 Remove from the CREATE screen (move to a later transition screen)

These are workflow/reporting fields that pollute creation and should appear only
when relevant in the workflow, not at create time:

- UI Points, API/HAL Points, QA Points, Integration Points, Data S&A Points
- Sum of Story Points (rollup — never entered by hand)
- QA Failure Reasons, Blocked Cause, Product Review, Escalate to
- Department, Delivery Project, Target Environment, Product Involvement
- Test Plan Status, File Expected Date, Current behaviour
- Notion Documentation Link (superseded by proper links / the description)
- Start date, Due date (set during planning, not creation)

### 5.4 Fields that duplicate the description — pick ONE home

For each, the **field** is the source of truth; remove the equivalent row from
the description template (already reflected in section 4):

- Release notes, T-shirt size, Story points, Product Manager, Fix version,
  Requires Documentation, Dependencies (→ links).

---

## 6. Sign-off is recorded in BOTH places (decided)

Approval is captured **twice, deliberately**, because each answers a different question:

- **Jira status transition** = the *machine-readable gate* (the ticket physically
  cannot move to the next stage until approved). This is what workflow automation
  and reporting rely on.
- **Sign-off rows in the template** = the *when & who* record inside the document
  itself (name + date + approved/rejected + notes). This travels with the spec,
  survives export, and tells a reader/agent who approved what and when without
  digging through the Jira history log.

Both must stay in sync. The template sign-off row is filled at the same moment the
status transition is performed. This is why sections 4.1–4.3 keep the approval
tables even though a status transition also exists.

---

## 7. Open decisions for the team

1. Confirm the Epic gate: block **In refinement → In Progress** until the spec is
   complete (validator or manual DoR checklist?).
2. Confirm required-field table (5.2) with the Jira admin.
3. Confirm removing reporting fields from the create screen (5.3).
4. Confirm Release Notes becomes conditionally-required on Task (5.2).
5. Confirm dual sign-off (status transition + template row) — section 6.
