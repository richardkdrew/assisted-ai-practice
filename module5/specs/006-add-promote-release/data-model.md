# Data Model: Promote Release Tool

**Feature**: 006-add-promote-release
**Created**: 2025-10-05
**Purpose**: Define data structures, validation rules, and state transitions for the promote-release tool

## Overview

The promote-release tool manages the lifecycle of promoting application releases between environments. This document defines all data structures, validation rules, constants, and state transitions required for implementation.

## Constants

### Valid Environments
```python
# Defined in stdio-mcp-server/src/validation.py (Feature 005)
VALID_ENVIRONMENTS = frozenset({"dev", "staging", "uat", "prod"})
```

**Rationale**: Immutable set provides O(1) lookup and prevents accidental modification.

### Valid Promotion Paths
```python
# New constant in stdio-mcp-server/src/validation.py
VALID_PROMOTION_PATHS = frozenset({
    ("dev", "staging"),
    ("staging", "uat"),
    ("uat", "prod"),
})
```

**Rules**:
- Strict forward flow only (no environment skipping)
- No backward promotion (e.g., prod→staging is invalid)
- No self-promotion (e.g., dev→dev is invalid)

**Rationale**: Frozenset of tuples provides efficient path lookup while enforcing immutability and order significance.

### Timeout Configuration
```python
PROMOTION_TIMEOUT_SECONDS = 300.0  # 5 minutes
```

**Rationale**: Per clarification session, 300 seconds accommodates most deployment operations while preventing indefinite hangs.

## Core Data Structures

### 1. PromotionRequest (Input)

**Purpose**: Validated input parameters for a promotion operation

**Python Type Representation**:
```python
from typing import TypedDict

class PromotionRequest(TypedDict):
    """Validated promotion request parameters.

    All fields have been validated and normalized:
    - app: Non-empty, trimmed, sanitized
    - version: Non-empty, trimmed, sanitized
    - from_env: Valid environment name, normalized to lowercase
    - to_env: Valid environment name, normalized to lowercase
    - promotion_path: Validated against VALID_PROMOTION_PATHS
    """
    app: str
    version: str
    from_env: str  # Normalized (lowercase)
    to_env: str    # Normalized (lowercase)
```

**Validation Sequence**:
```
Raw Input (app, version, from_env, to_env)
  ↓
1. Trim whitespace on all fields
  ↓
2. Validate non-empty for all fields → ValueError if empty
  ↓
3. Validate from_env ∈ VALID_ENVIRONMENTS → ValueError if invalid
  ↓
4. Normalize from_env to lowercase
  ↓
5. Validate to_env ∈ VALID_ENVIRONMENTS → ValueError if invalid
  ↓
6. Normalize to_env to lowercase
  ↓
7. Validate from_env ≠ to_env → ValueError if same
  ↓
8. Validate (from_env, to_env) ∈ VALID_PROMOTION_PATHS → ValueError if invalid
  ↓
9. Sanitize app and version for shell safety
  ↓
PromotionRequest (validated)
```

**Field Constraints**:

| Field | Type | Constraints | Example Valid | Example Invalid |
|-------|------|-------------|---------------|-----------------|
| app | str | Non-empty after trim, no shell metacharacters | "web-api", "mobile-app" | "", "app;rm -rf", "app\|ls" |
| version | str | Non-empty after trim, no shell metacharacters | "1.2.3", "v2.0.1-beta", "release-2024" | "", "1.2.3;echo" |
| from_env | str | Must be in VALID_ENVIRONMENTS, normalized | "dev", "staging", "uat" | "production", "test", "" |
| to_env | str | Must be in VALID_ENVIRONMENTS, normalized, ≠ from_env | "staging", "uat", "prod" | "dev" (if from_env="dev" and skipping staging), "" |

### 2. PromotionResult (Output)

**Purpose**: Structured response from a promotion operation

**Python Type Representation**:
```python
from typing import TypedDict, Literal

class PromotionResult(TypedDict):
    """Result of a promotion operation.

    Returned to MCP client with all relevant information
    about the promotion attempt, success or failure.
    """
    status: Literal["success", "error"]
    promotion: PromotionDetails
    production_deployment: bool
    timestamp: str  # ISO 8601 format

class PromotionDetails(TypedDict):
    """Details of the promotion operation."""
    app: str
    version: str
    from_env: str
    to_env: str
    cli_output: str
    cli_stderr: str
    execution_time_seconds: float
```

**Success Response Example**:
```json
{
  "status": "success",
  "promotion": {
    "app": "web-api",
    "version": "1.2.3",
    "from_env": "staging",
    "to_env": "uat",
    "cli_output": "Deployment successful: web-api v1.2.3 promoted to uat\nRollout completed in 42s",
    "cli_stderr": "",
    "execution_time_seconds": 45.3
  },
  "production_deployment": false,
  "timestamp": "2025-10-05T12:34:56.789Z"
}
```

