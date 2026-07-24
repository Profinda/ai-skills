---
name: profinda-code-review
description: Performs code review in three modes: quick (bugs, security, regressions), full (spec, correctness, naming, tests, linting, JIRA ticket), and fix (propose and apply fixes with re-review). Loads project-specific rules from $REPO/AI_REVIEW.md when present. Use when user invokes /profinda-review, asks for a code review, mentions "review my changes", or uses the words "quick review", "full review", or "review fix".
---

# Code Review

## Quick start

Determine the review scope first, then pick a mode:

```bash
TARGET=$(git remote show origin | grep 'HEAD branch' | awk '{print $NF}')
BASE=$(git merge-base HEAD "origin/$TARGET" 2>/dev/null || git merge-base HEAD main)
git diff "$BASE"
```

Scope includes: all committed changes since branch diverged, staged changes, unstaged changes to tracked files, and related context (tests, config, public interfaces).

---

## Project-specific rules

**Before running any review**, check whether the repository contains a file at `$REPO/AI_REVIEW.md` (i.e. `AI_REVIEW.md` in the repository root).

- If it exists: read it fully and merge its rules into every applicable review category below. Project rules **take precedence** over generic defaults when they conflict.
- If it does not exist: proceed with generic defaults only.

> `AI_REVIEW.md` is the per-repository convention file. Teams use it to document stack-specific patterns, architectural decisions, naming conventions, required linters, and anything else reviewers must know.

---

## Modes

### `/profinda-review quick`

Focus only on high-impact issues. Output at most a handful of comments.

Check:
- **Bugs** — nil/null dereferences, off-by-one errors, wrong conditionals, unreachable code
- **Security** — injection vectors, missing auth, exposed secrets, unsafe deserialization
- **Regressions** — broken existing behaviour, missing DB index for new queries, removed public API without deprecation
- **Critical missing tests** — untested happy path or error path of changed code

Skip: style, naming, architecture, minor code smells.

Format output as a short numbered list. Mark severity: `[critical]` or `[warning]`.

---

### `/profinda-review full`

Comprehensive review. Group findings by category.

Check (in order):

1. **Bugs** — exhaustive: logic errors, edge cases, error handling, resource leaks
2. **Security** — auth & authorisation, input validation, secrets, sensitive data in logs, dependency vulnerabilities
3. **Typos & misspellings** — identifiers, comments, string literals, documentation
4. **Naming & consistency** — variable/function/class names follow project conventions; consistent terminology across the changed files
5. **Design & architecture** — module boundaries respected, single responsibility, no leaky abstractions, correct layer for the logic
6. **Spec & correctness** — does the code match the ticket/requirement? If a JIRA ticket number is available (from branch name, commit message, or PR description), verify the implementation covers the acceptance criteria
7. **Linting** — check against the linter configured in the project (look for `.rubocop.yml`, `eslint.config.*`, `pyproject.toml`, `.flake8`, `biome.json`, etc.). Flag any rule violations you can detect statically; note which rules apply
8. **Tests** — coverage of happy path and error/edge cases, test isolation, no flaky patterns
9. **Project-specific rules** — anything defined in `AI_REVIEW.md` that does not fit the above categories

Format: group findings by category. Each finding: file + line reference, explanation, suggested fix.

---

### `/profinda-review fix`

Apply fixes after a review. Use this workflow:

1. Run `/profinda-review full` first (or use existing review output).
2. Group all findings into fix areas (e.g. "auth bug in X", "missing index", "N+1 in Y").
3. **Show the plan** before touching any file:
   ```
   Fix plan:
   1. [area] short description — files affected
   2. ...
   Proceed? (yes / adjust plan)
   ```
4. After confirmation, apply fixes one area at a time.
5. After all fixes, run the project's test suite on affected files.
6. Run the project's linter on changed files.
7. Perform a second `/profinda-review quick` pass on the applied changes and report any remaining issues.

---

## Scope resolution

```bash
# Determine target branch
TARGET=$(gh pr view --json baseRefName -q .baseRefName 2>/dev/null) \
  || TARGET=$(git remote show origin | grep 'HEAD branch' | awk '{print $NF}') \
  || TARGET=main

# Compute merge base
BASE=$(git merge-base HEAD "origin/$TARGET")

# Full diff (committed + staged + unstaged tracked)
git diff "$BASE"
```

If the diff is very large (>500 changed lines), ask the user whether to narrow scope before proceeding.

---

## Generic review checklist

See [REFERENCE.md](REFERENCE.md) for detailed, language-agnostic checklists covering all review categories.
