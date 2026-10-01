// Session operations for the team, done through the V2 plugin context instead of V1 HTTP calls.
import { ORCHESTRATOR, addResource, ensureWorkspace, getCommon, inboxCounts, logMessage, mutateInbox, orchestratorOf, readRoster, registerMember, workspaceDir, type Member } from "./store.ts"
import { linkedWorktreeRepo } from "./close.ts"
import { age, parseModel, standardBrief } from "./protocol.ts"

// Busy/idle per session, fed by session.execution.* events (see events.ts). Kept on globalThis so every
// plugin instance (one per location) and every reload shares one view.
type Activity = { busy: boolean; at: number; outcome?: string }
const ACTIVITY = Symbol.for("workbench.team.activity")
export const activity: Map<string, Activity> = ((globalThis as any)[ACTIVITY] ??= new Map())

export type Live = { busy: boolean | null; since?: number; outcome?: string }

export function live(member: Member): Live {
  const entry = activity.get(member.sessionId)
  return entry ? { busy: entry.busy, since: entry.at, outcome: entry.outcome } : { busy: null }
}

const runLabel = (info: Live) => (info.busy === null ? "?" : info.busy ? "busy" : "idle")

export function createTeamSessions(ctx: any) {
  async function deliver(target: Member, text: string, options: { urgent?: boolean } = {}) {
    // "queue" waits for the target's current turn to finish (like V1 prompt_async); "steer" lands mid-turn.
    await ctx.session.prompt({ sessionID: target.sessionId, text, delivery: options.urgent ? "steer" : "queue" })
  }

  async function inspect(member: Member, maxChars = 2500) {
    const messages: any[] = await ctx.session.context({ sessionID: member.sessionId })
    const assistants = messages.filter((message) => message.type === "assistant")
    const last = assistants[assistants.length - 1]
    const out: { lastText: string; pendingQuestion?: string; lastTools: string[]; lastUser?: string; messages: number; error?: string } = {
      lastText: "",
      lastTools: [],
      messages: messages.length,
    }
    if (last) {
      const content: any[] = Array.isArray(last.content) ? last.content : []
      out.lastText = content
        .filter((item) => item.type === "text")
        .map((item) => item.text)
        .join("\n")
        .slice(0, maxChars)
      const tools = content.filter((item) => item.type === "tool")
      out.lastTools = tools.slice(-4).map((item) => `${item.name}:${item.state?.status}`)
      const question = tools.find((item) => item.name === "question" && ["pending", "running"].includes(item.state?.status))
      if (question) {
        out.pendingQuestion = (question.state.input?.questions ?? [])
          .map((entry: any) => `${entry.question}${entry.options ? " [" + entry.options.map((option: any) => option.label).join(" | ") + "]" : ""}`)
          .join("\n")
          .slice(0, 1500)
      }
      if (last.error) out.error = last.error.type ?? last.error.name ?? String(last.error.message ?? "error")
    }
    const users = messages.filter((message) => message.type === "user")
    out.lastUser = users[users.length - 1]?.text?.slice(0, 300)
    return out
  }

  async function spawn(input: {
    team: string
    name: string
    role?: string
    directory: string
    title: string
    brief: string
    model?: string
    agent?: string
  }): Promise<Member> {
    const agent = input.agent || "player"
    const model = parseModel(input.model)
    const session = await ctx.session.create({
      title: input.title,
      agent,
      ...(model ? { model } : {}),
      location: { directory: input.directory },
    })
    const member = await registerMember(input.team, {
      name: input.name,
      role: input.role || "player",
      sessionId: session.id,
      directory: input.directory,
      agent,
      model: input.model,
      title: input.title,
      state: "starting",
    })
    const workspace = await ensureWorkspace(input.team)
    const repo = await linkedWorktreeRepo(input.directory)
    if (repo) await addResource(input.team, { kind: "worktree", ref: input.directory, repo, owner: input.name, note: "registered at spawn" })
    const common = await getCommon(input.team)
    const text = standardBrief({ team: input.team, name: input.name, title: input.title, common, brief: input.brief, role: input.role, workspace })
    await ctx.session.prompt({ sessionID: session.id, text })
    await logMessage(input.team, { from: ORCHESTRATOR, to: input.name, kind: "spawn", text: input.brief.slice(0, 500) })
    return member
  }

  async function rosterTable(team: string): Promise<string> {
    const roster = await readRoster(team)
    const members = Object.values(roster.members)
    if (!members.length) return `Team "${team}" has no members yet.`
    const orchestrator = members.find((member) => member.role === "orchestrator")
    const counts = orchestrator ? await inboxCounts(team, orchestrator.name) : undefined
    const lines: string[] = [
      `Team "${team}" (${members.length} members)` +
        (counts && (counts.wake || counts.quiet) ? ` | inbox unread: ${counts.wake} need you, ${counts.quiet} quiet (team_inbox)` : ""),
      `workspace: ${workspaceDir(team)}`,
    ]
    for (const member of members) {
      const info = live(member)
      lines.push(
        `- ${member.name} [${member.role}] state=${member.state} run=${runLabel(info)}${info.outcome && !info.busy ? ` last=${info.outcome}` : ""} updated=${age(member.updatedAt)} ago` +
          `\n    session=${member.sessionId} dir=${member.directory}${member.agent ? ` agent=${member.agent}` : ""}${member.model ? ` model=${member.model}` : ""}` +
          (member.progress ? `\n    progress: ${member.progress}` : "") +
          (member.question ? `\n    QUESTION FOR USER: ${member.question}` : "") +
          (member.prs?.length ? `\n    prs: ${member.prs.join(" ")}` : ""),
      )
    }
    return lines.join("\n")
  }

  const cap = (text: string, max: number) => (text.length > max ? text.slice(0, max) + " [...cut, see team_inbox]" : text)

  async function flushOrchestrator(team: string): Promise<number> {
    const orchestrator = await orchestratorOf(team)
    if (!orchestrator) return 0
    if (live(orchestrator).busy) return 0
    const batch = await mutateInbox(team, (items) => {
      const mine = items.filter((item) => item.to === orchestrator.name)
      const pick = mine.filter((item) => item.wake && !item.surfaced)
      for (const item of pick) item.surfaced = true
      return { pick, quiet: mine.filter((item) => !item.wake && !item.read).length }
    })
    if (!batch.pick.length) return 0
    const lines = batch.pick.map((item) => `- from ${item.from} [${item.kind}]: ${cap(item.text, 900)}`)
    const text =
      `[team:${team}] inbox: ${batch.pick.length} item(s) need you\n\n${lines.join("\n")}\n\n` +
      (batch.quiet ? `(${batch.quiet} quiet info item(s) unread: team_inbox)\n` : "") +
      `--\nAnswer a player with team_send(to=<name>, ...). Do not acknowledge. When several arrive, handle them in one pass.`
    try {
      await deliver(orchestrator, text)
    } catch (error) {
      await mutateInbox(team, (items) => {
        for (const item of items) if (batch.pick.some((picked) => picked.id === item.id)) item.surfaced = false
      })
      throw error
    }
    await logMessage(team, { from: "inbox", to: orchestrator.name, kind: "digest", text: `${batch.pick.length} item(s)` })
    return batch.pick.length
  }

  return { deliver, inspect, spawn, rosterTable, flushOrchestrator, live }
}

export type TeamSessions = ReturnType<typeof createTeamSessions>

// One flush timer per team across all plugin instances.
const TIMERS = Symbol.for("workbench.team.flushTimers")
const timers: Map<string, ReturnType<typeof setTimeout>> = ((globalThis as any)[TIMERS] ??= new Map())

export function scheduleFlush(sessions: TeamSessions, team: string, ms: number) {
  if (timers.has(team)) return
  timers.set(
    team,
    setTimeout(async () => {
      timers.delete(team)
      try {
        await sessions.flushOrchestrator(team)
      } catch {}
    }, ms),
  )
}

export function clearFlushTimers() {
  for (const timer of timers.values()) clearTimeout(timer)
  timers.clear()
}
