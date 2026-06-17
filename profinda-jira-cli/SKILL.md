---
name: profinda-jira-cli
description: jira-cli and Jira REST API command reference for ProFinda. Covers viewing, creating, moving, and commenting on SP project issues. Use when executing Jira operations from the terminal — creating tickets, transitioning states, adding comments, or querying field IDs.
---

# jira-cli — ProFinda Command Reference

## Setup check

```bash
jira me   # should return your Jira username
```

If not installed: `brew install ankitpokhrel/tap/jira-cli` then `jira init`.
Config lives at `~/.config/.jira/.config.yml`. API token must be set as `JIRA_API_TOKEN` in your shell environment.

## Common CLI commands

```bash
jira issue view SP-1234                          # View ticket details
jira issue view SP-1234 --raw                    # Full JSON (all fields)
jira issue list -s "In Progress" -a "$(jira me)" # My in-progress tickets
jira issue list --plain --columns key,summary    # Plain text output
jira issue move SP-1234 "In Progress"            # Transition ticket
jira issue move SP-1234 "Waiting Review"         # Move after PR
jira issue move SP-1234 "Closed"                 # Close ticket
jira issue move SP-1234                          # Interactive — shows available transitions
jira issue comment add SP-1234 "message"         # Add comment
jira issue assign SP-1234 "$(jira me)"           # Assign to self
jira sprint list --state active                  # Active sprints
```

## Creating issues — use REST API

`jira issue create` cannot set option-type custom fields (`--custom` sends 400). Use `curl` instead.

```bash
# Requires JIRA_EMAIL and JIRA_API_TOKEN set in your shell (see README)
curl -s -X POST -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  "https://profinda.atlassian.net/rest/api/3/issue" \
  -d '<JSON_PAYLOAD>' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('key', json.dumps(d, indent=2)))"
```

See [REFERENCE.md](REFERENCE.md) for full payload templates, required fields by issue type, and all field option IDs.

## Creating sub-tasks

Sub-tasks require `parent` field in the payload:

```json
{
  "fields": {
    "project": {"key": "SP"},
    "issuetype": {"id": "10002"},
    "parent": {"key": "SP-1234"},
    "summary": "Sub-task summary"
  }
}
```

Sub-tasks inherit most custom fields from the parent — only `summary` and `parent` are required.

## Move ticket + comment after PR

```bash
jira issue move SP-1234 "Waiting Review"
jira issue comment add SP-1234 "PR: https://github.com/Profinda/management/pull/999"
```

## Discover field options dynamically

If a field ID or option ID in REFERENCE.md looks outdated:

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "https://profinda.atlassian.net/rest/api/3/issue/createmeta/SP/issuetypes/<ISSUE_TYPE_ID>" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
fields = data if isinstance(data, list) else data.get('values', [])
for f in fields:
    if f.get('required') or f.get('fieldId') in ['fixVersions','customfield_10988','customfield_10694','customfield_10598','customfield_11021']:
        name = f.get('name', f.get('fieldId'))
        fid = f.get('fieldId')
        allowed = f.get('allowedValues', [])
        print(f'\n--- {name} ({fid}) [required={f.get(\"required\")}] ---')
        for v in allowed:
            print(f'  id={v.get(\"id\")}, value={v.get(\"value\", v.get(\"name\", \"?\"))}')
"
```
