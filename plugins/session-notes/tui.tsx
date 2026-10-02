/** @jsxImportSource @opentui/solid */
// Terminal UI for session notes: a sidebar section with the current session's notes, and a /notes panel to read
// and edit them. Uses the same notes the agent writes (session-notes_set) and the Chrome extension shows, through
// this plugin's RPC, so an edit here also reaches the web UI.
import { For, Show, createSignal, onCleanup } from "solid-js"
import { usePlugin } from "@opencode/plugin/tui"
import { SessionNotesRpc } from "./rpc.ts"

type Notes = {
  worktree?: string
  branch?: string
  intent?: string
  jiraEpic?: string
  jiraTicket?: string
  title?: string
  prUrls?: string[]
  localUrl?: string
  progress?: string
  updatedAt?: string
}

type Edit = Partial<Record<"intent" | "progress" | "jiraEpic" | "jiraTicket" | "title" | "localUrl" | "addPr" | "removePr", string>>

const PANEL = "session-notes.panel"
const JIRA_BASE_URL = "https://profinda.atlassian.net/browse/"
const POLL_MS = 4000

const prLabel = (url: string) => {
  const number = url.match(/\/(?:pull|pull-requests|merge_requests)\/(\d+)/)?.[1]
  return number ? `PR#${number}` : "PR"
}
const clip = (text: string | undefined, max: number) => {
  const value = (text ?? "").trim()
  return value.length > max ? value.slice(0, max - 1) + "…" : value
}
const hasNotes = (notes: Notes | null) =>
  !!notes && !!(notes.intent || notes.progress || notes.jiraTicket || notes.jiraEpic || notes.prUrls?.length || notes.localUrl)

// Editable fields, in panel order.
const FIELDS: { key: keyof Edit & keyof Notes; label: string }[] = [
  { key: "intent", label: "Intent" },
  { key: "progress", label: "Progress" },
  { key: "jiraTicket", label: "Jira ticket" },
  { key: "jiraEpic", label: "Jira epic" },
  { key: "title", label: "Suggested title" },
  { key: "localUrl", label: "Preview URL" },
]

function notesApi(context: any) {
  const rpc = context.client.rpc(SessionNotesRpc)
  const unwrap = (result: any) => result?.output ?? result?.data ?? result
  return {
    async get(sessionID: string): Promise<Notes | null> {
      return unwrap(await rpc.get({ sessionID }))?.notes ?? null
    },
    async update(sessionID: string, edit: Edit): Promise<Notes> {
      return unwrap(await rpc.update({ sessionID, edit })).notes
    },
  }
}

// Live notes for one session: fetched on mount, after each run of that session, and on a slow poll (the agent,
// the web UI or another terminal can change them).
function useNotes(context: any, sessionID: () => string | undefined) {
  const api = notesApi(context)
  const [notes, setNotes] = createSignal<Notes | null>(null)
  const [error, setError] = createSignal<string | undefined>()
  const refresh = async () => {
    const id = sessionID()
    if (!id) return
    try {
      setNotes(await api.get(id))
      setError(undefined)
    } catch (e) {
      setError(String((e as Error)?.message ?? e).slice(0, 120))
    }
  }
  void refresh()
  const timer = setInterval(() => void refresh(), POLL_MS)
  const stop = context.data.on("session.execution.succeeded", (event: any) => {
    if (event?.data?.sessionID === sessionID()) void refresh()
  })
  onCleanup(() => {
    clearInterval(timer)
    stop?.()
  })
  return { notes, error, refresh, setNotes, api }
}

function Sidebar(props: { sessionID: string }) {
  const context = usePlugin() as any
  const t = context.theme
  const { notes } = useNotes(context, () => props.sessionID)
  const links = () => {
    const n = notes()
    return [n?.jiraTicket, ...(n?.prUrls ?? []).map(prLabel), n?.localUrl ? "Preview" : undefined].filter(Boolean).join(" · ")
  }
  return (
    <box flexDirection="column" marginTop={1}>
      <text fg={t.text.muted}>Session notes</text>
      <Show when={hasNotes(notes())} fallback={<text fg={t.text.muted}>none yet · /notes to add</text>}>
        <Show when={notes()?.branch}>
          <text fg={t.hue.accent[500]}>⎇ {notes()!.branch}</text>
        </Show>
        <Show when={links()}>
          <text fg={t.hue.blue[500]}>{links()}</text>
        </Show>
        <Show when={notes()?.intent}>
          <text fg={t.text.base}>{clip(notes()!.intent, 140)}</text>
        </Show>
        <Show when={notes()?.progress}>
          <text fg={t.text.muted}>{clip(notes()!.progress, 220)}</text>
        </Show>
      </Show>
    </box>
  )
}

