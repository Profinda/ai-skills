// Session notes plugin: agents record intent, progress, Jira, PRs and a preview link for their session, and the
// "OpenCode Session Notes" Chrome extension shows them next to the session title in the web UI.
// V2 plugin: a default-exported { id, setup } definition, no runtime dependency on @opencode/plugin.
import { LEGACY_DIR, applyEdit, cleanupLegacy, currentBranch, jiraLink, mergeNotes, prLink, readLegacyNotes, resolveWorktree, storageKey } from "./lib/notes.ts"
import { SessionNotesRpc } from "./rpc.ts"
import { createRecorder, installAutomation } from "./lib/automation.ts"

const str = (description: string) => ({ type: "string", description })

const SET_INPUT = {
  type: "object",
  additionalProperties: false,
  required: ["progress"],
  properties: {
    worktree: str(
      "Always determine and pass the ABSOLUTE PATH of the directory you are ACTUALLY working in right now " +
        "(run `pwd` if unsure) — do not rely on the session's own default working directory, since it's " +
        "frequently a different directory than wherever the session originally started (e.g. a git worktree " +
        "you created yourself via `git worktree add`). This path is echoed back verbatim in the confirmation " +
        "so the user can copy it elsewhere (e.g. to open the codebase in an editor).",
    ),
    intent: str(
      "In your own words: what is this session actually trying to achieve? What triggered it? Set this " +
        "ONCE, early in the session (e.g. right after understanding the initial request) — it should stay " +
        "stable even as the work progresses, so returning to this session later still shows the original " +
        "goal. Omit on later calls to leave it unchanged; only pass it again if the goal itself genuinely " +
        "changed (e.g. scope pivoted). This is distinct from `progress`, which tracks evolving status.",
    ),
    jiraEpic: str(
      "Jira epic key (e.g. 'SP-100'), if this session's ticket belongs to one. Omit to leave whatever was " +
        "set before unchanged; pass an empty string to explicitly clear it.",
    ),
    jiraTicket: str(
      "Jira ticket key (e.g. 'SP-123') for this session. Check the session title (a '[SP-123]' bracket " +
        "prefix), the current branch name, or ask the user if genuinely unclear — this is almost always known. " +
        "If omitted, falls back to whatever was set before, then to extracting one from the branch name.",
    ),
    prUrl: str(
      "A pull request URL for this session. ADDS to the session's list of PRs rather than replacing it — a " +
        "single session can span more than one PR (follow-ups, split work, etc.), and every one reported " +
        "across multiple calls this session is kept, not just the latest. Omit if there's no new PR to report.",
    ),
    localUrl: str(
      "URL where a human can view the RUNNING application for the branch being worked on in THIS worktree " +
        "right now (e.g. a docker-compose'd dev server, a Vite/webpack dev server, a deployed preview " +
        "environment for this branch). NOT the opencode web UI's own URL, NOT a login/marketing page, NOT a " +
        "URL for something unrelated to this branch's changes. Omit to leave whatever was set before " +
        "unchanged (don't fabricate a port or URL you haven't actually confirmed is up); pass an empty " +
        "string to explicitly clear it once a preview server is no longer running.",
    ),
    progress: str(
      "What's been done, what's left to do, and what phase this session is in (planning / actively coding / " +
        "in review / ready to merge / done). Update this every time you call the tool — unlike `intent`, " +
        "this is expected to change often. One or two sentences is usually enough, but use more if useful.",
    ),
    title: str(
      "A short, punchy title for this session (3-8 words, plain description only — do NOT include a " +
        "'[SP-123]'/'DONE'/type bracket prefix yourself, the tool builds that automatically from jiraTicket, " +
        "done, and type). E.g. 'Fix session notes cross-contamination bug'. This is written into the notes " +
        "for the user to copy-paste into the actual opencode session title themselves if they like it — " +
        "never rename the session automatically. Always pass `type` alongside this.",
    ),
    type: {
      type: "string",
      enum: ["Question", "Investigation", "Code"],
      description:
        "What kind of session this is, shown in the suggested title. 'Question' — answering/explaining " +
        "something, no code changes made. 'Investigation' — researching, debugging, reading code/docs without " +
        "necessarily changing anything yet. 'Code' — actively writing or editing code. Always pass this " +
        "whenever you pass `title`; defaults to 'Code' if omitted.",
    },
    done: {
      type: "boolean",
      description:
        "True ONLY if the work for this session is fully complete AND cleaned up — same bar as the /done " +
        "command (PR merged, worktree/branch cleaned up, ticket transitioned, no loose ends). Prefixes the " +
        "suggested title with 'DONE'. Do not set this speculatively just because you think you're finished — " +
        "verify first. Defaults to false.",
    },
  },
}

const CLEANUP_INPUT = {
  type: "object",
  additionalProperties: false,
  properties: {
    worktree: str("Absolute path to the project directory to clean up. Defaults to the session's own directory."),
    olderThanDays: { type: "number", description: "Age threshold in days (default 30)" },
  },
}

