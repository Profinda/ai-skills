---
name: profinda-jira
description: ProFinda Jira workflow for agents. Covers PRD in Epic description, User Stories, sub-tasks as progress tracker, and HANDOFF comments for session continuity. Use when user provides a Jira ticket ID (SP-XXXX), asks to start work on a ticket, or when no ticket exists and the agent should offer to create one.
---

# ProFinda Jira Workflow

Use `mcp-atlassian` MCP tools for all Jira operations. See [MCP.md](MCP.md) for tool reference and patterns.

## When the developer provides a Jira ID

1. **Read the ticket** — `jira_get_issue` with `comment_limit: 10`
2. **Check for HANDOFF comment** — scan comments for `[AGENT HANDOFF]`; if found, resume from it
3. **Move to In Progress** — `jira_transition_issue` (call `jira_get_transitions` first)
4. **Write the spec into the description** — before any implementation, update the ticket description with your understanding of the problem, the plan, and key decisions (see description structures below). This is the output of the brainstorm and the plan the agent follows.
5. **Create sub-tasks** — for Stories and Tasks, break the plan into sub-tasks or a checklist (see below)
6. **Proceed with implementation** — transition sub-tasks as you go, refine the description as understanding evolves

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

## Description as spec and plan

The ticket description is the agent's primary working document — written before implementation starts, refined as understanding grows. It serves as the output of the brainstorm and the plan the agent follows. Never leave it as the original one-liner the developer wrote.

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
