# Implementation Plan: Promote Release Tool

**Feature**: 006-add-promote-release
**Branch**: `006-add-promote-release`
**Created**: 2025-10-05
**Status**: ✅ READY FOR IMPLEMENTATION

## Executive Summary

This plan details the implementation of the `promote-release` MCP tool, which wraps the `devops-cli promote` command with comprehensive validation, production safety measures, and constitutional compliance.

**Complexity**: HIGH - Most complex tool to date, requiring:
- Multi-parameter validation with interdependencies
- Strict promotion path enforcement (dev→staging→uat→prod)
- Production deployment safeguards with enhanced audit logging
- 300-second timeout management for long-running operations

**Estimated Effort**: 4-6 hours (including TDD test implementation)

**Risk Level**: MEDIUM
- Production deployments carry inherent risk (mitigated by enhanced logging)
- 300s timeout may be insufficient for some deployments (can be adjusted later)
- CLI version changes could break integration (mitigated by tests)

## Technical Context

### Feature Specification
**Source**: [spec.md](spec.md)

**Key Requirements**:
- Tool name: `promote-release`
- 4 required parameters: app, version, from_env, to_env
- Strict forward promotion flow: dev→staging→uat→prod (no skipping)
- Environment validation using Feature 005 infrastructure
- 300-second (5-minute) CLI execution timeout
- Production deployments log enhanced audit trail but proceed automatically

### Clarifications Resolved
Per `/clarify` session (2025-10-05):

1. **App validation**: Let CLI handle existence; MCP validates non-empty strings only
2. **Version format**: Accept any non-empty string; CLI validates existence
3. **Promotion paths**: Strict forward flow only (no skipping, no backward)
4. **Timeout**: 300 seconds for all promotion operations
5. **Production warnings**: Enhanced logging with audit trail; non-blocking

**Deferred** (low impact on MVP):
- Concurrency handling for same app/env (server is stateless; CLI/infrastructure handles)
- Rollback support (confirmed out of scope; manual rollback procedures)

### Constitutional Compliance

| Principle | Compliance Strategy |
|-----------|---------------------|
| I. Simplicity First | Reuse existing helpers (execute_cli_command, validate_environment); minimal new code |
| II. Explicit Over Implicit | Explicit validation for all parameters; clear error messages for each failure mode |
| III. Type Safety & Documentation | Type hints on all functions; comprehensive docstrings; structured logging to stderr |
| IV. Human-in-the-Loop | Production deployments logged with full audit trail before execution |
| V. Dependencies | No new external dependencies; Python 3.11+ stdlib only |
| VI. MCP Protocol Compliance | FastMCP handles protocol; all logging to stderr |
| VII. Commit Discipline | TDD approach with commits after tests, implementation, integration |
| VIII. Automation via Make | All testing via `make test`, execution via `make dev` |

## Architecture

### Existing Infrastructure (Reuse)

From Feature 005 (`stdio-mcp-server/src/validation.py`):
```python
VALID_ENVIRONMENTS = frozenset({"dev", "staging", "uat", "prod"})

def validate_environment(env: str | None) -> str | None:
    # Case-insensitive validation, lowercase normalization
    # Raises ValueError with helpful message on failure
```

From `stdio-mcp-server/src/server.py`:
```python
async def execute_cli_command(
    args: list[str],
    timeout: float = 30.0,
    cwd: str | None = None,
) -> CLIExecutionResult:
    # Async subprocess execution with timeout
    # Returns NamedTuple(stdout, stderr, returncode)
```

### New Components

**1. Validation Functions** (`validation.py`):

```python
def validate_non_empty(param_name: str, value: str) -> str:
    """Trim and validate non-empty; raise ValueError if empty."""

VALID_PROMOTION_PATHS = frozenset({
    ("dev", "staging"),
    ("staging", "uat"),
    ("uat", "prod"),
})

def validate_promotion_path(from_env: str, to_env: str) -> None:
    """Validate promotion path follows strict forward flow."""
```

**2. MCP Tool** (`server.py`):

```python
@mcp.tool()
async def promote_release(
    app: str,
    version: str,
    from_env: str,
    to_env: str
) -> dict[str, Any]:
    """Promote application release between environments."""
```

### Data Flow

