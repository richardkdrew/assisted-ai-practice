"""Configuration models for MCP server connections.

This module defines the data structures used to configure MCP servers,
including connection parameters, environment variables, and transport settings.

Supports multiple backend types:
- ChromaDB: Vector database for semantic search
- Graphiti: Temporal knowledge graph for entities/relationships
- Neo4j: Graph database (via Graphiti or direct)
- Custom: User-defined MCP servers

Example .env configuration:
```
# MCP Backend Selection
MCP_ENABLED=true
MCP_MEMORY_BACKEND=chroma  # Options: chroma, graphiti, file, none

# ChromaDB MCP Server
MCP_CHROMA_ENABLED=true
MCP_CHROMA_URL=http://localhost:8001/sse
MCP_CHROMA_TRANSPORT=sse
MCP_CHROMA_COLLECTION=agent_memories

# Graphiti MCP Server
MCP_GRAPHITI_ENABLED=false
MCP_GRAPHITI_URL=http://localhost:8000/sse
MCP_GRAPHITI_TRANSPORT=sse

# Neo4j (for Graphiti backend)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
```
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MCPTransport(str, Enum):
    """Supported MCP transport types."""

    SSE = "sse"  # Server-Sent Events (HTTP)
    STDIO = "stdio"  # Standard I/O (local process)
    WEBSOCKET = "websocket"  # WebSocket (future support)


class MemoryBackend(str, Enum):
    """Supported memory storage backends."""

    FILE = "file"  # File-based JSON storage (legacy)
    CHROMA = "chroma"  # ChromaDB vector database via MCP
    GRAPHITI = "graphiti"  # Graphiti knowledge graph via MCP
    NONE = "none"  # No memory (stateless)


@dataclass
class MCPServerConfig:
    """Configuration for a single MCP server connection.

    Attributes:
        name: Server identifier (e.g., 'chroma', 'graphiti')
        enabled: Whether this server should be used
        url: Server URL for network transports (SSE, WebSocket)
        transport: Transport protocol to use
        command: Command to run for stdio transport
        args: Arguments for stdio command
        env: Additional environment variables for the server
        tool_prefix: Optional prefix for registered tools
        collection_name: Collection/database name for data storage
    """

    name: str
    enabled: bool = True
    url: str | None = None
    transport: MCPTransport = MCPTransport.SSE
    command: str | None = None
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    tool_prefix: str = ""
    collection_name: str | None = None

    @classmethod
    def from_env(cls, name: str, prefix: str) -> "MCPServerConfig":
        """Create server config from environment variables.

        Args:
            name: Server name (e.g., 'chroma', 'graphiti')
            prefix: Environment variable prefix (e.g., 'MCP_CHROMA')

        Returns:
            MCPServerConfig instance

        Example:
            >>> config = MCPServerConfig.from_env('chroma', 'MCP_CHROMA')
        """
        return cls(
            name=name,
            enabled=os.getenv(f"{prefix}_ENABLED", "false").lower() == "true",
            url=os.getenv(f"{prefix}_URL"),
            transport=MCPTransport(
                os.getenv(f"{prefix}_TRANSPORT", "sse").lower()
            ),
            command=os.getenv(f"{prefix}_COMMAND"),
            args=os.getenv(f"{prefix}_ARGS", "").split()
            if os.getenv(f"{prefix}_ARGS")
            else [],
            tool_prefix=os.getenv(f"{prefix}_TOOL_PREFIX", ""),
            collection_name=os.getenv(f"{prefix}_COLLECTION"),
        )

    def validate(self) -> None:
        """Validate the configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.enabled:
            return

        if self.transport == MCPTransport.SSE:
            if not self.url:
                raise ValueError(
                    f"MCP server '{self.name}': SSE transport requires url"
                )
        elif self.transport == MCPTransport.STDIO:
            if not self.command:
                raise ValueError(
                    f"MCP server '{self.name}': stdio transport requires command"
                )


