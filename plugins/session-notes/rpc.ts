// RPC contract for session notes, used by the Chrome extension and the terminal UI (tui.tsx).
// POST /api/rpc/session-notes/get    {"input": {"sessionID": "ses_..."}} -> {"output": {"notes", "source", "directory"}}
// POST /api/rpc/session-notes/update {"input": {"sessionID": "ses_...", "edit": {...}}} -> {"output": {"notes"}}
const s = { type: "string" }
const nullableObject = { type: ["object", "null"] }

export const SessionNotesRpc = {
  id: "session-notes",
  methods: {
    get: {
      input: { type: "object", properties: { sessionID: s }, required: ["sessionID"] },
      output: {
        type: "object",
        properties: {
          notes: nullableObject,
          source: { type: "string", enum: ["storage", "legacy", "none"] },
          directory: { type: ["string", "null"] },
        },
        required: ["notes", "source", "directory"],
      },
    },
    // A person's edit (terminal UI): only the given fields change. addPr/removePr edit the PR list.
    update: {
      input: {
        type: "object",
        properties: {
          sessionID: s,
          edit: {
            type: "object",
            properties: { intent: s, progress: s, jiraEpic: s, jiraTicket: s, title: s, localUrl: s, addPr: s, removePr: s },
            additionalProperties: false,
          },
        },
        required: ["sessionID", "edit"],
      },
      output: { type: "object", properties: { notes: { type: "object" } }, required: ["notes"] },
    },
  },
  events: {},
}
