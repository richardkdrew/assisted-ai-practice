"""MCP-based memory store implementations for Investigator Agent.

This module provides memory store implementations that use MCP servers
as backends, supporting both vector databases (ChromaDB) and knowledge
graphs (Graphiti/Neo4j).

The MCP approach provides:
- Interchangeable backends without code changes
- Standard protocol for memory operations
- Separation of concerns (memory logic vs storage)
- Future-proof extensibility
"""

import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING

from investigator_agent.memory.protocol import Memory

if TYPE_CHECKING:
    from investigator_agent.mcp.client import MCPClient

logger = logging.getLogger(__name__)


class MCPChromaMemoryStore:
    """Memory store using ChromaDB via MCP for vector-based retrieval.

    This implementation stores agent memories (feature assessments, decisions,
    justifications) in ChromaDB and uses semantic search for retrieval.

    Advantages:
    - Semantic similarity search (better than keyword matching)
    - Scalable to thousands of memories
    - Natural language queries work well
    - No manual indexing required

    Usage:
        >>> from investigator_agent.mcp.client import MCPClient
        >>> mcp_client = MCPClient(server_url="http://localhost:8001/sse")
        >>> await mcp_client.connect()
        >>>
        >>> memory_store = MCPChromaMemoryStore(mcp_client)
        >>> await memory_store.initialize()
    """

    def __init__(self, mcp_client: "MCPClient", collection_name: str = "agent_memories"):
        """Initialize ChromaDB memory store via MCP.

        Args:
            mcp_client: Connected MCP client for ChromaDB server
            collection_name: Name of the collection to store memories
        """
        self.mcp_client = mcp_client
        self.collection_name = collection_name
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the memory collection in ChromaDB."""
        if self._initialized:
            return

        try:
            # Try to create collection (idempotent)
            await self.mcp_client.call_tool(
                "chroma_create_collection",
                {
                    "name": self.collection_name,
                    "metadata": {
                        "description": "Agent memory store for feature assessments",
                        "created_at": datetime.now().isoformat(),
                    },
                },
            )
            logger.info(f"Initialized ChromaDB collection: {self.collection_name}")
            self._initialized = True

        except Exception as e:
            # Collection might already exist, which is fine
            logger.debug(f"Collection initialization: {e}")
            self._initialized = True

    async def store(self, memory: Memory) -> str:
        """Store a memory in ChromaDB.

        Args:
            memory: Memory object to store

        Returns:
            Memory ID
        """
        if not self._initialized:
            await self.initialize()

        try:
            # Create document text for embedding
            document_text = f"""
Feature: {memory.feature_id}
Decision: {memory.decision}
Justification: {memory.justification}

Key Findings:
{json.dumps(memory.key_findings, indent=2)}
            """.strip()

            # Store in ChromaDB
            await self.mcp_client.call_tool(
                "chroma_add_documents",
                {
                    "collection": self.collection_name,
                    "documents": [document_text],
                    "metadatas": [
                        {
                            "memory_id": memory.id,
                            "feature_id": memory.feature_id,
                            "decision": memory.decision,
                            "timestamp": memory.timestamp.isoformat(),
                            **(memory.metadata or {}),
                        }
                    ],
                    "ids": [memory.id],
                },
            )

            logger.info(f"Stored memory {memory.id} for feature {memory.feature_id}")
            return memory.id

        except Exception as e:
            logger.error(f"Failed to store memory: {e}", exc_info=True)
            raise

    async def retrieve(
        self,
        query: str | None = None,
        feature_id: str | None = None,
        decision: str | None = None,
        limit: int = 10,
    ) -> list[Memory]:
        """Retrieve memories using semantic search or filters.

        Args:
            query: Natural language query for semantic search
            feature_id: Filter by feature ID
            decision: Filter by decision type
            limit: Maximum number of results

        Returns:
            List of Memory objects
        """
        if not self._initialized:
            await self.initialize()

        try:
            # Build metadata filter
            where_filter = {}
            if feature_id:
                where_filter["feature_id"] = feature_id
            if decision:
                where_filter["decision"] = decision

            # Perform query
            if query:
                # Semantic search
                result_json = await self.mcp_client.call_tool(
                    "chroma_query",
                    {
                        "collection": self.collection_name,
                        "query_texts": [query],
                        "n_results": limit,
                        "where": where_filter if where_filter else None,
                    },
                )
            else:
                # Get by metadata filter
                result_json = await self.mcp_client.call_tool(
                    "chroma_get_documents",
                    {
                        "collection": self.collection_name,
                        "where": where_filter if where_filter else None,
                    },
                )

            # Parse results and reconstruct Memory objects
            # Note: This is a simplified implementation
            # In production, you'd store full Memory JSON in metadata
            memories = []
            # TODO: Parse ChromaDB response and reconstruct Memory objects
            # For now, return empty list as placeholder

            return memories

        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}", exc_info=True)
            return []

    async def retrieve_by_id(self, memory_id: str) -> Memory | None:
        """Retrieve a specific memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory object or None if not found
        """
        if not self._initialized:
            await self.initialize()

        try:
            result_json = await self.mcp_client.call_tool(
                "chroma_get_documents",
                {"collection": self.collection_name, "ids": [memory_id]},
            )

            # TODO: Parse result and reconstruct Memory
            # For now, return None as placeholder
            return None

        except Exception as e:
            logger.error(f"Failed to retrieve memory {memory_id}: {e}", exc_info=True)
            return None

    async def list_all(self) -> list[Memory]:
        """List all memories in the store.

        Returns:
            List of all Memory objects
        """
        return await self.retrieve(limit=1000)

    async def delete(self, memory_id: str) -> bool:
        """Delete a memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            True if deleted, False otherwise
        """
        if not self._initialized:
            await self.initialize()

        try:
            await self.mcp_client.call_tool(
                "chroma_delete_documents",
                {"collection": self.collection_name, "ids": [memory_id]},
            )
            logger.info(f"Deleted memory {memory_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}", exc_info=True)
            return False

    async def clear_all(self) -> bool:
        """Clear all memories from the store.

        Returns:
            True if successful
        """
        if not self._initialized:
            await self.initialize()

        try:
            # Delete the entire collection and recreate
            await self.mcp_client.call_tool(
                "chroma_delete_collection", {"name": self.collection_name}
            )
            self._initialized = False
            await self.initialize()
            logger.info(f"Cleared all memories from {self.collection_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to clear memories: {e}", exc_info=True)
            return False


class MCPGraphitiMemoryStore:
    """Memory store using Graphiti/Neo4j via MCP for graph-based retrieval.

    This implementation stores agent memories in a temporal knowledge graph
    using Graphiti, which provides:
    - Temporal relationships between memories
    - Entity extraction and linking
    - Graph-based reasoning
    - Time-aware queries

    Advantages over vector store:
    - Understands relationships between features
    - Temporal reasoning (what changed when)
    - Entity-centric queries (all memories about user X)
    - Better for complex, interconnected data

    Usage:
        >>> from investigator_agent.mcp.client import MCPClient
        >>> mcp_client = MCPClient(server_url="http://localhost:8000/sse")
        >>> await mcp_client.connect()
        >>>
        >>> memory_store = MCPGraphitiMemoryStore(mcp_client)
    """

    def __init__(self, mcp_client: "MCPClient"):
        """Initialize Graphiti memory store via MCP.

        Args:
            mcp_client: Connected MCP client for Graphiti server
        """
        self.mcp_client = mcp_client

    async def store(self, memory: Memory) -> str:
        """Store a memory in the knowledge graph.

        Creates episode nodes and extracts entities/relationships.

        Args:
            memory: Memory object to store

        Returns:
            Memory ID
        """
        try:
            # Create episode text
            episode_text = f"""
