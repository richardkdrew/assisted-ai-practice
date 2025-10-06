# Quickstart: DevOps CLI Wrapper (Phase 1: get-status)

**Feature**: 003-i-have-a (DevOps CLI Wrapper)
**Date**: 2025-10-04
**Phase**: 1 (Design - Test Scenarios)

## Overview

This document defines test scenarios for validating the `get_deployment_status` MCP tool implementation. Each scenario represents a user interaction pattern and expected system behavior.

---

## Prerequisites

1. **MCP Server Running**:
   ```bash
   cd module5
   make dev  # Starts server with MCP Inspector
   ```

2. **DevOps CLI Tool Available**:
   ```bash
   ./acme-devops-cli/devops-cli --help  # Should display help
   ```

3. **Tool Registered**:
   - Server capabilities should list `get_deployment_status` tool
   - Parameters: `application` (optional string), `environment` (optional string)

---

## Scenario 1: Get All Deployment Statuses

**User Intent**: View all deployments across all applications and environments

**MCP Inspector Steps**:
1. Click "Tools" tab
2. Select `get_deployment_status` tool
3. Leave all parameters empty (or omit them)
4. Click "Execute"

**Expected Result**:
```json
{
  "status": "success",
  "deployments": [
    {
      "id": "deploy-001",
      "applicationId": "web-app",
      "environment": "prod",
      "version": "v2.1.3",
      "status": "deployed",
      "deployedAt": "2024-01-15T10:30:00Z",
      "deployedBy": "alice@company.com",
      "commitHash": "abc123def456"
    },
    // ... more deployments
  ],
  "total_count": 6,
  "filters_applied": {
    "application": null,
    "environment": null
  },
  "timestamp": "2025-10-04T..."
}
```

**Success Criteria**:
- ✅ Tool executes without errors
- ✅ Returns JSON object with required fields
- ✅ `deployments` array contains multiple items
- ✅ `filters_applied` shows both filters as `null`

---

## Scenario 2: Filter by Application Only

**User Intent**: View all deployments for a specific application across all environments

**MCP Inspector Steps**:
1. Select `get_deployment_status` tool
2. Set parameter: `application = "web-app"`
3. Leave `environment` empty
4. Click "Execute"

**Expected Result**:
```json
{
  "status": "success",
  "deployments": [
    {
      "id": "deploy-001",
      "applicationId": "web-app",
      "environment": "prod",
      "version": "v2.1.3",
      "status": "deployed",
      "deployedAt": "2024-01-15T10:30:00Z",
      "deployedBy": "alice@company.com",
      "commitHash": "abc123def456"
    },
    {
      "id": "deploy-002",
      "applicationId": "web-app",
      "environment": "staging",
      "version": "v2.1.4",
      "status": "deployed",
      "deployedAt": "2024-01-16T12:00:00Z",
      "deployedBy": "bob@company.com",
      "commitHash": "def456ghi789"
    }
  ],
  "total_count": 2,
  "filters_applied": {
    "application": "web-app",
    "environment": null
  },
  "timestamp": "2025-10-04T..."
}
```

**Success Criteria**:
- ✅ All returned deployments have `applicationId = "web-app"`
- ✅ Deployments across multiple environments included
- ✅ `filters_applied.application` is `"web-app"`
- ✅ `filters_applied.environment` is `null`

---

## Scenario 3: Filter by Environment Only

**User Intent**: View all deployments in a specific environment across all applications

**MCP Inspector Steps**:
1. Select `get_deployment_status` tool
2. Leave `application` empty
3. Set parameter: `environment = "prod"`
4. Click "Execute"

**Expected Result**:
```json
{
  "status": "success",
  "deployments": [
    {
      "id": "deploy-001",
      "applicationId": "web-app",
      "environment": "prod",
      "version": "v2.1.3",
      "status": "deployed",
      "deployedAt": "2024-01-15T10:30:00Z",
      "deployedBy": "alice@company.com",
      "commitHash": "abc123def456"
    },
    {
      "id": "deploy-003",
      "applicationId": "api-service",
      "environment": "prod",
      "version": "v1.8.2",
      "status": "deployed",
      "deployedAt": "2024-01-16T11:00:00Z",
      "deployedBy": "carol@company.com",
      "commitHash": "ghi789jkl012"
    }
    // ... more prod deployments
  ],
  "total_count": 3,
  "filters_applied": {
    "application": null,
    "environment": "prod"
  },
  "timestamp": "2025-10-04T..."
}
```

