"""Tests for file-based memory store."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from investigator_agent.memory import FileMemoryStore, Memory


@pytest.fixture
def temp_memory_dir():
    """Create a temporary directory for memory storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def memory_store(temp_memory_dir):
    """Create a FileMemoryStore instance."""
    return FileMemoryStore(temp_memory_dir)


@pytest.fixture
def sample_memory():
    """Create a sample memory for testing."""
    return Memory(
        id="mem_001",
        feature_id="FEAT-MS-001",
        decision="ready",
        justification="All tests passing, UAT approved, security review complete",
        key_findings={
            "test_coverage": 95,
            "uat_pass_rate": 100,
            "security_issues": 0,
        },
        timestamp=datetime(2025, 10, 15, 10, 30, 0),
        metadata={"conversation_id": "conv_123", "tools_used": ["get_jira_data", "get_analysis"]},
    )


def test_store_memory(memory_store, sample_memory):
    """Test storing a memory."""
    memory_id = memory_store.store(sample_memory)

    assert memory_id == "mem_001"
    # Verify file was created
    memory_file = memory_store.memory_dir / "mem_001.json"
    assert memory_file.exists()


def test_retrieve_by_id(memory_store, sample_memory):
    """Test retrieving a memory by ID."""
    memory_store.store(sample_memory)

    retrieved = memory_store.retrieve_by_id("mem_001")

    assert retrieved is not None
    assert retrieved.id == "mem_001"
    assert retrieved.feature_id == "FEAT-MS-001"
    assert retrieved.decision == "ready"
    assert retrieved.justification == sample_memory.justification
    assert retrieved.key_findings == sample_memory.key_findings


def test_retrieve_by_id_not_found(memory_store):
    """Test retrieving a non-existent memory."""
    retrieved = memory_store.retrieve_by_id("nonexistent")
    assert retrieved is None


def test_retrieve_by_feature_id(memory_store):
    """Test retrieving memories by feature ID."""
    # Store multiple memories
    mem1 = Memory(
        id="mem_001",
        feature_id="FEAT-MS-001",
        decision="ready",
        justification="Ready for production",
        key_findings={},
        timestamp=datetime(2025, 10, 15, 10, 30, 0),
    )
    mem2 = Memory(
        id="mem_002",
        feature_id="FEAT-MS-001",
        decision="not_ready",
        justification="Not ready yet",
        key_findings={},
        timestamp=datetime(2025, 10, 14, 10, 30, 0),
    )
    mem3 = Memory(
        id="mem_003",
        feature_id="FEAT-QR-002",
        decision="borderline",
        justification="Borderline case",
        key_findings={},
        timestamp=datetime(2025, 10, 13, 10, 30, 0),
    )

    memory_store.store(mem1)
    memory_store.store(mem2)
    memory_store.store(mem3)

    # Retrieve by feature ID
    results = memory_store.retrieve(feature_id="FEAT-MS-001")

    assert len(results) == 2
    assert all(m.feature_id == "FEAT-MS-001" for m in results)
    # Should be in reverse chronological order
    assert results[0].id == "mem_001"
    assert results[1].id == "mem_002"


def test_retrieve_by_decision(memory_store):
    """Test retrieving memories by decision type."""
    mem1 = Memory(
        id="mem_001",
        feature_id="FEAT-MS-001",
        decision="ready",
        justification="Ready",
        key_findings={},
        timestamp=datetime(2025, 10, 15, 10, 30, 0),
    )
    mem2 = Memory(
        id="mem_002",
        feature_id="FEAT-QR-002",
        decision="not_ready",
        justification="Not ready",
        key_findings={},
        timestamp=datetime(2025, 10, 14, 10, 30, 0),
    )

    memory_store.store(mem1)
    memory_store.store(mem2)

    # Retrieve by decision
    results = memory_store.retrieve(decision="ready")

    assert len(results) == 1
    assert results[0].decision == "ready"


def test_retrieve_with_query(memory_store):
    """Test retrieving memories with text query."""
    mem1 = Memory(
        id="mem_001",
        feature_id="FEAT-MS-001",
        decision="ready",
        justification="All security tests passed with flying colors",
        key_findings={"security_scan": "clean"},
        timestamp=datetime(2025, 10, 15, 10, 30, 0),
    )
    mem2 = Memory(
        id="mem_002",
        feature_id="FEAT-QR-002",
        decision="not_ready",
        justification="Performance issues detected",
        key_findings={},
        timestamp=datetime(2025, 10, 14, 10, 30, 0),
    )

    memory_store.store(mem1)
    memory_store.store(mem2)

    # Query for security-related memories
    results = memory_store.retrieve(query="security")

    assert len(results) == 1
    assert results[0].id == "mem_001"


