import test from "node:test"
import assert from "node:assert/strict"
import { callKey, editFor, factFrom, type ToolEvent } from "./triggers.ts"

const shell = (command: string, output: string, exit = 0, status = "completed"): ToolEvent => ({
  tool: "shell",
  sessionID: "ses_1",
  id: "call_1",
  input: { command },
  status,
  result: { output: { exit, output, status: "completed" }, content: [{ type: "text", text: output }] },
})

const jira = (tool: string, input: any, payload: unknown, status = "completed"): ToolEvent => ({
  tool,
  sessionID: "ses_1",
  id: "call_2",
  input,
  status,
  result: { output: { result: typeof payload === "string" ? payload : JSON.stringify(payload) } },
})

test("gh pr create with a PR url is a pr fact", () => {
  const fact = factFrom(shell('gh pr create --title "x" --body "y"', "\nhttps://github.com/Profinda/premiumui/pull/13243\n"))
  assert.deepEqual(fact, { type: "pr", url: "https://github.com/Profinda/premiumui/pull/13243" })
})

test("gh pr create inside a compound command still matches", () => {
  const fact = factFrom(shell("git push -u origin HEAD && gh pr create --fill", "Branch pushed\nhttps://github.com/a/b/pull/7\n"))
  assert.deepEqual(fact, { type: "pr", url: "https://github.com/a/b/pull/7" })
})

test("other gh pr commands and other shell commands do nothing", () => {
  assert.equal(factFrom(shell("gh pr view --json url", "https://github.com/a/b/pull/7")), undefined)
  assert.equal(factFrom(shell("gh pr list", "https://github.com/a/b/pull/7")), undefined)
  assert.equal(factFrom(shell("echo gh pr create", "gh pr create")), undefined)
})

test("failed pr create does not match", () => {
  assert.equal(factFrom(shell("gh pr create", "https://github.com/a/b/pull/7", 1)), undefined)
  assert.equal(factFrom(shell("gh pr create", "", 0, "error")), undefined)
  assert.equal(factFrom(shell("gh pr create", "a pull request already exists")), undefined)
})

test("jira create returns the new ticket from the result", () => {
  const fact = factFrom(jira("mcp-atlassian_jira_create_issue", { project_key: "SP", issue_type: "Story" }, { message: "Issue created successfully", issue: { key: "SP-1234" } }))
  assert.deepEqual(fact, { type: "jira", key: "SP-1234", role: "ticket" })
})

test("jira create of an epic is an epic fact", () => {
  const fact = factFrom(jira("mcp-atlassian_jira_create_issue", { issue_type: "Epic" }, { issue: { key: "SP-100" } }))
  assert.deepEqual(fact, { type: "jira", key: "SP-100", role: "epic" })
})

test("jira update falls back to the input key", () => {
  const fact = factFrom(jira("mcp-atlassian_jira_update_issue", { issue_key: "SP-55", fields: "{}" }, { message: "Issue updated successfully" }))
  assert.deepEqual(fact, { type: "jira", key: "SP-55", role: "ticket" })
})

test("the server name does not matter", () => {
  const fact = factFrom(jira("atlassian_jira_update_issue", { issue_key: "SP-55" }, "ok"))
  assert.deepEqual(fact, { type: "jira", key: "SP-55", role: "ticket" })
})

test("jira reads, comments and failures do nothing", () => {
  assert.equal(factFrom(jira("mcp-atlassian_jira_get_issue", { issue_key: "SP-1" }, { key: "SP-1" })), undefined)
  assert.equal(factFrom(jira("mcp-atlassian_jira_add_comment", { issue_key: "SP-1" }, "ok")), undefined)
  assert.equal(factFrom(jira("mcp-atlassian_jira_update_issue", { issue_key: "SP-1" }, "boom", "error")), undefined)
  assert.equal(factFrom(jira("mcp-atlassian_jira_create_issue", {}, "no key in here")), undefined)
})

test("execute wrapper itself never matches", () => {
  const wrapper: ToolEvent = { tool: "execute", sessionID: "s", id: "c", input: { code: "gh pr create" }, status: "completed", result: { output: "https://github.com/a/b/pull/1" } }
  assert.equal(factFrom(wrapper), undefined)
})

test("pr edit: adds once, fills progress only when empty", () => {
  const fact = { type: "pr", url: "https://github.com/a/b/pull/7" } as const
  assert.deepEqual(editFor(null, fact), { addPr: fact.url, progress: "PR opened, in review." })
  assert.deepEqual(editFor({ progress: "Fixing tests" }, fact), { addPr: fact.url })
  assert.equal(editFor({ prUrls: [fact.url], progress: "x" }, fact), null)
})

test("jira edit: fills only empty ticket or epic, never replaces", () => {
  assert.deepEqual(editFor(null, { type: "jira", key: "SP-1", role: "ticket" }), { jiraTicket: "SP-1" })
  assert.equal(editFor({ jiraTicket: "SP-9" }, { type: "jira", key: "SP-1", role: "ticket" }), null)
  assert.deepEqual(editFor({ jiraTicket: "SP-9" }, { type: "jira", key: "SP-100", role: "epic" }), { jiraEpic: "SP-100" })
  assert.equal(editFor({ jiraEpic: "SP-7" }, { type: "jira", key: "SP-100", role: "epic" }), null)
  assert.deepEqual(editFor({ jiraTicket: " " }, { type: "jira", key: "SP-1", role: "ticket" }), { jiraTicket: "SP-1" })
})

test("calls sharing one execute call id still get distinct keys", () => {
  const first = jira("mcp-atlassian_jira_create_issue", { summary: "a", issue_type: "Epic" }, { issue: { key: "SP-1" } })
  const second = jira("mcp-atlassian_jira_create_issue", { summary: "b", issue_type: "Story" }, { issue: { key: "SP-2" } })
  assert.equal(first.id, second.id)
  assert.notEqual(callKey(first), callKey(second))
  assert.equal(callKey(first), callKey({ ...first }))
})
