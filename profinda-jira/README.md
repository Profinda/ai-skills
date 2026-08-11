# profinda-jira — Developer Setup

This skill requires the `mcp-atlassian` MCP server configured in your AI client.

```bash
brew install uv   # mcp-atlassian runs via uvx, no permanent install needed
```

Generate a Jira API token at https://id.atlassian.com/manage-profile/security/api-tokens and set both variables in your shell:

```bash
# ~/.zshrc.local (or equivalent)
export JIRA_EMAIL="your.name@profinda.com"
export JIRA_API_TOKEN="your-token-here"
```

For **OpenCode** (`~/.config/opencode/opencode.json`):

```jsonc
{
  "mcp": {
    "mcp-atlassian": {
      "type": "local",
      "command": ["uvx", "mcp-atlassian"],
      "enabled": true,
      "environment": {
        "JIRA_URL": "https://profinda.atlassian.net",
        "JIRA_USERNAME": "{env:JIRA_EMAIL}",
        "JIRA_API_TOKEN": "{env:JIRA_API_TOKEN}"
      }
    }
  }
}
```

For **Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
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
