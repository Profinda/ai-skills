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
| `profinda-jira` | Jira workflow: PRD in Epic, Stories, sub-tasks as progress tracker, HANDOFF comments |
| `profinda-jira-cli` | jira-cli and REST API command reference — field IDs, payload templates, transitions |
| `profinda-git-workflow` | Branching, committing, worktree, JIRA ticket conventions |
| `profinda-opera` | Step-based operation DSL (`Opera::Operation::Base`) |
| `profinda-prd` | Write a Product Requirements Document from conversation context |
| `profinda-rfc` | Create RFC documents |
| `profinda-write-a-skill` | Create new OpenCode skills with proper structure |

## Developer setup — jira-cli

`profinda-jira-cli` and `profinda-jira` require `jira-cli` to be installed locally.

```bash
brew install ankitpokhrel/tap/jira-cli
jira init   # follow prompts: instance = https://profinda.atlassian.net, project = SP
```

Generate a Jira API token at https://id.atlassian.com/manage-profile/security/api-tokens and set both variables in your shell:

```bash
# ~/.zshrc.local (or equivalent)
export JIRA_EMAIL="your.name@profinda.com"
export JIRA_API_TOKEN="your-token-here"
```

Verify setup:

```bash
jira me   # should return your Jira display name
```

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

### Add a repo-local skill

Place it directly in `.claude/skills/<skill-name>/` — no submodule needed. It will be picked up by AI client automatically.
