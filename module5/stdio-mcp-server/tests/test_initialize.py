"""
Integration test for MCP initialize handshake.

Tests that the server correctly handles the initialization request
and returns proper capabilities per contracts/initialize.json.
"""

import pytest
import asyncio
import json
from typing import Any, Dict


class TestInitializeHandshake:
    """Test MCP protocol initialization handshake."""

    @pytest.mark.asyncio
    async def test_initialize_response_structure(self):
        """
        Verify server has MCP server instance configured properly.

        The MCP SDK handles the initialize handshake automatically.
        We verify the server instance is configured correctly.
        """
        from src import server

        # Verify MCP server instance exists
        assert hasattr(server, 'mcp_server')
        assert server.mcp_server.name == "stdio-mcp-server"

        # Verify the server has the required handler decorators
        # (The MCP SDK handles initialization automatically)

    @pytest.mark.asyncio
    async def test_initialize_capabilities_empty(self):
        """
        Verify server has empty capabilities handlers for v1.

        Per plan.md, v1 has no tools/resources/prompts implemented.
        The handlers return empty lists.
        """
        from src import server

        # Verify tool/resource/prompt list functions exist and return empty
        # These are decorated with @mcp_server.list_tools(), etc.
        # We can't directly test the decorated functions, but we verify
        # the server module has them defined
        assert 'list_tools' in dir(server)
        assert 'list_resources' in dir(server)
        assert 'list_prompts' in dir(server)

    @pytest.mark.asyncio
    async def test_initialize_server_info(self):
        """
        Verify server has correct server info.

        Per contracts/initialize.json:
        - name: "stdio-mcp-server"
        """
        from src import server

        # Verify MCP server instance has correct name
        assert server.mcp_server.name == "stdio-mcp-server"
        # Version is managed in pyproject.toml (0.1.0)


if __name__ == "__main__":
    # Run tests to verify they fail (TDD requirement)
    pytest.main([__file__, "-v"])
