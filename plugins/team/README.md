# Team plugin

Coordinate parallel OpenCode sessions on one body of work. An `orchestrator` session splits the work, spawns `player` sessions in their own worktrees, keeps them in sync, and the sessions message each other directly through `team_*` tools, so the user does not relay between them.

> **Minimum supported version: OpenCode V2 (2.0.0 or newer).** This plugin only works on V2. It uses the V2 plugin API (`{ id, setup }` definition, `ctx.tool.transform`, `ctx.rpc`, `ctx.session.prompt` with `delivery`) and the V2 service. OpenCode V1 (1.x) cannot load it, and nothing here has been ported to V1. If `opencode --version` prints 1.x, stop, tell the user to upgrade (`opencode upgrade`), and do not try to adapt the plugin.

## Install (instructions for the agent configuring this)

Do these steps in order. Stop and report if a check fails. Never overwrite an existing file the user wrote without asking.

### 1. Check requirements

| Requirement | Check | Why |
|---|---|---|
| OpenCode 2.0.0 or newer | `opencode --version` prints `opencode v2.x.y` | The plugin API it uses does not exist in V1 |
| Node 22.18 or newer | `node --version` | `bin/team` runs TypeScript directly (type stripping) |
| `git` | `git --version` | Worktrees, `prs` |
| `gh`, authenticated, and `python3` | `gh auth status`, `python3 --version` | `bin/prs` (PR radar). Optional: the plugin works without it |

### 2. Get this repo

The plugin lives in the shared `Profinda/ai-skills` repo, under `plugins/team/`. Use the same clone the skills installer uses so one `git pull` updates both:

```sh
[ -d ~/.config/ai-skills/.git ] \
  && git -C ~/.config/ai-skills pull --ff-only \
  || git clone git@github.com:Profinda/ai-skills.git ~/.config/ai-skills
```

Below, `TEAM_DIR` means `$HOME/.config/ai-skills/plugins/team`.

### 3. Register the plugin