```
MCP Client Request
  ↓
promote_release(app, version, from_env, to_env)
  ↓
1. Validate & trim all parameters (validate_non_empty)
  ↓
2. Validate environments (validate_environment) → normalize to lowercase
  ↓
3. Validate promotion path (validate_promotion_path)
  ↓
4. Check if production deployment (to_env == "prod")
   └─ If yes: Log WARNING + audit trail
  ↓
5. Execute CLI: ["promote", app, version, from_env, to_env]
   timeout=300.0
  ↓
6. Check CLI return code
   ├─ returncode == 0: Build success response
   └─ returncode != 0: Raise RuntimeError with CLI error
  ↓
7. Return PromotionResult
  ↓
MCP Client Response
```

## Implementation Phases

### Phase 0: Research ✅
**Artifact**: [research.md](research.md)

**Completed**: Analysis of existing CLI wrapping patterns, validation infrastructure, and constitutional compliance approach.

**Key Findings**:
- `execute_cli_command()` ready for reuse with 300s timeout
- `validate_environment()` from Feature 005 ready for reuse
- Need new `validate_non_empty()` and `validate_promotion_path()` functions
- Production logging pattern established

---

### Phase 1: Design ✅
**Artifacts**:
- [data-model.md](data-model.md) - Data structures and validation rules
- [contracts/validation.schema.json](contracts/validation.schema.json) - Test contracts
- [quickstart.md](quickstart.md) - Integration examples

**Completed**:
- Defined PromotionRequest and PromotionResult structures
- Specified all validation functions with test cases
- Documented 9 integration scenarios
- Created test contracts for TDD implementation

---

### Phase 2: Implementation (Next Steps)

#### Task 2.1: Add Validation Functions

**File**: `stdio-mcp-server/src/validation.py`

**Implementation**:

```python
# Add after existing validate_environment function

def validate_non_empty(param_name: str, value: str) -> str:
    """
    Validate that a parameter is non-empty after trimming whitespace.

    Args:
        param_name: Name of parameter (for error messages)
        value: Value to validate

    Returns:
        Trimmed value if non-empty

    Raises:
        ValueError: If value is empty after trimming
    """
    value_trimmed = value.strip()
    if not value_trimmed:
        logger.warning(f"Validation failed: {param_name} cannot be empty")
        raise ValueError(f"{param_name} cannot be empty")
    return value_trimmed


VALID_PROMOTION_PATHS = frozenset({
    ("dev", "staging"),
    ("staging", "uat"),
    ("uat", "prod"),
})


def validate_promotion_path(from_env: str, to_env: str) -> None:
    """
    Validate promotion path follows strict forward flow rules.

    Valid paths: dev→staging, staging→uat, uat→prod
    No skipping environments, no backward promotion.

    Args:
        from_env: Source environment (must be normalized lowercase)
        to_env: Target environment (must be normalized lowercase)

    Raises:
        ValueError: If promotion path is invalid
    """
    if from_env == to_env:
        logger.warning(f"Validation failed: cannot promote to same environment ({from_env})")
        raise ValueError("cannot promote to same environment")

    if (from_env, to_env) not in VALID_PROMOTION_PATHS:
        # Find valid next environments from from_env
        valid_next = [to for (frm, to) in VALID_PROMOTION_PATHS if frm == from_env]

        if valid_next:
            logger.warning(
                f"Validation failed: invalid promotion path {from_env}→{to_env}, "
                f"valid next: {valid_next}"
            )
            raise ValueError(
                f"invalid promotion path: {from_env}→{to_env} "
                f"(valid next environment from {from_env}: {', '.join(valid_next)})"
            )
        else:
            logger.warning(
                f"Validation failed: backward or invalid promotion {from_env}→{to_env}"
            )
            raise ValueError(
                f"invalid promotion path: {from_env}→{to_env} "
                f"(backward or invalid promotion not allowed)"
            )
```

**Tests**: See Task 2.2

**Commit**: `feat: add validation functions for promotion path enforcement`

---

#### Task 2.2: Add Validation Tests

**File**: `stdio-mcp-server/tests/test_promotion_validation.py` (new)

**Implementation** (using contracts):