function Panel(props: { panel: any }) {
  const context = usePlugin() as any
  const t = context.theme
  const { notes, error, refresh, setNotes, api } = useNotes(context, () => props.panel.sessionID)

  const save = async (edit: Edit, message: string) => {
    try {
      setNotes(await api.update(props.panel.sessionID, edit))
      context.ui.toast.show({ message, variant: "success", duration: 2000 })
    } catch (e) {
      context.ui.toast.show({ message: `Could not save: ${String((e as Error)?.message ?? e).slice(0, 120)}`, variant: "error" })
    }
  }

  const editField = async () => {
    const key = await context.ui.dialog.select({
      title: "Edit session note",
      options: FIELDS.map((field) => ({
        title: field.label,
        value: field.key,
        description: clip((notes() as any)?.[field.key] || "(empty)", 70),
      })),
    })
    if (!key) return
    const field = FIELDS.find((candidate) => candidate.key === key)!
    const current = String((notes() as any)?.[key] ?? "")
    const value = await context.ui.dialog.prompt({ title: field.label, placeholder: current || field.label, value: current })
    if (value === undefined || value === null) return
    await save({ [key]: String(value) }, `${field.label} saved`)
  }

  const addPr = async () => {
    const url = await context.ui.dialog.prompt({ title: "Add pull request", placeholder: "https://github.com/org/repo/pull/123" })
    if (url && String(url).trim()) await save({ addPr: String(url).trim() }, "PR added")
  }

  const removePr = async () => {
    const prs = notes()?.prUrls ?? []
    if (!prs.length) return context.ui.toast.show({ message: "No PRs to remove" })
    const url = await context.ui.dialog.select({ title: "Remove pull request", options: prs.map((pr) => ({ title: prLabel(pr), value: pr, description: pr })) })
    if (url) await save({ removePr: String(url) }, "PR removed")
  }

  context.keymap.layer(() => ({
    commands: [
      { id: "session-notes.panel.edit", title: "Edit a field", bind: "e", run: () => void editField() },
      { id: "session-notes.panel.add-pr", title: "Add a PR", bind: "a", run: () => void addPr() },
      { id: "session-notes.panel.remove-pr", title: "Remove a PR", bind: "d", run: () => void removePr() },
      { id: "session-notes.panel.refresh", title: "Refresh", bind: "r", run: () => void refresh() },
      { id: "session-notes.panel.fullscreen", title: "Toggle full screen", bind: "f", run: props.panel.toggleFullscreen },
    ],
  }))

  const row = (label: string, value: string | undefined, color?: any) => (
    <box flexDirection="column" marginBottom={1}>
      <text fg={t.text.muted}>{label}</text>
      <text fg={color ?? t.text.base}>{value?.trim() ? value : "—"}</text>
    </box>
  )

  return (
    <box flexDirection="column" padding={1}>
      <text fg={t.text.base}>Session notes</text>
      <text fg={t.text.muted}>e edit · a add PR · d remove PR · r refresh · f full screen</text>
      <box marginTop={1} flexDirection="column">
        <Show when={error()}>
          <text fg={t.text.feedback.error}>{error()}</text>
        </Show>
        {row("Worktree", notes()?.worktree)}
        {row("Branch", notes()?.branch, t.hue.accent[500])}
        {row("Intent", notes()?.intent)}
        {row("Progress", notes()?.progress)}
        {row("Jira", [notes()?.jiraTicket, notes()?.jiraEpic ? `epic ${notes()!.jiraEpic}` : ""].filter(Boolean).join(" · ") + (notes()?.jiraTicket ? `  ${JIRA_BASE_URL}${notes()!.jiraTicket}` : ""), t.hue.blue[500])}
        <box flexDirection="column" marginBottom={1}>
          <text fg={t.text.muted}>Pull requests</text>
          <Show when={notes()?.prUrls?.length} fallback={<text fg={t.text.base}>—</text>}>
            <For each={notes()!.prUrls}>{(url) => <text fg={t.hue.green[500]}>{prLabel(url)}  {url}</text>}</For>
          </Show>
        </box>
        {row("Preview", notes()?.localUrl, t.hue.orange[500])}
        {row("Suggested title", notes()?.title)}
        <text fg={t.text.muted}>{notes()?.updatedAt ? `updated ${new Date(notes()!.updatedAt!).toLocaleString()}` : "no notes saved yet"}</text>
      </box>
    </box>
  )
}

export default {
  id: "session-notes",
  setup(context: any) {
    const currentSession = (): string | undefined => {
      const route = context.ui.router.current()
      return route?.type === "session" ? route.sessionID : undefined
    }

    const setProgress = async (text: string) => {
      const sessionID = currentSession()
      if (!sessionID) return context.ui.toast.show({ message: "Open a session first", variant: "warning" })
      try {
        await notesApi(context).update(sessionID, { progress: text })
        context.ui.toast.show({ message: "Progress saved to session notes", variant: "success", duration: 2000 })
      } catch (e) {
        context.ui.toast.show({ message: `Could not save: ${String((e as Error)?.message ?? e).slice(0, 120)}`, variant: "error" })
      }
    }

    const disposers = [
      context.ui.slot({ append: "sidebar.content", render: (props: { sessionID: string }) => <Sidebar sessionID={props.sessionID} /> }),
      context.ui.slot({
        append: "session.panel",
        render: (panel: any) => (
          <Show when={panel.name === PANEL}>
            <Panel panel={panel} />
          </Show>
        ),
      }),
      context.ui.slot({
        append: "app",
        render: () => {
          context.keymap.layer(() => ({
            mode: "global",
            commands: [
              {
                id: "session-notes.open",
                title: "Session notes: view and edit",
                group: "Session notes",
                palette: true,
                slash: { name: "notes", arguments: true },
                run: async (input?: string) => {
                  // "/notes some text" sets the progress; plain "/notes" opens the panel.
                  if (input && input.trim()) return void (await setProgress(input.trim()))
                  if (context.ui.panel.open(PANEL) === false) context.ui.toast.show({ message: "Open a session first", variant: "warning" })
                },
              },
            ],
          }))
          return null
        },
      }),
    ]
    return () => disposers.forEach((dispose: any) => typeof dispose === "function" && dispose())
  },
}
