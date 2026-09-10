# ProFinda Jira description templates

The description templates for each issue type. Each exists in **two formats that
must be kept in sync**:

| Issue type | Markdown (read/edit) | Jira ADF (paste into Jira) |
|---|---|---|
| Epic | `epic.md` | `adf/epic.adf.json` |
| Story | `story.md` | `adf/story.adf.json` |
| Task | `task.md` | `adf/task.adf.json` |
| Sub-task | `subtask.md` | `adf/subtask.adf.json` |

## Why two formats

- **Markdown** is the human- and agent-readable source. This is what people read
  in the repo, what the skill loads, and what reviewers edit.
- **ADF** (Atlassian Document Format) is what Jira actually stores. The styled
  Jira template tickets and any API that writes a description need ADF. People
  cannot read ADF JSON, so it is generated *from* the Markdown, not hand-written.

## Sync rule (important)

**The Markdown is the source of truth. The ADF is generated from it.**

When you change a template:
1. Edit the `.md` file.
2. Regenerate the matching `adf/*.adf.json` (see `adf/README.md`).
3. Commit both in the same PR. A CI check fails if they drift.

Never edit the ADF by hand — your change will be lost on the next regeneration,
and the two formats will silently diverge.

## Conventions these templates rely on

- **Dependencies** are **Jira issue links** (`blocks` / `is blocked by`), never a
  free-text section. The link graph is the source of truth; it is queryable and
  drives the board.
- **The plan lives in the Story/Task description.** It may be drafted as a local
  `PLAN.md` in the loop, but it must end up in Jira so it survives independent of
  any developer's machine.
- **Steps are sub-tasks OR a checklist** in the parent — the dev/agent chooses.
  Sub-tasks are recommended for multi-session/parallel work and for capturing
  per-step thinking durably.
- **Sign-off is recorded in the template AND via the status transition.** SOC-2 /
  ISO 27001 auditors do not accept a status change alone as a valid approval.
- **Fields, not prose.** T-shirt size, estimate (Sum of Story Points), Product
  Manager, Pod, Customer, Source, AI Service, Release notes, Fix version live in
  Jira fields — do not duplicate them in the description.
