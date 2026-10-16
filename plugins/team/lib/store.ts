// File-backed team state: roster, message log, shared rules and the orchestrator inbox.
// Kept on disk (not in plugin storage) so the `team` CLI and every plugin instance see the same state.
import { mkdir, readFile, writeFile, rename, readdir, appendFile, rm } from "node:fs/promises"
import path from "node:path"
import os from "node:os"

export const TEAM_HOME = process.env.TEAM_HOME || path.join(os.homedir(), ".local", "share", "opencode-team")
export const ORCHESTRATOR = "orchestrator"

export type MemberState = "starting" | "working" | "idle" | "blocked" | "waiting_user" | "review" | "done" | "error" | "retired"

export type Member = {
  name: string
  role: string
  sessionId: string
  directory: string
  // V1 rosters recorded the server each member lived on. V2 runs every session in one service, so it is unused.
  serverUrl?: string
  agent?: string
  model?: string
  title?: string
  state: MemberState
  progress?: string
  question?: string
  prs?: string[]
  joinedAt: string
  updatedAt: string
  lastIdleAt?: string
}

export type Roster = { team: string; members: Record<string, Member> }

const safe = (value: string) => value.replace(/[^A-Za-z0-9._-]/g, "_")
export const teamDir = (team: string) => path.join(TEAM_HOME, safe(team))
const rosterFile = (team: string) => path.join(teamDir(team), "roster.json")
const logFile = (team: string) => path.join(teamDir(team), "messages.jsonl")
const commonFile = (team: string) => path.join(teamDir(team), "common.md")
const inboxFile = (team: string) => path.join(teamDir(team), "inbox.json")
export const handoffDir = (team: string) => path.join(teamDir(team), "handoffs")
export const workspaceDir = (team: string) => path.join(teamDir(team), "workspace")
export const closedHome = () => path.join(TEAM_HOME, "_closed")
const resourcesFile = (team: string) => path.join(teamDir(team), "resources.json")

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))
export const now = () => new Date().toISOString()

export async function withLock<T>(team: string, fn: () => Promise<T>): Promise<T> {
  await mkdir(teamDir(team), { recursive: true })
  const lock = path.join(teamDir(team), ".lock")
  const deadline = Date.now() + 8000
  for (;;) {
    try {
      await mkdir(lock)
      break
    } catch {
      if (Date.now() > deadline) {
        await rm(lock, { recursive: true, force: true })
        continue
      }
      await sleep(25 + Math.random() * 50)
    }
  }
  try {
    return await fn()
  } finally {
    await rm(lock, { recursive: true, force: true })
  }
}

export async function readRoster(team: string): Promise<Roster> {
  try {
    return JSON.parse(await readFile(rosterFile(team), "utf8"))
  } catch {
    return { team, members: {} }
  }
}

async function writeRoster(roster: Roster) {
  const file = rosterFile(roster.team)
  const tmp = `${file}.${process.pid}.tmp`
  await writeFile(tmp, JSON.stringify(roster, null, 2))
  await rename(tmp, file)
}

export async function mutateRoster<T>(team: string, fn: (roster: Roster) => T | Promise<T>): Promise<T> {
  return withLock(team, async () => {
    const roster = await readRoster(team)
    const result = await fn(roster)
    await writeRoster(roster)
    return result
  })
}

export async function listTeams(): Promise<string[]> {
  try {
    const entries = await readdir(TEAM_HOME, { withFileTypes: true })
    return entries.filter((entry) => entry.isDirectory() && !entry.name.startsWith("_")).map((entry) => entry.name)
  } catch {
    return []
  }
}

export async function findBySession(sessionId: string): Promise<{ team: string; member: Member } | null> {
  for (const team of await listTeams()) {
    const roster = await readRoster(team)
    const member = Object.values(roster.members).find((candidate) => candidate.sessionId === sessionId)
    if (member) return { team, member }
  }
  return null
}

export async function resolveTeam(explicit: string | undefined, sessionId: string | undefined): Promise<string> {
  if (explicit) return explicit
  const found = sessionId ? await findBySession(sessionId) : null
  if (found) return found.team
  const teams = await listTeams()
  if (teams.length === 1) return teams[0]
  throw new Error(
    teams.length
      ? `Several teams exist (${teams.join(", ")}); pass \`team\` explicitly.`
      : "No team exists yet: the orchestrator creates one with team_join or team_spawn.",
  )
}

