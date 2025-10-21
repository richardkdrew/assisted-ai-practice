"""Memory system protocol interface.

This module defines the protocol (interface) for memory operations.
Implementations can be file-based, vector-based, or graph-based.
"""

from datetime import datetime
from typing import Any, Protocol


class Memory:
    """A memory entry storing past assessment information."""

    def __init__(
        self,
        id: str,
        feature_id: str,
        decision: str,
        justification: str,
        key_findings: dict[str, Any],
        timestamp: datetime,
        metadata: dict[str, Any] | None = None,
    ):
        """Initialize a memory entry.

        Args:
            id: Unique memory identifier
            feature_id: Feature that was assessed
            decision: Assessment decision (ready, not_ready, borderline)
            justification: Reasoning for the decision
            key_findings: Important findings from analysis
            timestamp: When assessment was made
            metadata: Additional metadata (conversation_id, tools used, etc.)
        """
        self.id = id
        self.feature_id = feature_id
        self.decision = decision
        self.justification = justification
        self.key_findings = key_findings
        self.timestamp = timestamp
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert memory to dictionary for storage."""
        return {
            "id": self.id,
            "feature_id": self.feature_id,
            "decision": self.decision,
            "justification": self.justification,
            "key_findings": self.key_findings,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Memory":
        """Create memory from dictionary."""
        return cls(
            id=data["id"],
            feature_id=data["feature_id"],
            decision=data["decision"],
            justification=data["justification"],
            key_findings=data["key_findings"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


class MemoryStore(Protocol):
    """Protocol defining the interface for memory storage systems."""

    def store(self, memory: Memory) -> str:
        """Store a memory and return its ID.

        Args:
            memory: Memory to store

        Returns:
            Memory ID
        """
        ...

    def retrieve(
        self,
        query: str | None = None,
        feature_id: str | None = None,
        decision: str | None = None,
        limit: int = 5,
    ) -> list[Memory]:
        """Retrieve memories matching criteria.

        Args:
            query: Text query for semantic search (optional)
            feature_id: Filter by specific feature ID
            decision: Filter by decision type
            limit: Maximum number of memories to return

        Returns:
            List of matching memories, most recent first
        """
        ...

    def retrieve_by_id(self, memory_id: str) -> Memory | None:
        """Retrieve a specific memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory if found, None otherwise
        """
        ...

    def list_all(self, limit: int | None = None) -> list[Memory]:
        """List all memories.

        Args:
            limit: Maximum number to return (None for all)

        Returns:
            List of all memories, most recent first
        """
        ...

    def delete(self, memory_id: str) -> bool:
        """Delete a memory.

        Args:
            memory_id: Memory to delete

        Returns:
            True if deleted, False if not found
        """
        ...

    def clear_all(self) -> int:
        """Clear all memories.

        Returns:
            Number of memories deleted
        """
        ...
