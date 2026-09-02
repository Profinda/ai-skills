---
name: profinda-jira
description: ProFinda Jira workflow for agents. Covers PRD in Epic description, User Stories, sub-tasks as progress tracker, and HANDOFF comments for session continuity. Use when user provides a Jira ticket ID (SP-XXXX), asks to start work on a ticket, or when no ticket exists and the agent should offer to create one.
---

# ProFinda Jira Workflow

Use `mcp-atlassian` MCP tools for all Jira operations (`jira_get_issue`, `jira_create_issue`, `jira_update_issue`, `jira_transition_issue`, `jira_add_comment`, `jira_get_transitions`, `jira_batch_create_issues`). Always call `jira_get_transitions` before transitioning — IDs vary by current state.

When creating Tasks, these custom fields are required in `additional_fields`:
```json
{"fixVersions": [{"id": "10421"}], "customfield_10988": {"id": "13600"}, "customfield_10694": {"id": "11070"}, "customfield_10598": {"id": "10328"}, "customfield_11021": {"id": "11140"}}
```
Use `jira_search_fields` + `jira_get_field_options` to discover or verify field option IDs dynamically.

## When the developer provides a Jira ID

1. **Read the ticket** — `jira_get_issue` with `comment_limit: 10`
2. **Check for HANDOFF comment** — scan comments for `[AGENT HANDOFF]`; if found, resume from it
3. **Restate the acceptance criteria** (read-only — uses only `jira_get_issue`):
   - Read the `## Acceptance criteria` section and description.
   - If AC are missing or thin, say so plainly and ask the developer to clarify. Do NOT write acceptance criteria back to Jira.
   - Restate the acceptance criteria in your own words.
4. **AC CONFIRMATION GATE — STOP HERE** (own step; not done when you finish restating):
   - End your turn with exactly this, nothing after: **Is this understanding correct? (yes / correct me)**
   - No tool calls in the same turn. Wait for the developer's reply.
   - Until they confirm: do NOT investigate the codebase, plan, or transition the ticket. Allowed: create a worktree, read the ticket + linked docs.
   - Escape hatch: if they say "skip the gate" / "just go", proceed.

   Red flags = you're about to skip. All mean STOP and ask:
   "explore codebase first" · "delegate explore agents" · "understand the goal first" · "AC are obvious" · "I already restated" · "I'll plan while I wait"

5. **Move to In Progress** — `jira_transition_issue`
6. **Write the spec into the description** — before any implementation, update the ticket description with your understanding of the problem, the plan, and key decisions (see templates below). This is the output of the brainstorm and the plan the agent follows.
7. **Create sub-tasks** — break the plan into sub-tasks or a checklist (see below)
8. **Proceed with implementation** — transition sub-tasks as you go, refine the description as understanding evolves

## When no Jira ticket exists

Before starting any non-trivial work, offer to create one:

> "No Jira ticket found. Should I create one in SP?
> - **User Story** — user-facing feature or behaviour change
> - **Task** — technical work, refactoring, or infrastructure
> Which fits better, or should I just proceed without one?"

If confirmed, create via `jira_create_issue` then follow the flow above.

## Sub-tasks vs. description checklist

| Use sub-tasks | Use description checklist |
|---|---|
| Work units that could run in parallel or be picked up independently | Ordered steps within a single atomic unit |
| More than ~4 steps | 3 steps or fewer |
| Steps span multiple sessions or agents | All steps done in one go |

## Description templates

The ticket description is the agent's primary working document — written before implementation starts, refined as understanding grows. Never leave it as the original one-liner the developer wrote.

### Epic — living PRD
```
## Goal
One sentence — what problem does this solve?

## Non-goals
What is explicitly out of scope.

## Success metrics
Measurable outcomes.

## User Stories
SP-101, SP-102, ...

## Architecture notes
Key decisions, constraints, services involved.
No file paths or code snippets.

## Open questions
Outstanding decisions that affect scope or design.
```

### Story — spec and acceptance criteria
```
## What and why
What behaviour is being added and why it matters.

## Acceptance criteria
- Given ... When ... Then ...

## Edge cases
Scenarios that need special handling.

## Implementation notes
Key decisions, constraints, affected areas.
Refined as implementation progresses.
```

### Task — plan and approach
```
## What and why
What is being changed and why.

## Approach
Step-by-step plan the agent will follow.

## Key decisions
Trade-offs made, alternatives considered.

## Risks / unknowns
Anything that could affect the approach.
```

## HANDOFF comment

Only when the developer requests it or an explicit agent handoff is happening. Post on the Story or Task, not the Epic.

```
[AGENT HANDOFF]
Date: YYYY-MM-DD
Branch: feature/SP-XXXX-short-description
Worktree: .worktrees/SP-XXXX-short-description (if applicable)

Completed:
- SP-XXXX sub-task title

Next:
- SP-XXXY what to do and why

Context:
- Chose X over Y because of Z constraint in lib/foo.rb:42

Blockers:
- None
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

No PRD files, no agent state files left in the repo. Jira is the record.

## Session end checklist

- [ ] Description written (spec + plan) before implementation started
- [ ] Completed sub-tasks transitioned to Done
- [ ] Description reflects final understanding (decisions, deviations from plan)
- [ ] Ticket in correct state (In Progress / Waiting Review / Closed)

Post a HANDOFF comment only if the developer asks for it, or if explicitly handing off to another agent or session.
