# Data Model - Additional DevOps CLI Tools

**Feature**: list-releases & check-health
**Date**: 2025-10-04

## Entities

### Tool Parameters (Input)

#### list_releases Parameters
- `app`: string, required, non-empty
- `limit`: integer | None, optional, must be ≥1 if provided

#### check_health Parameters
- `env`: string | None, optional, must be in ["prod", "staging", "uat", "dev"] (case-insensitive)

### Response Structures (Output)

Both tools return `dict[str, Any]` - structure determined by CLI tool output (pass-through).

#### list_releases Response
```python
{
    "status": str,              # "success" or "error"
    "releases": list[dict],     # CLI-defined structure
    "total_count": int,
    "filters_applied": {
        "app": str,
        "limit": int | None
    }
}
```

#### check_health Response
```python
{
    "status": str,              # "success" or "error"
    "health_checks": list[dict], # CLI-defined structure
    "timestamp": str             # ISO 8601
}
```

## Validation Rules

### Input Validation
Performed BEFORE calling `execute_cli_command`:

**list_releases**:
```python
if not app:
    raise ValueError("app parameter is required")
if limit is not None and limit < 1:
    raise ValueError("limit must be a positive integer")
```

**check_health**:
```python
if env is not None:
    env_lower = env.lower()
    if env_lower not in ["prod", "staging", "uat", "dev"]:
        raise ValueError(f"Invalid environment: {env}. Must be one of: prod, staging, uat, dev")
```

### Output Validation
Performed AFTER CLI execution (following `get_deployment_status` pattern):

```python
# Check returncode
if result.returncode != 0:
    raise RuntimeError(f"DevOps CLI failed: {result.stderr}")

# Parse JSON
try:
    data = json.loads(result.stdout)
except json.JSONDecodeError as e:
    raise ValueError(f"CLI returned invalid JSON: {e}")

# Tool-specific validation (optional - can trust CLI output)
# list-releases: check for "releases" key
# check-health: check for "health_checks" key
```

## State Transitions

N/A - Stateless tools (no persistent state, each call independent)

## Relationships

- Both tools use shared `execute_cli_command` wrapper
- Both tools follow same error handling pattern as `get_deployment_status`
- No cross-tool dependencies
