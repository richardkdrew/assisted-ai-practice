# Prompt for your AI assistant

## Chained tool test

```Use my devops-mcp-server to check the deployment status of the "web-app" 
application in the "prod" environment, then check the health of that 
environment, and finally list the last 3 releases for that application.

Please show me what tools you're using and chain them together.
```

## Simple connectivity test

```Use the devops-mcp-server to ping with the message "hello from Claude Code"
```

## Complex workflow test

```I need to promote the web-app from staging to UAT. First check the current deployment status in staging to see what version is deployed, then check UAT's health to make sure it's ready, and finally promote the release.
```

## Tool discovery test

```What MCP servers and tools are available? Show me the devops-mcp-server tools.
```
