// V1's session.idle / session.error hooks, rebuilt on V2's session.execution.* events.
import { findBySession, patchBySession, updateMember } from "./store.ts"
import { activity, scheduleFlush, type TeamSessions } from "./sessions.ts"

// The public event stream is server-wide and every plugin instance (one per location) subscribes to it,
// so each event is handled once, by whichever instance sees it first.
const SEEN = Symbol.for("workbench.team.seenEvents")
const seen: Set<string> = ((globalThis as any)[SEEN] ??= new Set())

function firstSighting(id: string | undefined): boolean {
  if (!id) return true
  if (seen.has(id)) return false
  seen.add(id)
  if (seen.size > 2000) {
    const oldest = seen.values().next().value
    if (oldest) seen.delete(oldest)
  }
  return true
}

const ENDED: Record<string, string> = {
  "session.execution.succeeded": "succeeded",
  "session.execution.failed": "failed",
  "session.execution.interrupted": "interrupted",
}

export async function handleEvent(event: any, sessions: TeamSessions) {
  const sessionId: string | undefined = event?.data?.sessionID
  if (!sessionId || !event.type?.startsWith("session.execution.")) return
  if (!firstSighting(event.id)) return

  if (event.type === "session.execution.started") {
    activity.set(sessionId, { busy: true, at: Date.now() })
    return
  }
  const outcome = ENDED[event.type]
  if (!outcome) return
  activity.set(sessionId, { busy: false, at: Date.now(), outcome })

  await patchBySession(sessionId, { lastIdleAt: new Date().toISOString() })
  const found = await findBySession(sessionId)
  if (!found) return
  if (outcome === "failed" && found.member.state !== "done") {
    await updateMember(found.team, found.member.name, { state: "error" })
  }
  if (found.member.role === "orchestrator") scheduleFlush(sessions, found.team, 1500)
}

export function subscribe(ctx: any, sessions: TeamSessions, signal: AbortSignal) {
  void (async () => {
    while (!signal.aborted) {
      try {
        for await (const event of ctx.event.subscribe({ signal })) {
          try {
            await handleEvent(event, sessions)
          } catch {}
        }
      } catch {}
      // The stream is volatile by contract (a slow consumer is dropped): reconnect unless unloading.
      if (!signal.aborted) await new Promise((resolve) => setTimeout(resolve, 1000))
    }
  })()
}
