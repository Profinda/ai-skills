# jira-cli Reference — Field IDs and Payload Templates

## Instance

- URL: `https://profinda.atlassian.net`
- Project: `SP` | Board ID: `175` | Board type: `scrum`
- Auth user: `francisco.ruiz@profinda.com`

## Issue type IDs

| Name | ID | Subtask |
|---|---|---|
| Story | `10000` | No |
| Task | `10001` | No |
| Sub-task | `10002` | Yes |
| Bug | `10003` | No |
| Epic | `10004` | No |
| Internal Bug | `10113` | No |
| Technical Issue | `10179` | No |
| Design | `10189` | No |
| Design Task | `10184` | Yes |

## Priority IDs

| Name | ID |
|---|---|
| P1 | `1` |
| P2 | `2` |
| P3 | `3` |
| P4 | `4` |

## Pod (`customfield_10988`)

| Name | ID |
|---|---|
| Audit | `13806` |
| Booking 99 | `11000` |
| Design (Internal) | `11003` |
| DevOps | `13598` |
| Dynamic Insights | `13773` |
| Firefighting | `13600` |
| Integrations | `13599` |
| Placeholder Pod | `13740` |
| Profile & Search | `11001` |
| Reporting & Insights | `11002` |
| Skills | `13739` |
| Squirtle Squad | `13938` |

## Environment (`customfield_10598`)

| Name | ID |
|---|---|
| Preview Environments | `11252` |
| Master | `10328` |
| Integration | `10317` |
| UAT | `10261` |
| Production | `10260` |

## Requires Documentation (`customfield_10694`)

| Name | ID |
|---|---|
| New | `10600` |
| Change To Existing | `10601` |
| None Required | `11070` |

## Source / Category (`customfield_11021`)

| Name | ID |
|---|---|
| Customer Specific Change (CR) | `11137` |
| Customer Specific Change (Unplanned) | `12156` |
| Customer Task | `11142` |
| Development Task | `11143` |
| Firefighting | `11536` |
| Product Gap | `11139` |
| Product Roadmap | `11136` |
| Product Roadmap (Customer Driven) | `11138` |
| Product Roadmap (Unplanned) | `12155` |
| Regression (Existing) | `11499` |
| Regression (Quarterly Work) | `11744` |
| Tech Roadmap | `11141` |
| Technical Debt | `11140` |

## Fix Versions (`fixVersions`)

| Name | ID |
|---|---|
| 2025 Q1 Release | `10282` |
| 2025 Q1.1 Release | `10352` |
| 2025 Q2 Release | `10385` |
| 2025 Q3 Release | `10455` |
| 2025 Q4 Release | `10456` |
| 2026 Q0 Release | `10418` |
| 2026 Q1 Release | `10419` |
| 2026 Q2 Release | `10420` |
| 2026 Q3 Release | `10421` |
| 2026 Q4 Release | `10422` |
| 2027 Q1 Release | `10489` |
| 2027 Q2 Release | `10490` |
| 2027 Q3 Release | `10491` |
| 2027 Q4 Release | `10492` |

Pick the version matching the current quarter. For unplanned/internal work use current or next quarter.

---

## Payload templates

### Task

```bash
JIRA_TOKEN=$(grep JIRA_API_TOKEN ~/.zshrc.local 2>/dev/null | sed 's/export JIRA_API_TOKEN=//' | tr -d '"' | tr -d "'")

curl -s -X POST -u "francisco.ruiz@profinda.com:$JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  "https://profinda.atlassian.net/rest/api/3/issue" \
  -d '{
    "fields": {
      "project": {"key": "SP"},
      "issuetype": {"id": "10001"},
      "summary": "Your task summary here",
      "priority": {"id": "3"},
      "fixVersions": [{"id": "10421"}],
      "customfield_10988": {"id": "13600"},
      "customfield_10694": {"id": "11070"},
      "customfield_10598": {"id": "10328"},
      "customfield_11021": {"id": "11140"},
      "description": {
        "type": "doc", "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Task description."}]}]
      }
    }
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('key', json.dumps(d, indent=2)))"
```