export default {
  id: "session-notes",
  async setup(ctx: any) {
    async function load(sessionID: string) {
      const session = await ctx.session.get({ sessionID })
      const directory: string | undefined = session?.location?.directory
      const stored = await ctx.storage.get(storageKey(sessionID))
      if (stored && typeof stored === "object") return { directory, notes: stored as Record<string, unknown>, source: "storage" as const }
      const legacy = await readLegacyNotes(directory, sessionID)
      return { directory, notes: legacy, source: legacy ? ("legacy" as const) : ("none" as const) }
    }

    async function setNotes(args: any, sessionID: string) {
      const current = await load(sessionID)
      const worktree = resolveWorktree(args.worktree, current.directory)
      const branch = await currentBranch(worktree)
      const { notes, ticketMismatch, branchTicket, existingTicket } = mergeNotes(current.notes, args, worktree, branch)
      await ctx.storage.set(storageKey(sessionID), notes)

      // Worktree gets its own line, unadorned, so it's trivial to copy-paste into another tool.
      const lines = [`Session notes saved for ${sessionID}`, `Worktree: ${worktree}`, `Branch: ${branch || "unknown"}`]
      if (current.source === "legacy") lines.push(`Imported the earlier notes from ${LEGACY_DIR}/${sessionID}.json.`)
      if (ticketMismatch) {
        lines.push(
          `⚠️ Branch at '${worktree}' matches ${branchTicket}, but this session's notes are tracking ${existingTicket} ` +
            `— kept ${existingTicket}. This usually means you ran a shell command without cd-ing back into this ` +
            `session's actual worktree first (a shared/primary checkout can be sitting on another task's branch). ` +
            `Verify you're in the right directory before reporting progress. If ${branchTicket} is genuinely correct ` +
            `now, pass jiraTicket explicitly to confirm the change.`,
        )
      }
      if (notes.jiraTicket) lines.push(`Jira: ${jiraLink(notes.jiraTicket)}`)
      if (notes.prUrls.length) lines.push(`PRs: ${notes.prUrls.map(prLink).join(", ")}`)
      if (notes.title) lines.push(`Suggested title: "${notes.title}"`)
      return lines.join("\n")
    }

    // Prune stored notes not updated for N days (every project), plus V1 files in this worktree.
    async function pruneStorage(days: number): Promise<string[]> {
      const cutoff = Date.now() - days * 24 * 60 * 60 * 1000
      const removed: string[] = []
      let after: string | undefined
      do {
        const page = await ctx.storage.scan({ prefix: "notes/", after, limit: 200 })
        for (const entry of page.entries) {
          const updated = Date.parse(String((entry.value as any)?.updatedAt ?? ""))
          if (Number.isFinite(updated) && updated < cutoff) {
            await ctx.storage.remove(entry.key)
            removed.push(entry.key.slice("notes/".length))
          }
        }
        after = page.next
      } while (after)
      return removed
    }

    async function cleanup(args: any, sessionID: string) {
      const { directory } = await load(sessionID)
      const worktree = resolveWorktree(args.worktree, directory)
      const days = args.olderThanDays ?? 30
      const stored = await pruneStorage(days)
      const legacy = await cleanupLegacy(worktree, days)
      const lines = [
        stored.length
          ? `Deleted notes of ${stored.length} session(s) not updated for ${days} days:\n${stored.map((id) => `- ${id}`).join("\n")}`
          : `No stored session notes older than ${days} days.`,
      ]
      if (legacy?.length) lines.push(`Deleted ${legacy.length} legacy file(s) from ${worktree}/${LEGACY_DIR}/:\n${legacy.map((d) => `- ${d}`).join("\n")}`)
      return lines.join("\n")
    }

    const recorder = createRecorder(ctx, load)

    await ctx.tool.transform((editor: any) => {
      editor.namespace({ name: "session-notes", description: "Notes shown next to the session title by the Session Notes browser extension" })
      editor.add({
        name: "plan_ready",
        description: "Call once when you have finished presenting a plan and are waiting for the user to approve it.",
        input: {
          type: "object",
          additionalProperties: false,
          required: ["summary"],
          properties: {
            summary: str("One or two sentences: what the plan will do."),
            intent: str("Why this session exists. Only if not set yet."),
          },
        },
        options: { namespace: "session-notes", pinned: true },
        async execute(args: any, context: any) {
          const progress = `Plan ready, awaiting approval: ${String(args.summary ?? "").trim()}`
          await recorder.record(context.sessionID, (notes) => {
            const intent = typeof args.intent === "string" && args.intent.trim() && !String(notes?.intent ?? "").trim() ? args.intent.trim() : undefined
            if (notes?.progress === progress && !intent) return null
            return { progress, ...(intent ? { intent } : {}) }
          })
          return { content: "Noted." }
        },
      })
      editor.add({
        name: "set",
        description:
          "Write session notes (intent, progress, suggested title, Jira ticket, PR link, local preview link) for the " +
          "CURRENT session, shown by the OpenCode Session Notes Chrome extension and the terminal notes panel. " +
          "Call early to set `intent`, `title`, and `progress`, and update `progress` as work advances.",
        input: SET_INPUT,
        options: { namespace: "session-notes", pinned: true },
        async execute(args: any, context: any) {
          return { content: await setNotes(args, context.sessionID) }
        },
      })
      editor.add({
        name: "cleanup",
        description:
          "Delete session notes not updated for N days (default 30), across all sessions, plus any leftover pre-V2 " +
          `${LEGACY_DIR}/*.json files in the current worktree. Use when the user asks to clean up stale session notes.`,
        input: CLEANUP_INPUT,
        options: { namespace: "session-notes" },
        async execute(args: any, context: any) {
          return { content: await cleanup(args ?? {}, context.sessionID) }
        },
      })
    })

    await installAutomation(ctx, recorder, cleanup)

    // Read path for the browser extension and the terminal UI (stored notes first, then the V1 file), and the
    // terminal UI's edit path.
    await ctx.rpc.register(SessionNotesRpc, {
      get: async (input: any) => {
        const current = await load(input.sessionID)
        return { notes: current.notes ?? null, source: current.source, directory: current.directory ?? null }
      },
      update: async (input: any) => {
        const current = await load(input.sessionID)
        const notes = applyEdit(current.notes, input.edit ?? {})
        if (!notes.worktree && current.directory) notes.worktree = current.directory
        await ctx.storage.set(storageKey(input.sessionID), notes)
        return { notes }
      },
    })
  },
}
