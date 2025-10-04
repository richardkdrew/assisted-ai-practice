"""
MCP STDIO Server Implementation.

Minimal Model Context Protocol server using STDIO transport.
Follows Constitution v1.1.0 requirements.
"""

import asyncio
import logging
import signal
import sys
from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime
from uuid import uuid4, UUID

from mcp.server import Server
from mcp.server.stdio import stdio_server


# ============================================================================
# State Enums (T010)
# ============================================================================

class ServerState(Enum):
    """Server lifecycle states per data-model.md."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"


class SessionState(Enum):
    """Protocol session states per data-model.md."""
    NOT_STARTED = "not_started"
    HANDSHAKE = "handshake"
    ACTIVE = "active"
    CLOSED = "closed"


# ============================================================================
# Logging Configuration (T011)
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
    logger = logging.getLogger("stdio-mcp-server")
    return logger


# Global logger instance
logger = configure_logging()


# ============================================================================
# Global State
# ============================================================================

# Shutdown event for graceful termination (T014)
shutdown_event = asyncio.Event()

# Server state tracking
server_state = ServerState.UNINITIALIZED
session_state = SessionState.NOT_STARTED
session_id: Optional[UUID] = None
client_info: Optional[Dict[str, str]] = None


# ============================================================================
# Signal Handlers (T014)
# ============================================================================

def handle_shutdown(signum: int, frame: Any) -> None:
    """
    Handle SIGINT and SIGTERM for graceful shutdown.

    Per research.md: Register signal handlers for graceful shutdown.
    Per Constitution Principle VI: Clean shutdown required.

    Args:
        signum: Signal number received
        frame: Current stack frame (unused)
    """
    global server_state

    logger.info(f"Received signal {signum}, initiating shutdown")
    server_state = ServerState.SHUTTING_DOWN
    shutdown_event.set()


# Register signal handlers
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


# ============================================================================
# Server Implementation (T012, T013)
# ============================================================================

# Create MCP Server instance
mcp_server = Server("stdio-mcp-server")


@mcp_server.list_tools()
async def list_tools() -> list:
    """
    List available tools.

    Per plan.md: v1 has no tools implemented.
    Returns empty list for now.
    """
    return []


@mcp_server.list_resources()
async def list_resources() -> list:
    """
    List available resources.

    Per plan.md: v1 has no resources implemented.
    Returns empty list for now.
    """
    return []


@mcp_server.list_prompts()
async def list_prompts() -> list:
    """
    List available prompts.

    Per plan.md: v1 has no prompts implemented.
    Returns empty list for now.
    """
    return []


# ============================================================================
# Main Entry Point (T015, T016)
# ============================================================================

async def main() -> None:
    """
    Main server event loop.

    Per research.md: Use MCP SDK's stdio_server context manager.
    Per Constitution Principle VI: STDIO communication only.

    Implements:
    - STDIO server setup
    - Server lifecycle management
    - Graceful shutdown handling
    """
    global server_state, session_state

    try:
        logger.info("Starting MCP server")
        server_state = ServerState.INITIALIZING

        # Set up STDIO transport per research.md
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server ready to accept connections")
            server_state = ServerState.READY

            # Run server with STDIO streams
            # The MCP SDK handles:
            # - JSON-RPC 2.0 framing
            # - Initialize handshake
            # - Method routing
            # - Error responses
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options()
            )

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        server_state = ServerState.SHUTTING_DOWN
        raise
    finally:
        # Cleanup (T014)
        logger.info("Closing streams")
        server_state = ServerState.STOPPED
        logger.info("Server stopped")


# ============================================================================
# Module Entry Point (T016)
# ============================================================================

if __name__ == "__main__":
    """
    Entry point for `python -m src.server` execution.

    Per research.md: Use asyncio.run(main()) pattern.
    """
    try:
        asyncio.run(main())
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
