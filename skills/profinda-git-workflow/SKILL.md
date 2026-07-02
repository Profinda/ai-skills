---
name: profinda-git-workflow
description: ProFinda git workflow conventions. Use when user asks about branching, committing, creating a worktree, pushing, or mentions a JIRA ticket (`SP-XXXX`).
---

# Git Workflow

## Quick Start

```bash
# 1. Create worktree + branch (requires SP ticket)
git worktree add .worktrees/SP-1234-my-feature -b SP-1234-my-feature

# 2. Work in the worktree
cd .worktrees/SP-1234-my-feature

# 3. Commit
git commit -m "Add user auth endpoint [SP-1234]"

# 4. End of session — clean up worktree (ask user first)
cd /path/to/main/repo
git worktree remove .worktrees/SP-1234-my-feature
```

## Protected Branches
Never commit directly to: `master`, `staging`, `integration`, `uat`, `production`. Always use a feature branch.

## JIRA Ticket
Required before any branch, worktree, or commit. Format: `SP-XXXX`. Ask user if not provided.

## Worktrees
All worktrees go in `.worktrees/` (gitignored). Example: `.worktrees/SP-1234-my-feature`.

At the end of a session, suggest cleaning up the worktree:
```bash
git worktree remove .worktrees/SP-1234-my-feature
git branch -d SP-1234-my-feature  # only after branch is merged
```
Always ask explicit confirmation before removing — worktree removal is destructive.

## Branch Naming
`SP-XXXX-<short-description>` — e.g. `SP-1234-add-user-auth`

## Commit Messages
Suffix with ticket in brackets: `Add user auth endpoint [SP-1234]`
Keep subject line short (50 chars or less).

## Destructive/Remote Operations — Always Ask First

Before executing ANY command below, STOP. State: (1) exact command, (2) what it does, (3) reversible or not. Then ask explicit yes/no confirmation. No exceptions.

| Command | Notes |
|---|---|
| `git push` (any flags) | Remote mutation |
| `git push --force` / `--force-with-lease` | Destructive remote |
| `git rebase` | Rewrites history |
| `git reset` (when commits already pushed) | Destructive |
| `git commit --amend` (when commits already pushed) | Destructive |
| `git branch -d` / `-D` | Branch deletion |
| `git stash drop` / `git stash clear` | Irreversible |
| `git clean` (any flags, especially `-f`, `-fd`, `-fx`) | Irreversible |
| `git worktree remove` | Destructive |
| `gh pr merge` / `gh pr close` | Remote mutation |
| `gh pr edit` (base change, CI-triggering labels) | Remote mutation |
| `gh release create` / `gh release delete` | Remote mutation |
| `gh repo delete` | Irreversible |