```python
"""Tests for promotion-specific validation functions."""

import pytest
from stdio-mcp-server.src.validation import (
    validate_non_empty,
    validate_promotion_path,
    VALID_PROMOTION_PATHS,
)


class TestValidateNonEmpty:
    """Tests for validate_non_empty function."""

    def test_valid_non_empty_string(self):
        """Standard non-empty string should pass validation."""
        result = validate_non_empty("app", "web-api")
        assert result == "web-api"

    def test_valid_with_whitespace(self):
        """Whitespace should be trimmed."""
        result = validate_non_empty("version", "  1.2.3  ")
        assert result == "1.2.3"

    def test_empty_string_raises_error(self):
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="app cannot be empty"):
            validate_non_empty("app", "")

    def test_whitespace_only_raises_error(self):
        """Whitespace-only string should raise ValueError."""
        with pytest.raises(ValueError, match="version cannot be empty"):
            validate_non_empty("version", "   ")

    def test_tab_newline_whitespace_raises_error(self):
        """All types of whitespace should be stripped."""
        with pytest.raises(ValueError, match="app cannot be empty"):
            validate_non_empty("app", "\t\n\r")


class TestValidatePromotionPath:
    """Tests for validate_promotion_path function."""

    def test_valid_dev_to_staging(self):
        """dev→staging is valid forward path."""
        validate_promotion_path("dev", "staging")  # Should not raise

    def test_valid_staging_to_uat(self):
        """staging→uat is valid forward path."""
        validate_promotion_path("staging", "uat")  # Should not raise

    def test_valid_uat_to_prod(self):
        """uat→prod is valid forward path (production deployment)."""
        validate_promotion_path("uat", "prod")  # Should not raise

    def test_invalid_same_environment(self):
        """Promoting to same environment should be rejected."""
        with pytest.raises(ValueError, match="cannot promote to same environment"):
            validate_promotion_path("dev", "dev")

    def test_invalid_skipping_staging(self):
        """Cannot skip staging from dev."""
        with pytest.raises(ValueError) as exc_info:
            validate_promotion_path("dev", "uat")

        error_msg = str(exc_info.value)
        assert "invalid promotion path" in error_msg
        assert "dev→uat" in error_msg
        assert "staging" in error_msg

    def test_invalid_skipping_uat(self):
        """Cannot skip uat from staging."""
        with pytest.raises(ValueError) as exc_info:
            validate_promotion_path("staging", "prod")

        error_msg = str(exc_info.value)
        assert "invalid promotion path" in error_msg
        assert "staging→prod" in error_msg
        assert "uat" in error_msg

    def test_invalid_backward_prod_to_uat(self):
        """Backward promotion from prod should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_promotion_path("prod", "uat")

        error_msg = str(exc_info.value)
        assert "invalid promotion path" in error_msg
        assert "prod→uat" in error_msg
        assert "backward" in error_msg

    def test_invalid_backward_staging_to_dev(self):
        """Backward promotion from staging should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_promotion_path("staging", "dev")

        error_msg = str(exc_info.value)
        assert "invalid promotion path" in error_msg
        assert "staging→dev" in error_msg
        assert "backward" in error_msg


class TestPromotionPathsConstant:
    """Tests for VALID_PROMOTION_PATHS constant."""

    def test_promotion_paths_structure(self):
        """Verify promotion paths are correctly defined."""
        assert ("dev", "staging") in VALID_PROMOTION_PATHS
        assert ("staging", "uat") in VALID_PROMOTION_PATHS
        assert ("uat", "prod") in VALID_PROMOTION_PATHS
        assert len(VALID_PROMOTION_PATHS) == 3

    def test_promotion_paths_immutable(self):
        """VALID_PROMOTION_PATHS should be immutable frozenset."""
        assert isinstance(VALID_PROMOTION_PATHS, frozenset)
```

**Execution**: `make test` (should show 18 new tests, all passing)

**Commit**: `test: add validation tests for promotion path enforcement`

---

#### Task 2.3: Implement promote_release Tool

**File**: `stdio-mcp-server/src/server.py`

**Implementation** (add after existing tools):

