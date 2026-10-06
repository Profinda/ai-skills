// The team_* tools. Names, arguments and replies match the V1 plugin so agent prompts keep working.
import {
  ORCHESTRATOR,
  fileToOrchestrator,
  findBySession,
  findTarget,
  getCommon,
  now,
  addResource,
  closedHome,
  ensureWorkspace,
  handoffDir,
  mutateRoster,
  readResources,
  removeResource,
  teamDir,
  workspaceDir,
  type Resource,
  logMessage,
  orchestratorOf,
  pairLimitCheck,
  peekInbox,
  renameMember,
  fanoutCheck,
  readLog,
  readRoster,
  registerMember,
  resolveTeam,
  setCommon,
  takeInbox,
  updateMember,
  type Member,
} from "./store.ts"
import { mkdir, rename, rm, writeFile } from "node:fs/promises"
import path from "node:path"
import { KINDS, STATES, envelope, notify } from "./protocol.ts"
import { dirSize, exists, inspectBranch, inspectWorktree, linkedWorktreeRepo, removeBranch, removeWorktree } from "./close.ts"
import { scheduleFlush, type TeamSessions } from "./sessions.ts"

type Caller = { sessionID: string; agent: string }

const str = (description?: string) => ({ type: "string", ...(description ? { description } : {}) })
const object = (properties: Record<string, unknown>, required: string[] = []) => ({
  type: "object",
  properties,
  required,
  additionalProperties: false,
})

