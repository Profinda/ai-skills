# NNNN - {Short title of the decision}

{Write 1-3 sentences summarising: what situation forced this decision, what was decided, and the primary reason why.
Be concrete. A future reader must understand the decision without reading further.
Bad: "We decided to use X." Good: "We chose X over Y because Z constraint made Y impractical at our scale."}

---

### Context

{What is the issue or situation motivating this decision or change?

Guide for a strong Context section:
- Describe the business or technical situation as it stands *before* the decision — what pain, constraint, or opportunity exists
- Include relevant team, skill, or organisational factors that shaped the options
- State any non-negotiable constraints (compliance, partner contracts, performance SLAs, budget)
- Briefly name the trade-offs in the current situation that made doing nothing unacceptable}

### Decision

{What is the change being proposed or made?

Guide for a strong Decision section:
- State the decision directly in the first sentence — do not bury it
- Explain *why* this option was chosen: what properties made it the right fit given the Context
- Be specific enough that a future engineer can verify whether the decision is still being followed}

### Consequences

{What becomes easier or more difficult because of this change?

Guide for a strong Consequences section:
- List positive outcomes first, then negative ones or trade-offs accepted
- Call out any non-obvious downstream effects on other systems, teams, or future decisions
- If this decision will be reviewed after a period (e.g. one month post-deploy), say so here}

#### Follow-up ADRs

{List any ADRs that this decision triggers or depends on.
Format: "See ADR-NNNN — {title}" per line.
If none, write: None.}

#### Supersedes / Superseded by

{Optional. Include only if this ADR supersedes a previous one, or is itself superseded.
Format:
- "Supersedes ADR-NNNN — {title}"
- "Superseded by ADR-NNNN — {title}"
If neither applies, omit this section entirely.}

### Alternatives

{Other options considered and the reasons for not choosing them.

Options:
- Prose paragraphs per alternative — preferred when the rejection reason is nuanced
- Bullet list — preferred for three or more quick rejections
- Link to RFC document — acceptable when a full RFC already captures the analysis (e.g. "See RFC: {link}")

For each alternative state: what it is, what was attractive about it, and the specific reason it was not chosen.
Vague rejections ("too complex", "not scalable") are not useful — be precise.}
