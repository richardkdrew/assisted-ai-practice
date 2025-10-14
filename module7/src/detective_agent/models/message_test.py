"""Tests for message data models."""

from datetime import datetime

from detective_agent.models.message import Conversation, Message


def test_message_creation():
    """Test creating a message."""
    msg = Message(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert isinstance(msg.timestamp, datetime)


def test_message_to_dict():
    """Test converting message to dict for API."""
    msg = Message(role="assistant", content="Hi there")
    data = msg.to_dict()
    assert data == {"role": "assistant", "content": "Hi there"}


def test_conversation_add_message():
    """Test adding messages to a conversation."""
    conv = Conversation(id="test-123")
    assert len(conv.messages) == 0

    conv.add_message("user", "Hello")
    assert len(conv.messages) == 1
    assert conv.messages[0].role == "user"
    assert conv.messages[0].content == "Hello"

    conv.add_message("assistant", "Hi")
    assert len(conv.messages) == 2
    assert conv.messages[1].role == "assistant"


def test_conversation_to_api_format():
    """Test converting conversation to API format."""
    conv = Conversation(id="test-123")
    conv.add_message("user", "Hello")
    conv.add_message("assistant", "Hi there")

    api_format = conv.to_api_format()
    assert len(api_format) == 2
    assert api_format[0] == {"role": "user", "content": "Hello"}
    assert api_format[1] == {"role": "assistant", "content": "Hi there"}


def test_conversation_updates_timestamp():
    """Test that adding messages updates the conversation timestamp."""
    conv = Conversation(id="test-123")
    original_time = conv.updated_at
    conv.add_message("user", "Test")
    assert conv.updated_at > original_time