def test_retrieve_with_limit(memory_store):
    """Test limiting number of retrieved memories."""
    # Store 5 memories
    for i in range(5):
        mem = Memory(
            id=f"mem_{i:03d}",
            feature_id="FEAT-TEST",
            decision="ready",
            justification=f"Memory {i}",
            key_findings={},
            timestamp=datetime(2025, 10, i + 1, 10, 30, 0),
        )
        memory_store.store(mem)

    # Retrieve with limit
    results = memory_store.retrieve(limit=3)

    assert len(results) == 3


def test_list_all(memory_store):
    """Test listing all memories."""
    # Store 3 memories
    for i in range(3):
        mem = Memory(
            id=f"mem_{i:03d}",
            feature_id="FEAT-TEST",
            decision="ready",
            justification=f"Memory {i}",
            key_findings={},
            timestamp=datetime(2025, 10, i + 1, 10, 30, 0),
        )
        memory_store.store(mem)

    # List all
    results = memory_store.list_all()

    assert len(results) == 3
    # Should be in reverse chronological order
    assert results[0].id == "mem_002"
    assert results[1].id == "mem_001"
    assert results[2].id == "mem_000"


def test_list_all_with_limit(memory_store):
    """Test listing all memories with limit."""
    # Store 5 memories
    for i in range(5):
        mem = Memory(
            id=f"mem_{i:03d}",
            feature_id="FEAT-TEST",
            decision="ready",
            justification=f"Memory {i}",
            key_findings={},
            timestamp=datetime(2025, 10, i + 1, 10, 30, 0),
        )
        memory_store.store(mem)

    # List with limit
    results = memory_store.list_all(limit=2)

    assert len(results) == 2


def test_delete_memory(memory_store, sample_memory):
    """Test deleting a memory."""
    memory_store.store(sample_memory)

    # Verify it exists
    assert memory_store.retrieve_by_id("mem_001") is not None

    # Delete it
    deleted = memory_store.delete("mem_001")

    assert deleted is True
    assert memory_store.retrieve_by_id("mem_001") is None
    # Verify file was deleted
    memory_file = memory_store.memory_dir / "mem_001.json"
    assert not memory_file.exists()


def test_delete_nonexistent(memory_store):
    """Test deleting a non-existent memory."""
    deleted = memory_store.delete("nonexistent")
    assert deleted is False


def test_clear_all(memory_store):
    """Test clearing all memories."""
    # Store 3 memories
    for i in range(3):
        mem = Memory(
            id=f"mem_{i:03d}",
            feature_id="FEAT-TEST",
            decision="ready",
            justification=f"Memory {i}",
            key_findings={},
            timestamp=datetime(2025, 10, i + 1, 10, 30, 0),
        )
        memory_store.store(mem)

    # Clear all
    count = memory_store.clear_all()

    assert count == 3
    assert len(memory_store.list_all()) == 0


def test_memory_persistence(temp_memory_dir, sample_memory):
    """Test that memories persist across store instances."""
    # Create store and save memory
    store1 = FileMemoryStore(temp_memory_dir)
    store1.store(sample_memory)

    # Create new store instance and retrieve
    store2 = FileMemoryStore(temp_memory_dir)
    retrieved = store2.retrieve_by_id("mem_001")

    assert retrieved is not None
    assert retrieved.id == sample_memory.id
    assert retrieved.feature_id == sample_memory.feature_id


def test_memory_to_dict():
    """Test converting memory to dictionary."""
    memory = Memory(
        id="mem_001",
        feature_id="FEAT-MS-001",
        decision="ready",
        justification="Ready for production",
        key_findings={"test": "value"},
        timestamp=datetime(2025, 10, 15, 10, 30, 0),
        metadata={"key": "value"},
    )

    data = memory.to_dict()

    assert data["id"] == "mem_001"
    assert data["feature_id"] == "FEAT-MS-001"
    assert data["decision"] == "ready"
    assert data["timestamp"] == "2025-10-15T10:30:00"
    assert data["metadata"] == {"key": "value"}


def test_memory_from_dict():
    """Test creating memory from dictionary."""
    data = {
        "id": "mem_001",
        "feature_id": "FEAT-MS-001",
        "decision": "ready",
        "justification": "Ready for production",
        "key_findings": {"test": "value"},
        "timestamp": "2025-10-15T10:30:00",
        "metadata": {"key": "value"},
    }

    memory = Memory.from_dict(data)

    assert memory.id == "mem_001"
    assert memory.feature_id == "FEAT-MS-001"
    assert memory.timestamp == datetime(2025, 10, 15, 10, 30, 0)
    assert memory.metadata == {"key": "value"}
