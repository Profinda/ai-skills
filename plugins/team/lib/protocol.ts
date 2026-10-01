// Text conventions shared by every team member: message envelopes, the player brief, desktop notifications.
import { execFile } from "node:child_process"
import { ORCHESTRATOR } from "./store.ts"

export const STATES = ["working", "blocked", "waiting_user", "review", "done", "idle"] as const
export const KINDS = ["info", "question", "blocker", "decision", "done", "urgent"] as const

export function parseModel(model?: string): { providerID: string; id: string; variant?: string } | undefined {
  if (!model) return undefined
  const slash = model.indexOf("/")
  if (slash < 1) throw new Error(`Model must look like provider/model[#variant], got '${model}'`)
  const [id, variant] = model.slice(slash + 1).split("#")
  return { providerID: model.slice(0, slash), id, ...(variant ? { variant } : {}) }
}

export function notify(title: string, message: string) {
  if (process.env.TEAM_NOTIFY === "0" || process.platform !== "darwin") return
  const clean = (value: string) => value.replace(/["\\]/g, "'").slice(0, 180)
  execFile("osascript", ["-e", `display notification "${clean(message)}" with title "${clean(title)}"`], () => {})
}

export function envelope(input: {
  team: string
  fromName: string
  fromRole: string
  kind: string
  text: string
  replyTo: string
}): string {
  const header = `[team:${input.team}] from ${input.fromName} (${input.fromRole}) kind=${input.kind}`
  const footer =
    `--\nThis arrived through the team channel. The sender cannot see your chat: answer with ` +
    `team_send(to="${input.replyTo}", ...) when an answer is needed, and do not reply just to acknowledge.`
  return `${header}\n\n${input.text}\n\n${footer}`
}

const workspaceNote = (workspace?: string) =>
  workspace
    ? `\nTEAM WORKSPACE: ${workspace}\nShared team files go there (status files, scripts, screenshots, QA output, handoffs): not in the repos. Anything you create OUTSIDE the repos that someone must clean up when the team closes (a database, a container project, a branch that exists only locally, a temp directory, a dev server) is registered with team_resource(action="add", ...), with the command that removes it. Worktrees spawned for you are registered automatically.\n`
    : ""

export function orchestratorBrief(input: { team: string; name: string; title: string; common: string; brief: string; workspace?: string }): string {
  const header =
    `You are "${input.name}", the ORCHESTRATOR of the team "${input.team}". You are taking over the role from the previous orchestrator session. ` +
    `Your session title is "${input.title}". You are not a player: your agent prompt defines the role.\n\n` +
    `TEAM PROTOCOL (tools team_*): players reach you with team_send and team_report. Only question, blocker and urgent sends and done/blocked reports wake you (batched, when you are idle); info and decision messages wait in team_inbox. ` +
    `Everything unread for the role is preserved for you. Read the roster for status, team_inbox for asks, and answer players with team_send. Do not broadcast status and do not acknowledge messages.\n`
  const common = input.common.trim() ? `\nTEAM RULES (already in force for every player):\n${input.common.trim()}\n` : ""
  return `${header}${workspaceNote(input.workspace)}${common}\nHANDOFF:\n${input.brief.trim()}`
}

export function standardBrief(input: { team: string; name: string; title: string; common: string; brief: string; role?: string; workspace?: string }): string {
  if (input.role === "orchestrator") return orchestratorBrief(input)
  const header =
    `You are "${input.name}", a player in the team "${input.team}", coordinated by the orchestrator session. ` +
    `Your session title is "${input.title}".\n\n` +
    `TEAM PROTOCOL (tools team_*):\n` +
    `- team_roster lists the other players and their status.\n` +
    `- team_report(state, progress, ...) at every milestone and whenever you start waiting: states working | blocked | waiting_user | review | done. Use waiting_user whenever you ask the user a question, and put the question in \`question\`.\n` +
    `- team_send(to, message, kind) to talk to the orchestrator ("${ORCHESTRATOR}") or to another player directly. Kinds: info | question | blocker | decision | urgent | done. The orchestrator's context is precious: only question, blocker and urgent wake it (batched); info and decision are filed quietly in its inbox. Wake it only when you truly need its judgment or a decision you cannot get elsewhere; status belongs in team_report, which never wakes anyone. Finishing or blocking via team_report(state=done|blocked) wakes it automatically, so do not also send a message. Consolidate: one complete message beats several small ones, and never acknowledge or ping-pong (rate limits apply).\n` +
    `- Messages from others arrive in this chat as "[team:${input.team}] from <name> ...": act on them, and reply with team_send only when an answer is needed.\n` +
    `- The user can also talk to you directly in this session; their word wins over team messages.\n`
  const common = input.common.trim() ? `\nTEAM RULES:\n${input.common.trim()}\n` : ""
  return `${header}${workspaceNote(input.workspace)}${common}\nYOUR TASK:\n${input.brief.trim()}`
}

export function age(iso?: string): string {
  if (!iso) return "-"
  const seconds = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 1000))
  if (seconds < 90) return `${seconds}s`
  if (seconds < 5400) return `${Math.round(seconds / 60)}m`
  return `${Math.round(seconds / 3600)}h`
}
