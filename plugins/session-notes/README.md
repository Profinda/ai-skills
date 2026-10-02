# Session notes plugin

Agents record what a session is for and where it stands (intent, progress, Jira epic/ticket, PRs, preview URL, suggested title). You see and edit them in the terminal UI (`tui.tsx`) and in the web UI through the "OpenCode Session Notes" Chrome extension, which ships in this folder (`chrome-extension/`). All three read and write the same notes.

> **Minimum supported version: OpenCode V2 (2.0.0 or newer).** This plugin only works on V2. It uses the V2 plugin API (`{ id, setup }` definition, `ctx.tool.transform`, `ctx.rpc`, `ctx.storage`), the V2 terminal plugin API (`@opencode/plugin/tui`) and the V2 web UI (`opencode pair`). OpenCode V1 (1.x) cannot load it. It was built and tested on 2.0.20. If `opencode --version` prints 1.x, stop, tell the user to upgrade (`opencode upgrade`), and do not try to adapt the plugin.

## Install (instructions for the agent configuring this)

Do these steps in order. Stop and report if a check fails. Keep every unrelated setting in the user's config.

### 1. Check requirements

| Requirement | Check | Why |
|---|---|---|
| OpenCode 2.0.0 or newer | `opencode --version` prints `opencode v2.x.y` | The plugin APIs it uses do not exist in V1 |
| `git` | `git --version` | The plugin reads the session's branch |
| Chrome, Brave, Edge or any Chromium browser | ask the user | Only for the web UI extension (step 5). The plugin and the terminal UI work without it |

### 2. Get this repo

The plugin lives in the shared `Profinda/ai-skills` repo, under `plugins/session-notes/`. Use the same clone the skills installer uses so one `git pull` updates everything:

```sh
[ -d ~/.config/ai-skills/.git ] \
  && git -C ~/.config/ai-skills pull --ff-only \
  || git clone git@github.com:Profinda/ai-skills.git ~/.config/ai-skills
```

### 3. Register the plugin

Add the absolute path `$HOME/.config/ai-skills/plugins/session-notes` to `plugins` in the user's global config, `~/.config/opencode/opencode.json` (or `opencode.jsonc`). Write the real path, not `~`. Keep every other setting and every other entry in `plugins`.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "plugins": ["/Users/<user>/.config/ai-skills/plugins/session-notes"]
}
```

The plugin has no npm dependencies, so there is nothing to install. The same folder also exports the terminal UI (`./tui` in `package.json`), which OpenCode loads together with the plugin.

### 4. Restart and verify

```sh
opencode service restart
opencode plugin list          # should list a `session-notes` row
```

Then open a new terminal session. The sidebar should show a "Session notes" section and `/notes` should open the notes panel. If the plugin is listed but the sidebar section is missing, the terminal half was not picked up from the config entry. Add the same path to `plugins` in `~/.config/opencode/cli.json` (the CLI-only plugin list), restart the terminal session, and tell the user you had to. If nothing is listed, read `~/.local/share/opencode/log/opencode.log` (filter `role=server`) before changing anything.

### 5. Install the browser extension (web UI)

Skip this if the user does not use the OpenCode web UI. Follow [`chrome-extension/README.md`](chrome-extension/README.md): it covers Chrome and Brave, loading the unpacked folder `~/.config/ai-skills/plugins/session-notes/chrome-extension`, and opening the web UI with `opencode pair`. The extension needs the plugin from steps 3 and 4 already running, because it reads the notes from the plugin's RPC.

### Update and uninstall

- Update: `git -C ~/.config/ai-skills pull --ff-only`, then `opencode service restart`, restart open terminal sessions, and click the reload icon on the extension's card (`chrome://extensions` or `brave://extensions`), then hard-refresh open OpenCode web tabs.
- Uninstall: remove the path from `plugins` (and from `cli.json` if you added it), restart the service, remove the extension from the browser. Stored notes live in the plugin's storage inside OpenCode and are not touched by this.