**Success Criteria**:
- ✅ All returned deployments have `environment = "prod"`
- ✅ Deployments across multiple applications included
- ✅ `filters_applied.application` is `null`
- ✅ `filters_applied.environment` is `"prod"`

---

## Scenario 4: Filter by Both Application and Environment

**User Intent**: View deployments for a specific application in a specific environment

**MCP Inspector Steps**:
1. Select `get_deployment_status` tool
2. Set parameter: `application = "web-app"`
3. Set parameter: `environment = "prod"`
4. Click "Execute"

**Expected Result**:
```json
{
  "status": "success",
  "deployments": [
    {
      "id": "deploy-001",
      "applicationId": "web-app",
      "environment": "prod",
      "version": "v2.1.3",
      "status": "deployed",
      "deployedAt": "2024-01-15T10:30:00Z",
      "deployedBy": "alice@company.com",
      "commitHash": "abc123def456"
    }
  ],
  "total_count": 1,
  "filters_applied": {
    "application": "web-app",
    "environment": "prod"
  },
  "timestamp": "2025-10-04T..."
}
```

**Success Criteria**:
- ✅ Only 1 deployment returned (most specific filter)
- ✅ Deployment matches both `applicationId = "web-app"` AND `environment = "prod"`
- ✅ Both filters shown in `filters_applied`

---

## Scenario 5: No Results (Non-Existent Application)

**User Intent**: Query an application that doesn't exist

**MCP Inspector Steps**:
1. Select `get_deployment_status` tool
2. Set parameter: `application = "nonexistent-app"`
3. Click "Execute"

**Expected Result**:
```json
{
  "status": "success",
  "deployments": [],
  "total_count": 0,
  "filters_applied": {
    "application": "nonexistent-app",
    "environment": null
  },
  "timestamp": "2025-10-04T..."
}
```

**Success Criteria**:
- ✅ No error thrown (empty results are valid)
- ✅ `deployments` is empty array `[]`
- ✅ `total_count` is `0`
- ✅ `status` is `"success"` (not an error condition)

---

## Scenario 6: CLI Execution Timeout (Error Case)

**User Intent**: Trigger timeout handling

**Setup**:
- Temporarily modify CLI tool to sleep for 35 seconds (exceeds 30s timeout)
- OR use network delay simulation

**MCP Inspector Steps**:
1. Select `get_deployment_status` tool
2. Execute with any parameters
3. Wait for timeout

**Expected Result** (JSON-RPC error):
```json
{
  "error": {
    "code": -32603,
    "message": "DevOps CLI timed out after 30 seconds"
  }
}
```

