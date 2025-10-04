# Research: Existing Patterns for CLI Wrapping & Validation

**Feature**: 006-add-promote-release
**Research Date**: 2025-10-05
**Purpose**: Analyze existing codebase patterns for implementing the promote-release tool

## Executive Summary

The codebase already contains well-established patterns for:
1. **CLI command execution** via `execute_cli_command()` helper
2. **Environment validation** via centralized `validate_environment()` (Feature 005)
3. **MCP tool definition** using FastMCP decorators
4. **Error handling** with explicit logging and structured results

**Recommendation**: Follow existing patterns for consistency. The promote-release tool should:
- Reuse `execute_cli_command()` with 300s timeout
- Leverage `validate_environment()` for from_env/to_env validation
- Add new `validate_promotion_path()` function for path validation
- Use FastMCP `@mcp.tool()` decorator for tool registration
- Return structured dictionaries matching existing tool patterns

## Existing Architecture Analysis

### 1. CLI Execution Pattern

**Location**: `stdio-mcp-server/src/server.py:108-177`

```python
async def execute_cli_command(
    args: list[str],
    timeout: float = 30.0,
    cwd: str | None = None,
) -> CLIExecutionResult
```

**Key Features**:
- Async subprocess execution with timeout management
- No shell injection (uses `create_subprocess_exec` with explicit args)
- Structured result via `CLIExecutionResult` NamedTuple (stdout, stderr, returncode)
- Comprehensive error handling (TimeoutError, FileNotFoundError, general exceptions)
- Automatic CLI path prepending (`../acme-devops-cli/devops-cli`)
- Execution timing and stderr logging

**Application to promote-release**:
✅ **Reuse directly** with `timeout=300.0` for promotion operations
✅ Command format: `await execute_cli_command(["promote", app, version, from_env, to_env], timeout=300.0)`
✅ Error handling already comprehensive; no modifications needed

### 2. Environment Validation Pattern

**Location**: `stdio-mcp-server/src/validation.py` (Feature 005)

**Key Features**:
- Centralized `VALID_ENVIRONMENTS = frozenset({"dev", "staging", "uat", "prod"})`
- `validate_environment(env: str | None) -> str | None` function
- Case-insensitive matching with lowercase normalization
- Whitespace trimming
- None handling (passes through for "all environments")
- Structured ValueError with helpful error messages listing valid options

**Usage in get_deployment_status** (line 248-250):
```python
if environment is not None:
    environment = validate_environment(environment)
```

**Application to promote-release**:
✅ **Reuse for from_env and to_env validation**
✅ Both parameters are required (not None), so validation will always execute
✅ Add new validation: `validate_promotion_path(from_env, to_env)` after environment validation

### 3. MCP Tool Definition Pattern

**Example**: `get_deployment_status` tool (lines 184-247)

**Key Features**:
- FastMCP `@mcp.tool()` decorator for automatic registration
- Comprehensive docstring with Args, Returns, Raises, Examples
- Type hints on all parameters and return type
- Optional parameters with `| None` type annotation and defaults
- Structured dictionary returns with consistent keys
- Explicit error handling with meaningful exceptions

**Return Structure Pattern**:
```python
{
    "status": "success" | "error",
    "data": {...},  # Tool-specific payload
    "timestamp": str,  # ISO 8601
    "metadata": {...}  # Optional contextual info
}
```

**Application to promote-release**:
✅ Use same decorator pattern: `@mcp.tool() async def promote_release(...)`
✅ All 4 parameters are required (no defaults)
✅ Return structure:
```python
{
    "status": "success" | "error",
    "promotion": {
        "app": str,
        "version": str,
        "from_env": str,
        "to_env": str,
        "cli_output": str,
        "execution_time": float
    },
    "production_deployment": bool,  # True if to_env == "prod"
    "timestamp": str
}
```

### 4. Parameter Validation Pattern

**Current Implementation** (get_deployment_status, check_health):
- Inline validation at function start
- Use centralized validators (validate_environment) where available
- Raise ValueError for validation failures (FastMCP converts to MCP error responses)
- Log validation failures to stderr

**Application to promote-release**:
Need new validation functions:

1. **Empty string validation** (for all 4 params):
```python
def validate_non_empty(param_name: str, value: str) -> str:
    value_trimmed = value.strip()
    if not value_trimmed:
        raise ValueError(f"{param_name} cannot be empty")
    return value_trimmed
```

2. **Promotion path validation** (strict forward flow):
```python
VALID_PROMOTION_PATHS = {
    ("dev", "staging"),
    ("staging", "uat"),
    ("uat", "prod"),
}

def validate_promotion_path(from_env: str, to_env: str) -> None:
    # Assumes from_env and to_env already validated and normalized
    if from_env == to_env:
        raise ValueError("cannot promote to same environment")

    if (from_env, to_env) not in VALID_PROMOTION_PATHS:
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

### 5. Production Safety Pattern

**Current Practice**: Enhanced logging for critical operations

**Application to promote-release**:
```python
if to_env == "prod":
    logger.warning(
        f"PRODUCTION DEPLOYMENT: Promoting {app} v{version} "
        f"from {from_env} to PRODUCTION"
    )
    logger.info(f"Production promotion audit trail: "
                f"app={app}, version={version}, from={from_env}, "
                f"timestamp={timestamp}, caller=MCP")
