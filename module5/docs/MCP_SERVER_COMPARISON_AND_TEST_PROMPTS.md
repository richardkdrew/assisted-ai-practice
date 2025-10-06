# MCP Server Comparison and Test Prompts

## Overview

This document compares the stdio and HTTP MCP servers for DevOps operations and provides natural language test prompts to evaluate each server's capabilities.

## Server Architecture Comparison

### STDIO MCP Server (`stdio-server-uv`)
- **Transport**: STDIO (standard input/output)
- **Backend**: Wraps the `acme-devops-cli` command-line tool
- **Data Source**: CLI tool that reads from local JSON files
- **Connection**: Direct process communication via stdin/stdout
- **Execution**: Spawns subprocess calls to the CLI tool

### HTTP MCP Server (`http-mcp-server`)
- **Transport**: HTTP
- **Backend**: Consumes the `acme-devops-api` REST API
- **Data Source**: HTTP API server with JSON endpoints
- **Connection**: HTTP requests to API endpoints
- **Execution**: Makes async HTTP calls using httpx client

## Tool Comparison Matrix

| Tool/Feature | STDIO Server | HTTP Server | Notes |
|--------------|--------------|-------------|-------|
| **ping** | ✅ | ✅ | Both support basic connectivity testing |
| **get_deployment_status** | ✅ | ✅ | Core functionality in both |
| **list_releases** | ✅ | ❌ | Only available in STDIO server |
| **check_health** | ✅ | ❌ | Only available in STDIO server |
| **promote_release** | ✅ | ❌ | Only available in STDIO server |
| **check_environment_health** | ❌ | ✅ | Only available in HTTP server |
| **get_performance_metrics** | ❌ | ✅ | Only available in HTTP server |
| **get_log_entries** | ❌ | ✅ | Only available in HTTP server |
| **check_api_health** | ❌ | ✅ | Only available in HTTP server |
| **Pagination Support** | ❌ | ✅ | HTTP server supports limit/offset |
| **Input Validation** | ✅ | ✅ | Both have parameter validation |

## Shared Functionality Test Prompts

These prompts can be used to test both servers and compare their responses:

### 1. Basic Connectivity Testing
```
"Test if the DevOps system is responding by sending a ping message"
"Check if the MCP server is working by pinging it with 'hello world'"
"Verify connectivity to the DevOps tools"
```

### 2. Deployment Status Queries
```
"Show me all current deployments across all environments"
"What deployments are currently running in production?"
"Get the deployment status for the web-app application"
"Show me deployments in the staging environment"
"What's the current deployment status for api-service in production?"
```

### 3. Application-Specific Deployment Queries
```
"Show me all deployments for the mobile-app"
"What's deployed in UAT for the web-app?"
"Get deployment information for data-processor across all environments"
```

## STDIO Server Unique Functionality Test Prompts

These prompts will only work with the STDIO server:

### 1. Release History Management
```
"Show me the release history for web-app"
"Get the last 5 releases for the mobile-app"
"What are the recent releases for api-service?"
"Show me all releases for data-processor with a limit of 10"
```

### 2. Environment Health Monitoring
```
"Check the health of the production environment"
"What's the health status across all environments?"
"Is the staging environment healthy?"
"Check health status for UAT"
```

### 3. Release Promotion Operations
```
"Promote web-app version 2.1.0 from staging to production"
"Move api-service v1.5.2 from dev to staging"
"Promote mobile-app version 3.0.1 from UAT to prod"
"Deploy data-processor v2.2.0 from staging to UAT"
```

## HTTP Server Unique Functionality Test Prompts

These prompts will only work with the HTTP server:

### 1. Advanced Health Monitoring
```
"Check the detailed health status of all services"
"What's the health status of web-app across all environments?"
"Show me detailed health information for production services"
"Get health metrics for api-service in staging with full details"
```

### 2. Performance Metrics Analysis
```
"Show me performance metrics for all applications"
"Get CPU and memory metrics for web-app in production"
"What are the performance metrics for the last 24 hours?"
"Show me metrics for api-service over the past 7 days"
"Get performance data for mobile-app in staging"
```

### 3. Log Management and Analysis
```
"Show me recent error logs from production"
"Get log entries for web-app in staging"
"What are the latest warning logs across all environments?"
"Show me debug logs for api-service"
"Get the last 100 log entries with pagination"
"Show me logs from mobile-app with error level filtering"
```

### 4. API Health Verification
```
"Check if the DevOps API is healthy and responding"
"Verify the API connection and response times"
"Test the API health endpoints"
```

### 5. Pagination and Large Dataset Handling
```
"Show me the first 25 deployments"
"Get deployment status with pagination, limit 10"
"Show me logs with 50 entries per page, starting from page 2"
"Get performance metrics with pagination support"
```

## Distinguishing Prompts by Server Type

### Prompts that Clearly Indicate STDIO Server Usage:
- Any mention of "CLI" or "command-line"
- Requests for release promotion/deployment operations
- Environment health checks (not service health)
- Release history queries

### Prompts that Clearly Indicate HTTP Server Usage:
- Requests for performance metrics or CPU/memory data
- Log analysis and filtering requests
- Pagination requirements ("show me the first X results")
- API health verification
- Detailed service health monitoring

### Ambiguous Prompts (Could Use Either):
- Basic deployment status queries
- Simple connectivity tests
- General application status requests

## Testing Strategy Recommendations

### For Comprehensive Testing:
1. Start with shared functionality prompts to ensure both servers work
2. Test unique features to understand each server's strengths
3. Compare response formats and data richness
4. Test error handling with invalid parameters
5. Evaluate performance differences between CLI and API approaches

### For Server Selection:
- **Choose STDIO Server** for: Release management, deployment operations, simple monitoring
- **Choose HTTP Server** for: Performance analysis, log management, detailed monitoring, large datasets

### For Development and Debugging:
- Use ping tools to verify connectivity
- Test with simple queries before complex operations
- Compare data consistency between both servers
- Validate error handling and edge cases

## Example Test Sequences

### Basic Functionality Test:
1. "Ping the DevOps system to test connectivity"
2. "Show me all current deployments"
3. "What's deployed in production?"

### STDIO Server Deep Test:
1. "Check health of all environments"
2. "Show me release history for web-app"
3. "Promote web-app v2.1.0 from staging to production"

### HTTP Server Deep Test:
1. "Check API health and response times"
2. "Show me performance metrics for production"
3. "Get error logs from the last 24 hours with pagination"

This comparison helps identify which server to use based on the specific DevOps operations needed and provides a comprehensive testing framework for both implementations.
