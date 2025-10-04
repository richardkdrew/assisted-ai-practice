"""
Integration tests for DevOps CLI tools using FastMCP in-memory testing.

Uses FastMCP Client with in-memory transport to test list-releases and check-health
tools end-to-end without external processes or network calls.

Pattern: async with Client(mcp) as client: ...
This eliminates process management and provides fast, reliable testing.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastmcp import Client
from src.server import mcp, CLIExecutionResult


# ============================================================================
# Integration Tests - list-releases Tool
# ============================================================================

@pytest.mark.asyncio
async def test_list_releases_integration_success():
    """
    Integration test: list-releases with valid app parameter.

    Tests complete flow:
    1. Client connects via in-memory transport
    2. Calls list-releases tool
    3. Mocked CLI returns release data
    4. Response validated end-to-end
    """
    # Mock CLI execution
    mock_result = CLIExecutionResult(
        stdout='{"status": "success", "releases": [{"id": "rel-1", "applicationId": "web-app", "version": "v2.1.0"}], "total_count": 1, "filters_applied": {"app": "web-app", "limit": null}}',
        stderr="",
        returncode=0
    )

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, return_value=mock_result):
        # Connect to server via in-memory transport
        async with Client(mcp) as client:
            # Call the tool
            result = await client.call_tool("list_releases", arguments={"app": "web-app"})

            # Validate response structure (FastMCP Client returns CallToolResult)
            assert result.is_error is False

            # Access structured data directly
            data = result.data

            assert data["status"] == "success"
            assert len(data["releases"]) == 1
            assert data["releases"][0]["applicationId"] == "web-app"
            assert data["releases"][0]["version"] == "v2.1.0"
            assert data["total_count"] == 1


@pytest.mark.asyncio
async def test_list_releases_integration_with_limit():
    """
    Integration test: list-releases with app and limit parameters.

    Validates:
    - Multiple parameter handling
    - Limit is passed to CLI correctly
    - Response contains limited results
    """
    mock_result = CLIExecutionResult(
        stdout='{"status": "success", "releases": [{"id": "r1"}, {"id": "r2"}, {"id": "r3"}], "total_count": 3, "filters_applied": {"app": "api-service", "limit": 3}}',
        stderr="",
        returncode=0
    )

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, return_value=mock_result):
        async with Client(mcp) as client:
            result = await client.call_tool("list_releases", arguments={"app": "api-service", "limit": 3})

            data = result.data

            assert data["status"] == "success"
            assert len(data["releases"]) == 3
            assert data["total_count"] == 3
            assert data["filters_applied"]["limit"] == 3


@pytest.mark.asyncio
async def test_list_releases_integration_missing_app_error():
    """
    Integration test: list-releases with missing app parameter.

    Validates:
    - Error handling for missing required parameter
    - Clear error message returned
    - No CLI execution attempted
    """
    async with Client(mcp) as client:
        # Should raise error before calling CLI
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("list_releases", arguments={"app": ""})

        # Verify error message
        assert "app parameter is required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_releases_integration_invalid_limit_error():
    """
    Integration test: list-releases with invalid limit (zero).

    Validates:
    - Parameter validation before CLI call
    - Clear error for invalid limit values
    """
    async with Client(mcp) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("list_releases", arguments={"app": "web-app", "limit": 0})

        assert "limit must be a positive integer" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_releases_integration_cli_failure():
    """
    Integration test: list-releases when CLI returns non-zero exit code.

    Validates:
    - CLI failure handling
    - Error propagation with stderr message
    """
    mock_result = CLIExecutionResult(
        stdout="",
        stderr="Error: Application 'unknown-app' not found",
        returncode=1
    )

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, return_value=mock_result):
        async with Client(mcp) as client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool("list_releases", arguments={"app": "unknown-app"})

            assert "DevOps CLI failed" in str(exc_info.value)
            assert "exit code 1" in str(exc_info.value)


# ============================================================================
# Integration Tests - check-health Tool
# ============================================================================

@pytest.mark.asyncio
async def test_check_health_integration_single_env():
    """
    Integration test: check-health for specific environment.

    Tests complete flow:
    1. Client connects via in-memory transport
    2. Calls check-health with env parameter
    3. Mocked CLI returns health data
    4. Response validated end-to-end
    """
    mock_result = CLIExecutionResult(
        stdout='{"status": "success", "health_checks": [{"environment": "prod", "status": "healthy", "metrics": {}}], "timestamp": "2025-10-04T12:00:00Z"}',
        stderr="",
        returncode=0
    )

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, return_value=mock_result):
        async with Client(mcp) as client:
            result = await client.call_tool("check_health", arguments={"env": "prod"})

            data = result.data

            assert data["status"] == "success"
            assert len(data["health_checks"]) == 1
            assert data["health_checks"][0]["environment"] == "prod"
            assert data["health_checks"][0]["status"] == "healthy"


@pytest.mark.asyncio
async def test_check_health_integration_case_insensitive():
    """
    Integration test: check-health with uppercase env (case-insensitive).

    Validates:
    - Case normalization (PROD → prod)
    - CLI receives lowercase env
    - Response is correct
    """
    mock_result = CLIExecutionResult(
        stdout='{"status": "success", "health_checks": [{"environment": "prod", "status": "healthy"}], "timestamp": "2025-10-04T12:00:00Z"}',
        stderr="",
        returncode=0
    )

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, return_value=mock_result) as mock_exec:
        async with Client(mcp) as client:
            result = await client.call_tool("check_health", arguments={"env": "PROD"})

            # Verify CLI was called with lowercase
            mock_exec.assert_called_once()
            call_args = mock_exec.call_args[0][0]
            assert "--env" in call_args
            env_index = call_args.index("--env") + 1
            assert call_args[env_index] == "prod"  # lowercase

            # Verify response
            data = result.data
            assert data["status"] == "success"


@pytest.mark.asyncio
async def test_check_health_integration_all_environments():
    """
    Integration test: check-health without env parameter (all environments).

    Validates:
    - Optional parameter handling
    - CLI returns health for all envs
    - Response contains multiple environments
    """
    mock_result = CLIExecutionResult(
        stdout='{"status": "success", "health_checks": [{"environment": "prod"}, {"environment": "staging"}, {"environment": "uat"}, {"environment": "dev"}], "timestamp": "2025-10-04T12:00:00Z"}',
        stderr="",
        returncode=0
    )

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, return_value=mock_result):
        async with Client(mcp) as client:
            result = await client.call_tool("check_health", arguments={})

            data = result.data

            assert data["status"] == "success"
            assert len(data["health_checks"]) == 4
            envs = [hc["environment"] for hc in data["health_checks"]]
            assert set(envs) == {"prod", "staging", "uat", "dev"}


@pytest.mark.asyncio
async def test_check_health_integration_invalid_env_error():
    """
    Integration test: check-health with invalid environment.

    Validates:
    - Env validation before CLI call
    - Clear error message with valid options
    """
    async with Client(mcp) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("check_health", arguments={"env": "invalid-env"})

        error_msg = str(exc_info.value)
        assert "Invalid environment" in error_msg
        assert "Must be one of" in error_msg
        assert "prod" in error_msg
        assert "staging" in error_msg


@pytest.mark.asyncio
async def test_check_health_integration_cli_timeout():
    """
    Integration test: check-health when CLI times out.

    Validates:
    - Timeout error handling
    - Clear timeout message
    """
    import asyncio

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, side_effect=asyncio.TimeoutError):
        async with Client(mcp) as client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool("check_health", arguments={"env": "prod"})

            assert "timed out" in str(exc_info.value).lower()


# ============================================================================
# Integration Tests - Tool Discovery
# ============================================================================

@pytest.mark.asyncio
async def test_integration_tool_discovery():
    """
    Integration test: Verify both new tools are discoverable.

    Validates:
    - list-releases tool registered
    - check-health tool registered
    - Tool metadata available
    """
    async with Client(mcp) as client:
        # List all available tools
        tools = await client.list_tools()

        tool_names = [tool.name for tool in tools]

        assert "list_releases" in tool_names
        assert "check_health" in tool_names

        # Get specific tool details
        list_releases_tool = next(t for t in tools if t.name == "list_releases")
        assert list_releases_tool.description is not None
        assert "release history" in list_releases_tool.description.lower()

        check_health_tool = next(t for t in tools if t.name == "check_health")
        assert check_health_tool.description is not None
        assert "health" in check_health_tool.description.lower()


@pytest.mark.asyncio
async def test_integration_concurrent_tool_calls():
    """
    Integration test: Multiple concurrent tool calls.

    Validates:
    - Tools handle concurrent requests
    - No shared state conflicts
    - All calls complete successfully
    """
    import asyncio

    mock_releases = CLIExecutionResult(
        stdout='{"status": "success", "releases": [], "total_count": 0}',
        stderr="",
        returncode=0
    )

    mock_health = CLIExecutionResult(
        stdout='{"status": "success", "health_checks": [], "timestamp": "2025-10-04T12:00:00Z"}',
        stderr="",
        returncode=0
    )

    async def mock_execute(args, timeout):
        if "releases" in args:
            return mock_releases
        else:
            return mock_health

    with patch('src.server.execute_cli_command', new_callable=AsyncMock, side_effect=mock_execute):
        async with Client(mcp) as client:
            # Launch multiple concurrent calls
            tasks = [
                client.call_tool("list_releases", arguments={"app": "app1"}),
                client.call_tool("check_health", arguments={"env": "prod"}),
                client.call_tool("list_releases", arguments={"app": "app2"}),
                client.call_tool("check_health", arguments={}),
            ]

            results = await asyncio.gather(*tasks)

            # All calls should succeed
            assert len(results) == 4
            for result in results:
                assert result.is_error is False
                assert result.data is not None