```

### 6. Error Handling & Logging Pattern

**Existing Patterns**:
- Log all CLI executions (INFO level) with command args
- Log stderr output from CLI (WARNING level)
- Log execution duration (DEBUG level)
- Catch TimeoutError separately from general exceptions
- Reraise exceptions after logging (let FastMCP convert to MCP errors)

**Application to promote-release**:
```python
try:
    result = await execute_cli_command(
        ["promote", app, version, from_env_lower, to_env_lower],
        timeout=300.0
    )

    if result.returncode != 0:
        logger.error(f"Promotion failed: {result.stderr}")
        raise RuntimeError(f"Promotion failed: {result.stderr}")

    return {
        "status": "success",
        "promotion": {...},
        ...
    }

except asyncio.TimeoutError:
    logger.error(f"Promotion timed out after 300s: {app} v{version} {from_env}→{to_env}")
    raise RuntimeError(
        f"Promotion operation timed out after 300 seconds. "
        f"The deployment may still be in progress. "
        f"Check deployment status manually."
    )
```

## Constitutional Compliance Analysis

### Principle I: Simplicity First
✅ Reuse existing helpers (execute_cli_command, validate_environment)
✅ Add only necessary new validation (promotion path logic)
✅ No unnecessary abstraction layers

### Principle II: Explicit Over Implicit
✅ Explicit validation for all parameters (empty strings, env names, paths)
✅ Explicit timeout handling (300s)
✅ Explicit error messages for each failure mode

### Principle III: Type Safety & Documentation
✅ Type hints: `async def promote_release(app: str, version: str, from_env: str, to_env: str) -> dict[str, Any]`
✅ Comprehensive docstring with Args, Returns, Raises, Examples
✅ Structured logging to stderr (INFO, WARNING, ERROR levels)

### Principle IV: Human-in-the-Loop
✅ Production deployments logged with enhanced audit trail
✅ Clear error messages for human interpretation
✅ Non-blocking (per clarification: log and proceed)

### Principle V: Dependencies
✅ No new external dependencies required
✅ Python 3.11+ stdlib only (asyncio, logging, typing)

### Principle VI: MCP Protocol Compliance
✅ FastMCP handles MCP protocol automatically
✅ All logging to stderr (no stdout pollution)
✅ ValueError exceptions converted to MCP error responses by framework

### Principle VII: Commit Discipline
✅ Implementation will follow TDD (tests first, then implementation)
✅ Each phase commits with conventional format

### Principle VIII: Automation via Make
✅ All testing via `make test`
✅ All execution via `make dev` or `make run`

## Recommended Implementation Approach

### Phase 1: Add Validation Functions
**File**: `stdio-mcp-server/src/validation.py`
- Add `validate_non_empty(param_name: str, value: str) -> str`
- Add `VALID_PROMOTION_PATHS` constant
- Add `validate_promotion_path(from_env: str, to_env: str) -> None`

### Phase 2: Implement promote-release Tool
**File**: `stdio-mcp-server/src/server.py`
- Add `@mcp.tool()` decorated `promote_release()` function
- Parameter validation order:
  1. Trim and validate non-empty for all params
  2. Validate from_env with `validate_environment()`
  3. Validate to_env with `validate_environment()`
  4. Validate promotion path with `validate_promotion_path()`
- Execute CLI with 300s timeout
- Log production deployments (if to_env == "prod")
- Return structured result

### Phase 3: Add Tests
**File**: `stdio-mcp-server/tests/test_promote_release.py`
- Test validation failures (empty params, invalid envs, invalid paths)
- Test CLI execution success/failure/timeout
- Test production logging
- Test structured response format

## Open Questions Deferred to Implementation

1. **Concurrency handling**: How to handle concurrent promotions for same app/env?
   - **Analysis**: MCP server is stateless (per FR-033), so no server-side blocking needed
   - **Recommendation**: Let concurrent requests execute independently; CLI or deployment infrastructure should handle conflicts

2. **Rollback support**: Automatic rollback on failure?
   - **Analysis**: Already confirmed out of scope in spec (line 275)
   - **Recommendation**: Document in tool docstring that manual rollback required

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| 300s timeout too short for complex deployments | Make timeout configurable in future if needed; start with 300s per clarification |
| CLI may change promote command format | Pin CLI version or add integration tests to detect breakage early |
| Production logging may not be sufficient for compliance | Document audit log format; can enhance later if needed |
| Promotion path validation too strict | Paths explicitly defined in clarifications; can be relaxed in future spec update |

## Conclusion

The existing codebase provides strong patterns for implementing promote-release:
- ✅ CLI execution infrastructure ready
- ✅ Environment validation infrastructure ready
- ✅ Error handling patterns established
- ✅ Constitutional compliance patterns proven

**Next Steps**:
1. Create data-model.md defining PromotionRequest structure
2. Create contracts defining test cases for validation
3. Create quickstart.md with integration examples
4. Implement following TDD approach (tests → implementation)
