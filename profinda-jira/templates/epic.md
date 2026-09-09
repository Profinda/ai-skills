<!--
EPIC = the living PRD. Starts light, enriched through 3-amigos, sizing and risk,
then gates into development. Risk and high-level architecture are done ONCE here —
Stories/Tasks do not repeat them.
Uses Jira native features, no duplication:
- Stage = the Jira STATUS field (not written here)
- Child Stories/Tasks = the Jira child-issues / links panel (not listed here)
- Open questions & discussion = Jira COMMENTS (not frozen here)
- t-shirt size, Product Manager, Pod, Customer, Source, AI Service, Product
  Involvement, Notion link = Jira FIELDS (not written here)
-->

## {light-green} A · CHANGE LOG
- PRD version: 1.0
- Last substantive change: {date} — {what changed and why}

## {green} B · PROBLEM DEFINITION & FEASIBILITY

### 1. Problem & why now
What problem are we solving? Why does it matter now? Evidence if available.

### 2. Goals & success metrics
- Goal:
- Success metric(s): user metric or technical measure. How we know it worked.

### 3. Who is affected (personas)
User persona(s), customer segment, or internal team. N/A for pure infra — say why.

## {teal} C · SCOPE

### 4. Scope (intent) & non-goals
- In scope (intent): behaviours/capabilities this epic delivers.
- Non-goals: explicitly NOT included.

## {navy} D · HIGH-LEVEL TECHNICAL DESIGN

### 5. High-level solution & architecture
System-level approach. Services, data flows, contracts affected.
No implementation detail, no file paths. (Detailed design lives on Stories/Tasks.)

## {red} E · RISK ASSESSMENT (done ONCE, here)
Full framework in Notion: **Risk Management / Risk Assessment Framework**. This
table lists **every risk type to evaluate** so nothing is skipped. For each type:
score it, or mark **N/A** with a one-line reason. Do not delete rows — an empty
row means "not yet assessed".

Scoring: **Critical = 8 · High = 5 · Medium = 3 · Low = 1 · N/A = 0**.
Escalate before build if the total is **≥ 17**, or if any single risk is Critical.

| Risk type | Level (score) | Description (or N/A + reason) | Mitigation |
|---|---|---|---|
| Data | | | |
| Customisation | | | |
| UX | | | |
| InfoSec | | | |
| Performance | | | |
| Business | | | |
| Political | | | |
| Resource | | | |
| Commercial | | | |
| Cost | | | |
| AI | | | |

**AI risk — extra detail (fill if the AI row is scored):** evaluate ethical,
social and legal impact — algorithmic bias, privacy, misinformation, societal
harm — at individual, group and societal level.

- **Total risk score:** {sum of all rows}
- **Highest single risk:** {type + level}
- **InfoSec (SOG) reviewed?** Yes / No / N/A — required if any InfoSec risk is
  Medium or above.
- **Escalated?** Yes / No — required if total ≥ 17 or any risk is Critical.

## {orange} F · PRD APPROVAL (gate to development)
Sign-off is recorded here AND via the Jira status transition. Auditors (SOC-2 /
ISO 27001) require the attributable record below — the status change alone is not
a valid approval.

| Role | Name & date | Approved / Rejected (notes) |
|------|-------------|-----------------------------|
| Product | | |
| Lead Engineer | | |
