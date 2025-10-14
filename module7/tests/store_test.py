"""Tests for conversation persistence."""

import pytest

from detective_agent.models import Conversation
from detective_agent.persistence.store import ConversationStore


@pytest.fixture
def store(tmp_path):
    """Create a temporary store for testing."""
    return ConversationStore(tmp_path)


def test_create_conversation(store):
    """Test creating a new conversation."""
    conv = store.create_conversation()
    assert conv.id is not None
    assert len(conv.messages) == 0


def test_save_and_load_conversation(store):
    """Test saving and loading a conversation."""
    conv = store.create_conversation()
    conv.add_message("user", "Hello")
    conv.add_message("assistant", "Hi there")

    store.save(conv)
    loaded = store.load(conv.id)

    assert loaded.id == conv.id
    assert len(loaded.messages) == 2
    assert loaded.messages[0].content == "Hello"
    assert loaded.messages[1].content == "Hi there"


def test_load_nonexistent_conversation(store):
    """Test loading a conversation that doesn't exist."""
    with pytest.raises(FileNotFoundError):
        store.load("nonexistent-id")


def test_list_conversations(store):
    """Test listing all conversations."""
    conv1 = store.create_conversation()
    conv1.add_message("user", "First")
    store.save(conv1)

    conv2 = store.create_conversation()
    conv2.add_message("user", "Second")
    store.save(conv2)

    conversations = store.list_conversations()
    assert len(conversations) == 2
    assert all(isinstance(conv_id, str) for conv_id, _ in conversations)


def test_list_conversations_sorted_by_updated_at(store):
    """Test that conversations are sorted by most recent first."""
    conv1 = store.create_conversation()
    store.save(conv1)

    conv2 = store.create_conversation()
    conv2.add_message("user", "New message")
    store.save(conv2)

    conversations = store.list_conversations()
    assert conversations[0][0] == conv2.id
    assert conversations[1][0] == conv1.id
