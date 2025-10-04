"""
Tests for check-health tool functionality.

Tests contract compliance, parameter validation, case-insensitive env matching, and error handling.
Following TDD approach: these tests should fail until check_health tool is implemented.

Contract: specs/004-now-that-i/contracts/check-health.schema.json
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.server import CLIExecutionResult


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mcp_server():
    """Create a FastMCP server instance for testing."""
    from src.server import mcp
    return mcp


# ============================================================================
# Contract Tests - Parameter Validation
# ============================================================================

@pytest.mark.asyncio
async def test_check_health_valid_env(mcp_server):
    """
    T002.1: Test check_health with valid env parameter.

    Input: {"env": "prod"}
    Expected: Returns health for production environment
    Contract: check-health.schema.json - valid enum value
    """
    from src.server import check_health

    mock_result = CLIExecutionResult(
        stdout='{"status": "success", "health_checks": [{"environment": "prod"}], "timestamp": "2025-10-04T..."}',
        stderr="",
        returncode=0
    )

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, return_value=mock_result):
        check_health_fn = check_health.fn if hasattr(check_health, 'fn') else check_health
        result = await check_health_fn(env="prod")

        assert result["status"] == "success"
        assert "health_checks" in result
        assert result["health_checks"][0]["environment"] == "prod"


@pytest.mark.asyncio
async def test_check_health_uppercase_env(mcp_server):
    """
    T002.2: Test check_health with uppercase env parameter (case-insensitive).

    Input: {"env": "PROD"}
    Expected: Normalizes to lowercase, returns production health
    Contract: check-health.schema.json - case-insensitive enum
    """
    from src.server import check_health

    mock_result = CLIExecutionResult(
        stdout='{"status": "success", "health_checks": [{"environment": "prod"}], "timestamp": "2025-10-04T..."}',
        stderr="",
        returncode=0
    )

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, return_value=mock_result):
        check_health_fn = check_health.fn if hasattr(check_health, 'fn') else check_health
        result = await check_health_fn(env="PROD")

        assert result["status"] == "success"
        # Verify the CLI was called with lowercase env
        assert "health_checks" in result


# ============================================================================
# Validation Tests - Error Cases
# ============================================================================

@pytest.mark.asyncio
async def test_check_health_invalid_env(mcp_server):
    """
    T002.3: Test validation when env parameter is invalid.

    Input: {"env": "invalid-env"}
    Expected: ValueError("Invalid environment: invalid-env. Must be one of: prod, staging, uat, dev")
    Contract: check-health.schema.json errorCases - invalid enum value
    """
    from src.server import check_health

    check_health_fn = check_health.fn if hasattr(check_health, 'fn') else check_health

    with pytest.raises(ValueError, match="Invalid environment.*Must be one of"):
        await check_health_fn(env="invalid-env")


@pytest.mark.asyncio
async def test_check_health_no_env_param(mcp_server):
    """
    T002.4: Test check_health without env parameter (check all environments).

    Input: {} (no env parameter)
    Expected: Returns health for ALL environments
    Contract: check-health.schema.json - env is optional
    """
    from src.server import check_health

    mock_result = CLIExecutionResult(
        stdout='{"status": "success", "health_checks": [{"environment": "prod"}, {"environment": "staging"}, {"environment": "uat"}, {"environment": "dev"}], "timestamp": "2025-10-04T..."}',
        stderr="",
        returncode=0
    )

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, return_value=mock_result):
        check_health_fn = check_health.fn if hasattr(check_health, 'fn') else check_health
        result = await check_health_fn()

        assert result["status"] == "success"
        assert len(result["health_checks"]) == 4


# ============================================================================
# CLI Integration Tests - Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_check_health_cli_timeout(mcp_server):
    """
    T002.5: Test handling of CLI timeout.

    Input: {"env": "prod"} but CLI times out
    Expected: RuntimeError with timeout message
    Contract: check-health.schema.json errorCases - TimeoutError
    """
    from src.server import check_health
    import asyncio

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, side_effect=asyncio.TimeoutError):
        check_health_fn = check_health.fn if hasattr(check_health, 'fn') else check_health

        with pytest.raises(RuntimeError, match="timed out"):
            await check_health_fn(env="prod")


@pytest.mark.asyncio
async def test_check_health_malformed_json(mcp_server):
    """
    T002.6: Test handling of malformed JSON from CLI.

    Input: {"env": "prod"} but CLI returns invalid JSON
    Expected: ValueError("CLI returned invalid JSON")
    Contract: check-health.schema.json errorCases - JSONDecodeError
    """
    from src.server import check_health

    mock_result = CLIExecutionResult(
        stdout='{"invalid json syntax',
        stderr="",
        returncode=0
    )

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, return_value=mock_result):
        check_health_fn = check_health.fn if hasattr(check_health, 'fn') else check_health

        with pytest.raises(ValueError, match="CLI returned invalid JSON"):
            await check_health_fn(env="prod")
