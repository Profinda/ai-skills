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
4. **If Epic**: treat description as the living PRD — read it, refine sections, never replace wholesale
5. **If Story**: read acceptance criteria; create sub-tasks for planned work units
6. **If Task**: create sub-tasks or use description checklist depending on complexity (see below)
7. **Proceed with implementation** — transition sub-tasks as you go

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

## Epic as living PRD

Structure the Epic description as:

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

- [ ] Completed sub-tasks transitioned to Done
- [ ] Story/Epic description updated if understanding changed
- [ ] Ticket in correct state (In Progress / Waiting Review / Closed)

Post a HANDOFF comment only if the developer asks for it, or if explicitly handing off to another agent or session.
