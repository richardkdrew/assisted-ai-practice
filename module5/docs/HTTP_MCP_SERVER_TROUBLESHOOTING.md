# HTTP MCP Server Troubleshooting Guide

## Overview

This guide covers common issues with the HTTP MCP server configuration and how to resolve them, particularly focusing on Cline integration issues.

## Common Issue: HTTP MCP Server Not Showing Up in Cline

### Problem Description
The HTTP MCP server may not appear in Cline's available MCP servers list, even though it's properly implemented and can run successfully when tested manually.

### Root Cause
The most common cause is incorrect command configuration in the Cline MCP settings file. The HTTP MCP server uses `uv` for dependency management, but may be configured to use `python` directly.

### Solution

#### 1. Check Current Configuration
Look at your Cline MCP settings file (usually located at `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`):

```json
{
  "mcpServers": {
    "http-mcp-server-python": {
      "type": "stdio",
      "command": "python",  // ❌ This may cause issues
      "args": ["server.py"],
      "cwd": "/path/to/http-mcp-server"
    }
  }
}
```

#### 2. Correct Configuration
Update the configuration to use `uv` instead:

```json
{
  "mcpServers": {
    "http-mcp-server-python": {
      "autoApprove": [
        "check_api_health",
        "get_deployment_status",
        "check_environment_health", 
        "get_performance_metrics",
        "get_log_entries",
        "ping"
      ],
      "disabled": false,
      "type": "stdio",
      "command": "uv",  // ✅ Use uv instead
      "args": [
        "--directory",
        "http-mcp-server",
        "run",
        "python",
        "server.py"
      ],
      "cwd": "/path/to/your/project/root",
      "env": {
        "API_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

#### 3. Key Configuration Points

- **Command**: Use `uv` instead of `python` directly
- **Args**: Include `--directory http-mcp-server` to specify the project directory
- **CWD**: Set to the project root, not the http-mcp-server subdirectory
- **Environment**: Ensure `API_BASE_URL` points to your running acme-devops-api

### Prerequisites Verification

Before configuring the HTTP MCP server, ensure:

#### 1. acme-devops-api is Running
```bash
# Test if the API is accessible
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"devops-dashboard-api","version":"1.0.0"}
```

#### 2. HTTP MCP Server Dependencies are Installed
```bash
cd http-mcp-server
uv sync
```

#### 3. Manual Server Test
```bash
cd http-mcp-server
uv run python server.py
```

Expected output should show:
- FastMCP server startup
- Successful connection to acme-devops-api
- Server ready message

## Testing the Fix

### 1. Restart Cline
After updating the configuration, restart VS Code or reload the Cline extension.

### 2. Test Basic Connectivity
Use the ping tool to verify the server is working:

```bash
# This should work if properly configured
ping("Testing HTTP MCP server connection")
```

### 3. Test API Integration
Verify the server can communicate with the acme-devops-api:

```bash
# Check API health
check_api_health()

# Get deployment status
get_deployment_status(limit=5)
```

### 4. Test Advanced Features
Verify pagination and filtering work:

```bash
# Test log retrieval with pagination
get_log_entries(level="error", limit=10, offset=0)

# Test performance metrics
get_performance_metrics(application="web-app")
```

## Additional Troubleshooting Steps

### Check Server Logs
If the server still doesn't work, check the logs:

```bash
# Run server manually to see detailed logs
cd http-mcp-server
uv run python server.py
```

Look for:
- Connection errors to acme-devops-api
- Import errors or missing dependencies
- FastMCP initialization issues

### Verify Port Availability
Ensure no conflicts with the API port:

```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill any conflicting processes if needed
pkill -f "api-server"
```

### Clean Installation
If issues persist, try a clean installation:

```bash
# Clean and reinstall HTTP MCP server
make http-clean
make http-install

# Restart API server
make api-down
make api-up
```

## Configuration Templates

### Minimal Working Configuration
```json
{
  "mcpServers": {
    "http-mcp-server": {
      "disabled": false,
      "type": "stdio", 
      "command": "uv",
      "args": ["--directory", "http-mcp-server", "run", "python", "server.py"],
      "cwd": "/path/to/project/root",
      "env": {
        "API_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

### Full Production Configuration
```json
{
  "mcpServers": {
    "http-mcp-server-python": {
      "autoApprove": [
        "check_api_health",
        "get_deployment_status", 
        "check_environment_health",
        "get_performance_metrics",
        "get_log_entries",
        "ping"
      ],
      "disabled": false,
      "type": "stdio",
      "command": "uv", 
      "args": [
        "--directory",
        "http-mcp-server",
        "run", 
        "python",
        "server.py"
      ],
      "cwd": "/Users/username/project/root",
      "env": {
        "API_BASE_URL": "http://localhost:8000",
        "HTTP_TIMEOUT": "30.0",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Verification Checklist

- [ ] acme-devops-api is running and healthy
- [ ] HTTP MCP server dependencies are installed via `uv sync`
- [ ] Configuration uses `uv` command instead of `python` directly
- [ ] CWD points to project root, not http-mcp-server subdirectory
- [ ] API_BASE_URL environment variable is set correctly
- [ ] Cline has been restarted after configuration changes
- [ ] Manual server test works: `uv run python server.py`
- [ ] Basic ping test works through Cline
- [ ] API integration test works: `check_api_health()`

## Success Indicators

When properly configured, you should see:

1. **HTTP MCP server appears in Cline's MCP servers list**
2. **All tools are available**: ping, check_api_health, get_deployment_status, etc.
3. **API integration works**: Server can retrieve data from acme-devops-api
4. **Pagination functions**: Large datasets can be retrieved with limit/offset
5. **Error handling works**: Invalid parameters return proper error messages

## Related Documentation

- [HTTP MCP Server README](../http-mcp-server/README.md)
- [MCP Server Comparison](./MCP_SERVER_COMPARISON_AND_TEST_PROMPTS.md)
- [Exercise 2 Implementation Plan](./exercise%202/IMPLEMENTATION-PLAN.md)

---

**Last Updated**: 2025-01-05  
**Status**: Verified Working  
**Cline Version**: Compatible with latest Cline releases
