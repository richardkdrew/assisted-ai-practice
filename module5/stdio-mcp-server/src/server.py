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

# Per plan.md: v1 has no tools, resources, or prompts implemented.
# FastMCP will automatically return empty lists for these capabilities.
# Future features can be added using decorators:
#
# @mcp.tool()
# def example_tool(arg: str) -> str:
#     """Tool description"""
#     return f"Result: {arg}"
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
