# mcp-atlassian — Agent Tool Reference

Use `mcp-atlassian` MCP tools for all Jira operations. Never shell out to `jira-cli` or `curl` for Jira — the MCP handles ADF conversion, authentication, and custom field resolution internally.

## Key tools

### Read

| Tool | Use |
|---|---|
| `jira_get_issue` | Read a ticket, its fields, and comments |
| `jira_search` | JQL search |
| `jira_get_transitions` | List available state transitions before transitioning |
| `jira_search_fields` | Discover custom field IDs by keyword |
| `jira_get_field_options` | Get allowed values for a custom field |

### Write

| Tool | Use |
|---|---|
| `jira_create_issue` | Create Story, Task, Epic, Sub-task, Bug |
| `jira_update_issue` | Update description, summary, custom fields |
| `jira_transition_issue` | Move to In Progress, Waiting Review, Closed, etc. |
| `jira_add_comment` | Add comments (including HANDOFF comments) |
| `jira_batch_create_issues` | Create multiple sub-tasks in one call |

## Common patterns

### Read a ticket
```json
{"issue_key": "SP-1234", "comment_limit": 10}
```

### Create a Task
```json
{
  "project_key": "SP",
  "issue_type": "Task",
  "summary": "My task summary",
  "description": "Markdown description here",
  "additional_fields": "{\"fixVersions\": [{\"id\": \"10421\"}], \"customfield_10988\": {\"id\": \"13600\"}, \"customfield_10694\": {\"id\": \"11070\"}, \"customfield_10598\": {\"id\": \"10328\"}, \"customfield_11021\": {\"id\": \"11140\"}}"
}
```

Field IDs for SP project custom fields are in [REFERENCE.md](REFERENCE.md). Use `jira_search_fields` + `jira_get_field_options` to discover or verify them dynamically.

### Create a Story
```json
{
  "project_key": "SP",
  "issue_type": "Story",
  "summary": "As a user, I can ...",
  "description": "### Acceptance criteria\n\n- Given ... When ... Then ..."
}
```

### Create a Sub-task
```json
{
  "project_key": "SP",
  "issue_type": "Subtask",
  "summary": "Sub-task summary",
  "additional_fields": "{\"parent\": {\"key\": \"SP-1234\"}}"
}
```

### Create multiple sub-tasks at once
```json
[
  {"project_key": "SP", "issue_type": "Subtask", "summary": "Write migration", "additional_fields": "{\"parent\": {\"key\": \"SP-1234\"}}"},
  {"project_key": "SP", "issue_type": "Subtask", "summary": "Add controller action", "additional_fields": "{\"parent\": {\"key\": \"SP-1234\"}}"},
  {"project_key": "SP", "issue_type": "Subtask", "summary": "Write tests", "additional_fields": "{\"parent\": {\"key\": \"SP-1234\"}}"}
]
```

### Transition an issue
Always call `jira_get_transitions` first — transition IDs vary by current state.
```json
// Step 1
{"issue_key": "SP-1234"}  // → jira_get_transitions → note the transition_id for "In Progress"

// Step 2
{"issue_key": "SP-1234", "transition_id": "21"}
```

### Update Epic description (living PRD)
Description is Markdown — the MCP converts to ADF automatically.
```json
{
  "issue_key": "SP-1234",
  "fields": "{\"description\": \"## Goal\\nOne sentence.\\n\\n## Non-goals\\nOut of scope.\\n\\n## Success metrics\\nMeasurable outcomes.\\n\\n## Architecture notes\\nKey decisions.\\n\\n## Open questions\\nTBD\"}"
}
```

### Post a HANDOFF comment
```json
{
  "issue_key": "SP-1234",
  "comment": "[AGENT HANDOFF]\nDate: 2026-06-17\nBranch: feature/SP-1234-my-feature\n\nCompleted:\n- SP-1235 Write migration\n\nNext:\n- SP-1236 Add controller action\n\nContext:\n- Chose X over Y because of Z constraint in lib/foo.rb:42\n\nBlockers:\n- None"
}
```

## Setup (per developer)

Install `uv` if not present:
```bash
brew install uv
```

Add to your OpenCode config (`~/.config/opencode/opencode.json`):
```json
{
  "mcp": {
    "mcp-atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "https://profinda.atlassian.net",
        "JIRA_USERNAME": "$JIRA_EMAIL",
        "JIRA_API_TOKEN": "$JIRA_API_TOKEN"
      }
    }
  }
}
```

For Claude Desktop, add the same block to `~/Library/Application Support/Claude/claude_desktop_config.json` under `mcpServers`.

`JIRA_EMAIL` and `JIRA_API_TOKEN` must be set in your shell environment — see the README.
