"""
MCP STDIO Server Implementation using FastMCP.

Minimal Model Context Protocol server using STDIO transport.
Follows Constitution v1.2.0 requirements with FastMCP framework.

Per Constitution Principle I (Simplicity First): FastMCP eliminates
boilerplate while maintaining full MCP protocol compliance.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any
from typing import NamedTuple

from fastmcp import FastMCP
from src.validation import (
    validate_environment,
    validate_non_empty,
    validate_promotion_path,
)


# ============================================================================
# Logging Configuration
# ============================================================================


def configure_logging() -> logging.Logger:
    """
    Configure structured logging to stderr.

    Per Constitution Principle III and VI:
    - All logs go to stderr (stdout reserved for MCP protocol)
    - Structured format with timestamps
    - Log levels: DEBUG, INFO, ERROR

    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,  # CRITICAL: Must be stderr, not stdout
    )
    return logging.getLogger("stdio-mcp-server")


# Configure logging
logger = configure_logging()


# ============================================================================
# FastMCP Server Instance
# ============================================================================

# Create FastMCP server instance
# FastMCP handles:
# - STDIO transport setup
# - JSON-RPC 2.0 framing
# - Initialize handshake
# - Signal handlers (SIGINT/SIGTERM)
# - Method routing
# - Error responses
mcp = FastMCP("stdio-mcp-server")


# ============================================================================
# Server Capabilities (Tools, Resources, Prompts)
# ============================================================================


@mcp.tool()
async def ping(message: str) -> str:
    """
    Test connectivity by echoing back a message.

    This tool accepts a message string and returns it prefixed with "Pong: ".
    Useful for verifying that the MCP server is running and responsive.

    Args:
        message: The message to echo back

    Returns:
        A pong response with the echoed message in format "Pong: {message}"
    """
    logger.debug(f"Ping received: {message}")
    return f"Pong: {message}"


# ============================================================================
# CLI Wrapper for DevOps CLI Tool
# ============================================================================


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
    cli_path = "../acme-devops-cli/devops-cli"
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

        return CLIExecutionResult(stdout=stdout, stderr=stderr, returncode=returncode)

    except asyncio.TimeoutError:
        logger.error(f"CLI command timed out after {timeout}s")
        raise

    except FileNotFoundError as e:
        logger.error(f"CLI tool not found at {cli_path}: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error executing CLI: {e}")
        raise


# ============================================================================
# DevOps CLI MCP Tools
# ============================================================================


@mcp.tool()
async def get_deployment_status(
    application: str | None = None,
    environment: str | None = None,
) -> dict[str, Any]:
    """Get deployment status information from DevOps CLI.

    Query deployment status for applications across environments with optional
    filtering by application ID and/or environment name.

    Args:
        application: Optional application filter (e.g., "web-app", "api-service").
                     If not provided, returns deployments for all applications.
        environment: Optional environment filter (e.g., "prod", "staging", "uat").
                     If not provided, returns deployments across all environments.

    Returns:
        Dictionary containing deployment information with structure:
        {
            "status": "success" | "error",
            "deployments": [
                {
                    "id": str,
                    "applicationId": str,
                    "environment": str,
                    "version": str,
                    "status": str,
                    "deployedAt": str (ISO 8601),
                    "deployedBy": str (email),
                    "commitHash": str
                },
                ...
            ],
            "total_count": int,
            "filters_applied": {
                "application": str | None,
                "environment": str | None
            },
            "timestamp": str (ISO 8601)
        }

    Raises:
        RuntimeError: If CLI execution times out or CLI tool is not found.
        ValueError: If CLI returns invalid JSON or missing required fields.

    Example:
        >>> # Get all deployments
        >>> result = await get_deployment_status()
        >>> print(result["total_count"])
        6

        >>> # Filter by application
        >>> result = await get_deployment_status(application="web-app")
        >>> print([d["applicationId"] for d in result["deployments"]])
        ["web-app", "web-app"]

        >>> # Filter by both
        >>> result = await get_deployment_status(
        ...     application="web-app",
        ...     environment="prod"
        ... )
        >>> print(result["deployments"][0]["version"])
        "v2.1.3"
    """
    # Validate environment parameter using centralized validation layer
    if environment is not None:
        environment = validate_environment(environment)

    # Build CLI arguments
    args = ["status", "--format", "json"]

    if application:
        args.extend(["--app", application])

    if environment:
        args.extend(["--env", environment])

    try:
        # Execute CLI command with timeout
        result = await execute_cli_command(args, timeout=30.0)

        # Check for CLI execution failure
        if result.returncode != 0:
            raise RuntimeError(
                f"DevOps CLI failed with exit code {result.returncode}: {result.stderr}"
            )

        # Parse JSON output
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse CLI output as JSON: {e}")
            logger.debug(f"Raw CLI output: {result.stdout}")
            raise ValueError(f"CLI returned invalid JSON: {e}")

        # Validate required fields
        required_fields = [
            "status",
            "deployments",
            "total_count",
            "filters_applied",
            "timestamp",
        ]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"CLI output missing required field: {field}")

        # Log CLI stderr if present (warnings, etc.)
        if result.stderr:
            logger.warning(f"CLI stderr: {result.stderr}")

        return data

    except asyncio.TimeoutError:
        logger.error("CLI execution timed out")
        raise RuntimeError("DevOps CLI timed out after 30 seconds")

    except FileNotFoundError:
        logger.error("CLI tool not found")
        raise RuntimeError("DevOps CLI tool not found at ../acme-devops-cli/devops-cli")


