// Terminal client for the team plugin. It calls the plugin's RPC through `opencode api`, which finds the
// running OpenCode service and handles its authentication.
import { execFileSync } from "node:child_process"
import { readFileSync } from "node:fs"

const [command, ...rest] = process.argv.slice(2)
const flags: Record<string, string> = {}
const positional: string[] = []
for (let index = 0; index < rest.length; index++) {
  if (rest[index].startsWith("--")) flags[rest[index].slice(2)] = rest[++index] ?? ""
  else positional.push(rest[index])
}

const usage = `team <command>
  teams                                   list teams
  roster <team>                           members, state, busy/idle
  inspect <team> <name>                   last message, pending question, recent tools
  send <team> <name|all> <message...> [--kind info|question|blocker|decision|urgent]   message as the orchestrator
  spawn <team> <name> --dir <worktree> --title <title> --brief <text|@file> [--model provider/model[#variant]] [--agent name]
  common <team> [--set <text|@file>]      show or set the shared rules
  log <team> [--limit n]                  recent team messages

Talks to the running OpenCode service. TEAM_SERVER=<url> (with OPENCODE_PASSWORD) targets another server.`

const text = (value: string) => (value.startsWith("@") ? readFileSync(value.slice(1), "utf8") : value)

function call(method: string, input: Record<string, unknown> = {}): string {
  const opencode = process.env.OPENCODE_BIN || "opencode"
  // Defaults to the background service; TEAM_SERVER targets another server (its password via OPENCODE_PASSWORD).
  const server = process.env.TEAM_SERVER ? ["--server", process.env.TEAM_SERVER] : []
  const raw = execFileSync(opencode, ["api", ...server, "POST", `/api/rpc/team/${method}`, "--data", JSON.stringify({ input })], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  })
  const parsed = JSON.parse(raw)
  if (parsed?.output?.text === undefined) throw new Error(raw.slice(0, 500))
  return parsed.output.text
}

function main() {
  const team = positional[0]
  switch (command) {
    case "teams":
      return console.log(call("teams"))
    case "roster":
      return console.log(call("roster", { team }))
    case "inspect":
      return console.log(call("inspect", { team, name: positional[1] }))
    case "send": {
      const [, to, ...message] = positional
      return console.log(call("send", { team, to, message: message.join(" "), ...(flags.kind ? { kind: flags.kind } : {}) }))
    }
    case "spawn":
      return console.log(
        call("spawn", {
          team,
          name: positional[1],
          directory: flags.dir,
          title: flags.title,
          brief: text(flags.brief),
          ...(flags.model ? { model: flags.model } : {}),
          ...(flags.agent ? { agent: flags.agent } : {}),
        }),
      )
    case "common":
      return console.log(call("common", { team, ...(flags.set !== undefined ? { text: text(flags.set) } : {}) }))
    case "log":
      return console.log(call("log", { team, limit: Number(flags.limit || 30) }))
    default:
      console.log(usage)
  }
}

try {
  main()
} catch (error: any) {
  console.error(String(error?.stderr || error?.message || error))
  process.exit(1)
}
