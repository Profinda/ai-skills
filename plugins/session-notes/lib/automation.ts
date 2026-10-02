// Keeps notes current without spending model turns: facts are read from finished tool calls and written by code.
// The model is only involved when a person types a bare /session-notes or the agent calls plan_ready itself.
import { applyEdit, currentBranch, isUsableDirectory, storageKey, type Edit } from "./notes.ts"
import { callKey, editFor, factFrom } from "./triggers.ts"

type Loaded = { directory: string | undefined; notes: Record<string, unknown> | null }
type Build = (notes: Record<string, unknown> | null) => Edit | null

// One plugin instance exists per location and each sees the same tool calls, so each call is handled once.
const SEEN = Symbol.for("workbench.session-notes.seenCalls")
const seen: Set<string> = ((globalThis as any)[SEEN] ??= new Set())

function firstSighting(key: string): boolean {
  if (seen.has(key)) return false
  seen.add(key)
  if (seen.size > 2000) {
    const oldest = seen.values().next().value
    if (oldest) seen.delete(oldest)
  }
  return true
}

const refreshPrompt = [
  "Update this session's notes. One `execute` call is enough, no search needed:",
  'return await tools["session-notes"].set({ progress, intent, prUrl, localUrl, jiraTicket, jiraEpic, worktree })',
  "- progress (required): what is done, what is left and the current phase, in one or two sentences.",
  "- intent: only if these notes have none yet or the goal changed.",
  "- prUrl, localUrl, jiraTicket, jiraEpic: only when new and confirmed. Pull requests and Jira tickets you created are already recorded. Never guess a URL.",
  "- worktree: absolute path of the directory you actually worked in. Shell calls do not keep cd, so cd back into your worktree first if you created one.",
  "Answer with the tool output and nothing else.",
].join("\n")

export function createRecorder(ctx: any, load: (sessionID: string) => Promise<Loaded>) {
  const roots = new Map<string, string>()
  const queues = new Map<string, Promise<unknown>>()

  // Subagents (a `developer` opening the PR) report into the session the person is looking at.
  async function rootOf(sessionID: string): Promise<string> {
    const cached = roots.get(sessionID)
    if (cached) return cached
    let current = sessionID
    for (let depth = 0; depth < 5; depth++) {
      const session = await ctx.session.get({ sessionID: current })
      if (!session?.parentID) break
      current = session.parentID
    }
    roots.set(sessionID, current)
    return current
  }

  async function seed(directory: string | undefined) {
    const worktree = isUsableDirectory(directory) ? directory : ""
    const branch = worktree ? await currentBranch(worktree) : ""
    return { worktree, branch, jiraTicket: branch.match(/[A-Z]{2,}-\d+/)?.[0] ?? "" }
  }

  // Serialized per session so a PR and a ticket arriving together cannot overwrite each other.
  function record(sessionID: string, build: Build): Promise<boolean> {
    const run = async () => {
      const root = await rootOf(sessionID)
      const current = await load(root)
      const edit = build(current.notes)
      if (!edit) return false
      const base = current.notes ?? (await seed(current.directory))
      await ctx.storage.set(storageKey(root), applyEdit(base, edit))
      return true
    }
    const previous = queues.get(sessionID) ?? Promise.resolve()
    const next = previous.then(run, run)
    queues.set(sessionID, next.catch(() => {}))
    return next
  }

  return { record }
}

export async function installAutomation(
  ctx: any,
  recorder: ReturnType<typeof createRecorder>,
  cleanup: (args: { olderThanDays?: number }, sessionID: string) => Promise<string>,
) {
  await ctx.tool.hook("execute.after", (event: any) => {
    const fact = factFrom(event)
    if (!fact || !firstSighting(callKey(event))) return
    void recorder.record(event.sessionID, (notes) => editFor(notes, fact)).catch(() => {})
  })

  // Queued in the inbox and shown to the model on its next turn, so only the cleanup result uses it.
  const say = (sessionID: string, text: string) => ctx.session.synthetic({ sessionID, text, resume: false })

  await ctx.command.transform((editor: any) => {
    editor.add({
      name: "session-notes",
      description: "Update this session's notes. With text, saves it as the progress with no model call.",
      async execute({ sessionID, prompt, delivery }: any) {
        const text = String(prompt?.text ?? "").trim()
        if (!text) return void (await ctx.session.prompt({ sessionID, text: refreshPrompt, delivery }))
        await recorder.record(sessionID, (notes) => (notes?.progress === text ? null : { progress: text }))
      },
    })
    editor.add({
      name: "session-notes-cleanup",
      description: "Delete session notes not updated for N days (default 30). Runs without a model call.",
      async execute({ sessionID, prompt }: any) {
        const days = Number.parseInt(String(prompt?.text ?? ""), 10)
        await say(sessionID, await cleanup({ olderThanDays: Number.isFinite(days) && days > 0 ? days : undefined }, sessionID))
      },
    })
  })
}
