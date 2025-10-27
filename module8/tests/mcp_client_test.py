"""Tests for MCP client and tool adapter."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from investigator_agent.mcp.client import MCPClient, MCPToolAdapter, setup_mcp_tools
from investigator_agent.tools.registry import ToolRegistry
from investigator_agent.observability.tracer import setup_tracer


# Setup tracer once for all tests in this module
setup_tracer(Path("/tmp/test_traces"))


class TestMCPClient:
    """Tests for MCPClient class."""

    def test_init_sse_transport(self):
        """Test initialization with SSE transport."""
        client = MCPClient(
            server_url="http://localhost:8001/sse",
            transport="sse"
        )

        assert client.server_url == "http://localhost:8001/sse"
        assert client.transport == "sse"
        assert client.session is None
        assert not client._connected
        assert client.tools == {}

    def test_init_stdio_transport(self):
        """Test initialization with stdio transport."""
        client = MCPClient(
            transport="stdio",
            command="python",
            args=["server.py"]
        )

        assert client.transport == "stdio"
        assert client.command == "python"
        assert client.args == ["server.py"]
        assert not client._connected

    def test_init_missing_url_for_sse(self):
        """Test that SSE transport requires server_url."""
        client = MCPClient(transport="sse")
        assert client.server_url is None

    def test_is_connected_initially_false(self):
        """Test that client is not connected initially."""
        client = MCPClient(server_url="http://localhost:8001/sse")
        assert not client.is_connected()

    @pytest.mark.asyncio
    async def test_connect_sse_success(self):
        """Test successful SSE connection."""
        client = MCPClient(
            server_url="http://localhost:8001/sse",
            transport="sse"
        )

        # Mock the sse_client context manager
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        mock_session = AsyncMock()
        mock_tools_response = Mock()

        # Create mock tool with name attribute
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "Test"
        mock_tool.inputSchema = {}

        mock_tools_response.tools = [mock_tool]
        mock_session.list_tools = AsyncMock(return_value=mock_tools_response)

        with patch('investigator_agent.mcp.client.sse_client') as mock_sse:
            with patch('investigator_agent.mcp.client.ClientSession') as mock_session_cls:
                # Setup context managers
                mock_sse.return_value.__aenter__ = AsyncMock(
                    return_value=(mock_read, mock_write)
                )
                mock_sse.return_value.__aexit__ = AsyncMock()

                mock_session_cls.return_value.__aenter__ = AsyncMock(
                    return_value=mock_session
                )
                mock_session_cls.return_value.__aexit__ = AsyncMock()

                await client.connect()

                # Verify tools were discovered
                assert "test_tool" in client.tools
                assert client._connected

    @pytest.mark.asyncio
    async def test_connect_without_server_url_raises(self):
        """Test that connect without server_url raises ValueError."""
        client = MCPClient(transport="sse")

        with pytest.raises(ValueError, match="server_url required"):
            await client.connect()

    @pytest.mark.asyncio
    async def test_connect_stdio_without_command_raises(self):
        """Test that stdio connect without command raises ValueError."""
        client = MCPClient(transport="stdio")

        with pytest.raises(ValueError, match="command required"):
            await client.connect()

    @pytest.mark.asyncio
    async def test_connect_unsupported_transport_raises(self):
        """Test that unsupported transport raises ValueError."""
        client = MCPClient(
            server_url="ws://localhost:8001",
            transport="websocket"  # Not yet supported
        )

        with pytest.raises(ValueError, match="Unsupported transport"):
            await client.connect()

    @pytest.mark.asyncio
    async def test_call_tool_success(self):
        """Test successful tool execution."""
        client = MCPClient(server_url="http://localhost:8001/sse")
        client._connected = True
        client.tools = {"test_tool": Mock(name="test_tool")}

        # Mock session
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_content = Mock()
        mock_content.text = "Tool result"
        mock_result.content = [mock_content]
        mock_session.call_tool = AsyncMock(return_value=mock_result)
        client.session = mock_session

        result = await client.call_tool("test_tool", {"arg": "value"})

        assert result == "Tool result"
        mock_session.call_tool.assert_called_once_with(
            "test_tool",
            {"arg": "value"}
        )

    @pytest.mark.asyncio
    async def test_call_tool_not_connected_raises(self):
        """Test that calling tool while not connected raises."""
        client = MCPClient(server_url="http://localhost:8001/sse")

        with pytest.raises(RuntimeError, match="Not connected"):
            await client.call_tool("test_tool", {})

    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool_raises(self):
        """Test that calling unknown tool raises ValueError."""
        client = MCPClient(server_url="http://localhost:8001/sse")
        client._connected = True
        client.session = AsyncMock()
        client.tools = {}

        with pytest.raises(ValueError, match="Unknown tool"):
            await client.call_tool("unknown_tool", {})

    @pytest.mark.asyncio
    async def test_call_tool_multiple_content_parts(self):
        """Test tool call with multiple content parts."""
        client = MCPClient(server_url="http://localhost:8001/sse")
        client._connected = True
        client.tools = {"test_tool": Mock()}

        mock_session = AsyncMock()
        mock_result = Mock()
        mock_content1 = Mock()
        mock_content1.text = "Part 1"
        mock_content2 = Mock()
        mock_content2.text = "Part 2"
        mock_result.content = [mock_content1, mock_content2]
        mock_session.call_tool = AsyncMock(return_value=mock_result)
        client.session = mock_session

        result = await client.call_tool("test_tool", {})

        assert result == "Part 1\nPart 2"

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection."""
        client = MCPClient(server_url="http://localhost:8001/sse")
        client._connected = True
        client.session = Mock()

        await client.disconnect()

        assert client.session is None
        assert not client._connected


