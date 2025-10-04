"""DevOps CLI Tool MCP Wrappers.

This module implements MCP tools that wrap the DevOps CLI tool commands,
enabling natural language interaction with deployment operations.

Phase 1 includes:
- get_deployment_status: Query deployment status with optional filters
"""

import asyncio
import json
import logging
from typing import Any

from ..cli_wrapper import execute_cli_command
from ..server import mcp

logger = logging.getLogger(__name__)


# T027: get_deployment_status tool implementation
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
        raise RuntimeError(
            "DevOps CLI tool not found at ./acme-devops-cli/devops-cli"
        )
