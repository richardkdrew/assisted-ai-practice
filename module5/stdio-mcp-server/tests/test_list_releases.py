"""
Tests for list-releases tool functionality.

Tests contract compliance, parameter validation, error handling, and CLI integration.
Following TDD approach: these tests should fail until list_releases tool is implemented.

Contract: specs/004-now-that-i/contracts/list-releases.schema.json
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
async def test_list_releases_valid_app(mcp_server):
    """
    T001.1: Test list_releases with valid app parameter.

    Input: {"app": "web-app"}
    Expected: Returns releases for web-app
    Contract: list-releases.schema.json - required app parameter
    """
    from src.server import list_releases

    # Mock the CLI execution
    mock_result = CLIExecutionResult(
        stdout='{"status": "success", "releases": [{"app": "web-app"}], "total_count": 1}',
        stderr="",
        returncode=0
    )

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, return_value=mock_result):
        list_releases_fn = list_releases.fn if hasattr(list_releases, 'fn') else list_releases
        result = await list_releases_fn(app="web-app")

        assert result["status"] == "success"
        assert "releases" in result
        assert result["total_count"] == 1


@pytest.mark.asyncio
async def test_list_releases_with_limit(mcp_server):
    """
    T001.2: Test list_releases with valid app and limit parameters.

    Input: {"app": "web-app", "limit": 5}
    Expected: Returns up to 5 releases
    Contract: list-releases.schema.json - optional limit parameter
    """
    from src.server import list_releases

    mock_result = CLIExecutionResult(
        stdout='{"status": "success", "releases": [1,2,3,4,5], "total_count": 5}',
        stderr="",
        returncode=0
    )

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, return_value=mock_result):
        list_releases_fn = list_releases.fn if hasattr(list_releases, 'fn') else list_releases
        result = await list_releases_fn(app="web-app", limit=5)

        assert result["status"] == "success"
        assert len(result["releases"]) == 5


# ============================================================================
# Validation Tests - Error Cases
# ============================================================================

@pytest.mark.asyncio
async def test_list_releases_missing_app(mcp_server):
    """
    T001.3: Test validation when app parameter is missing/empty.

    Input: {"app": ""}
    Expected: ValueError("app parameter is required")
    Contract: list-releases.schema.json errorCases - missing required parameter
    """
    from src.server import list_releases

    list_releases_fn = list_releases.fn if hasattr(list_releases, 'fn') else list_releases

    with pytest.raises(ValueError, match="app parameter is required"):
        await list_releases_fn(app="")


@pytest.mark.asyncio
async def test_list_releases_limit_zero(mcp_server):
    """
    T001.4: Test validation when limit is 0.

    Input: {"app": "web-app", "limit": 0}
    Expected: ValueError("limit must be a positive integer")
    Contract: list-releases.schema.json - limit minimum: 1
    """
    from src.server import list_releases

    list_releases_fn = list_releases.fn if hasattr(list_releases, 'fn') else list_releases

    with pytest.raises(ValueError, match="limit must be a positive integer"):
        await list_releases_fn(app="web-app", limit=0)


@pytest.mark.asyncio
async def test_list_releases_limit_negative(mcp_server):
    """
    T001.5: Test validation when limit is negative.

    Input: {"app": "web-app", "limit": -1}
    Expected: ValueError("limit must be a positive integer")
    Contract: list-releases.schema.json - limit minimum: 1
    """
    from src.server import list_releases

    list_releases_fn = list_releases.fn if hasattr(list_releases, 'fn') else list_releases

    with pytest.raises(ValueError, match="limit must be a positive integer"):
        await list_releases_fn(app="web-app", limit=-1)


# ============================================================================
# CLI Integration Tests - Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_list_releases_cli_timeout(mcp_server):
    """
    T001.6: Test handling of CLI timeout.

    Input: {"app": "web-app"} but CLI times out
    Expected: RuntimeError with timeout message
    Contract: list-releases.schema.json errorCases - TimeoutError
    """
    from src.server import list_releases
    import asyncio

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, side_effect=asyncio.TimeoutError):
        list_releases_fn = list_releases.fn if hasattr(list_releases, 'fn') else list_releases

        with pytest.raises(RuntimeError, match="timed out"):
            await list_releases_fn(app="web-app")


@pytest.mark.asyncio
async def test_list_releases_malformed_json(mcp_server):
    """
    T001.7: Test handling of malformed JSON from CLI.

    Input: {"app": "web-app"} but CLI returns invalid JSON
    Expected: ValueError("CLI returned invalid JSON")
    Contract: list-releases.schema.json errorCases - JSONDecodeError
    """
    from src.server import list_releases

    mock_result = CLIExecutionResult(
        stdout='{"invalid json syntax',
        stderr="",
        returncode=0
    )

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, return_value=mock_result):
        list_releases_fn = list_releases.fn if hasattr(list_releases, 'fn') else list_releases

        with pytest.raises(ValueError, match="CLI returned invalid JSON"):
            await list_releases_fn(app="web-app")