export function findTarget(members: Member[], wanted: string): Member {
  const needle = wanted.trim().toLowerCase()
  const exact = members.find((member) => member.name.toLowerCase() === needle)
  if (exact) return exact
  const partial = members.filter((member) => member.name.toLowerCase().includes(needle))
  if (partial.length === 1) return partial[0]
  const names = members.map((member) => member.name).join(", ")
  throw new Error(
    partial.length
      ? `'${wanted}' is ambiguous (${partial.map((member) => member.name).join(", ")}).`
      : `No member '${wanted}'. Members: ${names || "(none)"}.`,
  )
}

export async function registerMember(
  team: string,
  input: Partial<Member> & { name: string; sessionId: string; directory: string },
): Promise<Member> {
  return mutateRoster(team, (roster) => {
    const existing = roster.members[input.name]
    const member: Member = {
      role: "player",
      state: "working",
      joinedAt: now(),
      ...existing,
      ...input,
      updatedAt: now(),
    }
    roster.members[input.name] = member
    return member
  })
}

export async function updateMember(team: string, name: string, patch: Partial<Member>): Promise<Member> {
  return mutateRoster(team, (roster) => {
    const member = roster.members[name]
    if (!member) throw new Error(`No member '${name}' in team '${team}'`)
    Object.assign(member, patch, { updatedAt: now() })
    return member
  })
}

export async function patchBySession(sessionId: string, patch: Partial<Member>) {
  const found = await findBySession(sessionId)
  if (!found) return
  await updateMember(found.team, found.member.name, patch)
}

export async function orchestratorOf(team: string): Promise<Member | undefined> {
  const roster = await readRoster(team)
  return Object.values(roster.members).find((member) => member.role === "orchestrator")
}

export async function logMessage(team: string, entry: Record<string, unknown>) {
  await mkdir(teamDir(team), { recursive: true })
  await appendFile(logFile(team), JSON.stringify({ at: now(), ...entry }) + "\n")
}

export async function readLog(team: string, limit = 40): Promise<Record<string, unknown>[]> {
  try {
    const lines = (await readFile(logFile(team), "utf8")).trim().split("\n").filter(Boolean)
    return lines.slice(-limit).map((line) => JSON.parse(line))
  } catch {
    return []
  }
}

export async function getCommon(team: string): Promise<string> {
  try {
    return await readFile(commonFile(team), "utf8")
  } catch {
    return ""
  }
}

export async function setCommon(team: string, text: string) {
  await mkdir(teamDir(team), { recursive: true })
  await writeFile(commonFile(team), text)
}

export type InboxItem = {
  id: string
  at: string
  from: string
  to: string
  kind: string
  text: string
  wake: boolean
  surfaced: boolean
  read: boolean
}

export const WAKE_KINDS = new Set(["question", "blocker", "done", "urgent"])
const WAKE_LIMIT = 5
const PAIR_LIMIT = 8
const WINDOW_MS = 10 * 60 * 1000

async function readInbox(team: string): Promise<InboxItem[]> {
  try {
    return JSON.parse(await readFile(inboxFile(team), "utf8"))
  } catch {
    return []
  }
}

export async function mutateInbox<T>(team: string, fn: (items: InboxItem[]) => T): Promise<T> {
  return withLock(team, async () => {
    const items = await readInbox(team)
    const result = fn(items)
    await writeFile(inboxFile(team), JSON.stringify(items.slice(-300), null, 2))
    return result
  })
}

export async function fileToOrchestrator(team: string, to: string, from: string, kind: string, text: string): Promise<boolean> {
  const wake = WAKE_KINDS.has(kind)
  await mutateInbox(team, (items) => {
    const recent = items.filter((item) => item.from === from && item.to === to && Date.now() - Date.parse(item.at) < WINDOW_MS)
    if (recent.some((item) => item.text === text)) return
    if (wake && recent.filter((item) => item.wake).length >= WAKE_LIMIT) {
      throw new Error(
        `Rate limit: you already woke the orchestrator ${WAKE_LIMIT} times in 10 minutes. Consolidate into one message, use team_report for status, or use kind=info (no wake).`,
      )
    }
    items.push({ id: Math.random().toString(36).slice(2, 8), at: now(), from, to, kind, text, wake, surfaced: false, read: false })
  })
  return wake
}