@mcp.tool()
async def list_releases(
    app: str,
    limit: int | None = None,
) -> dict[str, Any]:
    """List release history for an application via DevOps CLI.

    Query release history with optional limit on number of results.
    Useful for tracking deployments and release timeline.

    Args:
        app: Application name to query (required, non-empty).
        limit: Maximum number of releases to return (optional, must be ≥1 if provided).

    Returns:
        Dictionary containing release information with structure:
        {
            "status": "success" | "error",
            "releases": [
                {
                    "id": str,
                    "applicationId": str,
                    "version": str,
                    "deployedAt": str (ISO 8601),
                    "deployedBy": str (email),
                    "commitHash": str
                },
                ...
            ],
            "total_count": int,
            "filters_applied": {
                "app": str,
                "limit": int | None
            }
        }

    Raises:
        ValueError: If app is empty or limit is invalid.
        RuntimeError: If CLI execution times out or CLI tool is not found.

    Example:
        >>> # Get last 5 releases for web-app
        >>> result = await list_releases(app="web-app", limit=5)
        >>> print(result["total_count"])
        5
    """
    # Validate app parameter (required)
    if not app:
        raise ValueError("app parameter is required")

    # Validate limit parameter (optional, must be positive)
    if limit is not None and limit < 1:
        raise ValueError("limit must be a positive integer")

    # Build CLI arguments
    args = ["releases", "--app", app, "--format", "json"]

    if limit is not None:
        args.extend(["--limit", str(limit)])

    try:
        # Execute CLI command with timeout
        result = await execute_cli_command(args, timeout=30.0)

        # Check for CLI execution failure
        if result.returncode != 0:
            raise RuntimeError(
                f"DevOps CLI failed with exit code {result.returncode}: {result.stderr}"
            )

        # Parse JSON output
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse CLI output as JSON: {e}")
            logger.debug(f"Raw CLI output: {result.stdout}")
            raise ValueError(f"CLI returned invalid JSON: {e}")

        # Log CLI stderr if present (warnings, etc.)
        if result.stderr:
            logger.warning(f"CLI stderr: {result.stderr}")

        return data

    except asyncio.TimeoutError:
        logger.error("CLI execution timed out")
        raise RuntimeError("DevOps CLI timed out after 30 seconds")

    except FileNotFoundError:
        logger.error("CLI tool not found")
        raise RuntimeError("DevOps CLI tool not found at ../acme-devops-cli/devops-cli")


@mcp.tool()
async def check_health(
    env: str | None = None,
) -> dict[str, Any]:
    """Check environment health status via DevOps CLI.

    Query health status for specific environment or all environments.
    Useful for monitoring system health and operational status.

    Args:
        env: Environment to check (optional, case-insensitive).
             Valid values: "prod", "staging", "uat", "dev".
             If not provided, checks ALL environments.

    Returns:
        Dictionary containing health check information with structure:
        {
            "status": "success" | "error",
            "health_checks": [
                {
                    "environment": str,
                    "status": str (healthy/degraded/unhealthy),
                    "metrics": dict,
                    "timestamp": str (ISO 8601)
                },
                ...
            ],
            "timestamp": str (ISO 8601)
        }

    Raises:
        ValueError: If env is invalid (not in allowed list).
        RuntimeError: If CLI execution times out or CLI tool is not found.

    Example:
        >>> # Check production environment
        >>> result = await check_health(env="prod")
        >>> print(result["health_checks"][0]["status"])
        "healthy"

        >>> # Check all environments
        >>> result = await check_health()
        >>> print(len(result["health_checks"]))
        4
    """
    # Validate env parameter using centralized validation layer
    env_lower = validate_environment(env)

    # Build CLI arguments
    args = ["health", "--format", "json"]

    if env_lower is not None:
        args.extend(["--env", env_lower])

    try:
        # Execute CLI command with timeout
        result = await execute_cli_command(args, timeout=30.0)

        # Check for CLI execution failure
        if result.returncode != 0:
            raise RuntimeError(
                f"DevOps CLI failed with exit code {result.returncode}: {result.stderr}"
            )

        # Parse JSON output
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse CLI output as JSON: {e}")
            logger.debug(f"Raw CLI output: {result.stdout}")
            raise ValueError(f"CLI returned invalid JSON: {e}")

        # Log CLI stderr if present (warnings, etc.)
        if result.stderr:
            logger.warning(f"CLI stderr: {result.stderr}")

        return data

    except asyncio.TimeoutError:
        logger.error("CLI execution timed out")
        raise RuntimeError("DevOps CLI timed out after 30 seconds")

    except FileNotFoundError:
        logger.error("CLI tool not found")
        raise RuntimeError("DevOps CLI tool not found at ../acme-devops-cli/devops-cli")


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


# Future features can be added using decorators:
#
# @mcp.resource("resource://example")
# def example_resource() -> str:
#     """Resource description"""
#     return "Resource content"
#
# @mcp.prompt()
# def example_prompt() -> str:
#     """Prompt description"""
#     return "Prompt content"


# ============================================================================
# Module Entry Point
# ============================================================================

if __name__ == "__main__":
    """
    Entry point for FastMCP server execution.

    FastMCP handles:
    - asyncio.run() execution
    - Signal handling (SIGINT/SIGTERM)
    - Graceful shutdown
    - Exit codes
    - STDIO transport setup

    Per Constitution Principle I: Minimal boilerplate, maximum clarity.
    """
    logger.info("Starting stdio-mcp-server with FastMCP")
    mcp.run(transport="stdio")
