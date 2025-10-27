"""File-based memory store implementation.

Stores memories as JSON files in a memory directory.
Simple but effective for learning and small-scale use.
"""

import json
from pathlib import Path

from investigator_agent.memory.protocol import Memory


class FileMemoryStore:
    """File-based implementation of memory storage."""

    def __init__(self, memory_dir: Path):
        """Initialize file-based memory store.

        Args:
            memory_dir: Directory to store memory files
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.memory_dir / "index.json"

        # Load or create index
        self._load_index()

    def _load_index(self) -> None:
        """Load memory index from file."""
        if self.index_file.exists():
            with open(self.index_file) as f:
                self.index = json.load(f)
        else:
            self.index = {"memories": []}
            self._save_index()

    def _save_index(self) -> None:
        """Save memory index to file."""
        with open(self.index_file, "w") as f:
            json.dump(self.index, f, indent=2)

    def _get_memory_file(self, memory_id: str) -> Path:
        """Get path to memory file.

        Args:
            memory_id: Memory identifier

        Returns:
            Path to memory JSON file
        """
        return self.memory_dir / f"{memory_id}.json"

    def store(self, memory: Memory) -> str:
        """Store a memory and return its ID.

        Args:
            memory: Memory to store

        Returns:
            Memory ID
        """
        # Save memory to individual file
        memory_file = self._get_memory_file(memory.id)
        with open(memory_file, "w") as f:
            json.dump(memory.to_dict(), f, indent=2)

        # Add to index if not already present
        memory_ids = [m["id"] for m in self.index["memories"]]
        if memory.id not in memory_ids:
            self.index["memories"].append(
                {
                    "id": memory.id,
                    "feature_id": memory.feature_id,
                    "decision": memory.decision,
                    "timestamp": memory.timestamp.isoformat(),
                }
            )
            # Sort by timestamp (most recent first)
            self.index["memories"].sort(key=lambda x: x["timestamp"], reverse=True)
            self._save_index()

        return memory.id

    def retrieve(
        self,
        query: str | None = None,
        feature_id: str | None = None,
        decision: str | None = None,
        limit: int = 5,
    ) -> list[Memory]:
        """Retrieve memories matching criteria.

        Args:
            query: Text query (simple substring match in file-based impl)
            feature_id: Filter by specific feature ID
            decision: Filter by decision type
            limit: Maximum number of memories to return

        Returns:
            List of matching memories, most recent first
        """
        matching_memories = []

        for memory_meta in self.index["memories"]:
            # Apply filters
            if feature_id and memory_meta["feature_id"] != feature_id:
                continue
            if decision and memory_meta["decision"] != decision:
                continue

            # Load full memory
            memory = self.retrieve_by_id(memory_meta["id"])
            if not memory:
                continue

            # Apply query filter (simple substring match)
            if query:
                searchable = f"{memory.feature_id} {memory.justification} {str(memory.key_findings)}"
                if query.lower() not in searchable.lower():
                    continue

            matching_memories.append(memory)

            # Check limit
            if len(matching_memories) >= limit:
                break

        return matching_memories

    def retrieve_by_id(self, memory_id: str) -> Memory | None:
        """Retrieve a specific memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory if found, None otherwise
        """
        memory_file = self._get_memory_file(memory_id)
        if not memory_file.exists():
            return None

        with open(memory_file) as f:
            data = json.load(f)
            return Memory.from_dict(data)

    def list_all(self, limit: int | None = None) -> list[Memory]:
        """List all memories.

        Args:
            limit: Maximum number to return (None for all)

        Returns:
            List of all memories, most recent first
        """
        memories = []
        count = 0

        for memory_meta in self.index["memories"]:
            memory = self.retrieve_by_id(memory_meta["id"])
            if memory:
                memories.append(memory)
                count += 1

                if limit and count >= limit:
                    break

        return memories

    def delete(self, memory_id: str) -> bool:
        """Delete a memory.

        Args:
            memory_id: Memory to delete

        Returns:
            True if deleted, False if not found
        """
        memory_file = self._get_memory_file(memory_id)
        if not memory_file.exists():
            return False

        # Remove file
        memory_file.unlink()

        # Remove from index
        self.index["memories"] = [m for m in self.index["memories"] if m["id"] != memory_id]
        self._save_index()

        return True

    def clear_all(self) -> int:
        """Clear all memories.

        Returns:
            Number of memories deleted
        """
        count = len(self.index["memories"])

        # Delete all memory files
        for memory_meta in self.index["memories"]:
            memory_file = self._get_memory_file(memory_meta["id"])
            if memory_file.exists():
                memory_file.unlink()

        # Clear index
        self.index["memories"] = []
        self._save_index()

        return count