export function createTeamOps(ctx: any, sessions: TeamSessions) {
  async function directoryOf(sessionID: string): Promise<string> {
    const session = await ctx.session.get({ sessionID })
    return session?.location?.directory ?? ctx.location.directory
  }

  async function send(input: { to: string; message: string; kind?: string; team?: string }, from: { sessionID?: string; name: string; role: string }) {
    const team = await resolveTeam(input.team, from.sessionID)
    const kind = input.kind || "info"
    const fromName = from.name
    const fromRole = from.role

    if (input.to === "user") {
      notify(`${team}: ${fromName} (${kind})`, input.message)
      await logMessage(team, { from: fromName, to: "user", kind, text: input.message })
      return "User notified on the desktop. They will read it in the session; also ask with the question tool if you need an answer."
    }

    const roster = await readRoster(team)
    const others = Object.values(roster.members).filter((member) => member.sessionId !== from.sessionID && member.name !== fromName)
    if (input.to === "all" && fromRole !== "orchestrator") {
      return "Players cannot send to 'all'. Put status in team_report (and the team's status file) and message only the specific members who must act."
    }
    const targets = input.to === "all" ? others : [findTarget(others, input.to)]
    if (!targets.length) return "Nobody to send to."

    const delivered: string[] = []
    const failed: string[] = []
    const queued: string[] = []
    for (const target of targets) {
      if (target.role === "orchestrator" && fromRole !== "orchestrator") {
        try {
          const wake = await fileToOrchestrator(team, target.name, fromName, kind, input.message)
          await logMessage(team, { from: fromName, to: target.name, kind, text: input.message })
          if (wake) scheduleFlush(sessions, team, 4000)
          queued.push(`${target.name} (${wake ? "will wake it, batched, delivered when it is idle" : "quiet inbox, no wake"})`)
        } catch (error) {
          failed.push(`${target.name} (${String((error as Error).message).slice(0, 220)})`)
        }
        continue
      }
      if (fromRole !== "orchestrator") {
        try {
          await pairLimitCheck(team, fromName, target.name)
          await fanoutCheck(team, fromName, input.message)
        } catch (error) {
          failed.push(`${target.name} (${String((error as Error).message).slice(0, 220)})`)
          continue
        }
      }
      const text = envelope({ team, fromName, fromRole, kind, text: input.message, replyTo: fromName })
      try {
        await sessions.deliver(target, text, { urgent: kind === "urgent" })
        await logMessage(team, { from: fromName, to: target.name, kind, text: input.message })
        delivered.push(target.name)
      } catch (error) {
        failed.push(`${target.name} (${String((error as Error).message).slice(0, 100)})`)
      }
    }
    return `Delivered to: ${delivered.join(", ") || "-"}.${queued.length ? ` Filed for: ${queued.join(", ")}.` : ""}${failed.length ? ` FAILED: ${failed.join("; ")}` : ""}`
  }

  async function inspectText(input: { name: string; team?: string; max_chars?: number }, sessionID?: string) {
    const team = await resolveTeam(input.team, sessionID)
    const roster = await readRoster(team)
    const member = findTarget(Object.values(roster.members), input.name)
    const info = sessions.live(member)
    const detail = await sessions.inspect(member, input.max_chars ?? 2500)
    return [
      `${member.name} [${member.role}] state=${member.state} run=${info.busy === null ? "?" : info.busy ? "busy" : "idle"}${info.outcome && !info.busy ? ` last=${info.outcome}` : ""}`,
      `messages=${detail.messages} lastTools=${detail.lastTools.join(", ") || "-"}${detail.error ? ` error=${detail.error}` : ""}`,
      detail.pendingQuestion ? `WAITING ON QUESTION:\n${detail.pendingQuestion}` : "",
      detail.lastUser ? `last user message: ${detail.lastUser}` : "",
      `last assistant text:\n${detail.lastText || "(none)"}`,
    ]
      .filter(Boolean)
      .join("\n")
  }

  async function common(input: { team: string; text?: string }) {
    if (input.text === undefined) return (await getCommon(input.team)) || "(no shared rules yet)"
    await setCommon(input.team, input.text)
    return `Saved ${input.text.length} chars of shared rules for "${input.team}". They apply to players spawned from now on; send them to existing players with team_send(to='all').`
  }

  async function log(input: { team?: string; limit?: number }, sessionID?: string) {
    const team = await resolveTeam(input.team, sessionID)
    const entries = await readLog(team, input.limit ?? 30)
    return entries.length
      ? entries.map((entry: any) => `${entry.at?.slice(11, 19)} ${entry.from} -> ${entry.to} [${entry.kind}${entry.state ? ":" + entry.state : ""}] ${String(entry.text).slice(0, 300)}`).join("\n")
      : "(no messages yet)"
  }

  async function spawnText(input: { team: string; name: string; directory: string; title: string; brief: string; model?: string; role?: string; agent?: string }) {
    const member = await sessions.spawn(input)
    return `Spawned "${member.name}" in ${member.directory} as session ${member.sessionId} (${member.agent}${member.model ? `, ${member.model}` : ""}).`
  }


  async function handoff(
    input: { team?: string; notes: string; name?: string; title?: string; model?: string; directory?: string },
    caller: { sessionID: string },
  ) {
    const team = await resolveTeam(input.team, caller.sessionID)
    const found = await findBySession(caller.sessionID)
    if (!found || found.member.role !== "orchestrator") throw new Error("Only the current orchestrator can hand over its role.")
    if (!input.notes || input.notes.trim().length < 200) {
      throw new Error("`notes` must carry your judgment for the successor (user preferences, decisions not in team_common, open questions, what to do first): at least a few paragraphs.")
    }
    const previous = found.member
    const stamp = now().replace(/[:.]/g, "-").slice(0, 19)
    const name = input.name || ORCHESTRATOR
    const [roster, common, log, unread] = await Promise.all([
      sessions.rosterTable(team),
      getCommon(team),
      readLog(team, 40),
      peekInbox(team, previous.name),
    ])
    const logLines = log.map((entry: any) => `${entry.at?.slice(11, 19)} ${entry.from} -> ${entry.to} [${entry.kind}${entry.state ? ":" + entry.state : ""}] ${String(entry.text).slice(0, 240)}`)
    const inboxLines = unread.map((item) => `- ${item.at.slice(11, 19)} from ${item.from} [${item.kind}${item.wake ? "" : ", quiet"}]: ${item.text}`)
    const doc = [
      `# Orchestrator handoff: team ${team}`,
      `Written ${now()} by ${previous.name} (session ${previous.sessionId}). The successor registers under the name "${name}", so every player message reaches it from now on.`,
      `## From the outgoing orchestrator (judgment: preferences, decisions, open questions, what to do first)\n${input.notes.trim()}`,
      `## Roster at handoff\n${roster}`,
      `## Unread inbox items (preserved: they are still unread for you, team_inbox returns them)\n${inboxLines.join("\n") || "(none)"}`,
      `## Shared rules in force (team_common)\n${common.trim() || "(none)"}`,
      `## Recent team messages (last ${logLines.length})\n${logLines.join("\n") || "(none)"}`,
      `## First steps for the successor\n1. Read this file, then team_roster (live) and team_inbox.\n2. Verify the facts that matter before relying on them: PR state (gh, prs reviews), the local stack, who is waiting on the user.\n3. Send the user one short message confirming the takeover, with state per session and the questions waiting on them.\n4. Do not message the retired session or members whose state is done or error.`,
    ].join("\n\n")
    const dir = handoffDir(team)
    await mkdir(dir, { recursive: true })
    const file = path.join(dir, `${stamp}.md`)
    await writeFile(file, doc)
    await writeFile(path.join(dir, "latest.md"), doc)

    const taken = new Set(Object.keys((await readRoster(team)).members))
    const baseName = `${previous.name}-prev-${stamp.replace(/[-T:]/g, "")}`
    let retiredName = baseName
    for (let n = 2; taken.has(retiredName); n++) retiredName = `${baseName}-${n}`
    await renameMember(team, previous.name, retiredName, {
      role: "former-orchestrator",
      state: "retired",
      progress: `Handed the role over at ${now()}; do not message this session.`,
      question: undefined,
    })
    try {
      const member = await sessions.spawn({
        team,
        name,
        role: "orchestrator",
        agent: "orchestrator",
        directory: input.directory || previous.directory,
        title: input.title || `__${team} [orchestrator] Coordinator (handoff ${stamp.slice(0, 10)})`,
        model: input.model || previous.model,
        brief: `Read the handoff file first: ${file} (also ${path.join(dir, "latest.md")}). It holds the outgoing orchestrator's notes, the roster, your unread inbox, the shared rules and the recent log. The previous orchestrator was ${previous.name} (session ${previous.sessionId}, now retired).`,
      })
      await logMessage(team, { from: previous.name, to: name, kind: "handoff", text: `Role handed over to session ${member.sessionId}; handoff file ${file}` })
      notify(`${team}: orchestrator handed over`, `New orchestrator session ${member.sessionId}`)
      return `Handed over. New orchestrator "${name}" is session ${member.sessionId}. Handoff file: ${file}. ${unread.length} unread inbox item(s) were preserved for it. Your entry is now "${retiredName}" (retired): stop coordinating, do not call team tools to act on the team, and tell the user the handover is done.`
    } catch (error) {
      await renameMember(team, retiredName, previous.name, { role: "orchestrator", state: "working", progress: previous.progress })
      throw new Error(`Handoff failed, you remain the orchestrator: ${String((error as Error).message).slice(0, 300)}`)
    }
  }

  async function resource(
    input: { team?: string; action?: string; kind?: string; ref?: string; repo?: string; cleanup?: string; note?: string; disposable?: boolean },
    caller: Caller,
  ) {
    const team = await resolveTeam(input.team, caller.sessionID)
    const action = input.action || "list"
    if (action === "list") {
      const items = await readResources(team)
      return items.length
        ? items.map((item) => `${item.id} [${item.kind}${item.disposable ? ", disposable" : ""}] ${item.ref}${item.repo ? ` (repo ${item.repo})` : ""}${item.owner ? ` owner=${item.owner}` : ""}${item.cleanup ? `\n    cleanup: ${item.cleanup}` : ""}${item.note ? `\n    note: ${item.note}` : ""}`).join("\n")
        : "No resources registered."
    }
    if (!input.ref) throw new Error("`ref` is required (path, branch name, database name, project name ...).")
    if (action === "remove") return (await removeResource(team, input.ref)) ? "Removed from the manifest (nothing was deleted on disk)." : "No such resource."
    if (action !== "add") throw new Error("action must be add, list or remove.")
    if (!input.kind) throw new Error("`kind` is required: worktree, branch, database, docker, process, dir or other.")
    if (input.kind === "branch" && !input.repo) throw new Error("A local branch needs `repo`: the absolute path of the repository it lives in.")
    if (input.kind === "worktree" && !input.repo) input.repo = (await linkedWorktreeRepo(input.ref)) ?? undefined
    if (!["worktree", "branch"].includes(input.kind) && !input.cleanup) {
      throw new Error("Resources other than worktrees and local branches need `cleanup`: the exact command that removes them. The plugin never runs it; the orchestrator runs it with the user's approval when the team closes.")
    }
    const found = await findBySession(caller.sessionID)
    const item = await addResource(team, {
      kind: input.kind,
      ref: input.ref,
      repo: input.repo,
      cleanup: input.cleanup,
      note: input.note,
      disposable: input.disposable,
      owner: found?.member.name ?? caller.agent,
    })
    return `Registered ${item.kind} ${item.ref} (${item.id}).`
  }

  async function closeTeam(input: { team?: string; confirm?: boolean; force?: boolean; include_discovered?: boolean }, caller: { sessionID: string }) {
    const team = await resolveTeam(input.team, caller.sessionID)
    const found = await findBySession(caller.sessionID)
    if (!found || found.team !== team || found.member.role !== "orchestrator") throw new Error("Only the team's orchestrator can close the team.")
    const roster = await readRoster(team)
    const members = Object.values(roster.members)
    const busy = members.filter((member) => member.sessionId !== caller.sessionID && member.state !== "retired" && sessions.live(member).busy)
    const open = members.filter((member) => member.sessionId !== caller.sessionID && !["done", "retired", "idle"].includes(member.state))
    const registered = await readResources(team)
    const known = new Set(registered.filter((item) => item.kind === "worktree").map((item) => item.ref))
    const discovered: Resource[] = []
    for (const member of members) {
      if (member.sessionId === caller.sessionID || known.has(member.directory) || discovered.some((item) => item.ref === member.directory)) continue
      const repo = await linkedWorktreeRepo(member.directory)
      if (repo) discovered.push({ id: "found", kind: "worktree", ref: member.directory, repo, owner: member.name, note: "found via the roster, not registered by anyone", createdAt: "" })
    }
    const worktrees = [...registered.filter((item) => item.kind === "worktree"), ...(input.include_discovered ? discovered : [])]
    const branches = registered.filter((item) => item.kind === "branch")
    const others = registered.filter((item) => !["worktree", "branch"].includes(item.kind))

    const lines: string[] = [`# Close team ${team}${input.confirm ? "" : " (dry run, nothing changed)"}`]
    lines.push(`Members: ${members.length}. ${busy.length ? `BUSY now: ${busy.map((member) => member.name).join(", ")}. ` : ""}${open.length ? `Not finished: ${open.map((member) => `${member.name} (${member.state})`).join(", ")}.` : "All finished."}`)
    const plan: { resource: Resource; verdict: string; detail: string; branch?: string; kind: "worktree" | "branch" }[] = []
    for (const item of worktrees) plan.push({ resource: item, ...(await inspectWorktree(item)), kind: "worktree" })
    lines.push("", "## Worktrees (git)")
    for (const entry of plan) lines.push(`- [${entry.verdict.toUpperCase()}] ${entry.resource.ref}${entry.resource.owner ? ` (${entry.resource.owner})` : ""}: ${entry.detail}`)
    if (!worktrees.length) lines.push("- none registered")
    const branchPlan: typeof plan = []
    for (const item of branches) {
      let inspected = await inspectBranch(item)
      const goesWithWorktree = plan.some((entry) => entry.branch === item.ref && (entry.verdict === "safe" || entry.verdict === "disposable"))
      if (inspected.verdict === "blocked" && inspected.detail.startsWith("still checked out") && goesWithWorktree) {
        inspected = { verdict: "safe", detail: "checked out in a worktree of this plan that is removed first" }
      }
      branchPlan.push({ resource: item, ...inspected, kind: "branch" })
    }
    lines.push("", "## Local branches (git)")
    for (const entry of branchPlan) lines.push(`- [${entry.verdict.toUpperCase()}] ${entry.resource.ref} in ${entry.resource.repo}: ${entry.detail}`)
    if (!branches.length) lines.push("- none registered")
    if (discovered.length && !input.include_discovered) {
      lines.push("", `## Worktrees found via the roster but NOT registered (left alone; they may predate the team or belong to someone else)`)
      for (const item of discovered) lines.push(`- ${item.ref} (${item.owner})`)
    }
    lines.push("", "## Everything else (listed only: the plugin never runs these; run them yourself or have the orchestrator run them with the user's approval)")
    for (const item of others) {
      const size = item.kind === "dir" && (await exists(item.ref)) ? ` [${await dirSize(item.ref)}]` : ""
      lines.push(`- ${item.kind} ${item.ref}${size}${item.owner ? ` (${item.owner})` : ""}\n    run: ${item.cleanup}${item.note ? `\n    note: ${item.note}` : ""}`)
    }
    if (!others.length) lines.push("- none registered")
    const workspace = workspaceDir(team)
    lines.push("", `## Team space: ${teamDir(team)}${(await exists(workspace)) ? ` (workspace ${await dirSize(workspace)})` : ""}`, "Closing moves the whole folder to the closed archive (roster, log, rules, inbox, handoffs, resources and the workspace). Delete the archive folder when you no longer need it.", "OpenCode sessions are not deleted: they keep their titles and can be removed from the session list.")

    if (!input.confirm) {
      lines.push("", "To close: show this report to the user, get an explicit yes, then call team_close with confirm=true. Safe and disposable items are removed; blocked ones are left in place and recorded.")
      return lines.join("\n")
    }
    if (busy.length && !input.force) {
      lines.push("", `REFUSED: ${busy.length} member(s) are still running. Wait, or call again with force=true.`)
      return lines.join("\n")
    }
    lines.push("", "## Result")
    for (const entry of plan) {
      if (entry.verdict === "missing") lines.push(`- worktree ${entry.resource.ref}: already gone`)
      else if (entry.verdict === "blocked") lines.push(`- worktree ${entry.resource.ref}: LEFT IN PLACE (${entry.detail})`)
      else lines.push(`- worktree ${entry.resource.ref}: ${await removeWorktree(entry.resource)}`)
    }
    for (const entry of branchPlan) {
      const fresh = await inspectBranch(entry.resource)
      if (fresh.verdict === "missing") lines.push(`- branch ${entry.resource.ref}: already gone`)
      else if (fresh.verdict === "blocked") lines.push(`- branch ${entry.resource.ref}: LEFT IN PLACE (${fresh.detail})`)
      else lines.push(`- branch ${entry.resource.ref}: ${await removeBranch(entry.resource)}`)
    }
    const stamp = now().replace(/[:.]/g, "-").slice(0, 19)
    await mutateRoster(team, (current) => {
      for (const member of Object.values(current.members)) {
        member.state = "retired"
        member.question = undefined
        member.progress = `Team closed ${stamp}`
      }
    })
    await logMessage(team, { from: found.member.name, to: "roster", kind: "close", text: lines.slice(-12).join(" | ").slice(0, 600) })
    await rm(path.join(teamDir(team), ".lock"), { recursive: true, force: true })
    const archive = path.join(closedHome(), `${team}-${stamp}`)
    await mkdir(closedHome(), { recursive: true })
    await rename(teamDir(team), archive)
    lines.push(`- team space archived at ${archive}`)
    lines.push("", "The team is closed: its tools no longer find it. Now run the commands in 'Everything else' that the user approves, then tell the user what was removed and what is left.")
    return lines.join("\n")
  }

  async function sender(caller: Caller) {
    const found = await findBySession(caller.sessionID)
    return {
      found,
      name: found?.member.name ?? `${caller.agent}-${caller.sessionID.slice(-6)}`,
      role: found?.member.role ?? caller.agent,
    }
  }

  const tools = [
    {
      name: "join",
      description:
        "Register THIS session in a team roster so other sessions can message it. The orchestrator calls it once at the start (role=orchestrator). Players spawned with team_spawn are registered already.",
      input: object(
        {
          team: str("Team name, e.g. PROPOSALS"),
          name: str(`Member name; defaults to '${ORCHESTRATOR}' for role=orchestrator`),
          role: str("orchestrator | player (default player)"),
          takeover: { type: "boolean", description: "Only with role=orchestrator when another orchestrator session is registered and is gone: replace it. To hand the role over in a controlled way use team_handoff instead." },
        },
        ["team"],
      ),
      async execute(args: any, caller: Caller) {
        const role = args.role || "player"
        if (role === "orchestrator") {
          const existing = await orchestratorOf(args.team)
          if (existing && existing.sessionId !== caller.sessionID && existing.state !== "retired" && !args.takeover) {
            throw new Error(`Team "${args.team}" already has an orchestrator (session ${existing.sessionId}). Use team_handoff from that session to hand the role over, or pass takeover=true if it is gone.`)
          }
        }
        const name = args.name || (role === "orchestrator" ? ORCHESTRATOR : `${caller.agent}-${caller.sessionID.slice(-6)}`)
        await ensureWorkspace(args.team)
        const member = await registerMember(args.team, {
          name,
          role,
          sessionId: caller.sessionID,
          directory: await directoryOf(caller.sessionID),
          agent: caller.agent,
          state: "working",
        })
        return `Joined team "${args.team}" as "${member.name}" (${member.role}). Session ${member.sessionId}.`
      },
    },
    {
      name: "roster",
      description:
        "Show the team roster: who is in it, state, last progress report, pending user questions, PRs, and whether each session is busy or idle right now.",
      input: object({ team: str(), live: { type: "boolean", description: "Kept for compatibility; live status is always shown" } }),
      async execute(args: any, caller: Caller) {
        return sessions.rosterTable(await resolveTeam(args.team, caller.sessionID))
      },
    },
    {
      name: "send",
      description:
        "Send a message to another session in the team (a player, or the orchestrator). It lands in their chat as a user message with a reply hint. Use it to hand over decisions, flag things that affect them, ask for something, or report completion. to='all' broadcasts. to='user' shows a desktop notification for the human.",
      input: object(
        {
          to: str(`Member name, '${ORCHESTRATOR}', 'all' or 'user'`),
          message: str("Self-contained message: facts, what you need, deadline if any"),
          kind: { type: "string", enum: [...KINDS], description: "info (default) | question | blocker | decision | done | urgent" },
          team: str(),
        },
        ["to", "message"],
      ),
      async execute(args: any, caller: Caller) {
        const from = await sender(caller)
        return send(args, { sessionID: caller.sessionID, name: from.name, role: from.role })
      },
    },
    {
      name: "report",
      description:
        "Publish THIS session's status to the roster so the orchestrator sees it without asking: call at milestones and whenever you start waiting. Use state=waiting_user when you asked the user something (put it in `question`), blocked when something outside your control stops you, review when PRs wait for reviewers, done when finished and everything is pushed.",
      input: object(
        {
          state: { type: "string", enum: [...STATES] },
          progress: str("One or two sentences: done, next, blockers"),
          question: str("With waiting_user: the exact question the user must answer"),
          prs: { type: "array", items: { type: "string" }, description: "PR URLs you own" },
          team: str(),
        },
        ["state", "progress"],
      ),
      async execute(args: any, caller: Caller) {
        const team = await resolveTeam(args.team, caller.sessionID)
        const found = await findBySession(caller.sessionID)
        if (!found) throw new Error("This session is not in the roster: call team_join first.")
        const patch: Partial<Member> = {
          state: args.state,
          progress: args.progress,
          question: args.state === "waiting_user" ? args.question : undefined,
        }
        if (args.prs?.length) patch.prs = Array.from(new Set([...(found.member.prs ?? []), ...args.prs]))
        await updateMember(team, found.member.name, patch)
        if (args.state === "waiting_user" || args.state === "blocked") {
          notify(`${team}: ${found.member.name} ${args.state === "blocked" ? "is blocked" : "needs you"}`, args.question || args.progress)
        }
        await logMessage(team, { from: found.member.name, to: "roster", kind: "report", state: args.state, text: args.progress })
        let note = ""
        if ((args.state === "done" || args.state === "blocked") && found.member.role !== "orchestrator") {
          const orchestrator = Object.values((await readRoster(team)).members).find((member) => member.role === "orchestrator")
          if (orchestrator) {
            try {
              const kind = args.state === "done" ? "done" : "blocker"
              await fileToOrchestrator(team, orchestrator.name, found.member.name, kind, `${args.progress}${args.prs?.length ? ` PRs: ${args.prs.join(" ")}` : ""}`)
              scheduleFlush(sessions, team, 4000)
              note = " The orchestrator is woken automatically; do not send a separate message."
            } catch (error) {
              note = ` (${String((error as Error).message).slice(0, 160)})`
            }
          }
        }
        return `Reported ${args.state}.${note}`
      },
    },
    {
      name: "spawn",
      description:
        "Orchestrator only. Create a new player session in a directory (usually a git worktree you created), register it, and send it its brief. The session uses the `player` agent, is titled with the given title, and gets the team protocol, the team's shared rules (team_common) and your brief. Returns the session id.",
      input: object(
        {
          team: str(),
          name: str("Short unique member name, e.g. SP-11442-api"),
          directory: str("Absolute directory the session works in (a worktree)"),
          title: str("Session title, e.g. '__PROPOSALS [SP-11442] Requirements'"),
          brief: str("The task: ticket, scope, ownership boundaries, acceptance, what to ask the user"),
          model: str("provider/model[#variant]; omit to inherit the default. Use a cheaper model only for trivial, mechanical work"),
          role: str(),
          agent: str("Default 'player'"),
        },
        ["team", "name", "directory", "title", "brief"],
      ),
      async execute(args: any) {
        return spawnText(args)
      },
    },
    {
      name: "inspect",
      description:
        "Orchestrator: look into a member's session without waiting for its report: busy/idle, its last message, any question it is waiting on, recent tools. Use when a player is silent or before routing a decision.",
      input: object({ name: str(), team: str(), max_chars: { type: "number" } }, ["name"]),
      async execute(args: any, caller: Caller) {
        return inspectText(args, caller.sessionID)
      },
    },
    {
      name: "common",
      description:
        "Get or set the team's shared rules that every spawned player receives in its brief (git/PR conventions, screenshot rules, ownership). Call without `text` to read.",
      input: object({ team: str(), text: str("New rules text; replaces the old one") }, ["team"]),
      async execute(args: any) {
        return common(args)
      },
    },
    {
      name: "inbox",
      description:
        "Orchestrator: read and clear your inbox. Wake-kind messages (question, blocker, urgent, done) are also pushed to you in a batched digest when you are idle; info and decision messages from players only wait here. Check it at the start of each monitoring round and before you end a turn.",
      input: object({ team: str() }),
      async execute(args: any, caller: Caller) {
        const team = await resolveTeam(args.team, caller.sessionID)
        const found = await findBySession(caller.sessionID)
        if (!found) throw new Error("This session is not in the roster: call team_join first.")
        const items = await takeInbox(team, found.member.name)
        return items.length
          ? items.map((item) => `${item.at.slice(11, 19)} from ${item.from} [${item.kind}${item.wake ? "" : ", quiet"}]: ${item.text}`).join("\n\n")
          : "Inbox empty."
      },
    },
    {
      name: "handoff",
      description:
        "Orchestrator only. Hand the orchestrator role to a fresh session: writes a handoff file (your notes + roster + unread inbox + shared rules + recent log), retires your roster entry, spawns the successor as 'orchestrator' with a proper orchestrator brief (not the player brief), and keeps your unread inbox for it. Put your JUDGMENT in `notes`: user preferences, durable decisions not yet in team_common, who owns what and why, open questions waiting on the user, risks, what to do first. Facts the tool can read itself (roster, inbox, rules, log) do not need repeating. After it returns, stop coordinating.",
      input: object(
        {
          team: str(),
          notes: str("Your judgment for the successor, several paragraphs: preferences, decisions, ownership, open questions, risks, first steps"),
          model: str("provider/model[#variant]; defaults to your own model"),
          title: str("Session title for the successor"),
          directory: str("Directory for the successor; defaults to yours"),
          name: str("Member name for the successor; keep the default 'orchestrator' so players keep addressing it"),
        },
        ["notes"],
      ),
      async execute(args: any, caller: Caller) {
        return handoff(args, caller)
      },
    },
    {
      name: "resource",
      description:
        "Register, list or remove something this team created that must be cleaned up when it closes. kind=worktree or branch (git, abs paths; worktrees spawned by team_spawn are registered automatically); database, docker, process, dir or other need `cleanup`, the exact command that removes it (never run by the plugin). Register what you create OUTSIDE the repos: a database, a container project, a local-only branch, a temp directory, a dev server. disposable=true marks a local-only worktree or branch that may be removed even with uncommitted or unpushed work (glue branches). Removing an entry only edits the manifest.",
      input: object(
        {
          team: str(),
          action: str("add | list | remove (default list)"),
          kind: str("worktree | branch | database | docker | process | dir | other"),
          ref: str("Absolute path, branch name, database name or project name"),
          repo: str("Absolute path of the repository (required for local branches)"),
          cleanup: str("Exact command that removes it (required for kinds other than worktree and branch)"),
          note: str("What it is and why it exists"),
          disposable: { type: "boolean", description: "Safe to lose even with local-only or uncommitted work" },
        },
        [],
      ),
      async execute(args: any, caller: Caller) {
        return resource(args, caller)
      },
    },
    {
      name: "close",
      description:
        "Orchestrator only. Close the team and clean up. Default is a DRY RUN: it inspects every registered worktree and local branch (uncommitted files, unpushed commits), lists databases, containers, directories and processes with their cleanup commands, and shows the team space size. Show that report to the user and get an explicit yes before calling again with confirm=true. Confirm removes only worktrees and local branches that are clean and already on a remote (or marked disposable), leaves blocked ones in place, retires all members and moves the team folder to the closed archive. Remote branches, PRs, sessions and anything outside the manifest are never touched. force=true only overrides the 'members still running' check.",
      input: object(
        {
          team: str(),
          confirm: { type: "boolean", description: "Actually remove the safe items and close (only after the user said yes)" },
          force: { type: "boolean", description: "Close even though some member sessions are still running" },
          include_discovered: { type: "boolean", description: "Also treat worktrees found via the roster but never registered as removable (default: leave them alone)" },
        },
        [],
      ),
      async execute(args: any, caller: Caller) {
        return closeTeam(args, caller)
      },
    },
    {
      name: "log",
      description: "Orchestrator: read the most recent team messages and reports (who told whom what).",
      input: object({ team: str(), limit: { type: "number" } }),
      async execute(args: any, caller: Caller) {
        return log(args, caller.sessionID)
      },
    },
  ]

  return { tools, send, inspectText, common, log, spawnText, handoff, resource, closeTeam }
}