## Terminal UI

- **Sidebar**: every session's sidebar has a "Session notes" section: branch, Jira ticket, PR numbers, preview, intent and progress. It refreshes after each run and every few seconds.
- **`/notes`** (also in the command palette as "Session notes: view and edit") opens the notes panel with every field in full. Keys: `e` edit a field (pre-filled), `a` add a PR, `d` remove a PR, `r` refresh, `f` full screen.
- **`/notes <text>`** sets the progress directly.

Edits from the terminal change only the fields you touch, keep the agent-reported worktree and branch, and bump `updatedAt`, so the extension picks them up. The terminal part loads automatically through the `./tui` export in `package.json`; restart open terminal sessions after changing it.

| Piece | Where |
|---|---|
| Tools `session-notes_set`, `session-notes_cleanup`, `session-notes_plan_ready` | `index.ts`, model in `lib/notes.ts` |
| Commands `/session-notes`, `/session-notes-cleanup` | `lib/automation.ts` |
| Automatic capture (tool hook) | `lib/automation.ts`, matchers in `lib/triggers.ts` (tests: `node --test lib/triggers.test.ts`) |
| Terminal UI | `tui.tsx` (sidebar section, `/notes` panel) |
| Chrome/Brave extension for the web UI | `chrome-extension/` (own README with install steps) |
| RPC (extension, terminal UI) | `rpc.ts`: `get` `{"sessionID"}`, `update` `{"sessionID", "edit": {intent, progress, jiraTicket, jiraEpic, title, localUrl, addPr, removePr}}` at `POST /api/rpc/session-notes/<method>` |

## Automatic updates and token cost

Notes update themselves, and by default no update costs a model turn.

| Moment | What happens | Model turns |
|---|---|---|
| `gh pr create` succeeds | The PR URL is added to the notes. Progress is set to "PR opened, in review." only if it was empty. | 0 |
| `jira_create_issue` or `jira_update_issue` succeeds | The ticket (or the epic, when an Epic was created) is filled in only if that field is empty. A ticket already on record is never replaced. | 0 |
| The agent calls `session-notes_plan_ready` | Its summary becomes the progress ("Plan ready, awaiting approval: ..."). Intent is filled in only if empty. | 0 extra, the agent makes the call inside its own turn |
| `/session-notes <text>` | The text is saved as the progress. | 0 |
| `/session-notes` | The agent writes progress (and intent if empty) with one `execute` call. | 1 short turn, only when you type it |
| `/session-notes-cleanup [days]` | Prunes old notes and posts the result. | 0 |

Details that keep it cheap and correct:

- Captures come from the `execute.after` tool hook, not from prompting the agent. Calls made inside one `execute` share that call's id, so calls are deduplicated by id, tool and input.
- A subagent's PR or ticket is recorded on the session you are looking at (its root session).
- Writes are serialized per session, and nothing is written when nothing changed, so the extension does not re-sync for no reason.
- The notes tools sit behind `execute`, so they add nothing to every request. Only `plan_ready` is pinned (about 100 tokens per request) so the plan agent can find it.
- The cleanup result is queued in the session inbox and reaches the model on its next turn, so it is the only command that leaves text in the context.

## Storage

Notes live in the plugin's own storage (`ctx.storage`, key `notes/<sessionID>`), shared by every project location. V2 session metadata would be the natural place, but in OpenCode 2.0.20 `ctx.session.update` drops `metadata` when a plugin calls it (a `title` update goes through; the same metadata update over HTTP works). Worth revisiting on a later release.

Notes a V1 agent wrote to `<session directory>/.opencode/session-notes/<sessionID>.json` are still returned by the RPC and imported on the next `session-notes_set` call. `session-notes_cleanup` prunes stored notes not updated for N days and deletes leftover V1 files in the worktree.
