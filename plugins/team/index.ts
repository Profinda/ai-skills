// Team plugin: an orchestrator session coordinates player sessions through the team_* tools.
// V2 plugin: a default-exported { id, setup } definition (the shape Plugin.define produces), so it needs no
// dependency on @opencode/plugin at runtime.
import { ORCHESTRATOR, listTeams } from "./lib/store.ts"
import { createTeamSessions, clearFlushTimers } from "./lib/sessions.ts"
import { createTeamOps } from "./lib/tools.ts"
import { subscribe } from "./lib/events.ts"
import { TeamRpc } from "./rpc.ts"

// setup runs once per location (project directory). Shared timers are cleared only when the last one unloads.
const INSTANCES = Symbol.for("team.instances")

export default {
  id: "team",
  async setup(ctx: any) {
    const g = globalThis as any
    g[INSTANCES] = (g[INSTANCES] ?? 0) + 1

    const sessions = createTeamSessions(ctx)
    const ops = createTeamOps(ctx, sessions)

    await ctx.tool.transform((editor: any) => {
      editor.namespace({ name: "team", description: "Coordinate orchestrator and player sessions working on one body of work" })
      for (const tool of ops.tools) {
        editor.add({
          name: tool.name,
          description: tool.description,
          input: tool.input,
          options: { namespace: "team" },
          async execute(args: unknown, context: any) {
            const content = await tool.execute(args ?? {}, { sessionID: context.sessionID, agent: context.agent })
            return { content }
          },
        })
      }
    })

    const asOrchestrator = { name: ORCHESTRATOR, role: "orchestrator" }
    await ctx.rpc.register(TeamRpc, {
      teams: async () => ({ text: (await listTeams()).join("\n") || "(none)" }),
      roster: async (input: any) => ({ text: await sessions.rosterTable(input.team) }),
      inspect: async (input: any) => ({ text: await ops.inspectText(input) }),
      send: async (input: any) => ({ text: await ops.send(input, asOrchestrator) }),
      spawn: async (input: any) => ({ text: await ops.spawnText(input) }),
      common: async (input: any) => ({ text: await ops.common(input) }),
      log: async (input: any) => ({ text: await ops.log(input) }),
    })

    const controller = new AbortController()
    subscribe(ctx, sessions, controller.signal)

    return () => {
      controller.abort()
      g[INSTANCES] = Math.max(0, (g[INSTANCES] ?? 1) - 1)
      if (g[INSTANCES] === 0) clearFlushTimers()
    }
  },
}
