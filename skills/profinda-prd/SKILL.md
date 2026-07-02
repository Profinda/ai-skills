---
name: profinda-prd
description: Turn conversation context and codebase understanding into a Product Requirements Document. Synthesises what is already known — does NOT interview the user. Use when user says "write a PRD", "create a PRD", "product requirements", invokes /profinda-prd, or edits files under docs/prd/.
---

## Workflow

### 1. Gather context silently

Do NOT interview the user. Synthesise what you already know from:
- The current conversation
- Codebase exploration (domain glossary, existing ADRs, RFCs)
- Any prototypes or spikes discussed

If critical information is missing, ask only targeted clarifying questions — never a full interview.

### 2. Explore the repo

If you haven't already, explore the codebase to understand the current state of the area
being changed. Use the project's domain vocabulary throughout the PRD, and respect any
ADRs or RFCs in the area you're touching.

### 3. Sketch modules

Identify the major modules you will need to build or modify. Actively look for opportunities
to extract **deep modules** — modules that encapsulate a lot of functionality behind a
simple, testable interface which rarely changes.

Present the module list to the user and ask:
- "Do these modules match your expectations?"
- "Which modules should have tests written for them?"

### 4. Determine next number

Scan `docs/prd/` for files matching `NNNN-*.md`. Take highest `NNNN`, increment by 1.
If `docs/prd/` does not exist, create it. First PRD is `0001`.

### 5. Derive slug

Slug = lowercase title, spaces to hyphens, remove special chars.
Example: "Usage Metrics Export" to `usage-metrics-export`

Additional rules:
- Strip or transliterate accented chars (e to e, u to u)
- Remove all chars that are not a-z, 0-9, or hyphen
- Consecutive hyphens to single hyphen
- Truncate to 60 characters maximum
- Numbers preserved: "Add 3 Export Formats" to `add-3-export-formats`

### 5b. Dedup check

Scan `docs/prd/` for existing files. If any filename or title is similar to the
proposed PRD title, warn the user:
> "Found existing PRD that may overlap: NNNN-slug.md -- confirm this is a new PRD?"
Proceed only after confirmation.

### 6. Fill the template

Load `TEMPLATE.md` (same directory as this skill). Replace all `{...}` placeholders
with real content synthesised from context.
Remove all guide text inside `{...}` blocks -- final PRD contains only real content.
Replace `NNNN` with actual number (zero-padded to 4 digits).
Filename: `docs/prd/NNNN-slug.md`

After filling: scan the output for any `{` or `}` characters remaining.
If any are found, the template was not fully filled -- strip or complete them before saving.

### 7. Revisions

After draft, user can say "revise {Section}" to update that section only.

### 8. Cross-reference

If this PRD relates to an existing RFC or ADR, add a reference:
> "See RFC: NNNN -- {title}" or "See ADR: NNNN -- {title}"

If this PRD will lead to architectural decisions, remind the user:
> "When implementation decisions are finalised, consider creating an ADR
> (profinda-adr skill) referencing this PRD."

---

## Key rules

- Do NOT interview the user section-by-section -- synthesise from existing context
- Ask targeted clarifying questions only when critical information is missing
- Never invent requirements -- only document what is known or confirmed
- Keep prose concise and actionable -- no fluff
- User stories should be extensive and cover edge cases
- Implementation decisions must not include file paths or code snippets (exception: decision-encoding snippets from prototypes, trimmed to the essential parts)
- Do not add Notion fields (Type, Team, Status, etc.) to the file -- those live in Notion
