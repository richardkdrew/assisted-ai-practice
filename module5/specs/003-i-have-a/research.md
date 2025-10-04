# Research: DevOps CLI Wrapper Implementation

**Feature**: 003-i-have-a (DevOps CLI Wrapper)
**Date**: 2025-10-04
**Phase**: 0 (Research & Technical Decisions)

## Research Questions

### 1. How to safely execute subprocess commands asynchronously in Python?

**Decision**: Use `asyncio.create_subprocess_exec()` with explicit argument passing

**Rationale**:
- `asyncio.create_subprocess_exec()` provides non-blocking subprocess execution compatible with FastMCP's async architecture
- Explicit argument passing (vs shell=True) prevents shell injection vulnerabilities
- Returns Process object with `.communicate()` for async stdout/stderr capture

**Pattern**:
```python
process = await asyncio.create_subprocess_exec(
    "./acme-devops-cli/devops-cli",
    "status",
    "--format", "json",
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
)
stdout, stderr = await process.communicate()
```

**Alternatives Considered**:
- `subprocess.run()`: Rejected - blocking, incompatible with async MCP server
- `shell=True`: Rejected - security risk (command injection)
- Threading: Rejected - adds complexity, async is native to FastMCP

**References**:
- Python asyncio docs: https://docs.python.org/3/library/asyncio-subprocess.html
- Security best practices: OWASP command injection prevention

---

### 2. What's the best practice for timeout management in async subprocess calls?

**Decision**: Use `asyncio.wait_for()` with configurable timeout (default 30s)

**Rationale**:
- `asyncio.wait_for()` cleanly raises `TimeoutError` after specified duration
- Prevents hanging MCP server if CLI tool becomes unresponsive
- Configurable timeout allows tuning per tool (status=30s, promote=60s)
- FastMCP can catch `TimeoutError` and return user-friendly error message

**Pattern**:
```python
try:
    result = await asyncio.wait_for(
        execute_cli_command(...),
        timeout=30.0
    )
except asyncio.TimeoutError:
    logger.error("CLI command timed out after 30s")
    raise MCPError("DevOps CLI command timed out")
```

**Alternatives Considered**:
- Manual timeout with `asyncio.create_task()` + `asyncio.sleep()`: Rejected - more complex, error-prone
- No timeout: Rejected - could hang server indefinitely
- Very short timeout (<5s): Rejected - CLI tool may legitimately need 10-20s for complex queries

**References**:
- asyncio.wait_for docs: https://docs.python.org/3/library/asyncio-task.html#asyncio.wait_for

---

### 3. How to capture and separate stdout/stderr from subprocess?

**Decision**: Use `PIPE` for both stdout and stderr, capture separately

**Rationale**:
- `subprocess.PIPE` captures output without leaking to MCP server's stdout
- Separate capture allows distinguishing normal output (stdout) from errors (stderr)
- Critical for MCP protocol compliance: server stdout must only contain JSON-RPC messages
- stderr can be logged for debugging while returning stdout as tool result

**Pattern**:
```python
process = await asyncio.create_subprocess_exec(
    *cmd_args,
    stdout=asyncio.subprocess.PIPE,  # Capture CLI output
    stderr=asyncio.subprocess.PIPE,  # Capture CLI errors
    cwd="/path/to/module5"           # Set working directory
)
stdout, stderr = await process.communicate()

if stderr:
    logger.warning(f"CLI stderr: {stderr.decode()}")
if process.returncode != 0:
    raise CLIExecutionError(f"CLI failed: {stderr.decode()}")
```

**Alternatives Considered**:
- `stderr=subprocess.STDOUT`: Rejected - mixes error and output, harder to parse
- No capture (inherit): Rejected - violates MCP protocol (corrupts stdout)
- `stderr=subprocess.DEVNULL`: Rejected - loses valuable error information

**References**:
- subprocess constants: https://docs.python.org/3/library/subprocess.html#subprocess.PIPE

---

### 4. How to handle JSON parsing errors from CLI output?