Add the absolute path of `TEAM_DIR` to `plugins` in the user's global config, `~/.config/opencode/opencode.json` (or `opencode.jsonc`). Expand `$HOME` yourself: write the real path, not `~`. Keep every other setting and every other entry in `plugins`.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "plugins": ["/Users/<user>/.config/ai-skills/plugins/team"]
}
```

If the file has no `plugins` key, add it. If it already lists plugins, append this path. The plugin has no npm dependencies, so there is nothing to install.

### 4. Link the two agents and the playbook skill

These make the `orchestrator` and `player` agents and the `orchestrating-sessions` skill available in every project:

```sh
mkdir -p ~/.config/opencode/agents ~/.config/opencode/skills
ln -s "$HOME/.config/ai-skills/plugins/team/agents/orchestrator.md" ~/.config/opencode/agents/orchestrator.md
ln -s "$HOME/.config/ai-skills/plugins/team/agents/player.md" ~/.config/opencode/agents/player.md
ln -s "$HOME/.config/ai-skills/plugins/team/skills/orchestrating-sessions" ~/.config/opencode/skills/orchestrating-sessions
```

If a target already exists, `ln -s` fails. That is on purpose. Look at what is there: a symlink into `~/.config/ai-skills` can be replaced, a user-written file or folder cannot until the user says so.

### 5. Put the shell helpers on PATH (optional)

The playbook skill calls `team` and `prs`:

```sh
mkdir -p ~/.local/bin
ln -s "$HOME/.config/ai-skills/plugins/team/bin/team" ~/.local/bin/team
ln -s "$HOME/.config/ai-skills/plugins/team/bin/prs" ~/.local/bin/prs
```

Make sure `~/.local/bin` is on `PATH`.

### 6. Restart and verify

```sh
opencode service restart
opencode plugin list          # should list a `team` row
team teams                    # prints "(none)" on a fresh install, so the plugin RPC works
```

Then start a new session and check that the `orchestrator` and `player` agents appear (Tab cycles primary agents) and that `team_join` shows up among the tools. If `team teams` fails, read `~/.local/share/opencode/log/opencode.log` (filter `role=server`) before changing anything.

### Update and uninstall

- Update: `git -C ~/.config/ai-skills pull --ff-only`, then `opencode service restart`. The symlinks and the config entry keep pointing at the clone.
- Uninstall: remove the path from `plugins`, delete the symlinks created in steps 4 and 5, restart the service. Team state under `~/.local/share/opencode-team/` is left alone; delete it only if the user asks.

### Optional companions

The agents delegate noisy work (CI logs, big diffs, browser QA, Jira grooming) to subagents named `developer`, `browser-qa` and `product-manager`. These are not part of this plugin, and the team tools do not depend on them. If the user has no such agents, tell them the orchestrator prompt names them, and suggest the built-in `general` and `explore` agents instead.

## What is in here

| Piece | Where (relative to this folder) |
|---|---|
| Plugin entry, V2 definition `{ id: "team", setup }` | `index.ts`, core in `lib/` |
| Tools `team_join team_roster team_send team_report team_spawn team_inspect team_common team_inbox team_log team_handoff team_resource team_close` | registered by `index.ts`, implemented in `lib/tools.ts` |
| RPC contract for the shell client | `rpc.ts` |
| `orchestrator` agent (primary) | `agents/orchestrator.md` |
| `player` agent (primary, what spawned sessions run) | `agents/player.md` |
| Playbook skill | `skills/orchestrating-sessions/SKILL.md` |
| Shell: `bin/team` (teams, roster, inspect, send, spawn, common, log), `bin/prs` (list, label, overlaps, reviews, worktrees, sim) | `bin/` |
| State | `~/.local/share/opencode-team/<team>/` (`roster.json`, `messages.jsonl`, `common.md`, `inbox.json`, `resources.json`, `handoffs/`, `workspace/`); override with `TEAM_HOME`. Closed teams move to `~/.local/share/opencode-team/_closed/` |

## Use

Start a session with the Orchestrator agent (Tab to switch) and describe the goal. It joins a team, spawns Players, and they report and message each other and it through `team_*`.

Hand the role over: `team_handoff(notes=...)` from the current orchestrator (see the playbook skill). It writes `handoffs/<time>.md` in the team's state directory, retires the old roster entry, spawns the successor as `orchestrator` with an orchestrator brief and keeps the unread inbox for it. `team_join(role=orchestrator)` refuses to replace a live orchestrator.

Adopt an existing session: switch it to the `player` agent (or just let it use the tools) and have it call `team_join`.

## How it runs on OpenCode V2

- `index.ts` default-exports a V2 plugin definition (`{ id: "team", setup }`), so it needs no npm dependency. `setup` runs once per project location. OpenCode reloads plugins when files under a watched config directory change; this plugin sits in the ai-skills clone, which is not watched, so run `opencode service restart` after updating it.
- Delivery uses the plugin context: `ctx.session.prompt` with `delivery: "queue"` (lands after the target's current turn), `"steer"` for `kind=urgent`. Spawning uses `ctx.session.create` with the worktree as the session location, the agent and the model. All sessions live in the one OpenCode service, so there are no per-member server URLs.
- Busy/idle comes from `session.execution.*` events. A member shows `run=?` until its session has run once since the service started. V2 has no todo tool, so the roster does not show todo counts.
- `bin/team` calls the plugin's RPC (`rpc.ts`, `POST /api/rpc/team/<method>`) through `opencode api`, which finds the running service and handles its authentication. `TEAM_SERVER=<url>` (with `OPENCODE_PASSWORD`) targets another server.
- `TEAM_NOTIFY=0` disables desktop notifications (they only fire on macOS).

Message economy: only question/blocker/urgent sends and done/blocked reports wake the orchestrator, batched in one digest when it is idle; everything else is pulled (`team_roster`, `team_inbox`, `team_log`). Rate limits: 5 wakes per sender and 8 messages per pair per 10 minutes.

## Where a team lives, and closing it

- **Team space:** `~/.local/share/opencode-team/<team>/`. Its `workspace/` folder is where the team keeps shared files (status files, scripts, screenshots, QA output); the path is in every brief and in `team_roster`. The plugin never writes into the repos.
- **Manifest:** `resources.json` lists what the team created and must be cleaned up. `team_spawn` registers each linked worktree it is given; members register the rest with `team_resource` (databases, container projects, local-only branches, temp directories, dev servers, each with the command that removes it).
- **Close:** `team_close` (orchestrator only). A dry run reports every registered worktree and local branch (uncommitted files, unpushed commits), lists the cleanup commands for everything else, and shows the sizes. `confirm=true`, only after the user says yes, removes the clean and already-pushed worktrees and branches (and ones marked disposable), leaves blocked ones in place, retires the members and moves the team folder to `_closed/`. It never touches remote branches, PRs, OpenCode sessions or anything outside the manifest; the main checkout of a repo is never removed; worktrees found only through the roster are left alone unless `include_discovered=true`.
