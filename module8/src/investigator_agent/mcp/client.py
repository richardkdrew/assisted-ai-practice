"""MCP client adapter for integrating MCP servers with the Investigator Agent.

This module provides a lightweight adapter layer that:
1. Connects to MCP servers using FastMCP client or official MCP SDK
2. Discovers tools from connected servers
3. Registers tools into the agent's ToolRegistry
4. Proxies tool execution to the appropriate MCP server

Supports multiple MCP transports:
- SSE (Server-Sent Events) for HTTP-based communication
- Stdio for local process communication
- WebSocket for bidirectional communication
"""

import logging
from typing import Any, Callable

import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

from investigator_agent.models import ToolCall, ToolDefinition, ToolResult
from investigator_agent.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for connecting to MCP servers and managing tool execution.

    This client handles the low-level communication with MCP servers,
    including connection management, tool discovery, and execution.

    Attributes:
        server_url: URL of the MCP server (for SSE transport)
        transport: Transport type ('sse', 'stdio', 'websocket')
        session: Active MCP client session
        tools: Discovered tools from the server
    """

    def __init__(
        self,
        server_url: str | None = None,
        transport: str = "sse",
        command: str | None = None,
        args: list[str] | None = None,
    ):
        """Initialize MCP client.

        Args:
            server_url: URL for SSE transport (e.g., 'http://localhost:8001/sse')
            transport: Transport type ('sse', 'stdio')
            command: Command to run for stdio transport
            args: Arguments for stdio command
        """
        self.server_url = server_url
        self.transport = transport
        self.command = command
        self.args = args or []
        self.session: ClientSession | None = None
        self.tools: dict[str, Any] = {}
        self._connected = False

    async def connect(self) -> None:
        """Connect to the MCP server and discover tools."""
        if self._connected:
            logger.warning("Already connected to MCP server")
            return

        try:
            if self.transport == "sse":
                if not self.server_url:
                    raise ValueError("server_url required for SSE transport")

                logger.info(f"Connecting to MCP server via SSE: {self.server_url}")

                # Create SSE client context
                async with sse_client(self.server_url) as (read, write):
                    async with ClientSession(read, write) as session:
                        self.session = session
                        await self._discover_tools()
                        self._connected = True

            elif self.transport == "stdio":
                if not self.command:
                    raise ValueError("command required for stdio transport")

                logger.info(f"Connecting to MCP server via stdio: {self.command}")

                # Create stdio client context
                server_params = StdioServerParameters(
                    command=self.command,
                    args=self.args
                )

                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        self.session = session
                        await self._discover_tools()
                        self._connected = True

            else:
                raise ValueError(f"Unsupported transport: {self.transport}")

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}", exc_info=True)
            raise

    async def _discover_tools(self) -> None:
        """Discover tools available from the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        try:
            # List available tools
            tools_response = await self.session.list_tools()

            # Store tools by name
            self.tools = {tool.name: tool for tool in tools_response.tools}

            logger.info(f"Discovered {len(self.tools)} tools from MCP server")
            for tool_name in self.tools:
                logger.debug(f"  - {tool_name}")

        except Exception as e:
            logger.error(f"Failed to discover tools: {e}", exc_info=True)
            raise

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute a tool on the MCP server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result as string
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")

        try:
            logger.info(f"Calling MCP tool: {name}")
            logger.debug(f"Arguments: {arguments}")

            # Call tool via MCP
            result = await self.session.call_tool(name, arguments)

            # Extract text content from response
            content_parts = []
            for content in result.content:
                if hasattr(content, "text"):
                    content_parts.append(content.text)

            response_text = "\n".join(content_parts)
            logger.debug(f"Tool result: {response_text[:200]}...")

            return response_text

        except Exception as e:
            logger.error(f"Failed to call tool {name}: {e}", exc_info=True)
            raise

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self.session:
            # Session cleanup happens via context manager
            self.session = None
            self._connected = False
            logger.info("Disconnected from MCP server")

    def is_connected(self) -> bool:
        """Check if connected to MCP server."""
        return self._connected