**Error Response Example**:
```json
{
  "status": "error",
  "promotion": {
    "app": "web-api",
    "version": "1.2.3",
    "from_env": "uat",
    "to_env": "prod",
    "cli_output": "",
    "cli_stderr": "Error: Version 1.2.3 not found in uat environment",
    "execution_time_seconds": 2.1
  },
  "production_deployment": true,
  "timestamp": "2025-10-05T12:35:01.123Z"
}
```

### 3. Production Deployment Marker

**Purpose**: Flag production deployments for enhanced logging

**Implementation**:
```python
def is_production_deployment(to_env: str) -> bool:
    """Check if promotion targets production environment."""
    return to_env == "prod"
```

**Behavior**:
- When `is_production_deployment() == True`:
  - Log WARNING: "PRODUCTION DEPLOYMENT: Promoting {app} v{version} from {from_env} to PRODUCTION"
  - Log INFO with full audit trail: app, version, from_env, timestamp
  - Set `production_deployment: true` in response
  - Proceed automatically (no blocking per clarification)

## Validation Functions

### 1. validate_non_empty

**Location**: `stdio-mcp-server/src/validation.py` (new)

**Signature**:
```python
def validate_non_empty(param_name: str, value: str) -> str:
    """Validate that a parameter is non-empty after trimming.

    Args:
        param_name: Name of parameter for error messages
        value: Value to validate

    Returns:
        Trimmed value if non-empty

    Raises:
        ValueError: If value is empty after trimming
    """
```

**Logic**:
```python
value_trimmed = value.strip()
if not value_trimmed:
    raise ValueError(f"{param_name} cannot be empty")
return value_trimmed
```

**Test Cases** (see contracts/validation.schema.json):
- `validate_non_empty("app", "web-api")` → `"web-api"`
- `validate_non_empty("app", "  web-api  ")` → `"web-api"`
- `validate_non_empty("app", "")` → `ValueError: app cannot be empty`
- `validate_non_empty("app", "   ")` → `ValueError: app cannot be empty`

### 2. validate_promotion_path

**Location**: `stdio-mcp-server/src/validation.py` (new)

**Signature**:
```python
def validate_promotion_path(from_env: str, to_env: str) -> None:
    """Validate promotion path follows strict forward flow rules.

    Args:
        from_env: Source environment (must be normalized lowercase)
        to_env: Target environment (must be normalized lowercase)

    Raises:
        ValueError: If promotion path is invalid (same env, backward, or skipping)
    """
```

**Logic**:
```python
if from_env == to_env:
    raise ValueError("cannot promote to same environment")

if (from_env, to_env) not in VALID_PROMOTION_PATHS:
    # Find valid next environments from from_env
    valid_next = [to for (frm, to) in VALID_PROMOTION_PATHS if frm == from_env]

    if valid_next:
        raise ValueError(
            f"invalid promotion path: {from_env}→{to_env} "
            f"(valid next environment from {from_env}: {', '.join(valid_next)})"
        )
    else:
        raise ValueError(
            f"invalid promotion path: {from_env}→{to_env} "
            f"(backward or invalid promotion not allowed)"
        )
```

**Test Cases** (see contracts/validation.schema.json):
- `validate_promotion_path("dev", "staging")` → `None` (success)
- `validate_promotion_path("staging", "uat")` → `None` (success)
- `validate_promotion_path("uat", "prod")` → `None` (success)
- `validate_promotion_path("dev", "dev")` → `ValueError: cannot promote to same environment`
- `validate_promotion_path("dev", "uat")` → `ValueError: invalid promotion path: dev→uat (valid next environment from dev: staging)`
- `validate_promotion_path("prod", "dev")` → `ValueError: invalid promotion path: prod→dev (backward or invalid promotion not allowed)`

### 3. sanitize_for_shell (optional enhancement)

**Purpose**: Additional safety layer to prevent shell injection

**Signature**:
```python
import shlex

def sanitize_for_shell(value: str) -> str:
    """Ensure value is safe for subprocess execution.

    Note: execute_cli_command uses create_subprocess_exec with explicit
    args (not shell=True), so shell injection is already prevented.
    This is defense-in-depth.

    Args:
        value: Value to sanitize

    Returns:
        Sanitized value safe for subprocess args

    Raises:
        ValueError: If value contains dangerous characters
    """
```

**Logic** (conservative approach):
```python
# Check for shell metacharacters
dangerous_chars = {';', '|', '&', '$', '`', '(', ')', '<', '>', '\n', '\r'}
if any(char in value for char in dangerous_chars):
    raise ValueError(f"parameter contains invalid characters: {value}")