```python
from datetime import datetime, timezone
from .validation import validate_environment, validate_non_empty, validate_promotion_path


@mcp.tool()
async def promote_release(
    app: str,
    version: str,
    from_env: str,
    to_env: str,
) -> dict[str, Any]:
    """
    Promote application release between environments.

    Executes the devops-cli promote command with comprehensive validation
    and production deployment safeguards. Follows strict forward promotion
    flow: dev→staging→uat→prod (no skipping, no backward promotion).

    Args:
        app: Application name (required, non-empty)
        version: Version identifier (required, non-empty)
        from_env: Source environment (required: dev|staging|uat|prod)
        to_env: Target environment (required: dev|staging|uat|prod)

    Returns:
        Dictionary containing:
        - status: "success" or "error"
        - promotion: Details (app, version, envs, CLI output, execution time)
        - production_deployment: Boolean (True if to_env is "prod")
        - timestamp: ISO 8601 timestamp

    Raises:
        ValueError: If validation fails (empty params, invalid envs, invalid path)
        RuntimeError: If CLI execution fails or times out

    Examples:
        >>> # Promote from dev to staging
        >>> result = await promote_release(
        ...     app="web-api",
        ...     version="1.2.3",
        ...     from_env="dev",
        ...     to_env="staging"
        ... )
        >>> print(result["status"])
        "success"

        >>> # Production deployment (uat → prod)
        >>> result = await promote_release(
        ...     app="mobile-app",
        ...     version="2.0.1",
        ...     from_env="uat",
        ...     to_env="prod"
        ... )
        >>> print(result["production_deployment"])
        True
    """
    start_time = asyncio.get_event_loop().time()

    # Step 1: Validate and trim all parameters
    app = validate_non_empty("app", app)
    version = validate_non_empty("version", version)
    from_env = validate_non_empty("from_env", from_env)
    to_env = validate_non_empty("to_env", to_env)

    # Step 2: Validate environments and normalize to lowercase
    from_env_lower = validate_environment(from_env)
    to_env_lower = validate_environment(to_env)

    # validate_environment returns None for None input, but our params are required
    assert from_env_lower is not None
    assert to_env_lower is not None

    # Step 3: Validate promotion path
    validate_promotion_path(from_env_lower, to_env_lower)

    # Step 4: Check for production deployment and log audit trail
    is_production = to_env_lower == "prod"
    timestamp = datetime.now(timezone.utc).isoformat()

    if is_production:
        logger.warning(
            f"PRODUCTION DEPLOYMENT: Promoting {app} v{version} "
            f"from {from_env_lower} to PRODUCTION"
        )
        logger.info(
            f"Production promotion audit trail: app={app}, version={version}, "
            f"from={from_env_lower}, timestamp={timestamp}, caller=MCP"
        )

    # Step 5: Execute CLI command with 300s timeout
    try:
        result = await execute_cli_command(
            ["promote", app, version, from_env_lower, to_env_lower],
            timeout=300.0,
        )

        execution_time = asyncio.get_event_loop().time() - start_time

        # Check CLI return code
        if result.returncode != 0:
            logger.error(f"Promotion failed: {result.stderr}")
            raise RuntimeError(f"Promotion failed: {result.stderr}")

        # Step 6: Build success response
        return {
            "status": "success",
            "promotion": {
                "app": app,
                "version": version,
                "from_env": from_env_lower,
                "to_env": to_env_lower,
                "cli_output": result.stdout,
                "cli_stderr": result.stderr,
                "execution_time_seconds": execution_time,
            },
            "production_deployment": is_production,
            "timestamp": timestamp,
        }

    except asyncio.TimeoutError:
        logger.error(
            f"Promotion timed out after 300s: {app} v{version} "
            f"{from_env_lower}→{to_env_lower}"
        )
        raise RuntimeError(
            f"Promotion operation timed out after 300 seconds. "
            f"The deployment may still be in progress. "
            f"Check deployment status manually."
        )
```

**Commit**: `feat: implement promote-release tool with path validation and production safeguards`

---

#### Task 2.4: Add Integration Tests

**File**: `stdio-mcp-server/tests/test_promote_release.py` (new)

**Implementation** (excerpt - full file uses all contracts):

