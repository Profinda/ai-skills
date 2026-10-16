// RPC contract used by bin/team (and anything else outside a session) to drive the team.
// Call over HTTP: POST /api/rpc/team/<method> with body {"input": {...}}; every method returns {"text": "..."}.
const text = { type: "object", properties: { text: { type: "string" } }, required: ["text"], additionalProperties: false }
const input = (properties: Record<string, unknown>, required: string[] = []) => ({ type: "object", properties, required })
const s = { type: "string" }

export const TeamRpc = {
  id: "team",
  methods: {
    // V2 validates every call against an input schema, so even argument-less methods declare one.
    teams: { input: input({}), output: text },
    roster: { input: input({ team: s }, ["team"]), output: text },
    inspect: { input: input({ team: s, name: s, max_chars: { type: "number" } }, ["team", "name"]), output: text },
    send: { input: input({ team: s, to: s, message: s, kind: s }, ["team", "to", "message"]), output: text },
    spawn: {
      input: input({ team: s, name: s, directory: s, title: s, brief: s, model: s, agent: s, role: s }, ["team", "name", "directory", "title", "brief"]),
      output: text,
    },
    common: { input: input({ team: s, text: s }, ["team"]), output: text },
    log: { input: input({ team: s, limit: { type: "number" } }, ["team"]), output: text },
  },
  events: {},
}