Required fields: `summary`, `fixVersions`, `customfield_10988` (Pod), `customfield_10694` (Requires Doc), `customfield_10598` (Environment), `customfield_11021` (Source).

### Story

```bash
curl -s -X POST -u "francisco.ruiz@profinda.com:$JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  "https://profinda.atlassian.net/rest/api/3/issue" \
  -d '{
    "fields": {
      "project": {"key": "SP"},
      "issuetype": {"id": "10000"},
      "summary": "As a user, I can ...",
      "description": {
        "type": "doc", "version": 1,
        "content": [
          {"type": "heading", "attrs": {"level": 3}, "content": [{"type": "text", "text": "Acceptance criteria"}]},
          {"type": "bulletList", "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Given ... When ... Then ..."}]}]}
          ]}
        ]
      }
    }
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('key', json.dumps(d, indent=2)))"
```

### Epic

```bash
curl -s -X POST -u "francisco.ruiz@profinda.com:$JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  "https://profinda.atlassian.net/rest/api/3/issue" \
  -d '{
    "fields": {
      "project": {"key": "SP"},
      "issuetype": {"id": "10004"},
      "summary": "Epic title",
      "description": {
        "type": "doc", "version": 1,
        "content": [
          {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Goal"}]},
          {"type": "paragraph", "content": [{"type": "text", "text": "One sentence goal."}]},
          {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Non-goals"}]},
          {"type": "paragraph", "content": [{"type": "text", "text": "What is out of scope."}]},
          {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Success metrics"}]},
          {"type": "paragraph", "content": [{"type": "text", "text": "Measurable outcomes."}]},
          {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Architecture notes"}]},
          {"type": "paragraph", "content": [{"type": "text", "text": "Key decisions and constraints."}]},
          {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Open questions"}]},
          {"type": "paragraph", "content": [{"type": "text", "text": "TBD"}]}
        ]
      }
    }
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('key', json.dumps(d, indent=2)))"
```

### Bug

```bash
curl -s -X POST -u "francisco.ruiz@profinda.com:$JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  "https://profinda.atlassian.net/rest/api/3/issue" \
  -d '{
    "fields": {
      "project": {"key": "SP"},
      "issuetype": {"id": "10003"},
      "summary": "Bug summary",
      "priority": {"id": "2"},
      "customfield_10988": {"id": "11001"},
      "customfield_10598": {"id": "10260"},
      "customfield_11021": {"id": "11499"},
      "description": {
        "type": "doc", "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Steps to reproduce..."}]}]
      }
    }
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('key', json.dumps(d, indent=2)))"
```

Required fields: `summary`, `priority`, `customfield_10988` (Pod), `customfield_10598` (Environment), `customfield_11021` (Source). Bug does **not** require `fixVersions` or `Requires Documentation`.

### Sub-task

```bash
curl -s -X POST -u "francisco.ruiz@profinda.com:$JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  "https://profinda.atlassian.net/rest/api/3/issue" \
  -d '{
    "fields": {
      "project": {"key": "SP"},
      "issuetype": {"id": "10002"},
      "parent": {"key": "SP-1234"},
      "summary": "Sub-task summary"
    }
  }' | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('key', json.dumps(d, indent=2)))"
```

## Updating a description (append/refine)

Fetch current ADF, merge, then PUT:

```bash
# 1. Fetch current description
CURRENT=$(curl -s -u "francisco.ruiz@profinda.com:$JIRA_TOKEN" \
  "https://profinda.atlassian.net/rest/api/3/issue/SP-1234?fields=description" \
  | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin)['fields']['description']))")

# 2. PUT with updated description
curl -s -X PUT -u "francisco.ruiz@profinda.com:$JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  "https://profinda.atlassian.net/rest/api/3/issue/SP-1234" \
  -d "{\"fields\": {\"description\": $UPDATED_ADF}}"
```

## Known lifecycle transitions

| From | Available transitions |
|---|---|
| To Do | In Progress, Closed |
| In Progress | Parked, Blocked, Waiting Review, Closed, Cancel |
| Waiting Review | In Progress, Closed, Cancel |
| Parked | In Progress, Closed |

Use `jira issue move SP-XXXX` (no state) to see current options interactively.