```python
"""Integration tests for promote_release tool."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from stdio-mcp-server.src.server import promote_release, CLIExecutionResult


@pytest.mark.asyncio
class TestPromoteReleaseIntegration:
    """Integration tests for promote_release tool."""

    @patch("stdio-mcp-server.src.server.execute_cli_command")
    async def test_success_non_production(self, mock_exec):
        """Successful non-production promotion."""
        mock_exec.return_value = CLIExecutionResult(
            stdout="Deployment successful: web-api v1.2.3 promoted to staging",
            stderr="",
            returncode=0,
        )

        result = await promote_release(
            app="web-api",
            version="1.2.3",
            from_env="dev",
            to_env="staging",
        )

        assert result["status"] == "success"
        assert result["promotion"]["app"] == "web-api"
        assert result["promotion"]["version"] == "1.2.3"
        assert result["promotion"]["from_env"] == "dev"
        assert result["promotion"]["to_env"] == "staging"
        assert result["production_deployment"] is False
        assert "timestamp" in result

        mock_exec.assert_called_once_with(
            ["promote", "web-api", "1.2.3", "dev", "staging"],
            timeout=300.0,
        )

    @patch("stdio-mcp-server.src.server.execute_cli_command")
    async def test_success_production_deployment(self, mock_exec):
        """Production deployment logs WARNING and sets flag."""
        mock_exec.return_value = CLIExecutionResult(
            stdout="Production deployment complete",
            stderr="",
            returncode=0,
        )

        result = await promote_release(
            app="mobile-app",
            version="2.0.1",
            from_env="uat",
            to_env="prod",
        )

        assert result["status"] == "success"
        assert result["production_deployment"] is True

    @pytest.mark.parametrize("app,expected_error", [
        ("", "app cannot be empty"),
        ("   ", "app cannot be empty"),
    ])
    async def test_validation_error_empty_app(self, app, expected_error):
        """Empty app parameter fails validation."""
        with pytest.raises(ValueError, match=expected_error):
            await promote_release(
                app=app,
                version="1.0.0",
                from_env="dev",
                to_env="staging",
            )

    async def test_validation_error_invalid_path(self):
        """Invalid promotion path fails validation."""
        with pytest.raises(ValueError, match="invalid promotion path"):
            await promote_release(
                app="web-api",
                version="1.0.0",
                from_env="dev",
                to_env="prod",  # Skipping staging and uat
            )

    @patch("stdio-mcp-server.src.server.execute_cli_command")
    async def test_cli_execution_failure(self, mock_exec):
        """CLI execution failure raises RuntimeError."""
        mock_exec.return_value = CLIExecutionResult(
            stdout="",
            stderr="Error: Version not found",
            returncode=1,
        )

        with pytest.raises(RuntimeError, match="Promotion failed"):
            await promote_release(
                app="web-api",
                version="9.9.9",
                from_env="dev",
                to_env="staging",
            )

    @patch("stdio-mcp-server.src.server.execute_cli_command")
    async def test_cli_timeout(self, mock_exec):
        """CLI timeout raises RuntimeError with helpful message."""
        mock_exec.side_effect = asyncio.TimeoutError()

        with pytest.raises(RuntimeError, match="timed out after 300 seconds"):
            await promote_release(
                app="slow-app",
                version="1.0.0",
                from_env="dev",
                to_env="staging",
            )

    async def test_case_insensitive_normalization(self):
        """Environment names normalized to lowercase."""
        with patch("stdio-mcp-server.src.server.execute_cli_command") as mock_exec:
            mock_exec.return_value = CLIExecutionResult(
                stdout="Success",
                stderr="",
                returncode=0,
            )

            result = await promote_release(
                app="web-api",
                version="1.0.0",
                from_env="DEV",
                to_env="STAGING",
            )

            assert result["promotion"]["from_env"] == "dev"
            assert result["promotion"]["to_env"] == "staging"

            mock_exec.assert_called_once_with(
                ["promote", "web-api", "1.0.0", "dev", "staging"],
                timeout=300.0,
            )
```

**Execution**: `make test` (should show all validation + integration tests passing)

**Commit**: `test: add integration tests for promote-release tool`

---

#### Task 2.5: Update Documentation

**File**: `stdio-mcp-server/README.md`

Add to "Available Tools" section:

```markdown
### promote-release

Promote application releases between environments with validation and production safeguards.

**Parameters**:
- `app` (string, required): Application name
- `version` (string, required): Version identifier
- `from_env` (string, required): Source environment (dev|staging|uat|prod)
- `to_env` (string, required): Target environment (dev|staging|uat|prod)

**Valid Promotion Paths**: dev→staging→uat→prod (strict forward flow only)

**Timeout**: 300 seconds (5 minutes)

**Example**:
```json
{
  "name": "promote-release",
  "arguments": {
    "app": "web-api",
    "version": "1.2.3",
    "from_env": "dev",
    "to_env": "staging"
  }
}
```

**Production Deployments** (to_env="prod"): Enhanced audit logging with WARNING level.
```

**File**: `module5/CLAUDE.md`

Add to "Recent Changes" section:

```markdown
## Recent Changes

1. **Feature 006-add-promote-release implemented** (2025-10-05): Promote release tool - wraps devops-cli promote command with strict path validation (dev→staging→uat→prod), 300s timeout, production deployment safeguards, comprehensive error handling
```