**Decision**: Explicit try/except with structured error messages and validation

**Rationale**:
- CLI tool might return malformed JSON if it crashes or changes output format
- `json.loads()` raises `JSONDecodeError` which FastMCP should catch and report
- Validate expected fields exist after parsing (e.g., "status", "deployments")
- Helps debug CLI tool issues vs MCP server issues

**Pattern**:
```python
try:
    data = json.loads(stdout.decode())
except json.JSONDecodeError as e:
    logger.error(f"Failed to parse CLI output as JSON: {e}")
    logger.debug(f"Raw output: {stdout.decode()}")
    raise ValueError(f"CLI returned invalid JSON: {e}")

# Validate expected structure
if "status" not in data:
    raise ValueError("CLI output missing 'status' field")
```

**Alternatives Considered**:
- Silent failure: Rejected - violates Principle II (Explicit Over Implicit)
- Return raw string: Rejected - MCP clients expect structured data
- Custom JSON parser: Rejected - stdlib `json` is well-tested and sufficient

**References**:
- json.JSONDecodeError: https://docs.python.org/3/library/json.html#json.JSONDecodeError

---

### 5. FastMCP error handling patterns for tool execution failures?

**Decision**: Raise Python exceptions, let FastMCP convert to JSON-RPC errors

**Rationale**:
- FastMCP automatically catches exceptions in tool functions
- Converts Python exceptions to JSON-RPC error responses (code -32603)
- Exception messages become user-facing error descriptions
- No need to manually construct MCP error objects

**Pattern**:
```python
@mcp.tool()
async def get_deployment_status(
    application: str | None = None,
    environment: str | None = None
) -> dict[str, Any]:
    """Get deployment status from DevOps CLI."""
    try:
        result = await execute_cli_command(["status", ...])
        return json.loads(result.stdout)
    except asyncio.TimeoutError:
        raise RuntimeError("DevOps CLI timed out after 30 seconds")
    except FileNotFoundError:
        raise RuntimeError("DevOps CLI tool not found at ./acme-devops-cli/devops-cli")
    except json.JSONDecodeError as e:
        raise ValueError(f"CLI returned invalid JSON: {e}")
```

**Error Mapping**:
- `TimeoutError` → "Command timed out" (user-friendly)
- `FileNotFoundError` → "CLI tool not found" (actionable)
- `JSONDecodeError` → "Invalid output format" (helps debug)
- Non-zero exit code → "CLI command failed: {stderr}" (includes CLI error message)

**Alternatives Considered**:
- Return error objects in tool response: Rejected - FastMCP handles this automatically
- Custom MCP error codes: Rejected - standard -32603 is sufficient, message is informative
- Catch all exceptions as generic error: Rejected - specific errors help debugging

**References**:
- FastMCP error handling: Exceptions automatically converted to JSON-RPC errors
- JSON-RPC error codes: -32603 = Internal error

---

## Technology Stack Summary

**Core Dependencies** (existing):
- Python 3.11+
- FastMCP 2.0+
- pytest + pytest-asyncio

**New Modules** (stdlib only):
- `asyncio`: Async subprocess execution
- `subprocess`: Process management
- `json`: JSON parsing
- `pathlib`: Path handling for CLI tool location
- `logging`: Structured logging to stderr
- `typing`: Type hints (Any, Optional, etc.)

**No New External Dependencies Required** ✅

---

## CLI Tool Analysis

**Location**: `./acme-devops-cli/devops-cli` (relative to module5/ directory)

**Commands Analyzed**:
1. `status` - Get deployment status
   - Params: `--app APP`, `--env ENV`, `--format {json,table}`
   - Output: JSON with `status`, `deployments[]`, `total_count`, `filters_applied`, `timestamp`
   - Example: `{"status": "success", "deployments": [...]}`

**Output Format**:
- Default: JSON (structured)
- Alternative: Table (human-readable, not for MCP)
- Error handling: Returns JSON with error status on failures

