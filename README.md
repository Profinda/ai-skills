# ProFinda AI Skills

Shared skill library for ProFinda repos. Skills teach the AI agent conventions, workflows, and patterns specific to ProFinda.

## Skill Tiers

Two tiers — pick based on scope:

| Tier | Location | When to use |
|---|---|---|
| **Shared** | this repo, mounted via submodule at `<repo>/.claude/skills/shared/` | Used in multiple ProFinda repos |
| **Repo-local** | `<repo>/.claude/skills/<skill-name>/` | Specific to one repo only |

## Example Directory Structure

```
~/.config/opencode/skills/     ← global/personal skills
    caveman/
    grill-me/

profinda_saas/
└── .claude/
    └── skills/
        ├── shared/            ← git submodule → ai-skills (this repo)
        │   ├── profinda-adr/
        │   ├── profinda-git-workflow/
        │   ├── profinda-opera/
        │   ├── profinda-rfc/
        │   └── profinda-write-a-skill/
        └── profinda-domain-interface/   ← repo-local skill (api only)
```

## Naming Convention

All skills use the `profinda-` prefix — e.g. `profinda-my-skill`.

**Rule:** if a skill describes conventions or tools used in 2+ ProFinda repos → add to `ai-skills` (shared). If it references engine-specific code or domain models unique to one repo → keep it repo-local.

## Current Skills

| Skill | Description |
|---|---|
| `profinda-adr` | Create and maintain Architecture Decision Records |
| `profinda-jira` | Jira workflow: Epic = living PRD, Story/Task, optional sub-task steps, dependencies as links, dual sign-off. Includes description templates (MD + ADF). Uses `mcp-atlassian` MCP. |
| `profinda-git-workflow` | Branching, committing, worktree, JIRA ticket conventions |
| `profinda-opera` | Step-based operation DSL (`Opera::Operation::Base`) |
| `profinda-prd` | **Deprecated** — the PRD now lives in the Epic. Use `profinda-jira`. |
| `profinda-rfc` | Create RFC documents |
| `profinda-write-a-skill` | Create new OpenCode skills with proper structure |

## Developer setup

Each skill that requires additional tooling documents its own setup. See the skill's `README.md`:

- [`profinda-jira/README.md`](profinda-jira/README.md) — mcp-atlassian MCP server setup

## Review Process

Before merging a new skill or significant change, get approval from **at least 4 developers**. Open a PR in `ai-skills` and request reviews — skills affect all repos using the submodule.

## Adding a New Skill

Load the `profinda-write-a-skill` skill first. Do not write skills without it.

```
# In OpenCode/ClaudeCode chat:
/profinda-write-a-skill
```

Then decide tier (see **Skill Tiers** above) before writing.

## Using in a Repo

### Initial setup

```bash
git submodule add git@github.com:Profinda/ai-skills.git .claude/skills/shared
git commit -m "Add ai-skills shared submodule"
```

### Clone with submodules

```bash
# Fresh clone
git clone --recurse-submodules <repo-url>

# Already cloned without submodules
git submodule init && git submodule update
```

### Update to latest shared skills

```bash
git submodule update --remote .claude/skills/shared
git add .claude/skills/shared
git commit -m "Bump ai-skills submodule"
```

### Make shared skills available in Claude

Shared skills live in `.claude/skills/shared/` but must be symlinked to `.claude/skills/` to appear in Claude.

Run this script once after cloning:

```bash
for dir in .claude/skills/shared/*/; do
  ln -s "shared/$(basename "$dir")" ".claude/skills/$(basename "$dir")"
done
```

This creates symlinks so each skill in `shared/` is accessible as a direct child of `.claude/skills/`.

**Note:** Add these symlinks to your repo's `.gitignore` so they stay local.

### Add a repo-local skill

Place it directly in `.claude/skills/<skill-name>/` — no submodule needed. It will be picked up by AI client automatically.