@dataclass
class MCPConfig:
    """Complete MCP configuration for the agent.

    This class manages all MCP server configurations and provides
    helper methods for common setups.

    Attributes:
        enabled: Global MCP enable flag
        memory_backend: Which backend to use for agent memory
        servers: Dictionary of server configurations by name
    """

    enabled: bool = True
    memory_backend: MemoryBackend = MemoryBackend.FILE
    servers: dict[str, MCPServerConfig] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "MCPConfig":
        """Create MCP config from environment variables.

        Reads standard environment variables to configure:
        - Global MCP settings
        - ChromaDB server (if enabled)
        - Graphiti server (if enabled)
        - Custom servers (if configured)

        Returns:
            MCPConfig instance

        Example:
            >>> config = MCPConfig.from_env()
            >>> if config.enabled and config.chroma:
            ...     # Use ChromaDB
        """
        # Global settings
        enabled = os.getenv("MCP_ENABLED", "false").lower() == "true"
        memory_backend = MemoryBackend(
            os.getenv("MCP_MEMORY_BACKEND", "file").lower()
        )

        servers = {}

        # ChromaDB server
        chroma_config = MCPServerConfig.from_env("chroma", "MCP_CHROMA")
        if chroma_config.enabled or memory_backend == MemoryBackend.CHROMA:
            chroma_config.enabled = True
            chroma_config.collection_name = chroma_config.collection_name or "agent_memories"
            servers["chroma"] = chroma_config

        # Graphiti server
        graphiti_config = MCPServerConfig.from_env("graphiti", "MCP_GRAPHITI")
        if graphiti_config.enabled or memory_backend == MemoryBackend.GRAPHITI:
            graphiti_config.enabled = True
            servers["graphiti"] = graphiti_config

        return cls(
            enabled=enabled,
            memory_backend=memory_backend,
            servers=servers,
        )

    @classmethod
    def default_local(cls) -> "MCPConfig":
        """Create default configuration for local development.

        Returns configuration assuming Docker Compose setup with:
        - ChromaDB on port 8001
        - Graphiti on port 8000

        Returns:
            MCPConfig instance
        """
        return cls(
            enabled=True,
            memory_backend=MemoryBackend.CHROMA,
            servers={
                "chroma": MCPServerConfig(
                    name="chroma",
                    enabled=True,
                    url="http://localhost:8001/sse",
                    transport=MCPTransport.SSE,
                    collection_name="agent_memories",
                ),
                "graphiti": MCPServerConfig(
                    name="graphiti",
                    enabled=False,  # Optional
                    url="http://localhost:8000/sse",
                    transport=MCPTransport.SSE,
                ),
            },
        )

    @classmethod
    def production(cls, chroma_url: str, graphiti_url: str | None = None) -> "MCPConfig":
        """Create production configuration.

        Args:
            chroma_url: Production ChromaDB MCP server URL
            graphiti_url: Optional Graphiti MCP server URL

        Returns:
            MCPConfig instance
        """
        servers = {
            "chroma": MCPServerConfig(
                name="chroma",
                enabled=True,
                url=chroma_url,
                transport=MCPTransport.SSE,
                collection_name="agent_memories",
            )
        }

        if graphiti_url:
            servers["graphiti"] = MCPServerConfig(
                name="graphiti",
                enabled=True,
                url=graphiti_url,
                transport=MCPTransport.SSE,
            )

        return cls(
            enabled=True,
            memory_backend=MemoryBackend.CHROMA,
            servers=servers,
        )

    def validate(self) -> None:
        """Validate all server configurations.

        Raises:
            ValueError: If any configuration is invalid
        """
        if not self.enabled:
            return

        for server in self.servers.values():
            server.validate()

        # Validate memory backend has corresponding server
        if self.memory_backend == MemoryBackend.CHROMA:
            if "chroma" not in self.servers or not self.servers["chroma"].enabled:
                raise ValueError(
                    "Memory backend set to 'chroma' but ChromaDB server not enabled"
                )
        elif self.memory_backend == MemoryBackend.GRAPHITI:
            if "graphiti" not in self.servers or not self.servers["graphiti"].enabled:
                raise ValueError(
                    "Memory backend set to 'graphiti' but Graphiti server not enabled"
                )

    @property
    def chroma(self) -> MCPServerConfig | None:
        """Get ChromaDB server configuration."""
        return self.servers.get("chroma")

    @property
    def graphiti(self) -> MCPServerConfig | None:
        """Get Graphiti server configuration."""
        return self.servers.get("graphiti")

    def get_server(self, name: str) -> MCPServerConfig | None:
        """Get server configuration by name.

        Args:
            name: Server name

        Returns:
            Server configuration or None if not found
        """
        return self.servers.get(name)

    def enabled_servers(self) -> list[MCPServerConfig]:
        """Get list of enabled server configurations.

        Returns:
            List of enabled server configs
        """
        return [s for s in self.servers.values() if s.enabled]


# Singleton instance for easy access
_mcp_config: MCPConfig | None = None


def get_mcp_config(reload: bool = False) -> MCPConfig:
    """Get the global MCP configuration.

    Args:
        reload: Force reload from environment

    Returns:
        MCPConfig instance
    """
    global _mcp_config

    if _mcp_config is None or reload:
        _mcp_config = MCPConfig.from_env()

    return _mcp_config