Feature Assessment: {memory.feature_id}

Decision: {memory.decision}

Justification:
{memory.justification}

Key Findings:
{json.dumps(memory.key_findings, indent=2)}

Timestamp: {memory.timestamp.isoformat()}
            """.strip()

            # Add episode to Graphiti (entities/relationships extracted automatically)
            await self.mcp_client.call_tool(
                "graphiti_add_episode",
                {
                    "content": episode_text,
                    "metadata": {
                        "memory_id": memory.id,
                        "feature_id": memory.feature_id,
                        "decision": memory.decision,
                        "timestamp": memory.timestamp.isoformat(),
                        **(memory.metadata or {}),
                    },
                },
            )

            logger.info(f"Stored memory {memory.id} in knowledge graph")
            return memory.id

        except Exception as e:
            logger.error(f"Failed to store memory in graph: {e}", exc_info=True)
            raise

    async def retrieve(
        self,
        query: str | None = None,
        feature_id: str | None = None,
        decision: str | None = None,
        limit: int = 10,
    ) -> list[Memory]:
        """Retrieve memories using graph search.

        Args:
            query: Natural language query
            feature_id: Filter by feature ID
            decision: Filter by decision type
            limit: Maximum number of results

        Returns:
            List of Memory objects
        """
        try:
            # Use Graphiti hybrid search (combines semantic + graph structure)
            search_query = query or f"feature {feature_id}" if feature_id else "feature assessment"

            result_json = await self.mcp_client.call_tool(
                "graphiti_search",
                {
                    "query": search_query,
                    "limit": limit,
                    # Add temporal constraints if needed
                },
            )

            # TODO: Parse Graphiti results and reconstruct Memory objects
            # This requires understanding Graphiti's response format
            memories = []
            return memories

        except Exception as e:
            logger.error(f"Failed to retrieve from graph: {e}", exc_info=True)
            return []

    async def retrieve_by_id(self, memory_id: str) -> Memory | None:
        """Retrieve a specific memory by ID from the graph.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory object or None if not found
        """
        # TODO: Implement using Graphiti episode retrieval
        return None

    async def list_all(self) -> list[Memory]:
        """List all memories in the graph.

        Returns:
            List of all Memory objects
        """
        return await self.retrieve(limit=1000)

    async def delete(self, memory_id: str) -> bool:
        """Delete a memory from the graph.

        Args:
            memory_id: Memory identifier

        Returns:
            True if deleted
        """
        try:
            await self.mcp_client.call_tool(
                "graphiti_delete_episode", {"episode_id": memory_id}
            )
            logger.info(f"Deleted memory {memory_id} from graph")
            return True

        except Exception as e:
            logger.error(f"Failed to delete from graph: {e}", exc_info=True)
            return False

    async def clear_all(self) -> bool:
        """Clear all memories from the graph.

        Returns:
            True if successful
        """
        # TODO: Implement using Graphiti clear/reset operations
        logger.warning("clear_all not yet implemented for Graphiti")
        return False
