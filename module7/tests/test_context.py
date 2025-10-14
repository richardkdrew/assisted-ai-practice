"""Tests for context window management."""

import pytest

from context.manager import ContextManager
from models.message import Message


@pytest.fixture
def context_manager():
    """Create a context manager with default settings."""
    return ContextManager(max_messages=6)


def test_context_manager_no_truncation_needed(context_manager):
    """Test that messages under limit are not truncated."""
    messages = [
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi there"),
        Message(role="user", content="How are you?"),
    ]

    truncated, was_truncated = context_manager.truncate_messages(messages)

    assert not was_truncated
    assert len(truncated) == 3
    assert truncated == messages


def test_context_manager_truncates_old_messages(context_manager):
    """Test that old messages are dropped when exceeding limit."""
    messages = [
        Message(role="user", content="Message 1"),
        Message(role="assistant", content="Response 1"),
        Message(role="user", content="Message 2"),
        Message(role="assistant", content="Response 2"),
        Message(role="user", content="Message 3"),
        Message(role="assistant", content="Response 3"),
        Message(role="user", content="Message 4"),
        Message(role="assistant", content="Response 4"),
    ]

    truncated, was_truncated = context_manager.truncate_messages(messages)

    assert was_truncated
    assert len(truncated) == 6
    # Should keep the last 6 messages (8 total - 2 dropped = starting from index 2)
    assert truncated[0].content == "Message 2"
    assert truncated[1].content == "Response 2"
    assert truncated[-1].content == "Response 4"


def test_context_manager_exactly_at_limit(context_manager):
    """Test behavior when exactly at the message limit."""
    messages = [
        Message(role="user", content=f"Message {i}")
        for i in range(6)
    ]

    truncated, was_truncated = context_manager.truncate_messages(messages)

    assert not was_truncated
    assert len(truncated) == 6


def test_context_manager_custom_max_messages():
    """Test context manager with custom max messages."""
    manager = ContextManager(max_messages=4)
    messages = [
        Message(role="user", content=f"Message {i}")
        for i in range(8)
    ]

    truncated, was_truncated = manager.truncate_messages(messages)

    assert was_truncated
    assert len(truncated) == 4
    assert truncated[0].content == "Message 4"
    assert truncated[-1].content == "Message 7"


def test_context_manager_preserves_order(context_manager):
    """Test that message order is preserved after truncation."""
    messages = [
        Message(role="user", content="Old 1"),
        Message(role="assistant", content="Old Response 1"),
        Message(role="user", content="Keep 1"),
        Message(role="assistant", content="Keep Response 1"),
        Message(role="user", content="Keep 2"),
        Message(role="assistant", content="Keep Response 2"),
        Message(role="user", content="Keep 3"),
        Message(role="assistant", content="Keep Response 3"),
    ]

    truncated, was_truncated = context_manager.truncate_messages(messages)

    assert was_truncated
    assert len(truncated) == 6
    # Verify order
    assert truncated[0].content == "Keep 1"
    assert truncated[1].content == "Keep Response 1"
    assert truncated[2].content == "Keep 2"


def test_get_context_info_under_limit(context_manager):
    """Test context info when under limit."""
    messages = [
        Message(role="user", content="Test 1"),
        Message(role="assistant", content="Response 1"),
    ]

    info = context_manager.get_context_info(messages)

    assert info["total_messages"] == 2
    assert info["max_messages"] == 6
    assert not info["would_truncate"]
    assert info["messages_to_drop"] == 0


def test_get_context_info_over_limit(context_manager):
    """Test context info when over limit."""
    messages = [Message(role="user", content=f"Msg {i}") for i in range(10)]

    info = context_manager.get_context_info(messages)

    assert info["total_messages"] == 10
    assert info["max_messages"] == 6
    assert info["would_truncate"]
    assert info["messages_to_drop"] == 4


def test_empty_messages_list(context_manager):
    """Test handling of empty messages list."""
    messages = []

    truncated, was_truncated = context_manager.truncate_messages(messages)

    assert not was_truncated
    assert len(truncated) == 0


def test_single_message(context_manager):
    """Test handling of single message."""
    messages = [Message(role="user", content="Single message")]

    truncated, was_truncated = context_manager.truncate_messages(messages)

    assert not was_truncated
    assert len(truncated) == 1
