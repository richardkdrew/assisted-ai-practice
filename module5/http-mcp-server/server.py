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
from datetime import datetime
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


# ============================================================================
# HTTP Client Wrapper Functions
# ============================================================================


async def make_api_request(
    endpoint: str, params: Optional[dict] = None, timeout: Optional[float] = None
) -> dict[str, Any]:
    """
    Make HTTP request to acme-devops-api with comprehensive error handling.

    Per Constitution Principle II: Explicit error handling for all external interactions.

    Args:
        endpoint: API endpoint path (e.g., "/api/v1/deployments")
        params: Optional query parameters
        timeout: Optional request timeout (defaults to HTTP_TIMEOUT)

    Returns:
        Parsed JSON response from API

    Raises:
        RuntimeError: For all API-related errors with descriptive messages
    """
    try:
        client = await get_http_client()

        # Clean up parameters - remove None values and empty strings
        clean_params = {}
        if params:
            for key, value in params.items():
                if value is not None and value != "":
                    clean_params[key] = value

        logger.debug(f"Making API request to {endpoint} with params: {clean_params}")

        # Make the request with optional timeout override
        request_timeout = timeout or HTTP_TIMEOUT
        response = await client.get(
            endpoint, params=clean_params, timeout=request_timeout
        )
        response.raise_for_status()

        # Parse JSON response
        try:
            json_data = response.json()
            logger.debug(f"API request successful: {endpoint}")
            return json_data
        except ValueError as e:
            logger.error(f"Invalid JSON response from {endpoint}: {e}")
            raise RuntimeError(f"API returned invalid JSON: {e}")

    except httpx.TimeoutException as e:
        logger.error(f"API request timeout for {endpoint}: {e}")
        raise RuntimeError(
            f"API request timed out after {request_timeout}s: {endpoint}"
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"API returned error {e.response.status_code} for {endpoint}: {e}")
        error_detail = ""
        try:
            error_response = e.response.json()
            error_detail = error_response.get("message", e.response.text)
        except:
            error_detail = e.response.text
        raise RuntimeError(f"API error {e.response.status_code}: {error_detail}")
    except httpx.RequestError as e:
        logger.error(f"API request failed for {endpoint}: {e}")
        raise RuntimeError(f"Failed to connect to API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error for {endpoint}: {e}")
        raise RuntimeError(f"Unexpected API error: {e}")


def validate_api_response(response: dict, expected_status: str = "success") -> None:
    """
    Validate API response structure and status.

    Per Constitution Principle II: Explicit error handling for all external interactions.

    Args:
        response: API response dictionary
        expected_status: Expected status value (default: "success")

    Raises:
        RuntimeError: If response is invalid or has error status
    """
    if not isinstance(response, dict):
        raise RuntimeError("Invalid API response: not a JSON object")

    if response.get("status") != expected_status:
        error_msg = response.get("message", "Unknown API error")
        raise RuntimeError(f"API returned error status: {error_msg}")

    if "data" not in response:
        raise RuntimeError("Invalid API response: missing data field")


# ============================================================================
# DevOps API Tools
# ============================================================================


