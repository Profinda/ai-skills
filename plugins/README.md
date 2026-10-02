# ProFinda OpenCode plugins

Plugins for OpenCode, shared the same way the skills in the repo root are. Each folder is one self-contained plugin with its own README that says how to install it.

> **These plugins require OpenCode V2 (2.0.0 or newer).** They use the V2 plugin API and do not load on OpenCode V1. Run `opencode --version` before installing anything from here.

| Plugin | What it does |
|---|---|
| [`team`](team/README.md) | Lets an `orchestrator` session spawn and coordinate `player` sessions that report and message each other through `team_*` tools. Ships the two agents, the playbook skill and the `team` / `prs` shell helpers. |
| [`session-notes`](session-notes/README.md) | Agents record intent, progress, Jira ticket and PRs per session. Shown in the terminal UI (sidebar and `/notes`) and in the web UI through the Chrome/Brave extension that ships in `session-notes/chrome-extension/`. |

## Layout of a plugin

```
plugins/<name>/
├── README.md        what it is, requirements, install steps for the agent that sets it up
├── index.ts         default export { id, setup }, the V2 plugin definition
├── package.json
├── agents/          optional: agent definitions to link into ~/.config/opencode/agents/
├── skills/          optional: skills to link into ~/.config/opencode/skills/
└── chrome-extension/  optional: a browser extension that pairs with the plugin, with its own README
```

Plugins are installed from the `~/.config/ai-skills` clone (the one the skills installer maintains) by adding the plugin folder to `plugins` in `~/.config/opencode/opencode.json`, then symlinking any agents or skills it ships. The installer script does not manage plugins yet, so follow the plugin's README.
