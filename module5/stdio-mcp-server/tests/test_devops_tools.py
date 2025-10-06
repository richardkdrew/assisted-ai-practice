"""Tests for DevOps CLI Tool MCP Wrappers.

This module contains contract and unit tests for MCP tools that wrap
the DevOps CLI commands.

Test coverage:
- Tool registration and schema validation
- get_deployment_status with various filter combinations
- Error handling (timeout, not found, invalid JSON, CLI failures)
- Edge cases (no results, missing fields)
"""

import asyncio
import json
import unittest.mock
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.server import CLIExecutionResult
import src.server as server_module

pytestmark = pytest.mark.asyncio


# Helper to get the underlying function from FastMCP wrapper
def get_tool_function(tool_obj):
    """Extract the underlying function from FastMCP FunctionTool wrapper."""
    if hasattr(tool_obj, 'fn'):
        return tool_obj.fn
    elif hasattr(tool_obj, '__wrapped__'):
        return tool_obj.__wrapped__
    return tool_obj


# Get the actual callable function
get_deployment_status = get_tool_function(server_module.get_deployment_status)


# T012: Test tool registration (will be skipped for now - requires server setup)
@pytest.mark.skip(reason="Requires full server initialization - validated in integration tests")
async def test_get_status_tool_registered():
    """Test that get_deployment_status tool is registered with MCP server."""
    # This test would require initializing the full MCP server
    # Skipping for unit tests - will be validated via manual testing
    pass


# T013: Test get_deployment_status with no filters
async def test_get_status_no_filters():
    """Test querying all deployments without filters."""
    mock_cli_output = {
        "status": "success",
        "deployments": [
            {
                "id": "deploy-001",
                "applicationId": "web-app",
                "environment": "prod",
                "version": "v2.1.3",
                "status": "deployed",
                "deployedAt": "2024-01-15T10:30:00Z",
                "deployedBy": "alice@company.com",
                "commitHash": "abc123"
            }
        ],
        "total_count": 1,
        "filters_applied": {"application": None, "environment": None},
        "timestamp": "2025-10-04T17:00:00Z"
    }

    mock_result = CLIExecutionResult(
        stdout=json.dumps(mock_cli_output),
        stderr='',
        returncode=0
    )

    with patch('src.server.execute_cli_command', return_value=mock_result):
        result = await get_deployment_status()

        assert result["status"] == "success"
        assert "deployments" in result
        assert "total_count" in result
        assert result["filters_applied"]["application"] is None
        assert result["filters_applied"]["environment"] is None


# T014: Test filter by application
async def test_get_status_filter_by_app():
    """Test filtering deployments by application."""
    mock_cli_output = {
        "status": "success",
        "deployments": [
            {
                "id": "deploy-001",
                "applicationId": "web-app",
                "environment": "prod",
                "version": "v2.1.3",
                "status": "deployed",
                "deployedAt": "2024-01-15T10:30:00Z",
                "deployedBy": "alice@company.com",
                "commitHash": "abc123"
            }
        ],
        "total_count": 1,
        "filters_applied": {"application": "web-app", "environment": None},
        "timestamp": "2025-10-04T17:00:00Z"
    }

    mock_result = CLIExecutionResult(
        stdout=json.dumps(mock_cli_output),
        stderr='',
        returncode=0
    )

    with patch('src.server.execute_cli_command', return_value=mock_result) as mock_exec:
        result = await get_deployment_status(application="web-app")

        # Verify CLI was called with correct arguments
        mock_exec.assert_called_once()
        args = mock_exec.call_args[0][0]
        assert "--app" in args
        assert "web-app" in args

        # Verify result
        assert all(d["applicationId"] == "web-app" for d in result["deployments"])


# T015: Test filter by environment
async def test_get_status_filter_by_env():
    """Test filtering deployments by environment."""
    mock_cli_output = {
        "status": "success",
        "deployments": [
            {
                "id": "deploy-001",
                "applicationId": "web-app",
                "environment": "prod",
                "version": "v2.1.3",
                "status": "deployed",
                "deployedAt": "2024-01-15T10:30:00Z",
                "deployedBy": "alice@company.com",
                "commitHash": "abc123"
            }
        ],
        "total_count": 1,
        "filters_applied": {"application": None, "environment": "prod"},
        "timestamp": "2025-10-04T17:00:00Z"
    }

    mock_result = CLIExecutionResult(
        stdout=json.dumps(mock_cli_output),
        stderr='',
        returncode=0
    )

    with patch('src.server.execute_cli_command', return_value=mock_result) as mock_exec:
        result = await get_deployment_status(environment="prod")

        # Verify CLI was called with correct arguments
        args = mock_exec.call_args[0][0]
        assert "--env" in args
        assert "prod" in args

        # Verify result
        assert all(d["environment"] == "prod" for d in result["deployments"])


