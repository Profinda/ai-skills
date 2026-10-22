// Session notes model: what a session is for and where it stands. Stored in this plugin's own storage, keyed
// by session ID, instead of per-worktree files. (Session metadata would be the natural home, but in 2.0.20
// ctx.session.update drops `metadata` when called from a plugin, while `title` goes through.)
import { readFile, readdir, stat, unlink } from "node:fs/promises"
import { execFile } from "node:child_process"
import path from "node:path"

export const storageKey = (sessionID: string) => `notes/${sessionID}`
// Where V1 kept notes. Still read (once per session) so notes written before the upgrade are not lost.
export const LEGACY_DIR = path.join(".opencode", "session-notes")
export const JIRA_BASE_URL = "https://profinda.atlassian.net/browse/"

export type Notes = {
  worktree: string
  branch: string
  intent: string
  jiraEpic: string
  jiraTicket: string
  title: string
  prUrls: string[]
  localUrl: string
  progress: string
  updatedAt: string
}

export function jiraLink(ticket: string): string {
  return ticket ? `[${ticket}](${JIRA_BASE_URL}${encodeURIComponent(ticket)})` : ""
}

function prNumberFromUrl(url: string): string | null {
  const match = url.match(/\/(?:pull|pull-requests|merge_requests)\/(\d+)/)
  return match ? match[1] : null
}

export function prLink(url: string): string {
  const number = prNumberFromUrl(url)
  return `[${number ? `PR#${number}` : "PR"}](${url})`
}

export function asString(value: unknown): string | undefined {
  return typeof value === "string" ? value : undefined
}

// A session can span more than one PR (follow-ups, split work, etc.) — always accumulate rather than
// overwrite, so a later call reporting PR #2 doesn't erase the note's memory of PR #1. Also accepts older
// single-`prUrl` shaped notes.
export function mergePrUrls(existing: Record<string, unknown> | null, incoming: string | undefined): string[] {
  const prior = Array.isArray(existing?.prUrls)
    ? (existing!.prUrls as unknown[]).filter((u): u is string => typeof u === "string")
    : typeof existing?.prUrl === "string" && existing.prUrl
      ? [existing.prUrl as string]
      : []
  const next = incoming ? [...prior, incoming] : prior
  return Array.from(new Set(next.map((u) => u.trim()).filter(Boolean)))
}

export function isUsableDirectory(candidate: string | undefined): candidate is string {
  if (!candidate) return false
  const normalized = path.resolve(candidate)
  return normalized !== path.parse(normalized).root
}

// Prefer the agent's explicit working directory (often a git worktree it created), then the session's own
// directory, and fail loudly instead of running git against "/".
export function resolveWorktree(explicit: string | undefined, sessionDirectory: string | undefined): string {
  if (isUsableDirectory(explicit)) return explicit
  if (isUsableDirectory(sessionDirectory)) return sessionDirectory
  const got = explicit || sessionDirectory || "(empty)"
  throw new Error(
    `Could not resolve a usable project directory (got '${got}'). Pass \`worktree\` explicitly with the actual ` +
      "project directory path — run `pwd` to confirm it. If this session genuinely has no working directory, tell " +
      "the user directly rather than retrying silently.",
  )
}

export function currentBranch(worktree: string): Promise<string> {
  return new Promise((resolve) => {
    execFile("git", ["-C", worktree, "branch", "--show-current"], (error, stdout) => resolve(error ? "" : String(stdout).trim()))
  })
}

export async function readLegacyNotes(directory: string | undefined, sessionID: string): Promise<Record<string, unknown> | null> {
  if (!isUsableDirectory(directory)) return null
  try {
    return JSON.parse(await readFile(path.join(directory, LEGACY_DIR, `${sessionID}.json`), "utf8"))
  } catch {
    return null
  }
}

