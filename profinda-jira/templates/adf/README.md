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

## Using an ADF file

Paste the JSON as the `description` when creating/updating an issue via the Jira
REST API, or into the styled template ticket. Example:

```bash
curl -s -X POST -u "$EMAIL:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  "https://profinda.atlassian.net/rest/api/3/issue" \
  -d "{\"fields\": {\"project\": {\"key\": \"SP\"}, \"issuetype\": {\"id\": \"10004\"}, \"summary\": \"…\", \"description\": $(cat epic.adf.json) }}"
```
