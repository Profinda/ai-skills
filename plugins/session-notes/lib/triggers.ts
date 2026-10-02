// Facts the plugin can read straight from a finished tool call, so notes stay current without a model turn.
import type { Edit } from "./notes.ts"

export type ToolEvent = {
  tool: string
  sessionID: string
  id: string
  input?: any
  status: string
  result?: { output?: any; content?: unknown }
}

export type Fact =
  | { type: "pr"; url: string }
  | { type: "jira"; key: string; role: "ticket" | "epic" }

const PR_CREATE = /\bgh\s+pr\s+create\b/
const PR_URL = /https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/pull\/\d+/g
const JIRA_WRITE_TOOL = /_jira_(create|update)_issue$/
const JIRA_KEY = /\b[A-Z][A-Z0-9]+-\d+\b/

function resultText(event: ToolEvent): string {
  const output = event.result?.output
  if (typeof output === "string") return output
  if (typeof output?.output === "string") return output.output
  if (typeof output?.result === "string") return output.result
  const content = event.result?.content
  if (typeof content === "string") return content
  if (Array.isArray(content)) return content.map((part: any) => (typeof part?.text === "string" ? part.text : "")).join("\n")
  return ""
}

function prFromShell(event: ToolEvent): Fact | undefined {
  if (event.tool !== "shell" || event.status !== "completed") return
  if (typeof event.input?.command !== "string" || !PR_CREATE.test(event.input.command)) return
  const exit = event.result?.output?.exit
  if (typeof exit === "number" && exit !== 0) return
  const urls = resultText(event).match(PR_URL)
  if (urls?.length) return { type: "pr", url: urls[urls.length - 1] }
}

function jiraKeyFrom(event: ToolEvent): string | undefined {
  const text = resultText(event)
  try {
    const parsed = JSON.parse(text)
    const key = parsed?.issue?.key ?? parsed?.key
    if (typeof key === "string" && JIRA_KEY.test(key)) return key
  } catch {}
  const fromInput = event.input?.issue_key
  if (typeof fromInput === "string" && JIRA_KEY.test(fromInput)) return fromInput.match(JIRA_KEY)![0]
  return text.match(JIRA_KEY)?.[0]
}

function jiraFromTool(event: ToolEvent): Fact | undefined {
  if (event.status !== "completed" || !JIRA_WRITE_TOOL.test(event.tool)) return
  const key = jiraKeyFrom(event)
  if (!key) return
  const creatingEpic = event.tool.endsWith("_create_issue") && String(event.input?.issue_type ?? "").toLowerCase() === "epic"
  return { type: "jira", key, role: creatingEpic ? "epic" : "ticket" }
}

// Calls made inside one `execute` share that call's id, so the id alone cannot tell two of them apart.
export function callKey(event: ToolEvent): string {
  return `${event.id}|${event.tool}|${JSON.stringify(event.input ?? null)}`
}

export function factFrom(event: ToolEvent): Fact | undefined {
  return prFromShell(event) ?? jiraFromTool(event)
}

const empty = (value: unknown) => typeof value !== "string" || value.trim() === ""

// Only fill what is missing. A ticket or PR that is already on record is never replaced here, because this
// runs without the model's context and cannot tell a deliberate change from a stray ticket the session touched.
export function editFor(existing: Record<string, unknown> | null, fact: Fact): Edit | null {
  if (fact.type === "pr") {
    const prior = Array.isArray(existing?.prUrls) ? (existing!.prUrls as unknown[]) : []
    if (prior.includes(fact.url)) return null
    return { addPr: fact.url, ...(empty(existing?.progress) ? { progress: "PR opened, in review." } : {}) }
  }
  if (fact.role === "epic") return empty(existing?.jiraEpic) ? { jiraEpic: fact.key } : null
  return empty(existing?.jiraTicket) ? { jiraTicket: fact.key } : null
}