**Commit**: `docs: add promote-release tool documentation and update CLAUDE.md`

---

#### Task 2.6: Manual Testing with MCP Inspector

**Execution**:
1. `make dev` to start MCP Inspector
2. Test scenarios from [quickstart.md](quickstart.md):
   - ✅ Valid dev→staging promotion
   - ✅ Valid uat→prod promotion (check production logs)
   - ✅ Empty parameter validation error
   - ✅ Invalid environment validation error
   - ✅ Invalid path validation error (dev→prod)
   - ✅ Case-insensitive normalization

**Verification**: All 9 scenarios from quickstart.md should behave as documented

---

#### Task 2.7: Final Integration & Commit

**Execution**:
1. Run full test suite: `make test`
   - Expected: All tests passing (validation + integration)
   - Expected: Coverage ≥95% for new code

2. Test with real CLI (optional if CLI available):
   - Attempt real promotion
   - Verify CLI receives correct arguments
   - Verify timeout behavior

3. Create final commit:

**Commit**: `feat: complete Feature 006 - promote-release tool with full validation and tests`

---

## Progress Tracking

| Phase | Task | Status | Artifact |
|-------|------|--------|----------|
| 0 | Research | ✅ Complete | research.md |
| 1 | Data Model | ✅ Complete | data-model.md |
| 1 | Contracts | ✅ Complete | contracts/validation.schema.json |
| 1 | Integration Examples | ✅ Complete | quickstart.md |
| 2.1 | Add Validation Functions | ⏳ Pending | src/validation.py |
| 2.2 | Add Validation Tests | ⏳ Pending | tests/test_promotion_validation.py |
| 2.3 | Implement Tool | ⏳ Pending | src/server.py |
| 2.4 | Add Integration Tests | ⏳ Pending | tests/test_promote_release.py |
| 2.5 | Update Documentation | ⏳ Pending | README.md, CLAUDE.md |
| 2.6 | Manual Testing | ⏳ Pending | MCP Inspector verification |
| 2.7 | Final Integration | ⏳ Pending | Commit: feat complete |

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| 300s timeout insufficient for some deployments | MEDIUM | MEDIUM | Document timeout in error message; suggest manual status check; can be made configurable in future |
| CLI command format changes | LOW | HIGH | Integration tests will catch breakage; pin CLI version if possible |
| Production logging not captured by monitoring | LOW | MEDIUM | Document audit log format; ensure stderr is captured in production |
| Concurrent promotions for same app/env | LOW | MEDIUM | Document that CLI/infrastructure should handle; MCP server is stateless |

## Success Criteria

- ✅ All validation tests passing (18 tests)
- ✅ All integration tests passing (≥10 tests)
- ✅ Code coverage ≥95% for new code
- ✅ MCP Inspector manual tests pass all 9 scenarios
- ✅ Production deployments log WARNING with audit trail
- ✅ Invalid promotion paths rejected with helpful error messages
- ✅ 300s timeout enforced with clear error message
- ✅ Constitutional compliance verified (all 8 principles)

## Post-Implementation

### Follow-Up Tasks (Future Enhancements)
1. **Configurable Timeout**: Add optional `timeout` parameter (default 300s)
2. **Dry-Run Mode**: Add `dry_run: bool` parameter for validation-only mode
3. **Rollback Tool**: Implement separate `rollback_release()` tool
4. **Promotion History**: Add optional promotion tracking/history
5. **Flexible Promotion Paths**: Load paths from configuration file

### Monitoring & Observability
- **Logs to Monitor**:
  - WARNING: Production deployments
  - INFO: Production audit trail
  - ERROR: Promotion failures, timeouts
- **Metrics to Track**:
  - Promotion success rate per environment pair
  - Timeout occurrence frequency
  - Average CLI execution time
  - Production deployment frequency

### Documentation Updates
- Update main project README with promote-release example
- Add troubleshooting section for common timeout issues
- Document manual rollback procedures

---

## Summary

This implementation plan provides:
- ✅ Complete task breakdown with code examples
- ✅ TDD approach (tests before implementation)
- ✅ Constitutional compliance verification
- ✅ Risk analysis with mitigations
- ✅ Clear success criteria

**Ready for**: `/tasks` command to generate actionable task list

**Next Command**: `/tasks` (generate tasks.md from this plan)
