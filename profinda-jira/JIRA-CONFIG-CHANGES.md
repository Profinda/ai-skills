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

Columns: Epic · Story · Task · Bug · Sub-task.

| # | Field (ID) | Epic | Story | Task | Bug | Sub-task | Change vs today |
|---|---|---|---|---|---|---|---|
| 1.1 | Summary | R | R | R | R | R | none |
| 1.2 | Description (template) | R | R | R | R | R | none |
| 1.3 | Priority | R | R | R | R | O | Sub-task → optional |
| 1.4 | Parent | — | R | R | — | R | Story/Task parent = Epic (required); Sub-task parent required |
| 1.5 | Product Manager (10602) | R | R | **R** | O | — | **Require on Task too** — auto-copy from Epic (Change 8) |
| 1.6 | Pod (10988) | R | R | R | R | **—** | **Remove from Sub-task** (item 6). Pod = the team field (item 11) |
| 1.7 | Source/category (11021) | R | R | R | O | **—** | **Remove from Sub-task** (item 5) |
| 1.8 | Requires Documentation (10694) | O | R | R | O | **—** | **Remove from Sub-task** (item 7) |
| 1.9 | AI Service (11668) | R | **—** | **—** | — | — | **Remove from Story & Task** (item 8) — Epic-level decision only |
| 1.10 | Fix versions | O | R | R | O | **—** | **Remove from Sub-task** (item 9) |
| 1.11 | Environment (10598) | — | **—** | **—** | **R** | **—** | **Bug only** — where the bug was found (items 3, 10). Hidden elsewhere |
| 1.12 | Target Environment (11602) | O | R | R | O | — | Release destination incl. hotfix (item 2). Distinct from Environment |
| 1.13 | Tshirt size (10711) | R | O | O | — | — | Epic sizing field |
| 1.14 | Sum of Story Points (10599) | — | **R** | **R** | O | **—** | Estimate field. Story/Task only. See Change 6 + open question |
| 1.14b | Story Points (10022) — legacy | — | — | — | — | — | **Drop.** Null everywhere, hidden on Task |
| 1.15 | Release notes (10578) | — | O | **R if customer-facing** | O | — | Conditional-required on Task (Change 3) |
| 1.16 | Customer (10548) | **R** | **R** | **R** | **R** | **—** | **Required on all except Sub-task** (item 12) — auto-copy from Epic (Change 8) |
| 1.17 | Team (10300) — native | **—** | **—** | **—** | **—** | **—** | **Hidden everywhere** (item 11) — polluted with OpsGenie/departments; Pod replaces it |
| 1.18 | Product Involvement (11800) | **R** | — | — | — | — | **Epic create** — Product↔work relationship (owns / guides / none) |
| 1.19 | Notion Documentation Link (10635) | O | — | — | — | — | **Epic only, optional** — supplementary Notion material; PRD itself lives in the Epic |

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
| 2.5 | Data S&A Points | Estimation (discipline split) |
| 2.7 | QA Failure Reasons | Set during QA, not creation |
| 2.8 | Blocked Cause | Set when blocked |
| 2.9 | Product Review | Set during review |
| 2.10 | Escalate to | Set on escalation |
| 2.11 | **Department — DELETE the field entirely** | Redundant with Pod; polluted (item 1) |
| 2.12 | Delivery Project | Reporting |
| 2.13 | Test Plan Status | Set by QA workflow |
| 2.14 | File Expected Date | Niche, set when relevant |
| 2.15 | Current behaviour | Belongs in description if needed |
| 2.16 | Start date | Set at planning |
| 2.17 | Due date | Set at planning |

Note:
- **Target Environment is NOT removed** — a proper field (see 1.12).
- **Environment is not removed** — scoped to **Bug only** (see 1.11).
- **Product Involvement (11800) is NOT removed** — it stays on **Epic create**;
  it defines the Product↔work relationship (Product owns / guides / none). See 1.18.
- **Notion Documentation Link (10635) is NOT removed** — repurposed to **Epic
  only, optional**, for supplementary Notion material (the PRD itself now lives
  in the Epic description). See 1.19.

### 2b. Sub-task create screen — keep it minimal

A Sub-task is an executable step, not an estimation unit. Its parent Task/Story
carries the estimate. Strip the Sub-task create screen down to only what a step
needs; remove all estimation and reporting fields from it.

| # | Field | Action on Sub-task |
|---|---|---|
| 2b.1 | Sum of Story Points (10599) + all discipline point fields | **Remove** — estimate lives on the parent |
| 2b.2 | Pod (10988) | **Remove** (item 6) |
| 2b.3 | Source/category (11021) | **Remove** (item 5) |
| 2b.4 | Requires Documentation (10694) | **Remove** (item 7) |
| 2b.5 | Fix versions | **Remove** (item 9) |
| 2b.6 | Environment (10598) | **Remove** (item 10) |
| 2b.7 | Customer (10548) | **Remove** (item 12) |
| 2b.8 | AI Service, Tshirt size, Story Points (10022) | Remove |

Sub-task create screen keeps only: **Summary, Description (template), Parent
(required), Priority (optional)**, plus assignee. Everything else is inherited
from the parent Task/Story (and copied down by automation where needed).

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

## Change 6 — Estimate mandatory on Task/Story, absent on Sub-task

Rationale: every deliverable unit (Story, Task) must be estimated before it enters
a sprint. A Sub-task is just a step within an estimated parent, so it should not
carry its own estimate (double-counting and noise).

The estimate field **today** is the custom **`Sum of Story Points` (10599)**
(the legacy built-in `Story Points` 10022 is null everywhere and is being
dropped). See the open question below before finalising which field.

