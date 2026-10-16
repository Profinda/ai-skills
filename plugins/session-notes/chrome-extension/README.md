# OpenCode Session Notes browser extension

A Manifest V3 extension for Chrome, Brave, Edge and other Chromium browsers. It adds an editable notes popover next to the session title in the OpenCode V2 web UI: worktree and branch, an Intent (why the session exists), a separate Progress field (what is done, what is left), Jira epic and ticket, one or more PR links, and a preview link.

> **Requires OpenCode V2 (2.0.0 or newer) and the `session-notes` plugin from the parent folder.** The extension reads and writes notes through that plugin's RPC, so install and restart the plugin first (see [`../README.md`](../README.md), steps 1 to 4). On OpenCode V1 there is no V2 web UI and no plugin RPC, so nothing here works.

## Install (instructions for the agent configuring this)

The extension is not published to a store. The user loads it unpacked, once per browser profile. You cannot click through the browser for them, so give them these steps with the real folder path filled in.

1. Confirm the plugin is running: `opencode plugin list` shows `session-notes`.
2. Get the folder path. If the repo was cloned as the README says, it is `~/.config/ai-skills/plugins/session-notes/chrome-extension`. Run `echo "$HOME/.config/ai-skills/plugins/session-notes/chrome-extension"` and print the result, since the browser file picker does not expand `~`. On macOS the picker hides dot folders: press `Cmd+Shift+G` and paste the path.
3. Tell the user to open the extensions page:
   - Brave: `brave://extensions`
   - Chrome: `chrome://extensions`
   - Edge: `edge://extensions`
4. Turn on the **Developer mode** toggle on that page (top right in Chrome and Brave).
5. Click **Load unpacked** and select the `chrome-extension` folder above. The card "OpenCode Session Notes" appears. The extension has no toolbar button, so there is nothing to pin.
6. Open the web UI. Run `opencode pair` in a terminal: it prints a one-time link that opens the web UI on `http://localhost:<port>` (or `127.0.0.1`) and signs the browser in. Open a session. Next to the session title the `ⓘ` button should appear.

If nothing appears: the page must be `http://localhost:*` or `http://127.0.0.1:*` (the extension is limited to those), the tab must have been loaded after the extension was installed (hard-refresh with `Cmd+Shift+R`), and the web UI must have been opened with `opencode pair`. Without the token that `opencode pair` stores, every request is a 401 and no chips are shown.

### Update

After a `git pull` of `~/.config/ai-skills`, click the reload icon on the extension's card, then hard-refresh every open OpenCode web tab. A plain reload does not reconnect content scripts that are already running in open tabs.

### Uninstall

Click **Remove** on the extension's card. Notes typed in the browser are kept in `chrome.storage.local` and go away with the extension. Notes saved by the plugin stay in OpenCode.

## Use

Open any session in the web UI. Next to the session title you see:

- `⎇ branch`: as reported by the agent through `session-notes_set` (read-only, hover for the full worktree path)
- `SP-123 ↗`: the Jira ticket, once set, links straight to Jira
- `PR#345 ↗`: one chip per saved PR (a session can have several), showing the PR number so you can tell sessions apart at a glance
- `Preview ↗`: only shown once a URL is saved
- `ⓘ`: click to open the notes popover (turns green once something is saved)

The popover, top to bottom: Worktree (read-only), Intent (why this session exists, meant to stay stable), Jira Epic and Jira Ticket (each with an open-in-Jira button), Title (with a copy button), a Pull Requests list (add and remove rows freely), Local Preview URL, and at the bottom Progress, a large box for what is done, what is left and what phase you are in, meant to be updated often. Click **Save**. Reopening the same session, even after closing the tab or browser, restores what you typed, because notes are keyed by the session ID. Colors follow whatever OpenCode theme you use, through the app's own CSS variables.

Splitting Intent from Progress is the point. With many tabs open across projects, going back to one after a while should answer "why does this exist" and "where did we leave off" without scrolling to the first message.

## Agent-populated notes

An agent can fill all of this in instead of you typing it, through the `session-notes` plugin and its commands:

- `/session-notes [optional progress text]` writes the session's Progress (always fresh), Intent (set once, kept afterward), a PR link (added to the list, not replacing it), preview link, and Jira ticket and epic (taken from the branch name when not obvious), through the `session-notes_set` tool. Every field except Progress and PR is kept when omitted.
- `/session-notes-cleanup [days]` deletes stored notes older than N days (default 30).

The plugin keeps notes per session ID, so two sessions in the same worktree never mix. The extension polls the plugin's RPC (`POST /api/rpc/session-notes/get`) and syncs into `chrome.storage` whenever `updatedAt` changes. Syncing is skipped while the popover is open, so an agent run never overwrites what you are typing.

## Notes

- It only touches `http://127.0.0.1:*` and `http://localhost:*` pages.
- The only permission it asks for is `storage` (for `chrome.storage.local`).
- Requests go to the same origin. `opencode pair` gives the web UI a token (no cookie) that the UI keeps in `localStorage` (`opencode.global.dat:server`). The extension reads it from there and sends it as Basic auth (user `opencode`). It stores no credentials of its own. The session's directory comes from `/api/session/{id}`. If a session tab is backed by a different OpenCode server (another port added in Settings), the plugin lookup will not resolve for it, but notes typed by hand still work because they are stored locally.
- Jira links point at `https://profinda.atlassian.net/browse/<ticket>`. Edit `JIRA_BASE_URL` in `content.js` to change that (the terminal UI has the same constant in `../tui.tsx` and `../lib/notes.ts`).
