---
name: profinda-jira
description: ProFinda Jira workflow for agents. Covers PRD in Epic description, User Stories, sub-tasks as progress tracker and as the vehicle for handing off remaining work between sessions/agents, and short HANDOFF comments for pointers/context. Use when user provides a Jira ticket ID (SP-XXXX), asks to start work on a ticket, or when no ticket exists and the agent should offer to create one.
---

# ProFinda Jira Workflow

Use `mcp-atlassian` MCP tools for all Jira operations (`jira_get_issue`, `jira_create_issue`, `jira_update_issue`, `jira_transition_issue`, `jira_add_comment`, `jira_get_transitions`, `jira_batch_create_issues`). Always call `jira_get_transitions` before transitioning — IDs vary by current state.

- **Instance**: `https://profinda.atlassian.net` · **Default project**: `SP` · **Board**: `175` (scrum)
- Raw CLI/REST mechanics (auth, generic field-discovery queries) live in the separate `jira-cli` skill — this skill owns ProFinda's actual field IDs, required-fields-by-type, and workflow policy below. Use `jira_search_fields` + `jira_get_field_options` to verify/refresh any field option ID that looks stale.

## Required fields by issue type (`additional_fields`)

### Task
| Field | Key | Required |
|---|---|---|
| Fix Version | `fixVersions` | Yes |
| Pod | `customfield_10988` | Yes |
| Requires Documentation | `customfield_10694` | Yes |
| Environment | `customfield_10598` | Yes |
| Source (category) | `customfield_11021` | Yes |

Common default combo for a quick internal/technical Task (current quarter, Firefighting pod, Master env, no docs needed):
```json
{"fixVersions": [{"id": "10421"}], "customfield_10988": {"id": "13600"}, "customfield_10694": {"id": "11070"}, "customfield_10598": {"id": "10328"}, "customfield_11021": {"id": "11140"}}
```

### Bug
| Field | Key | Required |
|---|---|---|
| Priority | `priority` | Yes |
| Pod | `customfield_10988` | Yes |
| Environment | `customfield_10598` | Yes |
| Source (category) | `customfield_11021` | Yes |

Bug does **not** require `fixVersions` or Requires Documentation.

### Story / Epic
Required fields differ from Task/Bug — check dynamically with `jira_get_create_fields` rather than assuming.

## Field option reference

### Pod (`customfield_10988`)
| Name | ID |
|---|---|
| Audit | `13806` |
| Booking 99 | `11000` |
| Bulbasaur Squad | `14174` |
| Charmander Squad | `14176` |
| Design (Internal) | `11003` |
| DevOps | `13598` |
| Dynamic Insights | `13773` |
| Firefighting | `13600` |
| Integrations | `13599` |
| Pikachu Squad | `14175` |
| Placeholder Pod | `13740` |
| Profile & Search | `11001` |
| QA (not POD work) | `14379` |
| Reporting & Insights | `11002` |
| Skills | `13739` |
| Squirtle Squad | `13938` |

For Management-project issues, use `Firefighting` (`13600`) or `Placeholder Pod` (`13740`). This list changes as squads are renamed/added — re-verify with `jira_get_field_options` if a name looks unfamiliar.

### Environment (`customfield_10598`)
| Name | ID |
|---|---|
| Preview Environments | `11252` |
| Master | `10328` |
| Integration | `10317` |
| UAT | `10261` |
| Production | `10260` |

When in doubt, default to `Master` (`10328`).

### Requires Documentation (`customfield_10694`)
| Name | ID |
|---|---|
| New | `10600` |
| Change To Existing | `10601` |
| None Required | `11070` |

### Source / category (`customfield_11021`)
| Name | ID |
|---|---|
| Customer Specific Change (CR) | `11137` |
| Customer Specific Change (Unplanned) | `12156` |
| Customer Task | `11142` |
| Development Task | `11143` |
| Firefighting | `11536` |
| Product Gap | `11139` |
| Product Roadmap | `11136` |
| Product Roadmap (Customer Driven) | `11138` |
| Product Roadmap (Unplanned) | `12155` |
| Regression (Existing) | `11499` |
| Regression (Quarterly Work) | `11744` |
| Tech Roadmap | `11141` |
| Technical Debt | `11140` |

### Fix Versions
Pick the version matching the current quarter; for unplanned/internal work use the current or next quarter. IDs change every quarter — verify with `jira_get_project_versions` rather than trusting a stale list here.

### Priority
| Name | ID |
|---|---|
| P1 | `1` |
| P2 | `2` |
| P3 | `3` |
| P4 | `4` |

### Issue Types
| Name | ID | Sub-task? |
|---|---|---|
| Story | `10000` | No |
| Task | `10001` | No |
| Sub-task | `10002` | Yes |
| Bug | `10003` | No |
| Epic | `10004` | No |
| Internal Bug | `10113` | No |
| Technical Issue | `10179` | No |
| Design | `10189` | No |
| Design Task | `10184` | Yes |

## When the developer provides a Jira ID

1. **Read the ticket** — `jira_get_issue` with `comment_limit: 10`
2. **Check for open sub-tasks and a HANDOFF comment** — open sub-tasks carry the actual plan for remaining work (read their descriptions); scan comments for `[AGENT HANDOFF]` for a short pointer to which ones and any non-work context (gotchas, decisions)
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
| Work units that could run in parallel or be picked up independently, or that a handoff leaves for a future session/agent | Ordered steps within a single atomic unit, all done in the current session |
| More than ~4 steps | 3 steps or fewer |
| Steps span multiple sessions or agents | All steps done in one go |

