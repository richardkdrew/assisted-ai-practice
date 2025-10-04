# Data Model: DevOps CLI Wrapper

**Feature**: 003-i-have-a (DevOps CLI Wrapper - Phase 1)
**Date**: 2025-10-04
**Phase**: 1 (Design)

## Overview

This document defines the data structures for wrapping the DevOps CLI tool with MCP server tools. Phase 1 focuses on `get_deployment_status` tool only.

---

## Entity 1: CLIExecutionResult

**Purpose**: Encapsulates the result of executing a CLI command via subprocess.

**Type**: `NamedTuple` (immutable, lightweight)

**Attributes**:
- `stdout: str` - Standard output from CLI command (typically JSON)
- `stderr: str` - Standard error output (diagnostic messages)
- `returncode: int` - Process exit code (0 = success, non-zero = error)

**Validation Rules**:
- All attributes required (no None values)
- `stdout` and `stderr` are decoded strings (UTF-8)
- `returncode` is integer (0-255 typical range)

**Usage**:
```python
result = CLIExecutionResult(
    stdout='{"status": "success", ...}',
    stderr='',
    returncode=0
)
```

**Relationships**:
- Created by: `execute_cli_command()` in `cli_wrapper.py`
- Consumed by: MCP tool functions in `tools/devops.py`

---

## Entity 2: Deployment

**Purpose**: Represents a deployed application instance (parsed from CLI output).

**Type**: Python `dict` (matches CLI JSON output structure)

**Attributes**:
- `id: str` - Unique deployment identifier (e.g., "deploy-001")
- `applicationId: str` - Application identifier (e.g., "web-app", "api-service")
- `environment: str` - Deployment environment (e.g., "prod", "staging", "uat")
- `version: str` - Deployed version (e.g., "v2.1.3")
- `status: str` - Deployment status (e.g., "deployed", "failed", "pending")
- `deployedAt: str` - ISO 8601 timestamp (e.g., "2024-01-15T10:30:00Z")
- `deployedBy: str` - Email of deployer (e.g., "alice@company.com")
- `commitHash: str` - Git commit hash (e.g., "abc123def456")

**Validation Rules**:
- All fields required in CLI output
- `version` follows semantic versioning format
- `deployedAt` is ISO 8601 UTC timestamp
- `status` is one of: "deployed", "failed", "pending", "rolling_back"

**Example**:
```json
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
```

**Relationships**:
- Contained in: `DeploymentStatusResponse.deployments[]`
- Source: DevOps CLI `status` command output

---

## Entity 3: DeploymentStatusResponse

**Purpose**: Top-level response structure from `get_deployment_status` tool.

**Type**: Python `dict` (matches CLI JSON output)

**Attributes**:
- `status: str` - Overall request status ("success" or "error")
- `deployments: list[Deployment]` - Array of deployment objects
- `total_count: int` - Number of deployments returned
- `filters_applied: dict` - Applied filters (application, environment)
- `timestamp: str` - ISO 8601 timestamp of response generation

**Validation Rules**:
- `status` must be "success" or "error"
- `deployments` is array (may be empty if no matches)
- `total_count` matches length of `deployments` array
- `filters_applied` contains keys: `application` (str | null), `environment` (str | null)
- `timestamp` is ISO 8601 UTC timestamp

**Example** (with filters):
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
  "timestamp": "2025-10-04T17:21:45.504760Z"
}
```

**Example** (no results):
```json
{
  "status": "success",
  "deployments": [],
  "total_count": 0,
  "filters_applied": {
    "application": "nonexistent-app",
    "environment": null
  },
  "timestamp": "2025-10-04T17:21:45.504760Z"
}
```

**Relationships**:
- Returned by: `get_deployment_status()` MCP tool
- Source: DevOps CLI `status` command output (parsed JSON)

---

## Entity 4: ToolParameters (get_deployment_status)

**Purpose**: Input parameters for the `get_deployment_status` MCP tool.

**Type**: Function parameters (Python type hints)

**Attributes**:
- `application: str | None = None` - Optional application filter
- `environment: str | None = None` - Optional environment filter

**Validation Rules**:
- Both parameters are optional (default None = no filter)
- If provided, must be non-empty strings
- No format validation (CLI tool handles invalid values)

**Usage**:
```python
# All deployments
result = await get_deployment_status()

# Filter by application
result = await get_deployment_status(application="web-app")

# Filter by environment
result = await get_deployment_status(environment="prod")

