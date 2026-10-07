# ProFinda AI Skills

Shared skill library for ProFinda repos. Skills teach the AI agent conventions, workflows, and patterns specific to ProFinda.

## Skill Tiers

Two tiers — pick based on scope:

| Tier | Source of truth | When to use |
|---|---|---|
| **Shared** | this repo, installed into each consuming repo with [`npx skills`](https://www.npmjs.com/package/skills) and pinned in its `skills-lock.json` | Used in multiple ProFinda repos |
| **Repo-local** | the consuming repo itself | Specific to one repo only |

## Example Directory Structure

Both tiers live side by side in the consuming repo and are committed there, so a fresh clone already has every skill (and Copilot code review can read them):

```
profinda_saas/
├── skills-lock.json                   ← source + hash of each shared skill
├── .agents/skills/                    ← read by Copilot, Codex, OpenCode, ...
│   ├── profinda-opera/                ← shared (from ai-skills, listed in the lock)
│   ├── profinda-git-workflow/         ← shared
│   └── profinda-domain-interface/     ← repo-local (not in the lock)
└── .claude/skills/                    ← read by Claude Code
    ├── profinda-opera -> ../../.agents/skills/profinda-opera
    └── ...
```

## Naming Convention

All skills use the `profinda-` prefix — e.g. `profinda-my-skill`.

**Rule:** if a skill describes conventions or tools used in 2+ ProFinda repos → add to `ai-skills` (shared). If it references engine-specific code or domain models unique to one repo → keep it repo-local.

## Current Skills

| Skill | Description |
|---|---|
| `profinda-adr` | Create and maintain Architecture Decision Records |
| `profinda-design` | Build in ProFinda's design language (product UI, prototypes, decks, marketing, docs): brand palette, Light/Dark themes, Horizon accents, Mulish type, glass surfaces, line icons, constellation background, components, motion. Ships a drop-in dark background asset. |
| `profinda-deck` | Build ProFinda presentation decks from content, not markup: a content-driven engine renders a list of slide dicts into one self-contained HTML deck — 17 layouts (title/section/statement/quote/bullets/two-col/media/gallery/charts/stats/big-number/cards/table/timeline/compare/feature/closing), inline SVG charts, embedded media, 3D flythrough, speaker notes, and per-slide Horizon theming. Builds on `profinda-design`. |
| `profinda-jira` | Jira workflow: Epic = living PRD, Story/Task, optional sub-task steps, dependencies as links, dual sign-off. Includes description templates (MD + ADF). Uses `mcp-atlassian` MCP. |
| `profinda-git-workflow` | Branching, committing, worktree, JIRA ticket conventions |
| `profinda-opera` | Step-based operation DSL (`Opera::Operation::Base`) |
| `profinda-prd` | **Deprecated** — the PRD now lives in the Epic. Use `profinda-jira`. |
| `profinda-rfc` | Create RFC documents |
| `profinda-write-a-pr` | Write PR titles and descriptions that follow the repo's `.github/PULL_REQUEST_TEMPLATE.md` |
| `profinda-write-a-skill` | Create new OpenCode skills with proper structure |

## Developer setup

Each skill that requires additional tooling documents its own setup. See the skill's `README.md`:

- [`profinda-jira/README.md`](profinda-jira/README.md) — mcp-atlassian MCP server setup

## Review Process

Before merging a new skill or significant change, get approval from **at least 4 developers**. Open a PR in `ai-skills` and request reviews — skills affect every repo that installs them.

## Adding a New Skill

Load the `profinda-write-a-skill` skill first. Do not write skills without it.

```
# In OpenCode/ClaudeCode chat:
/profinda-write-a-skill
```

Then decide tier (see **Skill Tiers** above) before writing.

## Install (recommended)

The easiest way — no developer tools needed. Open **Terminal** and paste:

```bash
curl -fsSL https://raw.githubusercontent.com/Profinda/ai-skills/main/install.sh -o /tmp/ai-skills-install.sh && sh /tmp/ai-skills-install.sh
```

It's a friendly wrapper around `npx skills` (see below) that:

1. Installs Node.js if it's missing (via Homebrew on macOS, the system package manager on Linux) — it asks first.
2. Checks you can read this repo on GitHub, and offers to sign you in through the browser if not.
3. Removes links left by the previous version of this installer.
4. Asks whether the skills are for **just you** (every project) or for **everyone on the current repo** (you commit the result), then lets you add, update or remove skills.
5. Optionally keeps your personal skills up to date with a weekly background update in `~/.zshrc`.

Re-run it any time to change your selection.

## Using shared skills in a repo

Shared skills are installed with the [`skills`](https://www.npmjs.com/package/skills) CLI and **committed** to the consuming repo. Developers who clone it get the skills with no extra step. Run these from the consuming repo's root.

### Add

```bash
npx skills add Profinda/ai-skills -s profinda-opera -s profinda-git-workflow -a claude-code -y
git add -f .agents/skills .claude/skills skills-lock.json   # -f in case a global gitignore hides them
```

`-a claude-code` adds the `.claude/skills` symlinks; agents that read `.agents/skills` natively (Copilot, Codex, OpenCode, ...) need no flag. Run `npx skills add Profinda/ai-skills --list` to see what's available.

### Update

```bash
npx skills update -p -y
```

Commit the result; the `skills-lock.json` diff shows which skills changed. Never edit installed copies in the consuming repo — change the skill here, merge, then update.

Updating is the consuming repo's responsibility: merging here changes nothing until each repo runs the update and merges it. To automate this Dependabot-style, a consuming repo can add a scheduled GitHub Action that runs `npx skills update -p -y` and opens a PR when `skills-lock.json` changes (it needs a token with read access to `Profinda/ai-skills`).

### Remove

```bash
npx skills remove profinda-<name> -y
```

Always name the skill: `npx skills remove --all` also deletes the repo's own local skills, since they share `.agents/skills`.

### Restore from the lock file

```bash
npx skills experimental_install -y
```

## Personal (global) install

The installer above does this when you pick "just me". The equivalent command, to have a shared skill in every repo on your machine without committing it anywhere:

```bash
npx skills add Profinda/ai-skills -g
```

The CLI asks which skills and which agents to install to; `npx skills update -g -y` refreshes them.

## Add a repo-local skill

In the consuming repo, put it in `.agents/skills/<skill-name>/` and symlink it for Claude Code:

```bash
ln -s ../../.agents/skills/<skill-name> .claude/skills/<skill-name>
```

The CLI leaves skills that aren't in `skills-lock.json` alone (`npx skills list` shows them as `Source: local`). Pick a name that doesn't exist here, or a later `npx skills add` overwrites it.

## Migrating from the submodule setup

Repos that used the old `.claude/skills/shared` submodule:

```bash
git rm .claude/skills/shared   # also drops its .gitmodules entry; git rm .gitmodules if it's now empty
find .claude/skills -maxdepth 1 -type l -lname 'shared/*' -delete
# drop the .claude/skills/profinda-* lines from .gitignore, then follow "Add" above
```

Developers who ran the old `install.sh` locally must delete the `shared/*` symlinks and `.claude/skills/shared` before pulling the migrated repo. Personal installs made by the old `install.sh` keep working (they symlink into `~/.config/ai-skills`). Re-running the new installer removes those links, reinstalls through `npx skills`, and replaces the old weekly auto-update block in `~/.zshrc`.