class MCPToolAdapter:
    """Adapter for registering MCP server tools with the agent's ToolRegistry.

    This adapter bridges MCP servers with the agent's tool system by:
    1. Discovering tools from one or more MCP servers
    2. Converting MCP tool definitions to agent ToolDefinitions
    3. Creating proxy functions that execute tools via MCP
    4. Registering tools in the agent's ToolRegistry

    Example:
        >>> # Connect to ChromaDB MCP server
        >>> chroma_client = MCPClient(
        ...     server_url="http://localhost:8001/sse",
        ...     transport="sse"
        ... )
        >>> await chroma_client.connect()
        >>>
        >>> # Create adapter and register tools
        >>> adapter = MCPToolAdapter(tool_registry)
        >>> await adapter.register_mcp_server(chroma_client, prefix="chroma")
        >>>
        >>> # Now tools like 'chroma_query' are available to the agent
    """

    def __init__(self, tool_registry: ToolRegistry):
        """Initialize the MCP tool adapter.

        Args:
            tool_registry: Agent's tool registry for registration
        """
        self.tool_registry = tool_registry
        self.mcp_clients: dict[str, MCPClient] = {}

    async def register_mcp_server(
        self,
        mcp_client: MCPClient,
        prefix: str = "",
        tool_filter: Callable[[str], bool] | None = None,
    ) -> int:
        """Register all tools from an MCP server with the agent.

        Args:
            mcp_client: Connected MCP client
            prefix: Optional prefix for tool names (e.g., 'chroma_')
            tool_filter: Optional function to filter tools by name

        Returns:
            Number of tools registered
        """
        if not mcp_client.is_connected():
            raise RuntimeError("MCP client is not connected")

        registered_count = 0

        for tool_name, mcp_tool in mcp_client.tools.items():
            # Apply filter if provided
            if tool_filter and not tool_filter(tool_name):
                logger.debug(f"Skipping tool {tool_name} (filtered)")
                continue

            # Create agent tool definition
            agent_tool_name = f"{prefix}{tool_name}" if prefix else tool_name

            # Create proxy function that calls MCP server
            async def proxy_function(
                *,
                _mcp_client=mcp_client,
                _original_name=tool_name,
                **kwargs: Any,
            ) -> str:
                """Proxy function that forwards calls to MCP server."""
                return await _mcp_client.call_tool(_original_name, kwargs)

            # Register with tool registry using register method
            self.tool_registry.register(
                name=agent_tool_name,
                description=mcp_tool.description or f"MCP tool: {tool_name}",
                input_schema=mcp_tool.inputSchema,
                handler=proxy_function,
            )

            # Track MCP client for this tool
            self.mcp_clients[agent_tool_name] = mcp_client

            registered_count += 1
            logger.info(f"Registered MCP tool: {agent_tool_name}")

        logger.info(f"Registered {registered_count} tools from MCP server")
        return registered_count

    async def disconnect_all(self) -> None:
        """Disconnect all MCP clients."""
        for client in set(self.mcp_clients.values()):
            await client.disconnect()
        self.mcp_clients.clear()
        logger.info("Disconnected all MCP clients")


# Utility function for easy setup
async def setup_mcp_tools(
    tool_registry: ToolRegistry,
    chroma_url: str | None = None,
    graphiti_url: str | None = None,
) -> MCPToolAdapter:
    """Convenience function to set up MCP tools for common backends.

    Args:
        tool_registry: Agent's tool registry
        chroma_url: Optional ChromaDB MCP server URL
        graphiti_url: Optional Graphiti MCP server URL

    Returns:
        Configured MCPToolAdapter

    Example:
        >>> adapter = await setup_mcp_tools(
        ...     tool_registry,
        ...     chroma_url="http://localhost:8001/sse",
        ...     graphiti_url="http://localhost:8000/sse"
        ... )
    """
    adapter = MCPToolAdapter(tool_registry)

    if chroma_url:
        logger.info(f"Setting up ChromaDB MCP tools from {chroma_url}")
        chroma_client = MCPClient(server_url=chroma_url, transport="sse")
        await chroma_client.connect()
        await adapter.register_mcp_server(chroma_client, prefix="")

    if graphiti_url:
        logger.info(f"Setting up Graphiti MCP tools from {graphiti_url}")
        graphiti_client = MCPClient(server_url=graphiti_url, transport="sse")
        await graphiti_client.connect()
        await adapter.register_mcp_server(graphiti_client, prefix="")

    return adapter
