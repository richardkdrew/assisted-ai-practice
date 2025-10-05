# Implementation Tasks: Promote Release Tool

**Feature**: 006-add-promote-release
**Branch**: `006-add-promote-release`
**Status**: ⏳ IN PROGRESS
**Approach**: Test-Driven Development (TDD) - Tests first, then implementation

## Task Overview

This feature implements the `promote-release` MCP tool following strict TDD methodology:
1. Write tests first (must fail with NotImplementedError or assertion failures)
2. Implement minimal code to make tests pass
3. Verify all tests pass before proceeding

**Total Tasks**: 14
**Parallel Execution**: Tasks marked [P] can run concurrently
**Estimated Time**: 4-6 hours

---

## Phase 1: Setup & Validation Layer

### T001: Add Validation Function Stubs [P]
**File**: `module5/stdio-mcp-server/src/validation.py`
**Type**: Setup
**Dependencies**: None
**Parallel**: Yes - Different file from tests

**Objective**: Create placeholder functions for validation logic (will fail tests initially for TDD)

**Implementation**:
1. Add `validate_non_empty()` function stub:
   ```python
   def validate_non_empty(param_name: str, value: str) -> str:
       """Validate parameter is non-empty after trimming (stub)."""
       raise NotImplementedError("validate_non_empty not yet implemented")
   ```

2. Add `VALID_PROMOTION_PATHS` constant:
   ```python
   VALID_PROMOTION_PATHS = frozenset({
       ("dev", "staging"),
       ("staging", "uat"),
       ("uat", "prod"),
   })
   ```

3. Add `validate_promotion_path()` function stub:
   ```python
   def validate_promotion_path(from_env: str, to_env: str) -> None:
       """Validate promotion path follows strict forward flow (stub)."""
       raise NotImplementedError("validate_promotion_path not yet implemented")
   ```

**Success Criteria**:
- ✅ File compiles without syntax errors
- ✅ Functions are importable
- ✅ Type hints present on all functions

**Expected Test Result**: Tests will fail with NotImplementedError (correct for TDD)

---

### T002: Add validate_non_empty Tests [P]
**File**: `module5/stdio-mcp-server/tests/test_promotion_validation.py` (new)
**Type**: Test
**Dependencies**: T001 (stub functions must exist)
**Parallel**: Yes - Different file from implementation

**Objective**: Write failing tests for validate_non_empty function

**Implementation**:
```python
"""Tests for promotion-specific validation functions."""

import pytest
from stdio-mcp-server.src.validation import validate_non_empty


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
```

**Test Execution**: `cd module5/stdio-mcp-server && make test`

**Expected Result**: 5 tests FAIL with NotImplementedError (correct for TDD)

**Success Criteria**:
- ✅ All 5 tests fail with NotImplementedError
- ✅ Test file syntax is valid
- ✅ Tests are discoverable by pytest

---

### T003: Add validate_promotion_path Tests [P]
**File**: `module5/stdio-mcp-server/tests/test_promotion_validation.py`
**Type**: Test
**Dependencies**: T001 (stub functions must exist)
**Parallel**: Yes - Same file as T002 but independent test class

**Objective**: Write failing tests for validate_promotion_path function

