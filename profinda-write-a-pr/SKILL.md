---
name: profinda-write-a-pr
description: Write pull request titles and descriptions that follow the current repo's .github/PULL_REQUEST_TEMPLATE.md. Use when opening a PR, writing or editing a PR body/description, or filling in a PR checklist.
---

# Writing a PR

## Workflow

1. Read the repo's PR template (`.github/PULL_REQUEST_TEMPLATE.md` or `.github/pull_request_template.md`).
   Fill its sections in order; never add, rename, or remove sections (the optional Details block is the only
   addition). No template: use `## What` and `## To test`.
2. List every file changed against the base branch before drafting anything.
3. Fill each section using the rules below. Rules for a section the template doesn't have don't apply.

## Filling each section

- **PR title**: summarise everything the PR changes, not only its most frequent change or verb.
- **`JIRA:`**: ticket from the branch name (`SP-XXXX-...`); see the `profinda-git-workflow` skill.
- **Other link lines** (`UI:`, `API:`, `TEST RUN:`, ...): link the paired PR or run if one exists, else `N/A`.
- **`## What`**: see "Writing `## What`" below. Skip only for trivial one-liners.
- **Checklist tables**: copy the table verbatim and answer every row (never delete one to dodge it). Keep each
  note to a short phrase ("N/A", "Data-only migration"), never restating `## What`. Add any link the
  template requires for a given answer (e.g. release notes, Slack notification).
- **`## To test`**: numbered steps a reviewer can execute (action, endpoint, payload) — not "run the specs".
  `CURRENT`/`EXPECTED` state what the tester observes, not the cause or fix already in `## What`. For
  performance changes, put measured numbers in `CURRENT`/`EXPECTED` (a before/after table if there are
  several) and the script or command that produced them. Evidence stays visible, never in a toggle.
- **`## Screenshots`**: leave `### Before:` / `### After:` blank. User-filled only — never add, describe,
  or fabricate a screenshot here.
- **`## cURL requests`**: a runnable `curl` for each new/changed endpoint. Omit the section only when no
  API surface changed.
- **Details** (optional, any repo): after the last template section, a collapsed
  `<details><summary>Details</summary>…</details>` block for investigation findings, suggestions, next
  steps, and concerns that don't fit the template. It keeps them in git history for later agents without
  cluttering the review. Don't repeat anything stated above or narrate how the PR was built. Omit when empty.

## Writing `## What`

Skip preambles and keep prose brief. Pick the smallest view that makes the change clear — see
[REFERENCE.md](REFERENCE.md) for pseudocode, call-tree, file-tree, Mermaid, and diff examples. Use at most
one or two, place each next to the short text it supports, and keep only the files, calls, and states
needed to explain the change.

- Describe every change, including unrelated fixes; a change that doesn't fit the diagram still gets a line
  of text rather than being left out.
- State a fix applied at several sites once, then list the sites — no per-site "same"/"ditto" lines.
- Describe only the shipped diff; a bug introduced and fixed before pushing has no reviewer value.
- Describe changes mechanically (old condition → new condition), not domain intent the diff doesn't
  establish.
