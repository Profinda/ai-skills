---
name: profinda-prd
description: DEPRECATED. The ProFinda PRD now lives in the Jira Epic, not a markdown file. Use the profinda-jira skill instead. This skill is kept only as a pointer.
---

# profinda-prd — DEPRECATED

**The PRD is now the Jira Epic.** We no longer write PRD markdown files under
`docs/prd/`.

Use **`profinda-jira`** instead:
- The Epic description IS the PRD (see `profinda-jira/templates/epic.md`).
- It is a living document: starts light, enriched through 3-amigos, sizing and
  risk, and must be complete before entering development.
- Stories and Tasks under the Epic carry the delivery detail; risk and
  high-level architecture live once on the Epic.

Why the change: a PRD on someone's disk (or a markdown file that drifts from the
tickets) is not durable, not queryable, and not visible to the team or to agents
resuming the work. Jira is the single source of truth.

> If you have old `docs/prd/*.md` files, migrate their content into the relevant
> Epic description using `profinda-jira`, then remove the file.
