---
name: profinda-jira
description: ProFinda Jira workflow for agents. Covers PRD in Epic description, User Stories, sub-tasks as progress tracker, and HANDOFF comments for session continuity. Use when user provides a Jira ticket ID (SP-XXXX), asks to start work on a ticket, or when no ticket exists and the agent should offer to create one.
---

# ProFinda Jira Workflow

Load `profinda-jira-cli` for the CLI commands and REST API field reference needed to execute the steps below.

## When the developer provides a Jira ID

1. **Read the ticket** — `jira issue view SP-XXXX` to understand the scope
2. **Check for HANDOFF comment** — scan comments for `[AGENT HANDOFF]` block; if found, resume from it
3. **Move to In Progress** — `jira issue move SP-XXXX "In Progress"`
4. **If Epic**: treat the description as the living PRD — read it, do not overwrite, only append/refine
5. **If Story**: read acceptance criteria; create sub-tasks for your planned work units (see below)
6. **If Task**: create a sub-task checklist or sub-tasks depending on complexity (see below)
7. **Proceed with implementation** — update sub-task statuses as you go

## When no Jira ticket exists

Before starting any non-trivial work, offer to create a ticket:

> "No Jira ticket found. Should I create one in SP?
> - **User Story** — if this is a user-facing feature or behaviour change
> - **Task** — if this is technical work, refactoring, or infrastructure
> Which fits better, or should I just proceed without one?"

If the user confirms, load `profinda-jira-cli` and create the issue via REST API. Then follow the "developer provides a Jira ID" flow above.

## Sub-tasks vs. description checklist

| Use sub-tasks | Use description checklist |
|---|---|
| Work units that could run in parallel or be picked up independently | Ordered steps within a single atomic unit |
| More than ~4 steps | 3 steps or fewer |
| Steps span multiple sessions or agents | All steps done in one go |

## Epic as living PRD

The Epic description is the PRD. Structure it as:

```
## Goal
One sentence. What problem does this solve?

## Non-goals
What is explicitly out of scope.

## Success metrics
Measurable outcomes.

## User Stories
Links to child stories: SP-101, SP-102, ...

## Architecture notes
Key decisions, constraints, services involved.
No file paths or code snippets — refer to Jira sub-tasks or PRs for specifics.

## Open questions
Outstanding decisions that affect scope or design.
```

Update this description as understanding grows — never replace it wholesale, only refine sections.

## HANDOFF comment

Post a HANDOFF comment when:
- Context window is running out
- Switching to a different session or worktree
- Handing off to another agent or developer

Format (post as a comment on the Story or Task, not the Epic):

```
[AGENT HANDOFF]
Date: YYYY-MM-DD
Branch: feature/SP-XXXX-short-description
Worktree: .worktrees/SP-XXXX-short-description (if applicable)

Completed:
- SP-XXXX (sub-task title)
- SP-XXXY (sub-task title)

Next:
- SP-XXXZ — short description of what to do and why

Context:
Key decisions made this session that are not obvious from the code or ticket:
- e.g. "Chose X over Y because of Z constraint in lib/foo.rb:42"
- e.g. "Auth flow deliberately untouched — see SP-99 for context"

Blockers:
- None / describe any blockers
```

Any agent or developer reading this comment can resume without re-reading the full conversation.

## Commit discipline

Every commit references the Jira ID in brackets at the end:

```
Add rate limiter middleware [SP-1234]
```

No PRD files, no agent state files, no TODO comments left in the repo. Jira is the record.

## Session end checklist

- [ ] All completed sub-tasks moved to Done
- [ ] Story/Epic description updated if understanding changed
- [ ] HANDOFF comment posted if work is incomplete
- [ ] Ticket moved to correct state (`In Progress` / `Waiting Review` / `Closed`)
- [ ] PR URL added as comment if a PR was opened
