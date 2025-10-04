"""
Tests for ping tool functionality.

Tests contract compliance, basic functionality, edge cases, and validation.
Following TDD approach: these tests should fail until ping tool is implemented.
"""

import pytest
from fastmcp import FastMCP


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mcp_server():
    """Create a FastMCP server instance for testing."""
    from src.server import mcp
    return mcp


# ============================================================================
# Contract Tests
# ============================================================================

@pytest.mark.asyncio
async def test_ping_tool_registered(mcp_server):
    """
    T002: Verify ping tool is registered in server capabilities.

    Contract: The ping tool must be discoverable via MCP protocol.
    Source: contracts/ping-tool.json
    """
    # Get list of available tools from server
    # get_tools() returns a list of tool names (strings)
    tools = await mcp_server.get_tools()

    # Verify ping tool exists in list
    assert "ping" in tools, f"Ping tool not found in server capabilities. Available: {tools}"

    # Get the actual tool object to verify its metadata
    ping_tool = await mcp_server.get_tool("ping")

    # Verify tool has correct metadata
    assert ping_tool.name == "ping"
    assert ping_tool.description is not None
    assert "Test connectivity" in ping_tool.description

    # Verify the underlying function has correct signature
    import inspect
    ping_fn = ping_tool.fn
    sig = inspect.signature(ping_fn)

    # Verify message parameter exists with correct type
    assert "message" in sig.parameters
    assert sig.parameters["message"].annotation == str
    assert sig.parameters["message"].default == inspect.Parameter.empty  # Required
    assert sig.return_annotation == str


# ============================================================================
# Unit Tests - Success Cases
# ============================================================================

@pytest.mark.asyncio
async def test_ping_basic(mcp_server):
    """
    T003: Test basic ping functionality.

    Input: {"message": "test"}
    Expected: "Pong: test"
    Source: contracts/ping-tool.json example 1
    """
    # Get the ping tool and access its underlying function
    from src.server import ping

    # The decorator wraps the function, so access the wrapped function
    ping_fn = ping.fn if hasattr(ping, 'fn') else ping

    result = await ping_fn(message="test")
    assert result == "Pong: test"


@pytest.mark.asyncio
async def test_ping_empty_message(mcp_server):
    """
    T004: Test ping with empty message.

    Input: {"message": ""}
    Expected: "Pong: "
    Source: contracts/ping-tool.json example 2
    """
    from src.server import ping

    ping_fn = ping.fn if hasattr(ping, 'fn') else ping
    result = await ping_fn(message="")
    assert result == "Pong: "


@pytest.mark.asyncio
async def test_ping_special_characters(mcp_server):
    """
    T005: Test ping with special characters and Unicode.

    Input: {"message": "Hello! @#$% 世界"}
    Expected: "Pong: Hello! @#$% 世界"
    Verify Unicode and special characters preserved.
    Source: contracts/ping-tool.json example 3
    """
    from src.server import ping

    ping_fn = ping.fn if hasattr(ping, 'fn') else ping
    message = "Hello! @#$% 世界"
    result = await ping_fn(message=message)
    assert result == f"Pong: {message}"

    # Verify exact character preservation
    assert "世界" in result
    assert "@#$%" in result


@pytest.mark.asyncio
async def test_ping_whitespace_preservation(mcp_server):
    """
    T006: Test ping with whitespace preservation.

    Input: {"message": "  leading and trailing  "}
    Expected: "Pong:   leading and trailing  "
    Verify whitespace preserved exactly.
    Source: contracts/ping-tool.json example 4
    """
    from src.server import ping

    ping_fn = ping.fn if hasattr(ping, 'fn') else ping
    message = "  leading and trailing  "
    result = await ping_fn(message=message)
    assert result == f"Pong: {message}"

    # Verify whitespace is preserved
    assert result.startswith("Pong:  ")  # Two spaces after colon
    assert result.endswith("  ")  # Two trailing spaces


# ============================================================================
# Validation Tests - Error Cases
# ============================================================================

def test_ping_missing_parameter(mcp_server):
    """
    T007: Test validation when message parameter is missing.

    Input: {} (no message parameter)
    Expected: Validation error (FastMCP will handle this automatically)
    Source: contracts/ping-tool.json errorCases[0]

    Note: FastMCP automatically validates required parameters before
    calling the function, so we test the type signature enforcement.
    """
    from src.server import ping
    import inspect

    # Access the underlying function
    ping_fn = ping.fn if hasattr(ping, 'fn') else ping

    # Verify the function signature requires 'message' parameter
    sig = inspect.signature(ping_fn)
    assert "message" in sig.parameters

    # Verify message parameter has no default (making it required)
    message_param = sig.parameters["message"]
    assert message_param.default == inspect.Parameter.empty


def test_ping_invalid_type(mcp_server):
    """
    T008: Test validation when message parameter has invalid type.

    Input: {"message": 123} (number instead of string)
    Expected: Type validation error (FastMCP handles this via type hints)
    Source: contracts/ping-tool.json errorCases[1]

    Note: FastMCP automatically validates parameter types from type hints.
    We verify the type hint is correctly specified as str.
    """
    from src.server import ping
    import inspect

    # Access the underlying function
    ping_fn = ping.fn if hasattr(ping, 'fn') else ping

    # Verify the function has type hint for message parameter
    sig = inspect.signature(ping_fn)
    message_param = sig.parameters["message"]

    # Verify type annotation is str
    assert message_param.annotation == str, \
        f"Expected str type hint, got {message_param.annotation}"
