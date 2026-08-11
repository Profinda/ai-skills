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
4. **AC CONFIRMATION GATE — STOP HERE** (this is its own step; it is not "done" when you finish restating):
   - Your turn MUST end with this exact question and nothing after it:
     > **Is this understanding correct? (yes / correct me)**
   - **Do NOT call any tool in the same turn as the gate question.** End the turn. Wait for the developer's reply.
   - Until the developer replies "yes" (or equivalent confirmation), you MUST NOT:
     - investigate the application codebase (no file reads, grep, glob, or explore/subagent dispatch),
     - write or draft a plan,
     - transition the ticket or move it to In Progress.
   - Allowed before confirmation: creating a git worktree, reading the Jira ticket and its linked design docs.
   - **Escape hatch:** if the developer explicitly says "skip the gate" / "just go", proceed without waiting.

   **Red flags — these thoughts mean you are about to skip the gate. STOP and ask the question instead:**

   | Thought | Reality |
   |---|---|
   | "First understand the goal, then explore" | Restating IS the goal-understanding. The gate comes next. STOP. |
   | "Need to explore the codebase first" | Not until confirmed. STOP. |
   | "Let me delegate explore agents in parallel" | That is codebase investigation. STOP. |
   | "AC are obvious, I can proceed" | Only the developer decides that. Ask, or wait for 'skip the gate'. |
   | "I already restated, so step 3 is done" | Restating ≠ confirmation. Step 4 (the gate) is still pending. STOP. |
   | "I'll just plan while I wait" | Planning is blocked until confirmed. STOP. |

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