export type SetArgs = {
  worktree?: string
  intent?: string
  jiraEpic?: string
  jiraTicket?: string
  prUrl?: string
  localUrl?: string
  progress: string
  title?: string
  type?: "Question" | "Investigation" | "Code"
  done?: boolean
}

// Everything except `progress` is "preserve unless explicitly changed": an omitted (undefined) argument keeps
// what was saved, while an explicit "" clears it.
//
// `jiraTicket` deliberately prefers the EXISTING recorded value over a freshly re-derived branch match. Branch
// detection reads whatever `worktree` resolves to for THIS call, and a shared/primary checkout can be sitting on
// another task's branch; trusting that reading is how one session's notes got overwritten with another
// session's ticket. The branch match only seeds the ticket the first time; after that, only an explicit
// `jiraTicket` changes it.
export function mergeNotes(existing: Record<string, unknown> | null, args: SetArgs, worktree: string, branch: string) {
  const branchTicket = branch.match(/[A-Z]{2,}-\d+/)?.[0]
  const existingTicket = asString(existing?.jiraTicket)
  const jiraTicket = args.jiraTicket ?? existingTicket ?? branchTicket ?? ""
  const ticketMismatch = Boolean(existingTicket && branchTicket && branchTicket !== existingTicket && !args.jiraTicket)
  // The model supplies the plain description; the `[DONE SP-123 Code]` tag matches the /ticket and /done
  // conventions. Without a new title, keep the already-formatted one.
  const tags = [args.done ? "DONE" : "", jiraTicket, args.type ?? "Code"].filter(Boolean)
  const title = args.title ? `[${tags.join(" ")}] ${args.title}` : (asString(existing?.title) ?? "")

  const notes: Notes = {
    worktree,
    branch,
    intent: args.intent ?? asString(existing?.intent) ?? "",
    jiraEpic: args.jiraEpic ?? asString(existing?.jiraEpic) ?? "",
    jiraTicket,
    title,
    prUrls: mergePrUrls(existing, args.prUrl),
    localUrl: args.localUrl ?? asString(existing?.localUrl) ?? "",
    progress: args.progress,
    updatedAt: new Date().toISOString(),
  }
  return { notes, ticketMismatch, branchTicket, existingTicket }
}

export async function cleanupLegacy(worktree: string, days: number): Promise<string[] | null> {
  const dir = path.join(worktree, LEGACY_DIR)
  let entries: string[]
  try {
    entries = await readdir(dir)
  } catch {
    return null
  }
  const cutoff = Date.now() - days * 24 * 60 * 60 * 1000
  const deleted: string[] = []
  for (const entry of entries) {
    if (!entry.endsWith(".json")) continue
    const filePath = path.join(dir, entry)
    const info = await stat(filePath)
    if (info.mtimeMs < cutoff) {
      await unlink(filePath)
      deleted.push(entry)
    }
  }
  return deleted
}

// A person's edit from the terminal UI: change only the given fields. worktree and branch stay as the agent
// reported them (they come from git in the directory the agent worked in).
export type Edit = {
  intent?: string
  progress?: string
  jiraEpic?: string
  jiraTicket?: string
  title?: string
  localUrl?: string
  addPr?: string
  removePr?: string
}

export function applyEdit(existing: Record<string, unknown> | null, edit: Edit): Notes {
  const keep = (key: keyof Notes) => asString(existing?.[key]) ?? ""
  const prUrls = mergePrUrls(existing, edit.addPr).filter((url) => url !== edit.removePr?.trim())
  return {
    worktree: keep("worktree"),
    branch: keep("branch"),
    intent: edit.intent ?? keep("intent"),
    jiraEpic: edit.jiraEpic ?? keep("jiraEpic"),
    jiraTicket: edit.jiraTicket ?? keep("jiraTicket"),
    title: edit.title ?? keep("title"),
    prUrls,
    localUrl: edit.localUrl ?? keep("localUrl"),
    progress: edit.progress ?? keep("progress"),
    updatedAt: new Date().toISOString(),
  }
}
