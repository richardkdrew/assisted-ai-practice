"""CLI Wrapper Module for DevOps CLI Tool.

This module provides a reusable async subprocess wrapper for executing
the DevOps CLI tool (./acme-devops-cli/devops-cli) from MCP server tools.

Features:
- Async subprocess execution using asyncio
- Timeout management with configurable limits
- Separate stdout/stderr capture for MCP protocol compliance
- Explicit error handling for all failure modes
"""

import asyncio
import logging
from pathlib import Path
from typing import NamedTuple

logger = logging.getLogger(__name__)


# T024: CLIExecutionResult NamedTuple
class CLIExecutionResult(NamedTuple):
    """Result of executing a CLI command via subprocess.

    Attributes:
        stdout: Standard output from the CLI command (decoded as UTF-8).
        stderr: Standard error output from the CLI command (decoded as UTF-8).
        returncode: Process exit code (0 = success, non-zero = error).
    """

    stdout: str
    stderr: str
    returncode: int


# T025: execute_cli_command function
async def execute_cli_command(
    args: list[str],
    timeout: float = 30.0,
    cwd: str | None = None,
) -> CLIExecutionResult:
    """Execute DevOps CLI command asynchronously with timeout management.

    Args:
        args: CLI command arguments (e.g., ["status", "--format", "json"]).
              The CLI tool path (./acme-devops-cli/devops-cli) is prepended automatically.
        timeout: Maximum execution time in seconds (default: 30.0).
        cwd: Working directory for command execution (default: current directory).

    Returns:
        CLIExecutionResult containing stdout, stderr, and return code.

    Raises:
        asyncio.TimeoutError: If command execution exceeds timeout.
        FileNotFoundError: If CLI tool is not found at expected path.
        OSError: If subprocess creation fails for other reasons.

    Example:
        >>> result = await execute_cli_command(["status", "--format", "json"])
        >>> print(result.stdout)  # JSON output from CLI
    """
    cli_path = "./acme-devops-cli/devops-cli"
    full_args = [cli_path] + args

    logger.info(f"Executing DevOps CLI: {' '.join(args)}")
    start_time = asyncio.get_event_loop().time()

    try:
        # Create subprocess with explicit args (no shell injection risk)
        process = await asyncio.create_subprocess_exec(
            *full_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        # Wait for process with timeout
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            process.communicate(), timeout=timeout
        )

        # Decode output
        stdout = stdout_bytes.decode("utf-8")
        stderr = stderr_bytes.decode("utf-8")
        returncode = process.returncode

        duration = asyncio.get_event_loop().time() - start_time
        logger.debug(f"CLI command completed in {duration:.2f}s")

        if stderr:
            logger.warning(f"CLI stderr: {stderr}")

        return CLIExecutionResult(
            stdout=stdout, stderr=stderr, returncode=returncode
        )

    except asyncio.TimeoutError:
        logger.error(f"CLI command timed out after {timeout}s")
        raise

    except FileNotFoundError as e:
        logger.error(f"CLI tool not found at {cli_path}: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error executing CLI: {e}")
        raise