Create one with `jira_create_issue(issue_type="Subtask", additional_fields={"parent": "SP-XXXX"})` — use the parent's key, not `epicKey`/`epic_link` (those are for linking Stories/Tasks to an Epic, not a sub-task to its parent).

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

## Handing off remaining work

When a session ends with work still to do, don't leave "what's next" as bullet points in a comment — a comment can't be transitioned, assigned, or linked as a unit of work, and it forces the next agent to re-parse prose into a plan. Instead:

1. **Create a sub-task per remaining unit of work** (or update an existing one), each with a description following the Task template above (What and why / Approach / Key decisions / Risks). Do this even if only one agent/session ever picks it up — the sub-task is the plan, not a comment about the plan.
2. **Post a short comment** noting what was completed this session and linking the sub-task(s) that carry what's left. Don't restate their content in the comment.
3. The next session's prompt can then be as simple as "pick up SP-XXXX-Y" — the agent reads that sub-task's description for its plan, and the parent Story/Task + Epic for wider context.

Reserve a narrative comment for things that are genuinely not a unit of trackable work: environment gotchas, decisions/trade-offs made and why, or context a future session would otherwise waste time rediscovering.

Only post the comment below when the developer requests it or an explicit agent handoff is happening. Post on the Story or Task, not the Epic.

```
[AGENT HANDOFF]
Date: YYYY-MM-DD
Branch: feature/SP-XXXX-short-description
Worktree: .worktrees/SP-XXXX-short-description (if applicable)

Completed:
- SP-XXXX sub-task title

Next: see SP-XXXY, SP-XXXZ (sub-tasks created/updated this session)

Context:
- Chose X over Y because of Z constraint in lib/foo.rb:42
- Gotcha: <environment quirk that isn't itself a work item>

Blockers:
- None
```

## Transitions and closing

Available transitions vary by current state — always call `jira_get_transitions` rather than assuming. Known transitions from "In Progress": `Parked`, `Blocked`, `Closed`, `Waiting Review`, `Cancel`.

- **Starting work**: transition to `In Progress`.
- **PR opened**: transition to `Waiting Review` + add the PR URL as a comment.
- **Merged**: transition to `Closed` (or auto-closed by the PR).

Required fields on the `Closed` transition are screen-config driven and differ by hierarchy level:

- **Sub-task**: only **Resolution** is required. Closing is a one-liner — no story points, release notes, source, or fix version.
- **Task / Story / Epic**: also requires **Resolution + Sum of Story Points (`customfield_10599`) + Source/category (`customfield_11021`) + Fix Version**, and a validator may additionally require **Release notes (`customfield_10578`)** to already be set before transitioning.

Two gotchas:
- `Story Points` (`customfield_10022`) is often **not** on the transition screen even when a validator asks for "Story Points" — the screen field is `Sum of Story Points` (`customfield_10599`). Set that one, not `10022`.
- Moving an Epic to `In Progress` may require walking the ladder `Backlog → In refinement → Ready for Dev → In Progress`, and `Ready for Dev` requires Pod + T-shirt size + Fix Version.

## `mcp-atlassian` markdown-to-ADF gotcha

`mcp-atlassian`'s markdown-to-ADF conversion generally works fine (bold, headings, and inline code all convert correctly for normal content). But it can break on descriptions that are long and dense with special characters throughout (many underscores from identifiers like `lite_api`/`profinda_saas`, literal `{`/`}` from shell or JSON snippets quoted inside a backtick span, nested quotes inside a code span, etc.). When it breaks, the failure isn't localized — headings/bold/code throughout the *entire* description come out as literal Jira wiki-markup text (`h2. Why`, `\*bold\*`, `{{code span}}`) instead of real formatting, even in sections that individually look fine. Bullet lists and markdown links are comparatively robust.

Practical fix: avoid quoting complex shell/JSON snippets verbatim inside a single backtick span (paraphrase instead, or drop them into their own fenced code block); if that alone doesn't fix it, build the ADF `description` by hand instead of relying on `mcp-atlassian`'s conversion. For the coloured section banners used in this skill's `templates/` (`Epic`/`Story`/`Task`/`Subtask` in `profinda-jira/templates/`), you must build ADF directly anyway — `mcp-atlassian` has no concept of coloured banners. Reuse `templates/adf/generate.py`'s `md_to_adf()` function: write the description as Markdown using its supported subset (headings, `## {green|teal|navy|red|orange} Title` banners, single-line paragraphs, bullet/task lists, tables, blockquotes — no inline bold/code marks, block-level structure only), convert with that function, then `PUT` the resulting ADF JSON straight into `fields.description` via the REST API (skip `mcp-atlassian` for this). After creating/updating a description this way, always spot-check it by fetching the issue URL in a browser rather than trusting the tool call succeeded cleanly.

## Commit discipline

```
Add rate limiter middleware [SP-1234]
```

No PRD files, no agent state files left in the repo. Jira is the record.

## Session end checklist

- [ ] Description written (spec + plan) before implementation started
- [ ] Completed sub-tasks transitioned to Done
- [ ] Remaining work captured as sub-task(s) with a plan in their description — not as bullet points in a comment
- [ ] Description reflects final understanding (decisions, deviations from plan)
- [ ] Ticket in correct state (In Progress / Waiting Review / Closed)

Post a HANDOFF comment only if the developer asks for it, or if explicitly handing off to another agent or session — and even then, keep it short: link the sub-task(s) for what's next rather than describing them.
