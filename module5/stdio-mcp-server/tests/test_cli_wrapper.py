"""Tests for CLI Wrapper Module.

This module contains unit tests for the async subprocess wrapper
that executes the DevOps CLI tool.

Test coverage:
- CLIExecutionResult structure validation
- Successful CLI execution
- Timeout handling
- CLI tool not found errors
- Non-zero exit codes
- stdout/stderr capture separation
"""

import asyncio
import sys
import unittest.mock
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.server import CLIExecutionResult, execute_cli_command

pytestmark = pytest.mark.asyncio


# T006: Test CLIExecutionResult structure
async def test_cli_execution_result_structure():
    """Test that CLIExecutionResult NamedTuple has correct fields."""
    result = CLIExecutionResult(
        stdout="test output",
        stderr="test error",
        returncode=0
    )

    # Verify fields exist and have correct types
    assert isinstance(result.stdout, str)
    assert isinstance(result.stderr, str)
    assert isinstance(result.returncode, int)

    # Verify values
    assert result.stdout == "test output"
    assert result.stderr == "test error"
    assert result.returncode == 0

    # Verify immutability (NamedTuple behavior)
    with pytest.raises(AttributeError):
        result.stdout = "new value"


# T007: Test successful CLI execution
async def test_execute_cli_success():
    """Test successful execution of CLI command."""
    # Mock process with successful execution
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(
        return_value=(b'{"status": "success"}', b'')
    )
    mock_process.returncode = 0

    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await execute_cli_command(["status", "--format", "json"])

        assert isinstance(result, CLIExecutionResult)
        assert result.stdout == '{"status": "success"}'
        assert result.stderr == ''
        assert result.returncode == 0


# T008: Test CLI execution timeout
async def test_execute_cli_timeout():
    """Test that timeout is properly enforced."""
    # Mock process that takes too long
    async def slow_communicate():
        await asyncio.sleep(10)  # Longer than timeout
        return (b'output', b'')

    mock_process = AsyncMock()
    mock_process.communicate = slow_communicate

    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        with pytest.raises(asyncio.TimeoutError):
            await execute_cli_command(["status"], timeout=0.1)


# T009: Test CLI tool not found
async def test_execute_cli_not_found():
    """Test error handling when CLI tool doesn't exist."""
    with patch('asyncio.create_subprocess_exec', side_effect=FileNotFoundError("CLI not found")):
        with pytest.raises(FileNotFoundError):
            await execute_cli_command(["status"])


# T010: Test non-zero exit code
async def test_execute_cli_nonzero_exit():
    """Test handling of CLI command failures."""
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(
        return_value=(b'', b'Error: invalid command')
    )
    mock_process.returncode = 1

    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await execute_cli_command(["invalid"])

        assert isinstance(result, CLIExecutionResult)
        assert result.stdout == ''
        assert result.stderr == 'Error: invalid command'
        assert result.returncode == 1


# T011: Test stdout/stderr separation
async def test_execute_cli_stderr_capture():
    """Test that stdout and stderr are captured separately."""
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(
        return_value=(b'stdout data', b'stderr data')
    )
    mock_process.returncode = 0

    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await execute_cli_command(["status"])

        assert result.stdout == 'stdout data'
        assert result.stderr == 'stderr data'
        assert result.stdout != result.stderr  # Verify they're separate
