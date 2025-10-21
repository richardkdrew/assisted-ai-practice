"""MCP (Model Context Protocol) integration for the Investigator Agent.

This module provides client adapters for connecting to MCP servers that provide
various capabilities like knowledge graphs (Graphiti), vector databases (ChromaDB),
and other specialized tools.

Key components:
- MCPClient: Base client for connecting to MCP servers
- MCPToolAdapter: Adapter for registering MCP tools with the agent's ToolRegistry
- MCPConfig: Configuration for MCP server connections
- MemoryBackend: Enum of supported memory backends
- MCPServerConfig: Configuration for individual MCP servers
"""

from investigator_agent.mcp.client import MCPClient, MCPToolAdapter, setup_mcp_tools
from investigator_agent.mcp.config import (
    MCPConfig,
    MCPServerConfig,
    MCPTransport,
    MemoryBackend,
    get_mcp_config,
)

__all__ = [
    "MCPClient",
    "MCPToolAdapter",
    "setup_mcp_tools",
    "MCPConfig",
    "MCPServerConfig",
    "MCPTransport",
    "MemoryBackend",
    "get_mcp_config",
]
