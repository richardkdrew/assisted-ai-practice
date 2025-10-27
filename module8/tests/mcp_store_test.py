"""Tests for MCP-based memory stores."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from investigator_agent.memory.protocol import Memory
from investigator_agent.memory.mcp_store import MCPChromaMemoryStore, MCPGraphitiMemoryStore


class TestMCPChromaMemoryStore:
    """Tests for MCPChromaMemoryStore class."""

    def test_init(self):
        """Test initialization."""
        mock_client = Mock()
        store = MCPChromaMemoryStore(mock_client, collection_name="test_memories")

        assert store.mcp_client is mock_client
        assert store.collection_name == "test_memories"
        assert not store._initialized

    def test_init_default_collection_name(self):
        """Test initialization with default collection name."""
        mock_client = Mock()
        store = MCPChromaMemoryStore(mock_client)

        assert store.collection_name == "agent_memories"

    @pytest.mark.asyncio
    async def test_initialize_creates_collection(self):
        """Test that initialize creates the collection."""
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(return_value="Collection created")

        store = MCPChromaMemoryStore(mock_client, collection_name="test_coll")
        await store.initialize()

        assert store._initialized
        mock_client.call_tool.assert_called_once()
        call_args = mock_client.call_tool.call_args
        assert call_args[0][0] == "chroma_create_collection"
        assert call_args[0][1]["name"] == "test_coll"

    @pytest.mark.asyncio
    async def test_initialize_idempotent(self):
        """Test that initialize can be called multiple times."""
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(return_value="Collection created")

        store = MCPChromaMemoryStore(mock_client)
        await store.initialize()
        await store.initialize()  # Second call

        # Should only call tool once
        assert mock_client.call_tool.call_count == 1

    @pytest.mark.asyncio
    async def test_initialize_handles_existing_collection(self):
        """Test that initialize handles collection already existing."""
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(side_effect=Exception("Collection exists"))

        store = MCPChromaMemoryStore(mock_client)
        await store.initialize()

        # Should still mark as initialized
        assert store._initialized

    @pytest.mark.asyncio
    async def test_store_memory(self):
        """Test storing a memory."""
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(return_value="Added 1 documents")

        store = MCPChromaMemoryStore(mock_client)
        store._initialized = True

        memory = Memory(
            id="mem_123",
            feature_id="FEAT-001",
            decision="ready",
            justification="All tests pass",
            key_findings={"test_coverage": "95%"},
            timestamp=datetime(2025, 1, 1, 12, 0, 0),
            metadata={"author": "agent"}
        )

        result_id = await store.store(memory)

        assert result_id == "mem_123"
        mock_client.call_tool.assert_called_once()

        call_args = mock_client.call_tool.call_args
        assert call_args[0][0] == "chroma_add_documents"

        args = call_args[0][1]
        assert args["collection"] == "agent_memories"
        assert len(args["documents"]) == 1
        assert "FEAT-001" in args["documents"][0]
        assert args["ids"] == ["mem_123"]
        assert args["metadatas"][0]["feature_id"] == "FEAT-001"

    @pytest.mark.asyncio
    async def test_store_initializes_if_needed(self):
        """Test that store initializes collection if not initialized."""
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(return_value="Success")

        store = MCPChromaMemoryStore(mock_client)
        assert not store._initialized

        memory = Memory(
            id="mem_123",
            feature_id="FEAT-001",
            decision="ready",
            justification="Test",
            key_findings={},
            timestamp=datetime.now()
        )

        await store.store(memory)

        assert store._initialized
        # Called twice: once for init, once for add
        assert mock_client.call_tool.call_count == 2

    @pytest.mark.asyncio
    async def test_retrieve_returns_empty_list(self):
        """Test that retrieve returns empty list (placeholder)."""
        mock_client = AsyncMock()
        store = MCPChromaMemoryStore(mock_client)
        store._initialized = True

        memories = await store.retrieve(query="test")

        assert memories == []

    @pytest.mark.asyncio
    async def test_retrieve_by_id_returns_none(self):
        """Test that retrieve_by_id returns None (placeholder)."""
        mock_client = AsyncMock()
        store = MCPChromaMemoryStore(mock_client)
        store._initialized = True

        memory = await store.retrieve_by_id("mem_123")

        assert memory is None

    @pytest.mark.asyncio
    async def test_delete_memory(self):
        """Test deleting a memory."""
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(return_value="Deleted")

        store = MCPChromaMemoryStore(mock_client)
        store._initialized = True

        result = await store.delete("mem_123")

        assert result is True
        mock_client.call_tool.assert_called_once_with(
            "chroma_delete_documents",
            {"collection": "agent_memories", "ids": ["mem_123"]}
        )

    @pytest.mark.asyncio
    async def test_delete_handles_error(self):
        """Test that delete handles errors gracefully."""
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(side_effect=Exception("Not found"))

        store = MCPChromaMemoryStore(mock_client)
        store._initialized = True

        result = await store.delete("mem_123")

        assert result is False

    @pytest.mark.asyncio
    async def test_clear_all(self):
        """Test clearing all memories."""
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(return_value="Success")

        store = MCPChromaMemoryStore(mock_client, collection_name="test_coll")
        store._initialized = True

        result = await store.clear_all()

        assert result is True
        # Should delete collection and reinitialize
        assert mock_client.call_tool.call_count == 2

        # First call: delete collection
        first_call = mock_client.call_tool.call_args_list[0]
        assert first_call[0][0] == "chroma_delete_collection"
        assert first_call[0][1]["name"] == "test_coll"

    @pytest.mark.asyncio
    async def test_clear_all_handles_error(self):
        """Test that clear_all handles errors."""
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(side_effect=Exception("Error"))

        store = MCPChromaMemoryStore(mock_client)
        store._initialized = True

        result = await store.clear_all()

        assert result is False


class TestMCPGraphitiMemoryStore:
    """Tests for MCPGraphitiMemoryStore class."""

    def test_init(self):
        """Test initialization."""
        mock_client = Mock()
        store = MCPGraphitiMemoryStore(mock_client)

        assert store.mcp_client is mock_client

    @pytest.mark.asyncio
    async def test_store_memory(self):
        """Test storing a memory in knowledge graph."""
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(return_value="Episode added")

        store = MCPGraphitiMemoryStore(mock_client)

        memory = Memory(
            id="mem_123",
            feature_id="FEAT-001",
            decision="ready",
            justification="All tests pass",
            key_findings={"test_coverage": "95%"},
            timestamp=datetime(2025, 1, 1, 12, 0, 0)
        )

        result_id = await store.store(memory)

        assert result_id == "mem_123"
        mock_client.call_tool.assert_called_once()

        call_args = mock_client.call_tool.call_args
        assert call_args[0][0] == "graphiti_add_episode"

        args = call_args[0][1]
        assert "FEAT-001" in args["content"]
        assert args["metadata"]["memory_id"] == "mem_123"
        assert args["metadata"]["feature_id"] == "FEAT-001"
        assert args["metadata"]["decision"] == "ready"

    @pytest.mark.asyncio
    async def test_store_handles_error(self):
        """Test that store handles errors."""
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(side_effect=Exception("Graph error"))

        store = MCPGraphitiMemoryStore(mock_client)

        memory = Memory(
            id="mem_123",
            feature_id="FEAT-001",
            decision="ready",
            justification="Test",
            key_findings={},
            timestamp=datetime.now()
        )

        with pytest.raises(Exception, match="Graph error"):
            await store.store(memory)

    @pytest.mark.asyncio
    async def test_retrieve_returns_empty_list(self):
        """Test that retrieve returns empty list (placeholder)."""
        mock_client = AsyncMock()
        store = MCPGraphitiMemoryStore(mock_client)

        memories = await store.retrieve(query="test")

        assert memories == []

    @pytest.mark.asyncio
    async def test_retrieve_by_id_returns_none(self):
        """Test that retrieve_by_id returns None (placeholder)."""
        mock_client = AsyncMock()
        store = MCPGraphitiMemoryStore(mock_client)

        memory = await store.retrieve_by_id("mem_123")

        assert memory is None

    @pytest.mark.asyncio
    async def test_list_all_returns_empty_list(self):
        """Test that list_all returns empty list."""
        mock_client = AsyncMock()
        store = MCPGraphitiMemoryStore(mock_client)

        memories = await store.list_all()

        assert memories == []

    @pytest.mark.asyncio
    async def test_delete_memory(self):
        """Test deleting a memory from graph."""
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(return_value="Episode deleted")

        store = MCPGraphitiMemoryStore(mock_client)

        result = await store.delete("mem_123")

        assert result is True
        mock_client.call_tool.assert_called_once_with(
            "graphiti_delete_episode",
            {"episode_id": "mem_123"}
        )

    @pytest.mark.asyncio
    async def test_delete_handles_error(self):
        """Test that delete handles errors gracefully."""
        mock_client = AsyncMock()
        mock_client.call_tool = AsyncMock(side_effect=Exception("Not found"))

        store = MCPGraphitiMemoryStore(mock_client)

        result = await store.delete("mem_123")

        assert result is False

    @pytest.mark.asyncio
    async def test_clear_all_not_implemented(self):
        """Test that clear_all returns False (not implemented)."""
        mock_client = AsyncMock()
        store = MCPGraphitiMemoryStore(mock_client)

        result = await store.clear_all()

        assert result is False
