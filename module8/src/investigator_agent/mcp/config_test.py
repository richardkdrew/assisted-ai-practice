"""Tests for MCP configuration system."""

import os
import pytest
from unittest.mock import patch
from investigator_agent.mcp.config import (
    MCPConfig,
    MCPServerConfig,
    MCPTransport,
    MemoryBackend,
    get_mcp_config,
)


class TestMCPServerConfig:
    """Tests for MCPServerConfig class."""

    def test_init_defaults(self):
        """Test initialization with defaults."""
        config = MCPServerConfig(name="test")

        assert config.name == "test"
        assert config.enabled is True
        assert config.url is None
        assert config.transport == MCPTransport.SSE
        assert config.command is None
        assert config.args == []
        assert config.env == {}
        assert config.tool_prefix == ""
        assert config.collection_name is None

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        config = MCPServerConfig(
            name="chroma",
            enabled=True,
            url="http://localhost:8001/sse",
            transport=MCPTransport.SSE,
            collection_name="memories"
        )

        assert config.name == "chroma"
        assert config.url == "http://localhost:8001/sse"
        assert config.collection_name == "memories"

    def test_from_env_sse_transport(self):
        """Test loading SSE config from environment."""
        env_vars = {
            "MCP_CHROMA_ENABLED": "true",
            "MCP_CHROMA_URL": "http://localhost:8001/sse",
            "MCP_CHROMA_TRANSPORT": "sse",
            "MCP_CHROMA_COLLECTION": "test_collection",
            "MCP_CHROMA_TOOL_PREFIX": "chroma_",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = MCPServerConfig.from_env("chroma", "MCP_CHROMA")

            assert config.name == "chroma"
            assert config.enabled is True
            assert config.url == "http://localhost:8001/sse"
            assert config.transport == MCPTransport.SSE
            assert config.collection_name == "test_collection"
            assert config.tool_prefix == "chroma_"

    def test_from_env_stdio_transport(self):
        """Test loading stdio config from environment."""
        env_vars = {
            "MCP_LOCAL_ENABLED": "true",
            "MCP_LOCAL_TRANSPORT": "stdio",
            "MCP_LOCAL_COMMAND": "python",
            "MCP_LOCAL_ARGS": "server.py --port 8000",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = MCPServerConfig.from_env("local", "MCP_LOCAL")

            assert config.name == "local"
            assert config.transport == MCPTransport.STDIO
            assert config.command == "python"
            assert config.args == ["server.py", "--port", "8000"]

    def test_from_env_disabled(self):
        """Test loading disabled server from environment."""
        env_vars = {"MCP_TEST_ENABLED": "false"}

        with patch.dict(os.environ, env_vars, clear=False):
            config = MCPServerConfig.from_env("test", "MCP_TEST")

            assert config.enabled is False

    def test_validate_sse_without_url_raises(self):
        """Test that SSE transport without URL fails validation."""
        config = MCPServerConfig(
            name="test",
            enabled=True,
            transport=MCPTransport.SSE,
            url=None
        )

        with pytest.raises(ValueError, match="SSE transport requires url"):
            config.validate()

    def test_validate_stdio_without_command_raises(self):
        """Test that stdio transport without command fails validation."""
        config = MCPServerConfig(
            name="test",
            enabled=True,
            transport=MCPTransport.STDIO,
            command=None
        )

        with pytest.raises(ValueError, match="stdio transport requires command"):
            config.validate()

    def test_validate_disabled_server_ok(self):
        """Test that disabled server doesn't require validation."""
        config = MCPServerConfig(
            name="test",
            enabled=False,
            transport=MCPTransport.SSE,
            url=None  # Missing URL but disabled
        )

        config.validate()  # Should not raise

    def test_validate_sse_with_url_ok(self):
        """Test that valid SSE config passes validation."""
        config = MCPServerConfig(
            name="test",
            enabled=True,
            transport=MCPTransport.SSE,
            url="http://localhost:8001/sse"
        )

        config.validate()  # Should not raise


class TestMCPConfig:
    """Tests for MCPConfig class."""

    def test_init_defaults(self):
        """Test initialization with defaults."""
        config = MCPConfig()

        assert config.enabled is True
        assert config.memory_backend == MemoryBackend.FILE
        assert config.servers == {}

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        chroma_config = MCPServerConfig(
            name="chroma",
            url="http://localhost:8001/sse"
        )

        config = MCPConfig(
            enabled=True,
            memory_backend=MemoryBackend.CHROMA,
            servers={"chroma": chroma_config}
        )

        assert config.enabled is True
        assert config.memory_backend == MemoryBackend.CHROMA
        assert "chroma" in config.servers

    def test_from_env_chroma_enabled(self):
        """Test loading config with ChromaDB enabled."""
        env_vars = {
            "MCP_ENABLED": "true",
            "MCP_MEMORY_BACKEND": "chroma",
            "MCP_CHROMA_ENABLED": "true",
            "MCP_CHROMA_URL": "http://localhost:8001/sse",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPConfig.from_env()

            assert config.enabled is True
            assert config.memory_backend == MemoryBackend.CHROMA
            assert "chroma" in config.servers
            assert config.servers["chroma"].enabled is True

    def test_from_env_graphiti_enabled(self):
        """Test loading config with Graphiti enabled."""
        env_vars = {
            "MCP_ENABLED": "true",
            "MCP_MEMORY_BACKEND": "graphiti",
            "MCP_GRAPHITI_ENABLED": "true",
            "MCP_GRAPHITI_URL": "http://localhost:8000/sse",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPConfig.from_env()

            assert config.memory_backend == MemoryBackend.GRAPHITI
            assert "graphiti" in config.servers

    def test_from_env_file_backend(self):
        """Test loading config with file backend."""
        env_vars = {
            "MCP_ENABLED": "false",
            "MCP_MEMORY_BACKEND": "file",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPConfig.from_env()

            assert config.enabled is False
            assert config.memory_backend == MemoryBackend.FILE
            assert config.servers == {}

    def test_default_local(self):
        """Test default_local factory method."""
        config = MCPConfig.default_local()

        assert config.enabled is True
        assert config.memory_backend == MemoryBackend.CHROMA
        assert "chroma" in config.servers
        assert config.servers["chroma"].url == "http://localhost:8001/sse"
        assert "graphiti" in config.servers
        assert config.servers["graphiti"].enabled is False

    def test_production_factory(self):
        """Test production factory method."""
        config = MCPConfig.production(
            chroma_url="https://chroma.example.com/sse",
            graphiti_url="https://graphiti.example.com/sse"
        )

        assert config.enabled is True
        assert config.memory_backend == MemoryBackend.CHROMA
        assert config.servers["chroma"].url == "https://chroma.example.com/sse"
        assert config.servers["graphiti"].url == "https://graphiti.example.com/sse"

    def test_production_factory_chroma_only(self):
        """Test production factory with only ChromaDB."""
        config = MCPConfig.production(
            chroma_url="https://chroma.example.com/sse"
        )

        assert "chroma" in config.servers
        assert "graphiti" not in config.servers

    def test_validate_chroma_backend_without_server_raises(self):
        """Test that ChromaDB backend without server fails validation."""
        config = MCPConfig(
            enabled=True,
            memory_backend=MemoryBackend.CHROMA,
            servers={}  # No ChromaDB server configured
        )

        with pytest.raises(ValueError, match="ChromaDB server not enabled"):
            config.validate()

    def test_validate_graphiti_backend_without_server_raises(self):
        """Test that Graphiti backend without server fails validation."""
        config = MCPConfig(
            enabled=True,
            memory_backend=MemoryBackend.GRAPHITI,
            servers={}  # No Graphiti server configured
        )

        with pytest.raises(ValueError, match="Graphiti server not enabled"):
            config.validate()

    def test_validate_disabled_ok(self):
        """Test that disabled MCP doesn't require validation."""
        config = MCPConfig(
            enabled=False,
            memory_backend=MemoryBackend.CHROMA,
            servers={}  # No servers but disabled
        )

        config.validate()  # Should not raise

    def test_chroma_property(self):
        """Test chroma property accessor."""
        chroma_config = MCPServerConfig(name="chroma")
        config = MCPConfig(servers={"chroma": chroma_config})

        assert config.chroma is chroma_config

    def test_chroma_property_none_when_missing(self):
        """Test chroma property returns None when not configured."""
        config = MCPConfig()

        assert config.chroma is None

    def test_graphiti_property(self):
        """Test graphiti property accessor."""
        graphiti_config = MCPServerConfig(name="graphiti")
        config = MCPConfig(servers={"graphiti": graphiti_config})

        assert config.graphiti is graphiti_config

    def test_get_server(self):
        """Test get_server method."""
        chroma_config = MCPServerConfig(name="chroma")
        config = MCPConfig(servers={"chroma": chroma_config})

        assert config.get_server("chroma") is chroma_config
        assert config.get_server("nonexistent") is None

    def test_enabled_servers(self):
        """Test enabled_servers method."""
        chroma_config = MCPServerConfig(name="chroma", enabled=True)
        graphiti_config = MCPServerConfig(name="graphiti", enabled=False)

        config = MCPConfig(servers={
            "chroma": chroma_config,
            "graphiti": graphiti_config,
        })

        enabled = config.enabled_servers()

        assert len(enabled) == 1
        assert enabled[0].name == "chroma"


class TestGetMCPConfig:
    """Tests for get_mcp_config singleton."""

    def test_get_mcp_config_returns_instance(self):
        """Test that get_mcp_config returns MCPConfig instance."""
        config = get_mcp_config()

        assert isinstance(config, MCPConfig)

    def test_get_mcp_config_singleton(self):
        """Test that get_mcp_config returns same instance."""
        config1 = get_mcp_config()
        config2 = get_mcp_config()

        assert config1 is config2

    def test_get_mcp_config_reload(self):
        """Test that reload=True creates new instance."""
        config1 = get_mcp_config()

        env_vars = {"MCP_MEMORY_BACKEND": "chroma"}
        with patch.dict(os.environ, env_vars, clear=False):
            config2 = get_mcp_config(reload=True)

        assert config1 is not config2
        # Backend should be different due to env change
        assert config2.memory_backend == MemoryBackend.CHROMA


class TestMemoryBackendEnum:
    """Tests for MemoryBackend enum."""

    def test_enum_values(self):
        """Test that all expected values exist."""
        assert MemoryBackend.FILE == "file"
        assert MemoryBackend.CHROMA == "chroma"
        assert MemoryBackend.GRAPHITI == "graphiti"
        assert MemoryBackend.NONE == "none"

    def test_enum_from_string(self):
        """Test creating enum from string."""
        backend = MemoryBackend("chroma")
        assert backend == MemoryBackend.CHROMA


class TestMCPTransportEnum:
    """Tests for MCPTransport enum."""

    def test_enum_values(self):
        """Test that all expected values exist."""
        assert MCPTransport.SSE == "sse"
        assert MCPTransport.STDIO == "stdio"
        assert MCPTransport.WEBSOCKET == "websocket"

    def test_enum_from_string(self):
        """Test creating enum from string."""
        transport = MCPTransport("sse")
        assert transport == MCPTransport.SSE
