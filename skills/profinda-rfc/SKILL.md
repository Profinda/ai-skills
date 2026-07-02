---
name: profinda-rfc
description: Create RFC documents for the ProFinda project following ProFinda's Markdown format. Guides dev through section-by-section interview then writes polished draft to docs/rfc/. Use when user says "write an RFC", "create an RFC", "request for comments", invokes /profinda-rfc, or edits files under docs/rfc/.
---

## Qualification gate

Before starting RFC, check ALL three. If any fail, warn the user and continue — do not stop.

1. **Real problem** — is there a concrete pain point, not just a preference?
2. **Alternatives exist** — has at least one other approach been considered?
3. **Decision not already made** — if it's already decided, an ADR is more appropriate

If a check fails, say which one and why it matters:
- Failed (1): "No concrete problem stated — the RFC may be hard to evaluate. Consider anchoring it to a specific incident, metric, or constraint."
- Failed (2): "No alternatives considered yet — reviewers will ask. Consider noting at least one other approach in the Alternatives section."
- Failed (3): "This sounds like a decided outcome — consider writing an ADR instead (profinda-adr skill)."

Then proceed with the RFC.

---

## Workflow

### 1. Ask for topic

Ask: "What is your RFC topic/title?"

### 2. Determine next number

Scan `docs/rfc/` for files matching `NNNN-*.md`. Take highest `NNNN`, increment by 1.
If `docs/rfc/` does not exist, create it. First RFC is `0001`.

### 3. Derive slug

Slug = lowercase title, spaces → hyphens, remove special chars.
Example: "Migrate to TypeScript" → `migrate-to-typescript`

Additional rules:
- Strip or transliterate accented chars (é → e, ü → u)
- Remove all chars that are not a-z, 0-9, or hyphen
- Consecutive hyphens → single hyphen
- Truncate to 60 characters maximum
- Numbers preserved: "Use 3 read replicas" → `use-3-read-replicas`

### 3b. Dedup check

Scan `docs/rfc/` for existing files. If any filename or title is similar to the
proposed RFC title, warn the user:
> "Found existing RFC that may overlap: NNNN-slug.md — confirm this is a new RFC?"
Proceed only after confirmation.

### 4. Section-by-section interview

For each section in order, ask: "Do you want to fill in **{Section}**?"
- For **Abstract, Problem, Solution, Risks, Rollback**: add "(recommended — good practice)"
- If yes: ask 2-3 targeted questions (use internal guidance below)
- If no: write `_Skipped by author._` under the heading — do not omit the heading

### 5. Fill the template

Load `TEMPLATE.md`. Replace all `{...}` placeholders with real content from interview.
Remove all guide text inside `{...}` blocks — final RFC contains only real content.
Replace `NNNN` with actual number (zero-padded to 4 digits).
Filename: `docs/rfc/NNNN-slug.md`

### 6. Revisions

After draft, dev can say "revise {Section}" to update that section only.

### 7. Cross-reference

If this RFC is likely to result in an architectural decision, remind the user:
> "When the decision is made, create an ADR (profinda-adr skill) and reference this RFC
> in the ADR's Context section: 'See RFC: NNNN — {title}'"

### 8. Remind the user

After writing the file, say:
> Paste this into the ProFinda Notion RFC database and fill in: **Type, Team, Status, Epic/Ticket, Reviewers, Approvers, Tags**.

---

## Internal guidance per section

Use these to ask better questions. Do not surface guide text to dev.

| Section | Key questions to ask |
|---|---|
| Abstract | Ask this **last** — easier after other sections are complete. Core idea in one sentence? Primary benefit? |
| Problem | What breaks/hurts today? Evidence — incidents, metrics, postmortems? |
| Solution | How does it fix the problem? Immediate benefits? How to measure success? |
| Anticipated Difficulties | What will be hard during rollout? Any mitigations? |
| Risks | What could go wrong but might not? Likelihood? |
| Previous Examples | Prior art internally or externally? Failures too — useful for risk context. |
| Expert Opinion | Any experts consulted? Names or links? |
| Estimated Costs | Dev time? Tooling cost? Reskilling effort? |
| Implementation | PoC → Scale → Enforce. Rough timeline? |
| Completion & Evaluation | How to measure success at 30 / 90 / 365 days? |
| Rollback | How to revert? What triggers a rollback decision? |

---

## Key rules

- Never invent content — only document what dev confirms
- Keep prose concise, TLDR-friendly — no fluff
- Abstract is often best written last
- Do not add Notion fields (Type, Team, Status, etc.) to the file — those live in Notion