**Implementation** (add to existing file):
```python
from stdio-mcp-server.src.validation import (
    validate_non_empty,
    validate_promotion_path,
    VALID_PROMOTION_PATHS,
)


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

**Test Execution**: `cd module5/stdio-mcp-server && make test`

**Expected Result**: 8 path validation tests FAIL with NotImplementedError, 2 constant tests PASS

**Success Criteria**:
- ✅ 8 validation tests fail with NotImplementedError
- ✅ 2 constant tests pass (constant is defined in T001)
- ✅ Total: 13 tests added (5 from T002 + 8 here)

---

### T004: Implement validate_non_empty Function
**File**: `module5/stdio-mcp-server/src/validation.py`
**Type**: Implementation
**Dependencies**: T002 (tests must exist and be failing)
**Parallel**: No - Must verify T002 tests fail first

**Objective**: Implement validate_non_empty to make T002 tests pass

**Implementation** (replace stub from T001):
```python
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
```

**Test Execution**: `cd module5/stdio-mcp-server && make test`

**Expected Result**: All 5 validate_non_empty tests PASS

**Success Criteria**:
- ✅ All 5 tests from T002 pass
- ✅ Function has type hints
- ✅ Function has comprehensive docstring
- ✅ Logs warning to stderr on validation failure

---

### T005: Implement validate_promotion_path Function
**File**: `module5/stdio-mcp-server/src/validation.py`
**Type**: Implementation
**Dependencies**: T003 (tests must exist and be failing)
**Parallel**: No - Must verify T003 tests fail first

**Objective**: Implement validate_promotion_path to make T003 tests pass

**Implementation** (replace stub from T001):
```python
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

**Test Execution**: `cd module5/stdio-mcp-server && make test`

**Expected Result**: All 8 validate_promotion_path tests PASS (plus 2 constant tests already passing)

**Success Criteria**:
- ✅ All 10 tests from T003 pass
- ✅ Function has type hints
- ✅ Function has comprehensive docstring
- ✅ Error messages match test expectations (include path notation like "dev→uat")

---

### T006: Verify Validation Layer Complete
**File**: N/A (verification task)
**Type**: Verification
**Dependencies**: T004, T005 (both implementations complete)
**Parallel**: No - Final verification step

**Objective**: Verify all validation tests pass and validation layer is complete

**Execution**:
```bash
cd module5/stdio-mcp-server
make test
```

**Expected Output**:
```
test_promotion_validation.py::TestValidateNonEmpty::test_valid_non_empty_string PASSED
test_promotion_validation.py::TestValidateNonEmpty::test_valid_with_whitespace PASSED
test_promotion_validation.py::TestValidateNonEmpty::test_empty_string_raises_error PASSED
test_promotion_validation.py::TestValidateNonEmpty::test_whitespace_only_raises_error PASSED
test_promotion_validation.py::TestValidateNonEmpty::test_tab_newline_whitespace_raises_error PASSED
test_promotion_validation.py::TestValidatePromotionPath::test_valid_dev_to_staging PASSED
test_promotion_validation.py::TestValidatePromotionPath::test_valid_staging_to_uat PASSED
test_promotion_validation.py::TestValidatePromotionPath::test_valid_uat_to_prod PASSED
test_promotion_validation.py::TestValidatePromotionPath::test_invalid_same_environment PASSED
test_promotion_validation.py::TestValidatePromotionPath::test_invalid_skipping_staging PASSED
test_promotion_validation.py::TestValidatePromotionPath::test_invalid_skipping_uat PASSED
test_promotion_validation.py::TestValidatePromotionPath::test_invalid_backward_prod_to_uat PASSED
test_promotion_validation.py::TestValidatePromotionPath::test_invalid_backward_staging_to_dev PASSED
test_promotion_validation.py::TestPromotionPathsConstant::test_promotion_paths_structure PASSED
test_promotion_validation.py::TestPromotionPathsConstant::test_promotion_paths_immutable PASSED
```

**Success Criteria**:
- ✅ All 15 validation tests pass
- ✅ No test failures or errors
- ✅ Test coverage for validation.py ≥95%

**Commit**:
```bash
git add src/validation.py tests/test_promotion_validation.py
git commit -m "feat: add promotion path validation with strict forward flow enforcement

- Implemented validate_non_empty() for parameter trimming and validation
- Implemented validate_promotion_path() for strict forward flow (dev→staging→uat→prod)
- Added VALID_PROMOTION_PATHS constant (frozenset for O(1) lookup)
- Added 15 comprehensive unit tests (all passing)
- Enhanced error messages with next valid environment suggestions

Validation layer complete and ready for integration into promote-release tool."
```

---

## Phase 2: MCP Tool Implementation

