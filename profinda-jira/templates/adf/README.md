# ADF templates (generated — do not edit by hand)

These `*.adf.json` files are the Jira Atlassian Document Format versions of the
Markdown templates in `../`. They are **generated** from the Markdown, which is
the source of truth.

## Regenerate

```bash
cd profinda-jira/templates/adf
python3 generate.py
```

## Check sync (used in CI)

```bash
python3 generate.py --check   # exits 1 if any .adf.json is out of date
```

## Rules

- **Never edit `*.adf.json` by hand.** Edit the Markdown in `../`, then
  regenerate. Hand edits are overwritten and cause silent drift.
- Commit the regenerated ADF in the **same PR** as the Markdown change.
- `generate.py` supports the Markdown subset the templates use: headings,
  paragraphs, bullet/task lists, tables, blockquotes. HTML comments are dropped
  (guidance is not stored in Jira).

## Coloured section banners

A heading prefixed with a colour token becomes a full-width coloured header bar
(white bold text), matching the original Jira template. Syntax in the Markdown:

```md
## {green} B · PROBLEM DEFINITION & FEASIBILITY
```

Named colours (original palette): `green` #1d7a4e · `teal` #0f7b8c ·
`navy` #1b2a4a · `red` #b91c1c · `orange` #c96a00. Use `###` for the real
sub-headings underneath a banner. These colours persist through the Jira REST API
(verified round-trip).

## Using an ADF file

Paste the JSON as the `description` when creating/updating an issue via the Jira
REST API, or into the styled template ticket. Example:

```bash
curl -s -X POST -u "$EMAIL:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  "https://profinda.atlassian.net/rest/api/3/issue" \
  -d "{\"fields\": {\"project\": {\"key\": \"SP\"}, \"issuetype\": {\"id\": \"10004\"}, \"summary\": \"…\", \"description\": $(cat epic.adf.json) }}"
```
