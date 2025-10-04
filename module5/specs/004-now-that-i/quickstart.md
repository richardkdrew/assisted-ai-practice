# Quickstart - Additional DevOps CLI Tools

**Feature**: list-releases & check-health
**Date**: 2025-10-04

## Prerequisites
- DevOps CLI tool at `../acme-devops-cli/devops-cli`
- MCP server running (`make dev` or `make run`)
- FastMCP Inspector for interactive testing (`make dev`)

## Test Scenarios

### Scenario 1: Query Release History
**Goal**: DevOps engineer queries recent releases for an application

**Steps**:
1. Start FastMCP Inspector: `make dev`
2. In the inspector web UI, select `list-releases` tool
3. Set parameters:
   - `app`: "web-app"
   - `limit`: 5
4. Execute tool

**Expected Result**:
```json
{
  "status": "success",
  "releases": [
    {...},  // Up to 5 release objects
  ],
  "total_count": 5,
  "filters_applied": {
    "app": "web-app",
    "limit": 5
  }
}
```

**Validation**:
- Returns max 5 releases
- All releases have `applicationId`: "web-app"
- Response includes `status`, `releases`, `total_count`

### Scenario 2: Check Production Health
**Goal**: SRE checks health status of production environment

**Steps**:
1. Start FastMCP Inspector: `make dev`
2. In the inspector web UI, select `check-health` tool
3. Set parameters:
   - `env`: "prod"
4. Execute tool

**Expected Result**:
```json
{
  "status": "success",
  "health_checks": [
    {
      "environment": "prod",
      ...  // Health metrics from CLI
    }
  ],
  "timestamp": "2025-10-04T..."
}
```

**Validation**:
- Returns health for production only
- Response includes `status`, `health_checks`, `timestamp`

### Scenario 3: Check All Environments
**Goal**: Automation system checks health across all environments

**Steps**:
1. Start FastMCP Inspector: `make dev`
2. In the inspector web UI, select `check-health` tool
3. Leave `env` parameter empty (or omit it)
4. Execute tool

**Expected Result**:
```json
{
  "status": "success",
  "health_checks": [
    {"environment": "prod", ...},
    {"environment": "staging", ...},
    {"environment": "uat", ...},
    {"environment": "dev", ...}
  ],
  "timestamp": "2025-10-04T..."
}
```

**Validation**:
- Returns health for ALL 4 environments
- Array contains 4 health check objects

### Scenario 4: Error Handling - Missing Required Parameter
**Goal**: Verify validation works for missing app parameter

**Steps**:
1. Start FastMCP Inspector: `make dev`
2. In the inspector web UI, select `list-releases` tool
3. Leave `app` parameter empty
4. Execute tool

**Expected Result**:
Error response with message: "app parameter is required"

**Validation**:
- Tool returns error (not crashes)
- Error message is clear and actionable

### Scenario 5: Error Handling - Invalid Environment
**Goal**: Verify validation works for invalid env parameter

**Steps**:
1. Start FastMCP Inspector: `make dev`
2. In the inspector web UI, select `check-health` tool
3. Set parameters:
   - `env`: "invalid-env"
4. Execute tool

**Expected Result**:
Error response with message: "Invalid environment: invalid-env. Must be one of: prod, staging, uat, dev"

**Validation**:
- Tool returns error (not crashes)
- Error lists valid options

### Scenario 6: Case-Insensitive Environment
**Goal**: Verify case-insensitive env matching works

**Steps**:
1. Start FastMCP Inspector: `make dev`
2. In the inspector web UI, select `check-health` tool
3. Set parameters:
   - `env`: "PROD" (uppercase)
4. Execute tool

**Expected Result**:
Same as Scenario 2 (production health data)

**Validation**:
- Tool accepts "PROD", "Prod", "prod" equally
- Returns production environment data

## Manual Testing Checklist

- [ ] list-releases with valid app → returns releases
- [ ] list-releases with app + limit → returns limited results
- [ ] list-releases without app → returns error
- [ ] list-releases with limit=0 → returns error
- [ ] check-health with valid env → returns health for that env
- [ ] check-health with uppercase env → case-insensitive match works
- [ ] check-health with invalid env → returns error
- [ ] check-health without env → returns health for ALL envs
- [ ] Both tools handle CLI timeout gracefully
- [ ] Both tools handle malformed JSON from CLI

## Automated Testing

Run tests:
```bash
make test
```

Tests should cover:
- All quickstart scenarios above
- Edge cases (timeout, CLI not found, malformed JSON)
- Concurrent tool calls (no state conflicts)
