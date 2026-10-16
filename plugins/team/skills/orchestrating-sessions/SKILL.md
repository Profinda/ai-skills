---
name: orchestrating-sessions
description: Playbook and helper tools for coordinating several parallel OpenCode sessions on one body of work (spawning Player sessions, keeping them in sync, PR/review radar, local glue branch). Load when acting as the Orchestrator agent, or when asked to spin up, track or coordinate multiple sessions.
---

# Orchestrating sessions

The Orchestrator agent coordinates Player sessions. Tools: `team_join`, `team_common`, `team_spawn`, `team_roster`, `team_inspect`, `team_send`, `team_inbox`, `team_log` (the `team` plugin from `Profinda/ai-skills`, `plugins/team/`, which needs OpenCode V2 or newer). Shell helpers: `team` (same operations from a terminal) and `prs` (GitHub/git radar), both in the plugin's `bin/` folder and normally linked onto PATH. State lives in `~/.local/share/opencode-team/<team>/` (`roster.json`, `messages.jsonl`, `common.md`, `inbox.json`, `resources.json`, `handoffs/`, `workspace/`).

## Starting a team

1. Read the scope in the tracker (epic, tickets, links, PRs, dev info) and in code. Write down the dependency order, what is already built, what can run in parallel.
2. `team_join(team=NAME, role="orchestrator")`. Pick a title prefix the user can search (for example `__NAME [SP-123] Short title`).
3. Write the shared rules with `team_common` (see "Rules worth giving every player").
4. For each slice create the worktree (`git worktree add .worktrees/<branch> -b <branch> origin/<base>`, then `git submodule update --init`), then `team_spawn(team, name, directory, title, brief, model?)`. Default model for real work; a cheaper model only for trivial, mechanical, well-specified work, and you review its output.
5. A good brief has: ticket and epic links, scope and out-of-scope, the repo/worktree/branch and its base, ownership boundaries (what other players own), dependencies and merge order, known facts you verified, acceptance criteria, what to ask the user first, who to coordinate with, how to test. Tell players to restate the acceptance criteria and open questions to the user before coding.
6. Sessions the user started by hand can join: ask them to call `team_join` (or switch them to the `player` agent), or register them yourself by editing through `team_join` from their session.

## Keeping the team in sync

Message economy (protects your context): `team_report` never wakes you. Player `team_send` kinds `question`, `blocker`, `urgent` and `team_report` done/blocked wake you through one batched digest, delivered only when you are idle (4 s debounce, and again when a busy turn ends, so nothing is lost). `info` and `decision` wait in the inbox (`team_inbox`, counts shown in `team_roster`). Per-sender wake limit 5 per 10 minutes, per-pair limit 8 per 10 minutes. Your own sends to players always deliver. Read the roster for status; read the inbox for asks.

- Read state, do not guess: `team_roster` (live busy/idle, last report, pending user questions), `team_inspect(name)` (last message, pending question, tools), `team_log`.
- Surface first: members `waiting_user` (what the user must answer), `blocked`, `error`, and idle members whose last report is not done.
- Route decisions yourself: when a finding in one slice affects another, `team_send` the owner with the fact and the decision; do not make the user relay it. When the user decides, send it to every affected player in the same turn and update `team_common` if it is durable.
- Give each shared file/branch/PR exactly one owner. For sibling PRs touching the same files agree who lands first and that the other resolves by union afterwards; players never copy each other's changes or push to each other's branches.
- Stop drift: stale reports, stale PR bodies, stale stack builds. Ask owners to refresh; check `git` and `gh` yourself.

## Radar (run regularly)

- `prs overlaps <repo> <pr...>`: files touched by several PRs.
- `prs reviews <repo> [...] --label L --need 2`: approvals, stale approvals, who is requested, CI, urgency order (bottom of a stack first, then fewest approvals). Use it to tell the user whom to chase.
- `prs worktrees <repo-dir>`: uncommitted files, unpushed commits, branches with no remote.
- `prs sim <repo-dir> <base-ref> <branch...>`: merge order simulation in a throwaway worktree, conflicts per step (`db/schema.rb` version lines are routine churn).
- `prs label <repo> <label> <pr...>` and `prs list <repo> --label L`: a label on every PR of the effort (open and closed) makes filtering easy.
- Check the machine: `docker ps`, listening ports, per-worktree database names, shared Redis/HAL-like services, before parallel test runs.

## Integration stack (end to end locally)

Keep every shared artifact of the effort (stack status file, glue and seed scripts, QA scripts, screenshots, handoffs) in the team workspace (`<team space>/workspace/`, shown in `team_roster` and in every brief), not in the repos, so the whole footprint is in one place. Keep a repeatable local glue branch per repo (never pushed) built by a script that recreates it from current origin and merges a manifest of PR branches in order; record resolved conflicts (git rerere) so reruns reproduce them; stop on anything it cannot resolve. Reseed from the generator only: no local top-ups, every gap is a bug in the owning PR. Publish a `Status: READY/NOT READY` line, SHAs, URLs and logins in a stack file, write seed quality gaps to a gaps file the owners read, and run an end-to-end pass as a real user with the owning PR per failure. A stale glue build is the most common false alarm: print merged SHAs and warn when a merged branch moved on origin.