**Execution Pattern**:
```bash
./acme-devops-cli/devops-cli status --format json [--app APP] [--env ENV]
```

**Working Directory**:
- Must execute from `module5/` directory (CLI tool path is relative)
- Set `cwd` parameter in `create_subprocess_exec()`

---

## Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Async execution | `asyncio.create_subprocess_exec()` | Non-blocking, FastMCP compatible |
| Timeout | `asyncio.wait_for()` 30s default | Prevents hanging, configurable |
| stdout/stderr | Separate PIPE capture | Protocol compliance, debugging |
| JSON parsing | Explicit try/except | Explicit error handling (Principle II) |
| Error handling | Raise exceptions, FastMCP converts | Automatic, user-friendly messages |
| Dependencies | stdlib only | No new external packages (Principle V) |
| Working directory | `cwd=module5/` | CLI tool uses relative path |

---

## Implementation Modules

### Module 1: `cli_wrapper.py`
**Purpose**: Reusable async subprocess executor
**Functions**:
- `execute_cli_command(args, timeout, cwd)` → `CLIExecutionResult`
- Type: `CLIExecutionResult = NamedTuple[stdout: str, stderr: str, returncode: int]`

### Module 2: `tools/devops.py`
**Purpose**: MCP tool implementations using FastMCP decorators
**Functions** (Phase 1):
- `get_deployment_status(application, environment)` → `dict[str, Any]`
**Functions** (Future):
- `list_releases(limit, application)` → `dict[str, Any]`
- `check_health(environment, application)` → `dict[str, Any]`
- `promote_release(application, version, from_env, to_env)` → `dict[str, Any]`

---

## Testing Strategy

**Unit Tests** (`test_cli_wrapper.py`):
- Mock `create_subprocess_exec()` to avoid real CLI calls
- Test timeout handling
- Test error handling (non-zero exit codes)
- Test stdout/stderr capture

**Contract Tests** (`test_devops_tools.py`):
- Verify tool registered in server capabilities
- Validate parameter schema (application, environment optional)
- Validate return value structure

**Integration Tests** (`test_devops_tools.py`):
- Real CLI execution (requires CLI tool available)
- Various filter combinations
- Error scenarios (malformed JSON, timeouts)

---

## Performance Considerations

**Timeout Values**:
- `get_deployment_status`: 30s (query operation)
- `list_releases`: 30s (query operation)
- `check_health`: 30s (query operation)
- `promote_release`: 60s (write operation, may be slower)

**Overhead**:
- Subprocess creation: ~10-50ms
- JSON parsing: <1ms for typical payloads
- FastMCP routing: <1ms
- **Total overhead target**: <500ms

**Concurrency**:
- Each tool call runs in separate subprocess
- Multiple concurrent calls supported (FastMCP async)
- No shared state between calls

---

## Security Considerations

**Command Injection Prevention**:
- ✅ Use `create_subprocess_exec()` with explicit args (not shell=True)
- ✅ No string interpolation in command construction
- ✅ CLI tool path is hardcoded (not user-provided)

**Input Validation**:
- Application/environment parameters: No special validation needed (CLI tool validates)
- MCP client provides strings, passed directly to CLI
- CLI tool responsible for validating business logic

**Output Sanitization**:
- JSON parsing validates structure
- No execution of CLI output
- Errors logged to stderr (not returned to user verbatim if sensitive)

---

## Next Steps

**Phase 1 Artifacts** (generated by /plan):
- [x] research.md (this file)
- [ ] data-model.md
- [ ] contracts/get-status.json
- [ ] quickstart.md

**Phase 2** (/tasks command):
- [ ] Generate tasks.md with TDD task ordering

**Phase 3-4** (Implementation):
- [ ] Write tests (must fail initially)
- [ ] Implement cli_wrapper.py
- [ ] Implement tools/devops.py get_deployment_status
- [ ] Verify tests pass
- [ ] Manual testing via make dev

---

**Research Complete**: ✅ All unknowns resolved, ready for design phase
