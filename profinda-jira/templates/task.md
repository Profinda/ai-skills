# {Task title}

<!--
TASK = internal technical work (devops, non-breaking refactors). Owned by
Engineering. Inherits the Epic's architecture and risk — do NOT repeat them.
The PLAN lives in this description. The STEPS live in sub-tasks OR the checklist
below. Dependencies are Jira issue links. Estimate (Sum of Story Points),
Customer, Pod, Source, PM live in Jira fields.
-->

## What & why (technical end-state)
What is being changed and the technical end state. Why it matters.

## Requirements / definition of done
Specific, testable conditions that define completion.

## Detailed technical design
Inherits the Epic architecture — do not repeat it.
- Approach:
- Architecture / data / API changes:
- Feasibility notes:

## Plan
The plan/spec the dev or agent follows. May be drafted as a local PLAN.md in the
loop, but must live here so it survives independent of any machine.

## Steps
Choose ONE:
- **Sub-tasks** (recommended for multi-session/parallel work) — created and linked
  in Jira; progress = sub-task status. Delete this checklist if using sub-tasks.
- **Checklist** (small/atomic work):
  - [ ] Step 1
  - [ ] Step 2

## Rollout & rollback plan
How this ships and how it is reverted if it goes wrong.

## Monitoring & observability
Metrics/logs to confirm health. What to watch after release.

## ⚠️ Customer impact check (Release Notes gate)
Is this actually customer-visible after all?
- Breaking change? Yes / No
- UX change? Yes / No
- Public API / MCP change? Yes / No

If ANY = Yes → fill the **Release notes** field and set **Requires Documentation**.
If this is a large user-facing change, consider converting to a Story.

## Out of scope
Explicitly NOT included.

## Definition of Ready to Build
- [ ] Definition of done clear
- [ ] Rollback plan defined
- [ ] Customer impact check done

| Role | Name & date | Approved / Rejected |
|------|-------------|---------------------|
| Lead Engineer | | |

<!--
No Risk section: risk lives on the Epic (done once). New risk → update the Epic.
No Dependencies section: use Jira issue links.
Sign-off above is required in addition to the status transition (SOC-2/ISO 27001).
-->
