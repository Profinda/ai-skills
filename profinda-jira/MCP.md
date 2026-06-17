# mcp-atlassian Tool Reference

## Tools

| Tool | Use |
|---|---|
| `jira_get_issue` | Read ticket, fields, comments |
| `jira_search` | JQL search |
| `jira_get_transitions` | Available state transitions for an issue |
| `jira_search_fields` | Discover custom field IDs by keyword |
| `jira_get_field_options` | Allowed values for a custom field |
| `jira_create_issue` | Create Story, Task, Epic, Sub-task, Bug |
| `jira_update_issue` | Update description, summary, custom fields |
| `jira_transition_issue` | Move to In Progress, Waiting Review, Closed, etc. |
| `jira_add_comment` | Add comments and HANDOFF comments |
| `jira_batch_create_issues` | Create multiple sub-tasks in one call |

## Patterns

### Read a ticket
```json
{"issue_key": "SP-1234", "comment_limit": 10}
```

### Create a Story
```json
{
  "project_key": "SP",
  "issue_type": "Story",
  "summary": "As a user, I can ...",
  "description": "### Acceptance criteria\n\n- Given ... When ... Then ..."
}
```

### Create a Task
```json
{
  "project_key": "SP",
  "issue_type": "Task",
  "summary": "Task summary",
  "description": "Markdown description",
  "additional_fields": "{\"fixVersions\": [{\"id\": \"10421\"}], \"customfield_10988\": {\"id\": \"13600\"}, \"customfield_10694\": {\"id\": \"11070\"}, \"customfield_10598\": {\"id\": \"10328\"}, \"customfield_11021\": {\"id\": \"11140\"}}"
}
```

SP project requires these custom fields for Tasks. Field option IDs: see [FIELD_IDS.md](FIELD_IDS.md). Verify dynamically with `jira_search_fields` + `jira_get_field_options`.

### Create sub-tasks in batch
```json
[
  {"project_key": "SP", "issue_type": "Subtask", "summary": "Write migration", "additional_fields": "{\"parent\": {\"key\": \"SP-1234\"}}"},
  {"project_key": "SP", "issue_type": "Subtask", "summary": "Add controller action", "additional_fields": "{\"parent\": {\"key\": \"SP-1234\"}}"},
  {"project_key": "SP", "issue_type": "Subtask", "summary": "Write tests", "additional_fields": "{\"parent\": {\"key\": \"SP-1234\"}}"}
]
```

### Transition an issue
```json
// Step 1 — discover available transitions
{"issue_key": "SP-1234"}  // jira_get_transitions

// Step 2 — transition
{"issue_key": "SP-1234", "transition_id": "<id from step 1>"}
```

### Update Epic description
Description is Markdown — MCP converts to ADF automatically.
```json
{
  "issue_key": "SP-1234",
  "fields": "{\"description\": \"## Goal\\nOne sentence.\\n\\n## Non-goals\\n...\"}"
}
```

### Post HANDOFF comment
```json
{
  "issue_key": "SP-1234",
  "comment": "[AGENT HANDOFF]\nDate: 2026-06-17\nBranch: feature/SP-1234-my-feature\n\nCompleted:\n- SP-1235 Write migration\n\nNext:\n- SP-1236 Add controller action\n\nContext:\n- Chose X over Y because of Z\n\nBlockers:\n- None"
}
```
