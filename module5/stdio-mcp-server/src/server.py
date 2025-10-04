"""
MCP STDIO Server Implementation using FastMCP.

Minimal Model Context Protocol server using STDIO transport.
Follows Constitution v1.2.0 requirements with FastMCP framework.

Per Constitution Principle I (Simplicity First): FastMCP eliminates
boilerplate while maintaining full MCP protocol compliance.
"""

import logging
import sys

from fastmcp import FastMCP


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
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # CRITICAL: Must be stderr, not stdout
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


# T029: Import DevOps CLI wrapper tools
# This import registers MCP tools via @mcp.tool() decorator
# Tools registered: get_deployment_status
try:
    from .tools import devops  # noqa: F401
except ImportError:
    # Support both package import and direct execution for mcp dev
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from tools import devops  # noqa: F401


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