class TestMCPToolAdapter:
    """Tests for MCPToolAdapter class."""

    def test_init(self):
        """Test adapter initialization."""
        registry = ToolRegistry()
        adapter = MCPToolAdapter(registry)

        assert adapter.tool_registry is registry
        assert adapter.mcp_clients == {}

    @pytest.mark.asyncio
    async def test_register_mcp_server_not_connected_raises(self):
        """Test that registering non-connected client raises."""
        registry = ToolRegistry()
        adapter = MCPToolAdapter(registry)

        client = MCPClient(server_url="http://localhost:8001/sse")

        with pytest.raises(RuntimeError, match="not connected"):
            await adapter.register_mcp_server(client)

    @pytest.mark.asyncio
    async def test_register_mcp_server_success(self):
        """Test successful tool registration from MCP server."""
        registry = ToolRegistry()
        adapter = MCPToolAdapter(registry)

        # Create mock MCP client
        client = MCPClient(server_url="http://localhost:8001/sse")
        client._connected = True

        # Mock tools
        mock_tool1 = Mock()
        mock_tool1.name = "tool1"
        mock_tool1.description = "Tool 1"
        mock_tool1.inputSchema = {"type": "object", "properties": {}}

        mock_tool2 = Mock()
        mock_tool2.name = "tool2"
        mock_tool2.description = "Tool 2"
        mock_tool2.inputSchema = {"type": "object", "properties": {}}

        client.tools = {
            "tool1": mock_tool1,
            "tool2": mock_tool2,
        }

        count = await adapter.register_mcp_server(client)

        assert count == 2
        assert "tool1" in adapter.mcp_clients
        assert "tool2" in adapter.mcp_clients

        # Verify tools registered in registry
        tool_names = registry.get_tool_names()
        assert "tool1" in tool_names
        assert "tool2" in tool_names

    @pytest.mark.asyncio
    async def test_register_mcp_server_with_prefix(self):
        """Test tool registration with prefix."""
        registry = ToolRegistry()
        adapter = MCPToolAdapter(registry)

        client = MCPClient(server_url="http://localhost:8001/sse")
        client._connected = True

        mock_tool = Mock()
        mock_tool.name = "query"
        mock_tool.description = "Query tool"
        mock_tool.inputSchema = {"type": "object"}

        client.tools = {"query": mock_tool}

        count = await adapter.register_mcp_server(client, prefix="chroma_")

        assert count == 1
        assert "chroma_query" in adapter.mcp_clients

        tool_names = registry.get_tool_names()
        assert "chroma_query" in tool_names

    @pytest.mark.asyncio
    async def test_register_mcp_server_with_filter(self):
        """Test tool registration with filter function."""
        registry = ToolRegistry()
        adapter = MCPToolAdapter(registry)

        client = MCPClient(server_url="http://localhost:8001/sse")
        client._connected = True

        mock_tool1 = Mock(name="chroma_query", description="Query", inputSchema={})
        mock_tool2 = Mock(name="other_tool", description="Other", inputSchema={})

        client.tools = {
            "chroma_query": mock_tool1,
            "other_tool": mock_tool2,
        }

        # Filter to only register chroma_ tools
        count = await adapter.register_mcp_server(
            client,
            tool_filter=lambda name: name.startswith("chroma_")
        )

        assert count == 1
        assert "chroma_query" in adapter.mcp_clients
        assert "other_tool" not in adapter.mcp_clients

    @pytest.mark.asyncio
    async def test_disconnect_all(self):
        """Test disconnecting all MCP clients."""
        registry = ToolRegistry()
        adapter = MCPToolAdapter(registry)

        # Create mock clients
        client1 = AsyncMock()
        client1.disconnect = AsyncMock()

        client2 = AsyncMock()
        client2.disconnect = AsyncMock()

        adapter.mcp_clients = {
            "tool1": client1,
            "tool2": client1,  # Same client
            "tool3": client2,
        }

        await adapter.disconnect_all()

        # Each unique client disconnected once
        client1.disconnect.assert_called_once()
        client2.disconnect.assert_called_once()

        assert adapter.mcp_clients == {}


class TestSetupMCPTools:
    """Tests for setup_mcp_tools convenience function."""

    @pytest.mark.asyncio
    async def test_setup_with_chroma_only(self):
        """Test setup with only ChromaDB."""
        registry = ToolRegistry()

        with patch('investigator_agent.mcp.client.MCPClient') as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.connect = AsyncMock()
            mock_client.is_connected = Mock(return_value=True)
            mock_client.tools = {}
            mock_client_cls.return_value = mock_client

            adapter = await setup_mcp_tools(
                registry,
                chroma_url="http://localhost:8001/sse"
            )

            assert isinstance(adapter, MCPToolAdapter)
            mock_client.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_setup_with_both_backends(self):
        """Test setup with both ChromaDB and Graphiti."""
        registry = ToolRegistry()

        with patch('investigator_agent.mcp.client.MCPClient') as mock_client_cls:
            mock_clients = [AsyncMock(), AsyncMock()]
            for client in mock_clients:
                client.connect = AsyncMock()
                client.is_connected = Mock(return_value=True)
                client.tools = {}

            mock_client_cls.side_effect = mock_clients

            adapter = await setup_mcp_tools(
                registry,
                chroma_url="http://localhost:8001/sse",
                graphiti_url="http://localhost:8000/sse"
            )

            assert isinstance(adapter, MCPToolAdapter)
            assert mock_clients[0].connect.called
            assert mock_clients[1].connect.called

    @pytest.mark.asyncio
    async def test_setup_with_no_urls(self):
        """Test setup with no URLs returns empty adapter."""
        registry = ToolRegistry()

        adapter = await setup_mcp_tools(registry)

        assert isinstance(adapter, MCPToolAdapter)
        assert adapter.mcp_clients == {}