return value
```

**Note**: This is optional since `create_subprocess_exec` with explicit args already prevents shell injection. Include if extra paranoia desired.

## State Transitions

### Promotion Lifecycle

```
┌─────────────────┐
│   API Request   │
│  (app, version, │
│ from_env, to_env)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Validation    │──┐
│   (8 steps)     │  │ ValueError
└────────┬────────┘  │
         │           ▼
         │      ┌─────────┐
         │      │  Error  │
         │      │Response │
         │      └─────────┘
         ▼
┌─────────────────┐
│  Production?    │
│ (to_env==prod)  │
└────────┬────────┘
         │
    ┌────┴────┐
   Yes       No
    │         │
    ▼         │
┌─────────┐  │
│  Log    │  │
│ Warning │  │
└────┬────┘  │
     │       │
     └───┬───┘
         │
         ▼
┌─────────────────┐
│  Execute CLI    │
│ (timeout=300s)  │
└────────┬────────┘
         │
    ┌────┴────┐
  Success  Failure
    │         │
    │    ┌────┴────┐
    │  Timeout  Non-zero
    │    │      exit code
    │    │         │
    │    ▼         ▼
    │  ┌─────────────┐
    │  │   Error     │
    │  │  Response   │
    │  └─────────────┘
    ▼
┌─────────────────┐
│    Success      │
│   Response      │
└─────────────────┘
```

### Error States

| Error Type | HTTP Equivalent | MCP Error Code | User Action |
|-----------|-----------------|----------------|-------------|
| Empty parameter | 400 Bad Request | -32602 Invalid params | Provide all required parameters |
| Invalid environment | 400 Bad Request | -32602 Invalid params | Use valid environment name (dev, staging, uat, prod) |
| Invalid promotion path | 400 Bad Request | -32602 Invalid params | Follow strict forward flow (dev→staging→uat→prod) |
| CLI not found | 500 Internal Error | -32603 Internal error | Install devops-cli tool |
| CLI timeout | 504 Gateway Timeout | -32000 Server error | Check deployment status manually; may still be in progress |
| CLI execution failure | 500 Internal Error | -32000 Server error | Check CLI error message; fix deployment issue |

## Logging Requirements

### Standard Logs (All Promotions)

**INFO Level**:
```
Executing DevOps CLI: promote {app} {version} {from_env} {to_env}
CLI command completed in {duration}s
```

**WARNING Level** (if CLI stderr non-empty):
```
CLI stderr: {stderr_output}
```

**ERROR Level** (on failure):
```
Promotion failed: {stderr_output}
CLI command timed out after 300s
CLI tool not found at {path}
```

### Production Deployment Logs

**WARNING Level** (always for prod):
```
PRODUCTION DEPLOYMENT: Promoting {app} v{version} from {from_env} to PRODUCTION
```

**INFO Level** (audit trail):
```
Production promotion audit trail: app={app}, version={version}, from={from_env}, timestamp={timestamp}, caller=MCP
```

## Performance Characteristics

| Operation | Expected Duration | Constraint |
|-----------|-------------------|------------|
| Parameter validation | <1ms | <10ms (NF-001) |
| Environment validation | <1ms | <10ms (NF-001) |
| Path validation | <1ms | <10ms (NF-001) |
| Total validation overhead | <5ms | <10ms (NF-001) |
| CLI execution | 10s - 300s | 300s timeout (NF-002) |
| Total request duration | 10s - 300s | Dominated by CLI execution |

## Memory Footprint

| Component | Est. Memory | Notes |
|-----------|-------------|-------|
| Constants | <1 KB | VALID_ENVIRONMENTS, VALID_PROMOTION_PATHS |
| PromotionRequest | <1 KB | 4 short strings |
| CLI output buffer | <10 MB | Bounded by CLI output size |
| Total per request | <11 MB | Well within Python subprocess limits |

## Extension Points (Future Enhancements)

1. **Configurable Timeout**:
   - Add optional `timeout` parameter to `promote_release()`
   - Default remains 300s for backward compatibility

2. **Dry-Run Mode**:
   - Add optional `dry_run: bool` parameter
   - Validate without executing CLI

3. **Flexible Promotion Paths**:
   - Load VALID_PROMOTION_PATHS from config file
   - Allow environment-specific path overrides

4. **Rollback Support**:
   - Add separate `rollback_release()` tool
   - Track promotion history for rollback reference

## Summary

This data model provides:
- ✅ Complete type definitions for all structures
- ✅ Comprehensive validation rules matching spec requirements
- ✅ Clear state transition flows
- ✅ Constitutional compliance (explicit, typed, validated)
- ✅ Performance targets aligned with NF requirements
- ✅ Production safety through enhanced logging

**Ready for**: Contract definition (Phase 1) and test implementation (Phase 2)