const FANOUT_LIMIT = 3
const FANOUT_WINDOW_MS = 5 * 60 * 1000

export async function fanoutCheck(team: string, from: string, text: string) {
  const entries = await readLog(team, 300)
  const seen = new Set(
    entries
      .filter((entry: any) => entry.from === from && entry.text === text && Date.now() - Date.parse(entry.at) < FANOUT_WINDOW_MS)
      .map((entry: any) => entry.to),
  )
  if (seen.size >= FANOUT_LIMIT) {
    throw new Error(
      `Fan-out limit: this message already went to ${seen.size} members in 5 minutes. Players do not broadcast: put status in team_report (and the team's status file), and message only the members who must act.`,
    )
  }
}

export async function pairLimitCheck(team: string, from: string, to: string) {
  const entries = await readLog(team, 200)
  const count = entries.filter((entry: any) => entry.from === from && entry.to === to && Date.now() - Date.parse(entry.at) < WINDOW_MS).length
  if (count >= PAIR_LIMIT) {
    throw new Error(`Rate limit: ${count} messages from you to ${to} in 10 minutes. Stop and consolidate: one message with everything they need, or wait for their answer.`)
  }
}

export async function takeInbox(team: string, name: string): Promise<InboxItem[]> {
  return mutateInbox(team, (items) => {
    const mine = items.filter((item) => item.to === name && !item.read)
    for (const item of mine) {
      item.read = true
      item.surfaced = true
    }
    return mine
  })
}

export async function inboxCounts(team: string, name: string): Promise<{ wake: number; quiet: number }> {
  const items = (await readInbox(team)).filter((item) => item.to === name && !item.read)
  return { wake: items.filter((item) => item.wake).length, quiet: items.filter((item) => !item.wake).length }
}

export async function peekInbox(team: string, name: string): Promise<InboxItem[]> {
  return (await readInbox(team)).filter((item) => item.to === name && !item.read)
}

export async function renameMember(team: string, from: string, to: string, patch: Partial<Member>): Promise<void> {
  await mutateRoster(team, (roster) => {
    const member = roster.members[from]
    if (!member) throw new Error(`No member '${from}' in team '${team}'`)
    if (roster.members[to]) throw new Error(`Member '${to}' already exists in team '${team}'`)
    delete roster.members[from]
    roster.members[to] = { ...member, ...patch, name: to, updatedAt: now() }
  })
}

export async function ensureWorkspace(team: string): Promise<string> {
  const dir = workspaceDir(team)
  await mkdir(dir, { recursive: true })
  return dir
}

export type Resource = {
  id: string
  kind: string
  ref: string
  repo?: string
  cleanup?: string
  note?: string
  owner?: string
  disposable?: boolean
  createdAt: string
}

export async function readResources(team: string): Promise<Resource[]> {
  try {
    return JSON.parse(await readFile(resourcesFile(team), "utf8"))
  } catch {
    return []
  }
}

export async function addResource(team: string, input: Omit<Resource, "id" | "createdAt">): Promise<Resource> {
  return withLock(team, async () => {
    const items = await readResources(team)
    const existing = items.find((item) => item.kind === input.kind && item.ref === input.ref)
    if (existing) {
      Object.assign(existing, Object.fromEntries(Object.entries(input).filter(([, value]) => value !== undefined)))
      await writeFile(resourcesFile(team), JSON.stringify(items, null, 2))
      return existing
    }
    const item: Resource = { id: Math.random().toString(36).slice(2, 8), createdAt: now(), ...input }
    items.push(item)
    await writeFile(resourcesFile(team), JSON.stringify(items, null, 2))
    return item
  })
}

export async function removeResource(team: string, idOrRef: string): Promise<boolean> {
  return withLock(team, async () => {
    const items = await readResources(team)
    const next = items.filter((item) => item.id !== idOrRef && item.ref !== idOrRef)
    if (next.length === items.length) return false
    await writeFile(resourcesFile(team), JSON.stringify(next, null, 2))
    return true
  })
}
