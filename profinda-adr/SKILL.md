---
name: profinda-adr
description: Create and maintain Architecture Decision Records for the ProFinda project following ProFinda's Markdown format (Context / Decision / Consequences / Alternatives). Use when user says "write an ADR", "create an ADR", "architecture decision", or edits files under docs/adr/.
---

## Qualification gate

Before creating an ADR, check ALL three. If any fail, warn the user and continue — do not stop.

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will look at the code/system and wonder "why did they do it this way?"
3. **Real trade-off** — there were genuine alternatives and one was picked for specific reasons

If a check fails, say which one and why it matters:
- Failed (1): "This decision seems easy to reverse — ADRs are most valuable for hard-to-undo choices. Consider whether this needs documenting at all, or whether a code comment suffices."
- Failed (2): "This decision may not surprise a future reader — if the reasoning is obvious from the code, an ADR adds noise. Consider whether context is better placed inline."
- Failed (3): "No real trade-off identified — if there was only one viable option, an ADR may overstate the decision. Consider noting the constraint in a code comment instead."

Then proceed with the ADR.

---

## What qualifies as an ADR

- Architectural shape: monorepo, event sourcing, CQRS split
- Integration patterns between contexts: domain events vs synchronous HTTP
- Technology choices with lock-in: database, message bus, auth provider, deployment target
- Boundary and scope decisions: which context owns what data, explicit no-s are as valuable as yes-s
- Deliberate deviations from the obvious path — stops future engineers "fixing" something intentional
- Constraints not visible in the code: compliance, partner API contracts, performance SLAs
- Rejected alternatives when the rejection is non-obvious

---

## Workflow

### 1. Ask for topic

Ask: "What is your ADR topic/title?"

### 2. Determine next number

Scan `docs/adr/` for files matching `NNNN-*.md`. Take the highest `NNNN` and increment by 1.
If `docs/adr/` does not exist, create it. First ADR is `0001`.

### 3. Derive slug

Slug = lowercase title, spaces → hyphens, remove special chars.
Example: "Use PostgreSQL for write model" → `use-postgresql-for-write-model`

Additional rules:
- Strip or transliterate accented chars (é → e, ü → u)
- Remove all chars that are not a-z, 0-9, or hyphen
- Consecutive hyphens → single hyphen
- Truncate to 60 characters maximum
- Numbers preserved: "Use 3 read replicas" → `use-3-read-replicas`

### 3b. Dedup check

Scan `docs/adr/` for existing files. If any filename or title is similar to the
proposed ADR title, warn the user:
> "Found existing ADR that may overlap: NNNN-slug.md — confirm this is a new ADR?"
Proceed only after confirmation.

### 4. Filename

`docs/adr/NNNN-slug.md`

### 5. Fill the template

Load `TEMPLATE.md` (same directory as this skill). Replace all `{...}` placeholder with real content.
Remove all guide text inside `{...}` blocks — the final ADR must contain only real content, not instructions.
Replace `NNNN` in the title with the actual number (zero-padded to 4 digits).

After filling: scan the output for any `{` or `}` characters remaining.
If any are found, the template was not fully filled — strip or complete them before saving.

### 6. Cross-reference

If this ADR originated from an RFC, remind the user:
> "Add 'See RFC: NNNN — {title}' in the Context or Alternatives section."

### 7. Remind the user

After writing the file, say:
> Status, date, deciders, and approvers are tracked in Notion — not in this file.

---

## Key rules

- Never invent decisions — only document what the user confirms was decided
- Alternatives section may link to an RFC instead of inline prose
- Follow-up ADRs section: list related ADRs by number and title, or write "None"
- Do not add Status, Date, or Deciders fields — those live in Notion
- Keep the TL;DR summary to 1-3 sentences maximum