Action:
- Make **`Sum of Story Points` (10599)** required on Story and Task.
- Remove it (and all point fields) from the Sub-task screen (Change 2b).
- Drop the legacy `Story Points` (10022) from all screens.

### Change 6 — OPEN QUESTION / honest challenge: custom field vs built-in

Why does the custom `Sum of Story Points` exist instead of Jira's built-in
Story Points? The usual reason is that built-in Story Points **cannot roll up**
sub-task/discipline estimates to the parent, and can't hold a per-discipline
split (UI / API-HAL / QA / Integration / Data S&A). **But in our instance the
sum is maintained MANUALLY** — nothing computes it automatically. That removes
the main justification.

If we type the number by hand anyway, we could switch to **built-in Story
Points** and regain **native velocity / burndown / sprint reports** — which only
read the built-in estimation field. With the custom field, those native reports
are blank/wrong unless rebuilt in dashboards.

Decision needed from the PM team:
- **A) Keep `Sum of Story Points`** — consistent with historical data + discipline
  splits; accept native agile reports don't read it.
- **B) Move to built-in Story Points** — regain native reporting; decide what
  happens to discipline splits and whether to backfill history.

Templates use `Sum of Story Points` for now to stay consistent. Not settled.

---

## Change 7 — "In Progress" automation (assignee + points): exempt Sub-tasks

Finding (investigated via REST API): the `Work Commenced → In Progress`
transition (id 51) has **no field-required validators** — so the "must have
assignee + points" check is a **Jira Automation rule**, not a workflow
validator. It is **not** currently hard-blocking Sub-tasks (e.g. SP-10365 is a
Sub-task In Progress with no points). Automation config is not exposed via API;
the admin finds it under **Project settings → Automation**.

Action (keeps the check on Task/Story, removes it from Sub-task):
- **Assignee**: required on all issue types entering In Progress (unchanged).
- **Estimate (`Sum of Story Points`)**: required on **Story/Task only**. Add a
  condition **Issue type is not Sub-task** to the points branch of the rule so
  Sub-tasks are exempt.

---

## Change 8 — Attribution auto-copy from parent (kill the real duplication)

The honest challenge on duplication: **is it wasteful to repeat Customer / Pod /
Source / PM on Story/Task when they already exist on the Epic?**

Answer, precisely:
- **On Sub-tasks: yes, wasteful — removed.** Sub-tasks carry no effort estimate
  (points live on the parent), so attribution on a sub-task adds nothing to
  effort reporting. Removed (items 5, 6, 12).
- **On Story/Task: NOT wasteful — required.** The Story/Task is where the effort
  estimate (`Sum of Story Points`) lives. **JQL cannot filter an issue by its
  parent Epic's Customer/Pod.** So "effort per customer" and "effort per pod"
  reports **require the field physically on the estimate-bearing issue**. This is
  exactly the reporting reason suspected — confirmed.

The fix that removes the *manual* duplication without breaking reporting:
> **Automation rule:** on create of a Story/Task, if Customer / Pod / Source /
> Product Manager are empty, copy them from the parent Epic. Humans never
> re-type; the value is still physically on the issue for JQL/reporting.

Action:
- Keep Customer/Pod/Source required on Story/Task and PM required on Task.
- Add the copy-from-parent Automation rule so they default from the Epic.

---

## Change 9 — Team field cleanup (Pod becomes the team field)

Problem: the native **Team (10300)** field is **polluted** — it mixes OpsGenie
on-call teams and departments with delivery teams, so it is unreliable for
delivery attribution.

Decision: **Pod (10988) is the single controlled team field.** Native Team is
**hidden from all create screens** (not deleted — deleting is destructive and
would break history / any Plans usage). Pod is a controlled single-select and
already populated on real tickets.

Action:
- Hide native Team (10300) from Epic/Story/Task/Bug/Sub-task create screens.
- Treat Pod as the team of record for reporting.
- (Optional future) if native Team is wanted for Plans later, curate its option
  list to mirror Pod and de-pollute the OpsGenie/department entries first.

---

## Change 10 — Environment vs Target Environment (distinct, scoped)

The two fields have near-identical option lists (Environment has an "Integration"
vs "Integrations" typo) but different meanings. Keep both, scope them:

- **Environment (10598)** = *where a bug was found*. **Bug only** — required on
  Bug, hidden on Epic/Story/Task/Sub-task (items 3, 10).
- **Target Environment (11602)** = *release destination* (incl. hotfixes).
  Available on all delivery types; required on Story/Task (item 2).

Action:
- Make Environment required on Bug, remove it from non-Bug create screens.
- Keep Target Environment on Story/Task; fix the "Integration/Integrations" typo
  so both lists match.

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
| 6 — Estimate required on Task/Story, removed from Sub-task | PM lead | ☐ | | |
| 6 (open q) — Custom `Sum of Story Points` vs built-in Story Points | PM lead + Eng lead | ☐ | | |
| 7 — "In Progress" automation exempts Sub-tasks | PM lead + Jira admin | ☐ | | |
| 8 — Attribution auto-copy from parent Epic | PM lead + Jira admin | ☐ | | |
| 9 — Team hidden; Pod is the team field | PM lead + Jira admin | ☐ | | |
| 10 — Environment (Bug only) vs Target Environment | PM lead + Jira admin | ☐ | | |

Once approved, the Jira admin implements Changes 1–4 in the SP project screen
schemes and workflow; Change 7 is an Automation-rule edit; Change 5 is enforced
via the templates and skills.