# T016: Test filter by both application and environment
async def test_get_status_filter_both():
    """Test filtering by both application and environment."""
    mock_cli_output = {
        "status": "success",
        "deployments": [
            {
                "id": "deploy-001",
                "applicationId": "web-app",
                "environment": "prod",
                "version": "v2.1.3",
                "status": "deployed",
                "deployedAt": "2024-01-15T10:30:00Z",
                "deployedBy": "alice@company.com",
                "commitHash": "abc123"
            }
        ],
        "total_count": 1,
        "filters_applied": {"application": "web-app", "environment": "prod"},
        "timestamp": "2025-10-04T17:00:00Z"
    }

    mock_result = CLIExecutionResult(
        stdout=json.dumps(mock_cli_output),
        stderr='',
        returncode=0
    )

    with patch('src.server.execute_cli_command', return_value=mock_result) as mock_exec:
        result = await get_deployment_status(application="web-app", environment="prod")

        # Verify CLI was called with both filters
        args = mock_exec.call_args[0][0]
        assert "--app" in args and "web-app" in args
        assert "--env" in args and "prod" in args

        # Verify result matches both filters
        assert len(result["deployments"]) == 1
        assert result["deployments"][0]["applicationId"] == "web-app"
        assert result["deployments"][0]["environment"] == "prod"


# T017: Test no results (empty deployments)
async def test_get_status_no_results():
    """Test handling of queries that return no results."""
    mock_cli_output = {
        "status": "success",
        "deployments": [],
        "total_count": 0,
        "filters_applied": {"application": "nonexistent-app", "environment": None},
        "timestamp": "2025-10-04T17:00:00Z"
    }

    mock_result = CLIExecutionResult(
        stdout=json.dumps(mock_cli_output),
        stderr='',
        returncode=0
    )

    with patch('src.server.execute_cli_command', return_value=mock_result):
        result = await get_deployment_status(application="nonexistent-app")

        # Verify no error is raised
        assert result["status"] == "success"
        assert result["deployments"] == []
        assert result["total_count"] == 0


# T018: Test timeout error
async def test_get_status_timeout_error():
    """Test handling of CLI execution timeout."""
    with patch('src.server.execute_cli_command', side_effect=asyncio.TimeoutError()):
        with pytest.raises(RuntimeError, match="DevOps CLI timed out after 30 seconds"):
            await get_deployment_status()


# T019: Test CLI not found error
async def test_get_status_cli_not_found():
    """Test handling of missing CLI tool."""
    with patch('src.server.execute_cli_command', side_effect=FileNotFoundError("CLI not found")):
        with pytest.raises(RuntimeError, match="DevOps CLI tool not found"):
            await get_deployment_status()


# T020: Test invalid JSON error
async def test_get_status_invalid_json():
    """Test handling of malformed JSON from CLI."""
    mock_result = CLIExecutionResult(
        stdout='{incomplete json',
        stderr='',
        returncode=0
    )

    with patch('src.server.execute_cli_command', return_value=mock_result):
        with pytest.raises(ValueError, match="CLI returned invalid JSON"):
            await get_deployment_status()


# T021: Test CLI execution failure
async def test_get_status_cli_failure():
    """Test handling of CLI command failures."""
    mock_result = CLIExecutionResult(
        stdout='',
        stderr='Error: Database connection failed',
        returncode=1
    )

    with patch('src.server.execute_cli_command', return_value=mock_result):
        with pytest.raises(RuntimeError, match="DevOps CLI failed with exit code 1"):
            await get_deployment_status()


# T022: Test missing required fields
async def test_get_status_missing_fields():
    """Test handling of CLI output missing required fields."""
    mock_cli_output = {
        "partial": "data"
        # Missing: status, deployments, total_count, etc.
    }

    mock_result = CLIExecutionResult(
        stdout=json.dumps(mock_cli_output),
        stderr='',
        returncode=0
    )

    with patch('src.server.execute_cli_command', return_value=mock_result):
        with pytest.raises(ValueError, match="CLI output missing required field"):
            await get_deployment_status()
