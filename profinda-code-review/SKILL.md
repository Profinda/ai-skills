---
name: profinda-code-review
description: Performs code review of developer changes in three modes: quick (bugs, security, regressions), full (spec, correctness, architecture, tests), and fix (propose and apply fixes with re-review). Use when user invokes /profinda-review, asks for a code review, mentions "review my changes", or uses the words "quick review", "full review", or "review fix".
---

# ProFinda Code Review

## Quick start

Determine the review scope first, then pick a mode:

```bash
TARGET=$(git remote show origin | grep 'HEAD branch' | awk '{print $NF}')
BASE=$(git merge-base HEAD "origin/$TARGET" 2>/dev/null || git merge-base HEAD main)
git diff "$BASE"
```

Scope includes: all committed changes since branch diverged, staged changes, unstaged changes to tracked files, and related context (tests, migrations, public interfaces).

---

## Modes

### `/profinda-review quick`

Focus only on high-impact issues. Output at most a handful of comments.

Check:
- Real bugs (nil dereferences, off-by-one, wrong conditionals)
- Security (mass assignment, SQL injection, missing auth, exposed secrets)
- Regressions (broken existing behaviour, missing DB index for new queries)
- Critical missing tests (untested happy path or error path of changed code)

Skip: style, naming, architecture, minor code smells.

Format output as a short numbered list. Mark severity: `[critical]` or `[warning]`.

---

### `/profinda-review full`

Comprehensive review. Group findings by category.

Check (in order):
1. **Spec & correctness** - does the code do what the ticket/spec requires?
2. **Bugs** - same as quick, but exhaustive
3. **Security** - auth, authorisation policies, input validation, secrets
4. **Architecture** - engine isolation (engines must not access main-app models directly), correct use of Domain interfaces, Operations, Actions, Serializers
5. **Standards** - ProFinda conventions (see [REFERENCE.md](REFERENCE.md)), rubocop rules, frozen string literal, line/method length
6. **Code smells** - duplication, god objects, leaky abstractions, N+1 queries
7. **Tests** - coverage of edge cases, use of FactoryBot (no stubs for feature flags), spec organisation, BetterSpecs compliance

Format output grouped by category. Each finding: file + line reference, explanation, suggested fix.

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
5. After all fixes, run tests:
   ```bash
   bundle exec rspec <affected spec files>
   ```
6. Run rubocop on changed files:
   ```bash
   bundle exec rubocop <changed files>
   ```
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

## ProFinda-specific review checklist

See [REFERENCE.md](REFERENCE.md) for detailed checklists covering:
- Engine isolation rules
- Operations & steps
- Domain interface usage
- Policy registration
- Locale file sync
- Feature flags in tests
