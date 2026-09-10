<!--
STORY = user-facing feature (UI, public APIs, MCPs). Owned by Product.
Inherits the Epic's architecture and risk — do NOT repeat them here.
The PLAN lives in this description. The STEPS live in sub-tasks OR the checklist
below (your choice — see the skill/README). Dependencies are Jira issue links.
Estimate (Sum of Story Points), Customer, Pod, Source, PM live in Jira fields.
-->

## {green} B · WHAT & WHY

### User value
As a {persona}, I want {capability}, so that {benefit}.

## {teal} C · REQUIREMENTS

### Requirements (functional)
Numbered list of what the system must do for THIS story.

### UX / UI requirements
User-facing design requirements. Link Figma. N/A-with-reason if none.

### Acceptance criteria
- Given … When … Then … (specific, testable)

## {navy} D · TECHNICAL DESIGN

### Detailed technical design
Story-level design. Inherits the Epic architecture — do not repeat it.
- Approach:
- Architecture / data / API changes specific to this story:
- Feasibility notes:

### Plan
The plan/spec the dev or agent follows. May be drafted as a local PLAN.md in the
loop, but must live here so it survives independent of any machine.

### Steps
Choose ONE:
- **Sub-tasks** (recommended for multi-session/parallel work) — created and linked
  in Jira; progress = sub-task status. Delete this checklist if using sub-tasks.
- **Checklist** (small/atomic work):
  - [ ] Step 1
  - [ ] Step 2

### Out of scope
Explicitly NOT included in this story.

## {orange} E · APPROVAL — DEFINITION OF READY TO BUILD
- [ ] Acceptance criteria clear and testable
- [ ] UX linked or N/A
- [ ] Technical design agreed

| Role | Name & date | Approved / Rejected |
|------|-------------|---------------------|
| Lead Engineer | | |
| Product (or delegate) | | |

<!--
No Risk section: risk lives on the Epic (done once). New risk → update the Epic.
No Dependencies section: use Jira issue links (blocks / is blocked by).
No Test approach section: the test plan lives in SmartRuns (linked), not here.
Sign-off above is required in addition to the status transition (SOC-2/ISO 27001).
-->
