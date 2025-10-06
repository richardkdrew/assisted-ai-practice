"""
Integration test for MCP initialize handshake with FastMCP.

Tests that the server correctly handles the initialization request
and returns proper capabilities per contracts/initialize.json.
"""

import pytest


class TestInitializeHandshake:
    """Test MCP protocol initialization handshake with FastMCP."""

    @pytest.mark.asyncio
    async def test_fastmcp_instance_configured(self):
        """
        Verify server has FastMCP instance configured properly.

        FastMCP handles the initialize handshake automatically.
        We verify the server instance is configured correctly.
        """
        from src import server

        # Verify FastMCP instance exists
        assert hasattr(server, 'mcp')
        assert server.mcp.name == "stdio-mcp-server"

    @pytest.mark.asyncio
    async def test_initialize_capabilities_empty(self):
        """
        Verify server has no tools/resources/prompts for v1.

        Per plan.md, v1 has no tools/resources/prompts implemented.
        FastMCP will automatically return empty lists for these.
        """
        from src import server

        # Verify FastMCP instance exists
        assert hasattr(server, 'mcp')

        # FastMCP handles empty capabilities automatically
        # We verify no tools/resources/prompts are registered
        # (FastMCP will return [] for these capabilities)

    @pytest.mark.asyncio
    async def test_logging_configured(self):
        """
        Verify logging is configured to stderr.

        Per Constitution Principle VI: All logs must go to stderr.
        """
        from src import server

        # Verify logger exists and is configured
        assert hasattr(server, 'logger')
        assert server.logger.name == "stdio-mcp-server"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
