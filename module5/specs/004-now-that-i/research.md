# Phase 0: Research - Additional DevOps CLI Tools

**Date**: 2025-10-04
**Feature**: list-releases & check-health tools

## Existing Pattern Analysis

### Reference Implementation: `get_deployment_status`
Located in `stdio-mcp-server/src/server.py` (lines 184-299)

**Key Pattern Elements**:
1. **Function signature**: `@mcp.tool()` decorator + async function
2. **Type hints**: Parameters use `str | None`, returns `dict[str, Any]`
3. **CLI wrapper usage**: `await execute_cli_command(args, timeout=30.0)`
4. **Args construction**: Build list then conditionally extend
5. **Error handling**:
   - Check `returncode != 0` → raise RuntimeError
   - Try/except for `json.loads()` → raise ValueError
   - Validate required fields in response
6. **Logging**: `logger.error()` and `logger.debug()` to stderr

**Decision**: Follow this exact pattern for both new tools ✅

## Parameter Validation Strategy

### Existing Approach
`get_deployment_status` has **optional** parameters - validation is minimal (just pass to CLI).

### New Requirements
- `list-releases`: **required** `app` parameter
- `list-releases`: **optional** `limit` parameter (must be positive integer)
- `check-health`: **optional** `env` parameter (must be valid environment)

**Decision**: Add validation BEFORE calling `execute_cli_command`
- **Rationale**: Fail fast with clear errors, prevent invalid CLI calls
- **Pattern**:
  ```python
  if not app:
      raise ValueError("app parameter is required")
  if limit is not None and limit < 1:
      raise ValueError("limit must be a positive integer")
  ```

### Case-Insensitive Environment Matching
**Requirement**: env parameter accepts "PROD", "Prod", "prod" (all valid)

**Decision**: Normalize to lowercase before passing to CLI
```python
if env:
    env_normalized = env.lower()
    if env_normalized not in ["prod", "staging", "uat", "dev"]:
        raise ValueError(f"Invalid environment: {env}")
    args.extend(["--env", env_normalized])
```

**Alternatives Considered**:
- Let CLI handle validation → Rejected (slower feedback, unclear errors)
- Use regex → Rejected (over-engineering for simple enum)

## CLI Tool Contract

### list-releases Command
```bash
./devops-cli releases --app {app} [--limit {limit}] --format json
```

**Expected Output** (based on existing pattern):
```json
{
  "status": "success",
  "releases": [...],
  "total_count": int,
  "filters_applied": {...}
}
```

### check-health Command
```bash
./devops-cli health [--env {env}] --format json
```

**Expected Output** (based on existing pattern):
```json
{
  "status": "success",
  "health_checks": [...],
  "timestamp": "ISO 8601"
}
```

**Decision**: Pass-through CLI output structure (no transformation needed)
- **Rationale**: Consistent with `get_deployment_status` approach

## Testing Strategy

### FastMCP Tool Testing
**Discovery**: FastMCP tools are tested via:
1. **Unit tests** with mocked `execute_cli_command`
2. **Integration tests** with real CLI or mock subprocess
3. **Manual testing** via `make dev` (FastMCP inspector)

**Decision**: Follow existing test structure in `tests/` directory
- `test_list_releases.py` - mirrors `test_ping.py` structure
- `test_check_health.py` - mirrors `test_ping.py` structure

### Mocking Strategy
**Pattern from existing code**:
```python
@pytest.mark.asyncio
async def test_tool_with_params():
    # Mock execute_cli_command if needed
    # Call tool function
    # Assert response structure
```

**Decision**: Use pytest-asyncio (already in dev dependencies) ✅

## Summary of Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| **Implementation Pattern** | Follow `get_deployment_status` exactly | Proven, constitutional, simple |
| **Validation Approach** | Validate before CLI call | Fail fast, clear errors |
| **Case Sensitivity** | Normalize to lowercase | Simple, explicit |
| **CLI Output** | Pass-through structure | No transformation needed |
| **Testing** | pytest-asyncio + existing patterns | Already in place |
| **Timeout** | Share 30s default | Constitutional requirement |

## Next Phase: Design & Contracts
- Extract data models from CLI output
- Write JSON schemas for tool contracts
- Generate failing tests (TDD)
- Document in quickstart.md