**Success Criteria**:
- ✅ Tool returns error (not success)
- ✅ Error message is user-friendly
- ✅ Server remains responsive (doesn't hang)
- ✅ Stderr logs show timeout event

**Cleanup**: Restore original CLI tool

---

## Scenario 7: CLI Tool Not Found (Error Case)

**User Intent**: Handle missing CLI tool gracefully

**Setup**:
- Temporarily rename `./acme-devops-cli/devops-cli` to simulate missing tool
- OR update path in code to point to non-existent location

**MCP Inspector Steps**:
1. Select `get_deployment_status` tool
2. Execute with any parameters

**Expected Result** (JSON-RPC error):
```json
{
  "error": {
    "code": -32603,
    "message": "DevOps CLI tool not found at ./acme-devops-cli/devops-cli"
  }
}
```

**Success Criteria**:
- ✅ Error message clearly indicates missing CLI tool
- ✅ Provides exact path that was checked
- ✅ Stderr logs show `FileNotFoundError`

**Cleanup**: Restore CLI tool location

---

## Scenario 8: Malformed JSON Output (Error Case)

**User Intent**: Handle CLI returning invalid JSON

**Setup**:
- Temporarily modify CLI tool to return invalid JSON (e.g., `{incomplete`)
- OR inject corruption in subprocess stdout capture (advanced)

**MCP Inspector Steps**:
1. Select `get_deployment_status` tool
2. Execute with any parameters

**Expected Result** (JSON-RPC error):
```json
{
  "error": {
    "code": -32603,
    "message": "CLI returned invalid JSON: Expecting ',' delimiter: line 1 column 12 (char 11)"
  }
}
```

**Success Criteria**:
- ✅ Error message indicates JSON parsing failure
- ✅ Includes parse error details
- ✅ Stderr logs show raw CLI output for debugging
- ✅ Server doesn't crash

**Cleanup**: Restore original CLI tool

---

## Scenario 9: CLI Execution Failure (Non-Zero Exit Code)

**User Intent**: Handle CLI command returning error exit code

**Setup**:
- Modify CLI tool to `exit(1)` on certain inputs
- OR pass invalid arguments that CLI rejects

**MCP Inspector Steps**:
1. Select `get_deployment_status` tool
2. Execute (CLI will fail internally)

**Expected Result** (JSON-RPC error):
```json
{
  "error": {
    "code": -32603,
    "message": "DevOps CLI failed with exit code 1: <stderr output from CLI>"
  }
}
```

**Success Criteria**:
- ✅ Error message includes exit code
- ✅ Error message includes CLI stderr output
- ✅ Server logs show full subprocess details

**Cleanup**: Restore original CLI tool

---

## Scenario 10: Missing Required Fields in Output (Error Case)

**User Intent**: Detect structural problems in CLI output

**Setup**:
- Modify CLI tool to return JSON missing `status` or `deployments` field
- E.g., `{"partial": "data"}` instead of full structure

**MCP Inspector Steps**:
1. Select `get_deployment_status` tool
2. Execute with any parameters

**Expected Result** (JSON-RPC error):
```json
{
  "error": {
    "code": -32603,
    "message": "CLI output missing required field: status"
  }
}
```

**Success Criteria**:
- ✅ Error identifies specific missing field
- ✅ Validation catches issue before returning to client
- ✅ Stderr logs show actual CLI output for debugging

**Cleanup**: Restore original CLI tool

---

## Performance Validation

**Scenario 11: Response Time Check**

**Test**:
```bash
# Measure total execution time
time ./acme-devops-cli/devops-cli status --format json
# Expected: <1 second for CLI execution

# Then measure via MCP (includes overhead)
# Use MCP Inspector with timestamp comparison
# Expected: <2 seconds total (CLI + subprocess + parsing overhead)
```

**Success Criteria**:
- ✅ CLI execution: <1s
- ✅ Total MCP tool execution: <2s
- ✅ Overhead (MCP - CLI): <500ms

---

## Logging Validation

**Scenario 12: Verify Logging Output**

**Check stderr logs** (during any scenario execution):

Expected log entries:
```
2025-10-04 17:21:45 - devops - INFO - Executing DevOps CLI: status --format json
2025-10-04 17:21:46 - devops - DEBUG - CLI command completed in 0.85s
2025-10-04 17:21:46 - devops - DEBUG - CLI stdout: {"status": "success", ...}
```

**Success Criteria**:
- ✅ All logs go to stderr (not stdout)
- ✅ INFO logs for each CLI execution
- ✅ DEBUG logs include timing and output
- ✅ ERROR logs for failures include full details

---

## Test Coverage Summary

**Positive Tests** (Success Cases):
- ✅ Scenario 1: No filters
- ✅ Scenario 2: Application filter only
- ✅ Scenario 3: Environment filter only
- ✅ Scenario 4: Both filters
- ✅ Scenario 5: No results (empty array)

**Negative Tests** (Error Cases):
- ✅ Scenario 6: Timeout
- ✅ Scenario 7: CLI not found
- ✅ Scenario 8: Invalid JSON
- ✅ Scenario 9: Non-zero exit code
- ✅ Scenario 10: Missing required fields

**Non-Functional Tests**:
- ✅ Scenario 11: Performance (response time)
- ✅ Scenario 12: Logging (stderr only)

**Total Scenarios**: 12 (5 positive, 5 negative, 2 non-functional)

---

## Automated Test Mapping

These quickstart scenarios map to automated tests in `tests/test_devops_tools.py`:

| Scenario | Test Function |
|----------|---------------|
| 1 | `test_get_status_no_filters()` |
| 2 | `test_get_status_filter_by_app()` |
| 3 | `test_get_status_filter_by_env()` |
| 4 | `test_get_status_filter_by_both()` |
| 5 | `test_get_status_no_results()` |
| 6 | `test_get_status_timeout()` |
| 7 | `test_get_status_cli_not_found()` |
| 8 | `test_get_status_invalid_json()` |
| 9 | `test_get_status_cli_failure()` |
| 10 | `test_get_status_missing_fields()` |
| 11 | `test_get_status_performance()` |
| 12 | (Manual inspection of stderr during test runs) |

---

**Quickstart Complete**: ✅ Ready for task generation (/tasks command)
