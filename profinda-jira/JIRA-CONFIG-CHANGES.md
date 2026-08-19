# Jira Configuration Change Request — SP project

Status: **AWAITING PM TEAM + JIRA ADMIN APPROVAL**
Scope: SP project · issue types Epic, Story, Task, Sub-task
Companion doc: `PROPOSAL-templates-and-config.md` (templates & rationale)

This is the actionable change list for whoever administers the SP Jira project.
It is intentionally separate from the template redesign so it can be approved and
implemented on its own track. Each change is numbered for sign-off.

---

## Why

The create screens for Story and Task expose ~35 fields each. Many are
reporting/workflow fields that do not belong at creation time. Required fields
are inconsistent across issue types (e.g. Product Manager is required on Epic but
hidden on Story; Pod is required on Story/Task but optional on Epic). This slows
ticket creation, produces empty/garbage fields, and lets tickets start work
without the information that matters.

Goal: a lean, consistent create experience where the required fields are the ones
that genuinely gate work, and reporting fields appear later in the workflow.

---

## Change 1 — Align required fields across issue types

Legend: **R** required · O optional · — not on create screen (still editable later)

| # | Field (ID) | Epic | Story | Task | Sub-task | Change vs today |
|---|---|---|---|---|---|---|
| 1.1 | Summary | R | R | R | R | none |
| 1.2 | Description (template) | R | R | R | R | none |
| 1.3 | Priority | R | R | R | O | Sub-task → optional |
| 1.4 | Parent | — | R | R | R | Story/Task parent = Epic (make required) |
| 1.5 | Product Manager (10602) | R | R | O | — | **Expose + require on Story** |
| 1.6 | Pod (10988) | R | R | R | O | **Require on Epic** (was optional) |
| 1.7 | Source/category (11021) | R | R | R | O | Require consistently; sub-task optional |
| 1.8 | Requires Documentation (10694) | O | R | R | O | **Epic → optional** (set during refinement) |
| 1.9 | AI Service (11668) | R | O | O | — | **Expose optional on Story/Task** |
| 1.10 | Fix versions | O | R | R | O | none |
| 1.11 | Environment (10598) | — | R | R | O | none |
| 1.12 | Tshirt size (10711) | R | O | O | — | Epic sizing field |
| 1.13 | Story Points (10022 / 10529) | — | O | O | O | none |
| 1.14 | Release notes (10578) | — | O | **R if customer-facing** | — | **Conditional-required on Task** (Change 3) |
| 1.15 | Customer (10548) | O | O | O | — | none |
| 1.16 | Team (10300) | O | O | O | O | none |

---

## Change 2 — Remove these fields from the CREATE screen

Move to a later transition/edit screen where they are actually used. They remain
fully functional in the workflow — they just stop cluttering creation.

| # | Field | Reason |
|---|---|---|
| 2.1 | UI Points | Estimation, set in refinement/planning |
| 2.2 | API/HAL Points | Estimation |
| 2.3 | QA Points | Estimation |
| 2.4 | Integration Points | Estimation |
| 2.5 | Data S&A Points | Estimation |
| 2.6 | Sum of Story Points | Rollup — never entered by hand |
| 2.7 | QA Failure Reasons | Set during QA, not creation |
| 2.8 | Blocked Cause | Set when blocked |
| 2.9 | Product Review | Set during review |
| 2.10 | Escalate to | Set on escalation |
| 2.11 | Department | Reporting |
| 2.12 | Delivery Project | Reporting |
| 2.13 | Target Environment | Set at release planning |
| 2.14 | Product Involvement | Reporting |
| 2.15 | Test Plan Status | Set by QA workflow |
| 2.16 | File Expected Date | Niche, set when relevant |
| 2.17 | Current behaviour | Belongs in description if needed |
| 2.18 | Notion Documentation Link | Use issue links / description |
| 2.19 | Start date | Set at planning |
| 2.20 | Due date | Set at planning |

---

## Change 3 — Release Notes conditional-required on Task

Rationale: a Task is meant to be internal/non-customer-facing, but sometimes a
"refactor" turns out to be a breaking change or a UX/API change. We want a hard
gate so those never ship silently.

Rule to implement (workflow validator on the Task "ready for release"/"done"
transition):

> If the Task is a breaking change OR a UX change OR a public-API/MCP change,
> then **Release notes (10578)** must be non-empty AND **Requires Documentation
> (10694)** must be set.

If a full validator is not feasible short-term, enforce via the template
checklist + reviewer check as an interim measure.

---

## Change 4 — Epic lifecycle gate (Definition of Ready to Build)

Rationale: the Epic is a living document. It starts light and is enriched through
3-amigos, t-shirt sizing, and risk assessment. It must not enter development
half-specified.

Rule to implement (workflow validator on the Epic **In refinement → In Progress**
transition):

> Block the transition unless the Epic spec is complete: problem, goals, success
> metrics, personas, scope, high-level architecture, risk assessment (scored),
> and t-shirt size are all filled — N/A with a brief reason is acceptable.

Interim measure if a validator is not feasible: a manual DoR checklist confirmed
by the Product + Lead Engineer, recorded in the Epic sign-off table.

---

## Change 5 — Dependencies as issue links, not text fields

Rationale: dependencies are currently free-typed in template tables and scattered
across fields. Standardise on Jira issue links (`blocks` / `is blocked by`) so
dependency graphs are queryable and the board reflects reality.

Action: no field change required — this is a convention. Remove free-text
"Dependencies"/"Related tickets" rows from the templates (done in the template
redesign) and train teams/agents to use links.

---

## Approval

| Change | Owner to approve | Approved? | Name & date | Notes |
|---|---|---|---|---|
| 1 — Required fields alignment | PM lead + Jira admin | ☐ | | |
| 2 — Remove fields from create screen | PM lead + Jira admin | ☐ | | |
| 3 — Release Notes conditional-required | PM lead | ☐ | | |
| 4 — Epic lifecycle gate | PM lead + Eng lead | ☐ | | |
| 5 — Dependencies as links | Eng lead | ☐ | | |

Once approved, the Jira admin implements Changes 1–4 in the SP project screen
schemes and workflow; Change 5 is enforced via the templates and skills.