@mcp.tool()
async def get_deployment_status(
    application: Optional[str] = None,
    environment: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> dict[str, Any]:
    """
    Get deployment status information from DevOps API.

    Query deployment status for applications across environments with optional
    filtering by application ID and/or environment name. Supports pagination
    for handling large result sets.

    Args:
        application: Optional application filter (e.g., "web-app", "api-service").
                     If not provided, returns deployments for all applications.
        environment: Optional environment filter (e.g., "prod", "staging", "uat").
                     If not provided, returns deployments across all environments.
        limit: Optional maximum number of results to return (default: 50).
               Use a smaller value for quicker responses or a larger value
               to retrieve more results in a single request.
        offset: Optional pagination offset (default: 0).
               Use with limit to retrieve subsequent pages of results.
               For example, limit=50, offset=50 retrieves the second page.

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
            "pagination": {
                "total_count": int,
                "returned_count": int,
                "limit": int,
                "offset": int,
                "has_more": bool,
                "page_info": str (e.g., "Showing 1-50 of 120 results")
            },
            "filters_applied": {
                "application": str | None,
                "environment": str | None
            },
            "timestamp": str (ISO 8601)
        }

    Raises:
        RuntimeError: If API request fails or returns invalid data.
    """
    try:
        # Apply default pagination values if not provided
        effective_limit = 50 if limit is None else limit
        effective_offset = 0 if offset is None else offset

        # Validate pagination parameters
        if effective_limit <= 0:
            raise ValueError("Limit must be a positive integer")
        if effective_offset < 0:
            raise ValueError("Offset must be a non-negative integer")

        # Build query parameters
        params = {}
        if application:
            params["application"] = application.strip()
        if environment:
            params["environment"] = environment.strip()

        # Add pagination parameters
        params["limit"] = str(effective_limit)
        params["offset"] = str(effective_offset)

        logger.info(
            f"Getting deployment status with filters: application={application}, "
            f"environment={environment}, limit={effective_limit}, offset={effective_offset}"
        )

        # Make API request
        response = await make_api_request("/api/v1/deployments", params)

        # Validate response structure
        validate_api_response(response)

        # Extract data from API response
        api_data = response["data"]
        deployments = api_data.get("deployments", [])
        total = api_data.get("total", len(deployments))
        returned = api_data.get("returned", len(deployments))
        has_more = api_data.get("has_more", False)

        # Calculate pagination information
        start_index = effective_offset + 1 if returned > 0 else 0
        end_index = effective_offset + returned
        page_info = f"Showing {start_index}-{end_index} of {total} results"

        # Transform response for MCP consumption
        result = {
            "status": "success",
            "deployments": deployments,
            "pagination": {
                "total_count": total,
                "returned_count": returned,
                "limit": effective_limit,
                "offset": effective_offset,
                "has_more": has_more,
                "page_info": page_info,
            },
            "filters_applied": {"application": application, "environment": environment},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Add metadata if available
        if "metadata" in api_data:
            metadata = api_data["metadata"]
            result["metadata"] = {
                "available_applications": metadata.get("available_applications", []),
                "available_environments": metadata.get("available_environments", []),
            }

        logger.info(f"Successfully retrieved {returned} deployments (total: {total})")
        return result

    except ValueError as e:
        # Handle parameter validation errors
        logger.error(f"Parameter validation error in get_deployment_status: {e}")
        raise RuntimeError(f"Invalid parameter: {e}")
    except RuntimeError:
        # Re-raise RuntimeError from API calls
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_deployment_status: {e}")
        raise RuntimeError(f"Failed to get deployment status: {e}")


@mcp.tool()
async def check_environment_health(
    environment: Optional[str] = None,
    application: Optional[str] = None,
    detailed: Optional[bool] = None,
) -> dict[str, Any]:
    """
    Check health status of services across environments.

    Query health status for specific environment or application, or get
    overall system health with summary statistics.

    Args:
        environment: Optional environment filter (e.g., "prod", "staging", "uat").
                     If not provided, returns health status for all environments.
        application: Optional application filter (e.g., "web-app", "api-service").
                     If not provided, returns health status for all applications.
        detailed: Optional flag to include detailed health information.
                  If not provided, uses the API default (typically false).

    Returns:
        Dictionary containing health status information with structure:
        {
            "status": "success" | "error",
            "health_status": [
                {
                    "environment": str,
                    "applicationId": str,
                    "status": str ("healthy" | "degraded" | "unhealthy"),
                    "lastChecked": str (ISO 8601),
                    "uptime": str,
                    "responseTime": str,
                    "issues": list
                },
                ...
            ],
            "summary": {
                "totalServices": int,
                "healthyServices": int,
                "degradedServices": int,
                "unhealthyServices": int,
                "overallStatus": str ("healthy" | "degraded" | "unhealthy")
            },
            "filters_applied": {
                "environment": str | None,
                "application": str | None,
                "detailed": bool | None
            },
            "timestamp": str (ISO 8601)
        }

    Raises:
        RuntimeError: If API request fails or returns invalid data.
    """
    try:
        # Build query parameters
        params = {}
        if environment:
            params["environment"] = environment.strip()
        if application:
            params["application"] = application.strip()
        if detailed is not None:
            params["detailed"] = str(detailed).lower()

        logger.info(
            f"Checking environment health with filters: environment={environment}, "
            f"application={application}, detailed={detailed}"
        )

        # Make API request
        response = await make_api_request("/api/v1/health", params)

        # Validate response structure
        validate_api_response(response)

        # Extract data from API response
        api_data = response["data"]
        health_status = api_data.get("healthStatus", [])

        # Transform response for MCP consumption
        result = {
            "status": "success",
            "health_status": health_status,
            "summary": api_data.get("summary", {}),
            "filters_applied": {
                "environment": environment,
                "application": application,
                "detailed": detailed,
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Add metadata if available
        if "metadata" in api_data:
            result["metadata"] = api_data["metadata"]

        logger.info(
            f"Successfully retrieved health status for {len(health_status)} services"
        )
        return result

    except RuntimeError:
        # Re-raise RuntimeError from API calls
        raise
    except Exception as e:
        logger.error(f"Unexpected error in check_environment_health: {e}")
        raise RuntimeError(f"Failed to check environment health: {e}")


@mcp.tool()
async def get_performance_metrics(
    application: Optional[str] = None,
    environment: Optional[str] = None,
    time_range: Optional[str] = None,
) -> dict[str, Any]:
    """
    Get performance metrics with aggregations from DevOps API.

    Retrieve CPU, memory, request, and error metrics for applications
    with statistical aggregations and filtering capabilities.

    Args:
        application: Optional application filter (e.g., "web-app", "api-service").
                     If not provided, returns metrics for all applications.
        environment: Optional environment filter (e.g., "prod", "staging", "uat").
                     If not provided, returns metrics across all environments.
        time_range: Optional time range for metrics (e.g., "24h", "7d").
                    If not provided, uses the API default (typically "24h").

    Returns:
        Dictionary containing metrics information with structure:
        {
            "status": "success" | "error",
            "metrics": [
                {
                    "applicationId": str,
                    "environment": str,
                    "timestamp": str (ISO 8601),
                    "cpu": float,
                    "memory": float,
                    "requests": int,
                    "errors": int
                },
                ...
            ],
            "aggregations": {
                "cpu": {"avg": float, "min": float, "max": float},
                "memory": {"avg": float, "min": float, "max": float},
                "requests": {"avg": float, "min": float, "max": float},
                "errors": {"avg": float, "min": float, "max": float}
            },
            "total_count": int,
            "filters_applied": {
                "application": str | None,
                "environment": str | None,
                "time_range": str | None
            },
            "timestamp": str (ISO 8601)
        }

    Raises:
        RuntimeError: If API request fails or returns invalid data.
    """
    try:
        # Build query parameters
        params = {}
        if application:
            params["application"] = application.strip()
        if environment:
            params["environment"] = environment.strip()
        if time_range:
            params["time_range"] = time_range.strip()

        logger.info(
            f"Getting performance metrics with filters: application={application}, "
            f"environment={environment}, time_range={time_range}"
        )

        # Make API request
        response = await make_api_request("/api/v1/metrics", params)

        # Validate response structure
        validate_api_response(response)

        # Extract data from API response
        api_data = response["data"]
        metrics = api_data.get("metrics", [])

        # Transform response for MCP consumption
        result = {
            "status": "success",
            "metrics": metrics,
            "aggregations": api_data.get("aggregations", {}),
            "total_count": api_data.get("total", len(metrics)),
            "filters_applied": {
                "application": application,
                "environment": environment,
                "time_range": time_range,
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Add metadata if available
        if "metadata" in api_data:
            result["metadata"] = api_data["metadata"]

        logger.info(f"Successfully retrieved {len(metrics)} metrics")
        return result

    except RuntimeError:
        # Re-raise RuntimeError from API calls
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_performance_metrics: {e}")
        raise RuntimeError(f"Failed to get performance metrics: {e}")


@mcp.tool()
async def get_log_entries(
    application: Optional[str] = None,
    environment: Optional[str] = None,
    level: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> dict[str, Any]:
    """
    Get log entries with filtering and pagination capabilities.

    Retrieve application logs with filtering by level, application,
    and environment, including log summaries and metadata. Supports
    pagination for handling large result sets.

    Args:
        application: Optional application filter (e.g., "web-app", "api-service").
                     If not provided, returns logs for all applications.
        environment: Optional environment filter (e.g., "prod", "staging", "uat").
                     If not provided, returns logs across all environments.
        level: Optional log level filter (e.g., "error", "warn", "info", "debug").
               If not provided, returns logs of all levels.
        limit: Optional maximum number of log entries to return (default: 50).
               Use a smaller value for quicker responses or a larger value
               to retrieve more results in a single request.
        offset: Optional pagination offset (default: 0).
               Use with limit to retrieve subsequent pages of results.
               For example, limit=50, offset=50 retrieves the second page.

    Returns:
        Dictionary containing log entries with structure:
        {
            "status": "success" | "error",
            "logs": [
                {
                    "id": str,
                    "applicationId": str,
                    "environment": str,
                    "timestamp": str (ISO 8601),
                    "level": str,
                    "message": str,
                    "source": str,
                    "metadata": dict
                },
                ...
            ],
            "pagination": {
                "total_count": int,
                "returned_count": int,
                "limit": int,
                "offset": int,
                "has_more": bool,
                "page_info": str (e.g., "Showing 1-50 of 120 results")
            },
            "summary": {
                "totalLogs": int,
                "errorLogs": int,
                "warnLogs": int,
                "infoLogs": int,
                "debugLogs": int,
                "logLevels": list[str]
            },
            "filters_applied": {
                "application": str | None,
                "environment": str | None,
                "level": str | None
            },
            "timestamp": str (ISO 8601)
        }

    Raises:
        RuntimeError: If API request fails or returns invalid data.
    """
    try:
        # Apply default pagination values if not provided
        effective_limit = 50 if limit is None else limit
        effective_offset = 0 if offset is None else offset

        # Validate pagination parameters
        if effective_limit <= 0:
            raise ValueError("Limit must be a positive integer")
        if effective_offset < 0:
            raise ValueError("Offset must be a non-negative integer")

        # Build query parameters
        params = {}
        if application:
            params["application"] = application.strip()
        if environment:
            params["environment"] = environment.strip()
        if level:
            params["level"] = level.strip().lower()

        # Add pagination parameters
        params["limit"] = str(effective_limit)
        # Note: The API might not support offset for logs yet, but we'll include it
        # in our parameters for future compatibility
        params["offset"] = str(effective_offset)

        logger.info(
            f"Getting log entries with filters: application={application}, "
            f"environment={environment}, level={level}, limit={effective_limit}, offset={effective_offset}"
        )

        # Make API request
        response = await make_api_request("/api/v1/logs", params)

        # Validate response structure
        validate_api_response(response)

        # Extract data from API response
        api_data = response["data"]
        logs = api_data.get("logs", [])
        total = api_data.get("total", len(logs))

        # If the API doesn't return a "returned" count, use the length of logs
        returned = api_data.get("showing", len(logs))

        # Calculate if there are more results
        has_more = total > (effective_offset + returned)

        # Calculate pagination information
        start_index = effective_offset + 1 if returned > 0 else 0
        end_index = effective_offset + returned
        page_info = f"Showing {start_index}-{end_index} of {total} results"

        # Transform response for MCP consumption
        result = {
            "status": "success",
            "logs": logs,
            "pagination": {
                "total_count": total,
                "returned_count": returned,
                "limit": effective_limit,
                "offset": effective_offset,
                "has_more": has_more,
                "page_info": page_info,
            },
            "summary": api_data.get("summary", {}),
            "filters_applied": {
                "application": application,
                "environment": environment,
                "level": level,
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Add metadata if available
        if "metadata" in api_data:
            result["metadata"] = api_data["metadata"]

        logger.info(f"Successfully retrieved {returned} log entries (total: {total})")
        return result

    except ValueError as e:
        # Handle parameter validation errors
        logger.error(f"Parameter validation error in get_log_entries: {e}")
        raise RuntimeError(f"Invalid parameter: {e}")
    except RuntimeError:
        # Re-raise RuntimeError from API calls
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_log_entries: {e}")
        raise RuntimeError(f"Failed to get log entries: {e}")


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