### T007: Add promote_release Tool Stub [P]
**File**: `module5/stdio-mcp-server/src/server.py`
**Type**: Setup
**Dependencies**: T006 (validation layer must be complete)
**Parallel**: Yes - Can write stub while writing tests

**Objective**: Create promote_release tool stub (will fail integration tests initially)

**Implementation** (add after existing MCP tools):
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
    Promote application release between environments (stub).

    Args:
        app: Application name (required, non-empty)
        version: Version identifier (required, non-empty)
        from_env: Source environment (required: dev|staging|uat|prod)
        to_env: Target environment (required: dev|staging|uat|prod)

    Returns:
        Dictionary with promotion result

    Raises:
        NotImplementedError: Tool not yet implemented
    """
    raise NotImplementedError("promote_release tool not yet implemented")
```

**Success Criteria**:
- ✅ Tool is registered with FastMCP
- ✅ Tool appears in MCP Inspector tool list
- ✅ Calling tool raises NotImplementedError

---

### T008: Add promote_release Integration Tests [P]
**File**: `module5/stdio-mcp-server/tests/test_promote_release.py` (new)
**Type**: Test
**Dependencies**: T007 (tool stub must exist)
**Parallel**: Yes - Different file from implementation

**Objective**: Write failing integration tests for promote_release tool

**Implementation**:
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
        """Successful non-production promotion returns success response."""
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
        """Production deployment sets production_deployment flag."""
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

    @patch("stdio-mcp-server.src.server.execute_cli_command")
    async def test_case_insensitive_normalization(self, mock_exec):
        """Environment names normalized to lowercase."""
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

**Test Execution**: `cd module5/stdio-mcp-server && make test`

**Expected Result**: 7 integration tests FAIL with NotImplementedError

**Success Criteria**:
- ✅ All 7 tests fail with NotImplementedError
- ✅ Tests use mocking correctly (execute_cli_command is mocked)
- ✅ Tests are async (pytest-asyncio)

---

### T009: Implement promote_release Tool
**File**: `module5/stdio-mcp-server/src/server.py`
**Type**: Implementation
**Dependencies**: T008 (integration tests must exist and be failing)
**Parallel**: No - Must verify T008 tests fail first

**Objective**: Implement promote_release tool to make all integration tests pass

**Implementation** (replace stub from T007):
```python
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

**Test Execution**: `cd module5/stdio-mcp-server && make test`

**Expected Result**: All 7 integration tests PASS

**Success Criteria**:
- ✅ All 7 tests from T008 pass
- ✅ Tool has complete type hints and docstring
- ✅ Production deployments log WARNING to stderr
- ✅ 300s timeout is enforced
- ✅ Error messages match test expectations

---

### T010: Verify Full Test Suite Passes
**File**: N/A (verification task)
**Type**: Verification
**Dependencies**: T009 (promote_release implementation complete)
**Parallel**: No - Final verification before documentation

**Objective**: Verify all tests pass (validation + integration)

**Execution**:
```bash
cd module5/stdio-mcp-server
make test
```

**Expected Output**:
```
============================== test session starts ==============================
...
test_promotion_validation.py::TestValidateNonEmpty ............ [ 22%]
test_promotion_validation.py::TestValidatePromotionPath ..... [ 50%]
test_promotion_validation.py::TestPromotionPathsConstant ... [ 60%]
test_promote_release.py::TestPromoteReleaseIntegration ...... [100%]

===================== 22 passed, 1 skipped in X.XXs ========================
```

**Success Criteria**:
- ✅ 15 validation tests pass
- ✅ 7 integration tests pass
- ✅ No test failures or errors
- ✅ Coverage ≥95% for new code (validation.py, promote_release function)

**Commit**:
```bash
git add src/server.py tests/test_promote_release.py
git commit -m "feat: implement promote-release tool with production safeguards

- Implemented promote_release() MCP tool wrapping devops-cli promote command
- 4 required parameters: app, version, from_env, to_env
- Strict forward flow validation (dev→staging→uat→prod)
- 300-second timeout for long-running deployments
- Production deployment logging (WARNING + audit trail)
- Case-insensitive environment normalization
- Comprehensive error handling (validation, CLI failure, timeout)
- Added 7 integration tests (all passing)

Tool complete and ready for manual testing with MCP Inspector."
```

---

## Phase 3: Documentation & Manual Testing

### T011: Update README Documentation [P]
**File**: `module5/stdio-mcp-server/README.md`
**Type**: Documentation
**Dependencies**: T010 (implementation must be complete)
**Parallel**: Yes - Different file from CLAUDE.md

**Objective**: Document promote-release tool in README

**Implementation**: Add to "Available Tools" section:

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

**Success Criteria**:
- ✅ Tool is documented with all parameters
- ✅ Valid promotion paths are clearly stated
- ✅ Example request is provided
- ✅ Production deployment behavior is documented

---

### T012: Update CLAUDE.md [P]
**File**: `module5/CLAUDE.md`
**Type**: Documentation
**Dependencies**: T010 (implementation must be complete)
**Parallel**: Yes - Different file from README

**Objective**: Add Feature 006 to recent changes

**Implementation**: Add to "Recent Changes" section (at the top):

```markdown
## Recent Changes

1. **Feature 006-add-promote-release implemented** (2025-10-05): Promote release tool - wraps devops-cli promote command with strict path validation (dev→staging→uat→prod), 300s timeout, production deployment safeguards, comprehensive error handling
```

**Success Criteria**:
- ✅ Feature 006 added to Recent Changes
- ✅ Entry follows same format as existing entries
- ✅ Key features mentioned (path validation, timeout, production safeguards)

---

### T013: Manual Testing with MCP Inspector
**File**: N/A (manual testing task)
**Type**: Manual Testing
**Dependencies**: T011, T012 (documentation complete)
**Parallel**: No - Requires completed implementation

**Objective**: Verify tool works correctly in MCP Inspector across all scenarios

**Execution**:
```bash
cd module5/stdio-mcp-server
make dev
# MCP Inspector will open in browser
```

**Test Scenarios** (from quickstart.md):

1. **✅ Valid dev→staging promotion**:
   - app: "web-api", version: "1.2.3", from_env: "dev", to_env: "staging"
   - **Expected**: Success response, production_deployment: false

2. **✅ Valid uat→prod promotion** (production):
   - app: "mobile-app", version: "2.0.1", from_env: "uat", to_env: "prod"
   - **Expected**: Success response, production_deployment: true, WARNING in logs

3. **✅ Case-insensitive normalization**:
   - app: "admin-portal", version: "1.0.0", from_env: "STAGING", to_env: "UAT"
   - **Expected**: Normalized to lowercase in response

4. **✅ Empty parameter validation error**:
   - app: "   ", version: "1.0.0", from_env: "dev", to_env: "staging"
   - **Expected**: Error "app cannot be empty"

5. **✅ Invalid environment validation error**:
   - app: "web-api", version: "1.0.0", from_env: "development", to_env: "staging"
   - **Expected**: Error listing valid environments

6. **✅ Invalid promotion path (skipping)**:
   - app: "web-api", version: "1.0.0", from_env: "dev", to_env: "uat"
   - **Expected**: Error "invalid promotion path: dev→uat (valid next environment from dev: staging)"

7. **✅ Invalid promotion path (backward)**:
   - app: "web-api", version: "1.0.0", from_env: "prod", to_env: "staging"
   - **Expected**: Error "invalid promotion path: prod→staging (backward or invalid promotion not allowed)"

**Success Criteria**:
- ✅ All 7 scenarios behave as documented in quickstart.md
- ✅ Production deployments show WARNING in terminal stderr
- ✅ Error messages are clear and actionable
- ✅ Tool appears in MCP Inspector tool list

**Notes**: If real devops-cli is not available, mocked responses are acceptable for this testing phase.

---

### T014: Final Commit & Feature Complete
**File**: N/A (final integration task)
**Type**: Integration
**Dependencies**: T013 (manual testing complete)
**Parallel**: No - Final task

**Objective**: Create final commit marking Feature 006 as complete

**Pre-Commit Checklist**:
- ✅ All 22 tests passing (15 validation + 7 integration)
- ✅ Code coverage ≥95% for new code
- ✅ README.md updated with promote-release documentation
- ✅ CLAUDE.md updated with Feature 006 entry
- ✅ Manual testing complete (all 7 scenarios verified)
- ✅ No syntax errors or linting issues

**Execution**:
```bash
cd module5/stdio-mcp-server
make test  # Verify all tests pass
git add README.md
git add ../CLAUDE.md
git status  # Verify all changes staged
```

**Commit**:
```bash
git commit -m "docs: document Feature 006 promote-release tool and update recent changes

- Added promote-release documentation to README.md
- Updated CLAUDE.md with Feature 006 entry
- Manual testing complete with MCP Inspector (all 7 scenarios verified)

Feature 006 Complete:
- ✅ Validation layer (15 tests passing)
- ✅ Integration tests (7 tests passing)
- ✅ Production deployment safeguards
- ✅ 300s timeout handling
- ✅ Strict forward flow validation (dev→staging→uat→prod)
- ✅ Documentation complete
- ✅ Manual testing verified

Ready for production use."
```

**Success Criteria**:
- ✅ All files committed
- ✅ Commit message follows conventional format
- ✅ Feature 006 is fully documented and tested
- ✅ Ready for merge to main branch

---

## Parallel Execution Examples

Tasks marked [P] can be executed concurrently for faster development:

### Example 1: Phase 1 Initial Setup (T001, T002, T003)
```bash
# Terminal 1: Create validation stubs
# Execute T001

# Terminal 2: Write validate_non_empty tests
# Execute T002 (depends on T001 stub existing)

# Terminal 3: Write validate_promotion_path tests
# Execute T003 (depends on T001 stub existing)
```

### Example 2: Phase 2 Tool Setup (T007, T008)
```bash
# Terminal 1: Create promote_release stub
# Execute T007

# Terminal 2: Write integration tests
# Execute T008 (depends on T007 stub existing)
```

### Example 3: Phase 3 Documentation (T011, T012)
```bash
# Terminal 1: Update README
# Execute T011

# Terminal 2: Update CLAUDE.md
# Execute T012
```

---

## Task Dependency Graph

```
T001 (Validation stubs) [P]
  ├─→ T002 (validate_non_empty tests) [P]
  │    └─→ T004 (Implement validate_non_empty)
  │
  └─→ T003 (validate_promotion_path tests) [P]
       └─→ T005 (Implement validate_promotion_path)

T004 + T005 → T006 (Verify validation layer)

T006 → T007 (promote_release stub) [P]
        ├─→ T008 (Integration tests) [P]
        │    └─→ T009 (Implement promote_release)
        │
        └─→ [T008 written in parallel with T007]

T009 → T010 (Verify full test suite)

T010 → T011 (Update README) [P]
       T012 (Update CLAUDE.md) [P]

T011 + T012 → T013 (Manual testing)

T013 → T014 (Final commit)
```

---

## Summary

**Total Tasks**: 14
**TDD Approach**: Tests first (T002, T003, T008), then implementation (T004, T005, T009)
**Parallel Tasks**: 6 tasks can run concurrently (marked [P])
**Sequential Tasks**: 8 tasks must run in order
**Estimated Time**: 4-6 hours

**Key Milestones**:
- ✅ Validation layer complete: After T006
- ✅ Tool implementation complete: After T010
- ✅ Documentation complete: After T012
- ✅ Feature complete: After T014

**Constitutional Compliance**:
- ✅ TDD approach (tests before implementation)
- ✅ Make commands for all testing (`make test`)
- ✅ Conventional commit format
- ✅ Clear, explicit error handling
- ✅ Type hints on all functions
- ✅ Comprehensive docstrings

**Next Command**: Start with T001 to create validation function stubs
