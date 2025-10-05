"""
HTTP MCP Server Implementation using FastMCP.

HTTP-based Model Context Protocol server for consuming acme-devops-api.
Follows Constitution v1.2.0 requirements with FastMCP framework.

Per Constitution Principle I (Simplicity First): Single file architecture
with FastMCP framework for HTTP transport and httpx for API integration.
"""

import asyncio
import logging
import os
import sys
from typing import Any, Optional
from contextlib import asynccontextmanager

from fastmcp import FastMCP
import httpx


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
    return logging.getLogger("http-mcp-server")


# Configure logging
logger = configure_logging()


# ============================================================================
# FastMCP Server Instance
# ============================================================================

# Create FastMCP server instance
# FastMCP handles:
# - HTTP transport setup
# - JSON-RPC 2.0 framing
# - Initialize handshake
# - Signal handlers (SIGINT/SIGTERM)
# - Method routing
# - Error responses
mcp = FastMCP("http-mcp-server")


# ============================================================================
# HTTP Client Configuration
# ============================================================================

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "30.0"))

# Global HTTP client instance
_http_client: Optional[httpx.AsyncClient] = None


async def get_http_client() -> httpx.AsyncClient:
    """
    Get or create HTTP client for acme-devops-api communication.

    Per Constitution Principle II: Explicit error handling for all external interactions.

    Returns:
        Configured httpx.AsyncClient instance

    Raises:
        httpx.HTTPError: If connection to API fails
        RuntimeError: If client creation fails
    """
    global _http_client

    if _http_client is None:
        try:
            _http_client = httpx.AsyncClient(
                base_url=API_BASE_URL,
                timeout=httpx.Timeout(HTTP_TIMEOUT),
                follow_redirects=True,
            )

            # Test connection with health check
            logger.info(f"Testing connection to acme-devops-api at {API_BASE_URL}")
            response = await _http_client.get("/health")
            response.raise_for_status()

            logger.info("Successfully connected to acme-devops-api")

        except httpx.HTTPError as e:
            logger.error(f"Failed to connect to acme-devops-api: {e}")
            if _http_client:
                await _http_client.aclose()
                _http_client = None
            raise RuntimeError(
                f"Cannot connect to acme-devops-api at {API_BASE_URL}: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error creating HTTP client: {e}")
            if _http_client:
                await _http_client.aclose()
                _http_client = None
            raise RuntimeError(f"Failed to create HTTP client: {e}")

    return _http_client


async def close_http_client() -> None:
    """
    Close HTTP client connection.

    Per Constitution Principle VI: Graceful shutdown handling.
    """
    global _http_client

    if _http_client:
        try:
            await _http_client.aclose()
            logger.info("HTTP client closed successfully")
        except Exception as e:
            logger.error(f"Error closing HTTP client: {e}")
        finally:
            _http_client = None


# ============================================================================
# Server Lifecycle Management
# ============================================================================


@asynccontextmanager
async def lifespan_manager():
    """
    Manage server lifecycle with proper startup and shutdown.

    Per Constitution Principle VI: Graceful shutdown handling.
    """
    try:
        # Startup: Initialize HTTP client
        logger.info("Starting HTTP MCP server")
        await get_http_client()
        logger.info("Server startup completed successfully")

        yield

    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise
    finally:
        # Shutdown: Clean up resources
        logger.info("Shutting down HTTP MCP server")
        await close_http_client()
        logger.info("Server shutdown completed")


# ============================================================================
# Health Check Tool (Basic Implementation)
# ============================================================================


@mcp.tool()
async def ping(message: str) -> str:
    """
    Test connectivity by echoing back a message.

    This tool accepts a message string and returns it prefixed with "Pong: ".
    Useful for verifying that the HTTP MCP server is running and responsive.

    Args:
        message: The message to echo back

    Returns:
        A pong response with the echoed message in format "Pong: {message}"
    """
    logger.debug(f"Ping received: {message}")
    return f"Pong: {message}"


@mcp.tool()
async def check_api_health() -> dict[str, Any]:
    """
    Check health status of acme-devops-api.

    Per Constitution Principle II: Explicit error handling for external interactions.

    Returns:
        Dictionary containing health check results

    Raises:
        RuntimeError: If API health check fails
    """
    try:
        client = await get_http_client()

        # Check basic health endpoint
        response = await client.get("/health")
        response.raise_for_status()

        # Check API v1 health endpoint if available
        api_health = None
        try:
            api_response = await client.get("/api/v1/health")
            if api_response.status_code == 200:
                api_health = api_response.json()
        except httpx.HTTPError:
            # API v1 health endpoint might not be available, that's okay
            pass

        return {
            "status": "healthy",
            "api_base_url": API_BASE_URL,
            "basic_health": response.json() if response.content else {"status": "ok"},
            "api_v1_health": api_health,
            "response_time_ms": response.elapsed.total_seconds() * 1000,
        }

    except httpx.HTTPError as e:
        logger.error(f"API health check failed: {e}")
        raise RuntimeError(f"acme-devops-api health check failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during health check: {e}")
        raise RuntimeError(f"Health check error: {e}")


# Future API integration tools will be added here:
#
# @mcp.tool()
# async def get_deployments(...) -> dict[str, Any]:
#     """Get deployment data from acme-devops-api"""
#     pass
#
# @mcp.tool()
# async def get_metrics(...) -> dict[str, Any]:
#     """Get metrics data from acme-devops-api"""
#     pass


# ============================================================================
# Module Entry Point
# ============================================================================


async def main():
    """
    Entry point for HTTP MCP server execution.

    Per Constitution Principle I: Minimal boilerplate, maximum clarity.
    Per Constitution Principle VI: Graceful shutdown handling.
    """
    try:
        async with lifespan_manager():
            logger.info("HTTP MCP server is ready")
            # FastMCP will handle the server lifecycle
            await mcp.run_async()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    """
    Entry point for FastMCP server execution.

    FastMCP handles:
    - asyncio.run() execution
    - Signal handling (SIGINT/SIGTERM)
    - Graceful shutdown
    - Exit codes
    - HTTP transport setup

    Per Constitution Principle I: Minimal boilerplate, maximum clarity.
    """
    logger.info("Starting http-mcp-server with FastMCP")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)