## Rules worth giving every player (put them in `team_common`)

- Jira or the tracker is the source of truth; restate acceptance and ask open design questions before coding.
- Standing permission: commit and plain `git push` to the branch of a PR you own, never force. Ask first for opening a new PR, changing a base, pushing to shared branches, merging, deleting, removing worktrees, ticket transitions.
- Screenshots in PRs or tickets come only from the real app against a real backend with realistic seeded data; prototypes, Storybook and mocked pages are for building only. If the real UI is not reachable, write `N/A: reason`.
- PR bodies describe what the PR does now, following the repo template, links first, no history, no command logs; rewrite sentences instead of appending updates. Label every PR.
- No explanatory code comments; follow the repo's conventions and skills; verify in the repo's own isolated environment (unique DB, no shared containers).
- Use the team tools: report at milestones, `waiting_user` when asking the user, message other players directly for things that affect them.

## Reviewing big scope

Read the ticket and architecture first, then the diff of each risky PR (or delegate to `developer` with precise questions): does it do what the ticket says, what does it break elsewhere, are permissions/migrations/existing accounts handled, are specs using real grants instead of global stubs, does a fresh seed work. Send findings to the owning player with `team_send`; summarise to the user only what needs their decision.

## Footprint and closing a team

A team's footprint is more than its folder: the team space (state and `workspace/`), git worktrees, local branches, test databases, a container project, dev servers on ports, temp directories, and OpenCode sessions. It is only easy to clean if it was registered while it was created.

- While running: every worktree you give `team_spawn` is registered automatically. Tell players to register everything else with `team_resource(action="add", kind, ref, cleanup=<exact command>)`: a database they created, a compose project, a local-only branch (`kind=branch`, `repo`, `disposable=true` for throwaway glue branches), a temp directory, a dev server. Never rely on name patterns to find resources later: unrelated worktrees and databases carry similar names.
- Never register something the team did not create. A worktree that existed before the team, or belongs to the user, stays out of the manifest even if a player works in it (`team_close` lists such roster-only worktrees and leaves them alone).
- Closing: when the work is merged or abandoned, run `team_close` (dry run). Show the user the report, with what will be removed, what is blocked and why (uncommitted files, unpushed commits, local-only commits), and the cleanup commands for databases, containers, directories and processes. Only after an explicit yes call `team_close(confirm=true)`, then run the listed commands the user approved, with your shell, and report what was removed and what is left. Blocked items stay in place and are recorded in the closed archive (`~/.local/share/opencode-team/_closed/<team>-<time>/`, which also holds the roster, log, rules, handoffs and the workspace; the user deletes it when they no longer need it).
- Not covered, tell the user: remote branches and PRs (the devs own them), OpenCode sessions (kept, removable from the session list), Jira.

## Handing over the orchestrator role

Do it when your context is heavy after a long run, or the user asks. Not while a question to the user is pending. Use `team_handoff`, not `team_spawn` and not `team_join`:

- `team_spawn` gives the new session the PLAYER brief ("you are a player ... coordinated by the orchestrator session"), which is wrong for a successor. `team_join(role=orchestrator)` refuses to replace a live orchestrator unless `takeover=true`, which is only for a gone session.
- Do NOT read `team_inbox` right before handing over: it clears the unread items. `team_handoff` copies them into the handoff file and leaves them unread for the successor. Use `team_roster` and `team_log` to look at the state.
- The tool collects the FACTS itself: roster (live), unread inbox, shared rules, recent log. Your `notes` carry the JUDGMENT, which no tool can read: the user's preferences and how they want reports; durable decisions (put the durable ones into `team_common` first, so every player has them too); who owns what and which sessions are dead or finished; questions waiting on the user; the review queue and merge order; environment facts (stack URL and logins, ports, how screenshots get uploaded, any credential procedure the user authorised and its limits); risks; what to do first. A handoff with only a task list loses the user's preferences and the reasons behind decisions.
- It retires your roster entry (state retired, new name), spawns the successor under the name `orchestrator` so players keep addressing the same name, and rolls everything back if the spawn fails. Handoff files live in `~/.local/share/opencode-team/<team>/handoffs/` (`latest.md` is the newest).
- Afterwards: confirm the successor started (`team_inspect orchestrator`), tell the user the handover is done, and stop coordinating. Do not message players about it; they do not need to know.
- The successor's first steps: read the handoff, `team_roster` (live) and `team_inbox`, verify the facts that matter (`prs reviews`, the stack, who waits on the user) instead of trusting the handoff blindly, then send the user one short confirmation with state per session and the questions waiting on them.

## Reporting to the user

State per session (one line each), what needs them (questions with options and a recommendation), risks and blockers, PRs awaiting review (from `prs reviews`), next step. No lessons, no long history.