# Filter by both
result = await get_deployment_status(
    application="web-app",
    environment="prod"
)
```

**Relationships**:
- Accepted by: `get_deployment_status()` tool function
- Passed to: `execute_cli_command()` as CLI arguments

---

## Error Types

### CLIExecutionError

**Purpose**: Raised when CLI command execution fails.

**Type**: Python `Exception` subclass (or use built-in `RuntimeError`)

**Attributes**:
- `message: str` - Human-readable error description
- `returncode: int` - CLI process exit code
- `stderr: str` - CLI error output

**Example**:
```python
raise RuntimeError(
    f"DevOps CLI failed with exit code {returncode}: {stderr}"
)
```

**When Raised**:
- CLI process returns non-zero exit code
- CLI tool not found (`FileNotFoundError`)
- CLI execution times out (`asyncio.TimeoutError`)

---

## Data Flow

```
MCP Client (Claude Desktop)
  ↓ (natural language: "What's the deployment status of web-app in prod?")

FastMCP Server
  ↓ (calls tool: get_deployment_status(application="web-app", environment="prod"))

tools/devops.py
  ↓ (calls: execute_cli_command(["status", "--app", "web-app", "--env", "prod"]))

cli_wrapper.py
  ↓ (spawns: subprocess ["./acme-devops-cli/devops-cli", "status", ...])

DevOps CLI Tool (external)
  ↓ (returns JSON to stdout)

cli_wrapper.py
  ↓ (returns: CLIExecutionResult)

tools/devops.py
  ↓ (parses JSON, validates structure)
  ↓ (returns: DeploymentStatusResponse dict)

FastMCP Server
  ↓ (serializes to JSON-RPC response)

MCP Client
  ✓ (displays: structured deployment information)
```

---

## Type Definitions (Python)

**File**: `stdio-mcp-server/src/cli_wrapper.py`
```python
from typing import NamedTuple

class CLIExecutionResult(NamedTuple):
    """Result of executing a CLI command."""
    stdout: str
    stderr: str
    returncode: int
```

**File**: `stdio-mcp-server/src/tools/devops.py`
```python
from typing import Any

# Type aliases for clarity
DeploymentDict = dict[str, Any]
DeploymentStatusResponse = dict[str, Any]

# Tool function signature
async def get_deployment_status(
    application: str | None = None,
    environment: str | None = None
) -> DeploymentStatusResponse:
    """Get deployment status from DevOps CLI.

    Args:
        application: Optional application filter (e.g., "web-app")
        environment: Optional environment filter (e.g., "prod")

    Returns:
        DeploymentStatusResponse with structure:
        {
            "status": "success",
            "deployments": [Deployment, ...],
            "total_count": int,
            "filters_applied": {"application": str|null, "environment": str|null},
            "timestamp": str (ISO 8601)
        }

    Raises:
        RuntimeError: CLI execution failed or timed out
        ValueError: CLI returned invalid JSON
    """
    ...
```

---

## Validation Strategy

**No server-side validation of business logic**:
- Application/environment values are passed through to CLI tool
- CLI tool validates if application exists, environment is valid, etc.
- Server only validates JSON structure and required fields

**JSON Structure Validation**:
```python
# After parsing JSON from CLI output
data = json.loads(result.stdout)

# Validate required top-level fields
required_fields = ["status", "deployments", "total_count", "filters_applied", "timestamp"]
for field in required_fields:
    if field not in data:
        raise ValueError(f"CLI output missing required field: {field}")

# Validate deployments is list
if not isinstance(data["deployments"], list):
    raise ValueError("CLI output 'deployments' must be an array")

# Return as-is (no further validation of deployment fields)
return data
```

---

## Future Entities (Phases 2-4)

**Phase 2**: `list_releases`
- `Release` entity
- `ReleaseListResponse` entity

**Phase 3**: `check_health`
- `HealthCheck` entity
- `HealthStatusResponse` entity

**Phase 4**: `promote_release`
- `PromotionRequest` entity (input)
- `PromotionResponse` entity (output)

---

## Summary

**Total Entities**: 4 (Phase 1)
- 1 internal type (`CLIExecutionResult`)
- 3 CLI data types (`Deployment`, `DeploymentStatusResponse`, `ToolParameters`)

**Validation Approach**: Structural only (required fields, types), no business logic

**Type Safety**: Full type hints on all functions, leveraging Python 3.11+ features

**Error Handling**: Explicit exceptions with user-friendly messages

---

**Data Model Complete**: ✅ Ready for contract generation
