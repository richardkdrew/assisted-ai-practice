"""Tests for agent core logic."""

from unittest.mock import AsyncMock, Mock

import pytest

from detective_agent.agent import Agent
from detective_agent.config import Config
from detective_agent.models import Conversation
from detective_agent.persistence.store import ConversationStore


@pytest.fixture
def mock_provider():
    """Create a mock provider."""
    provider = Mock()
    # Mock response object
    mock_response = Mock()
    provider.send_message = AsyncMock(return_value=mock_response)
    provider.get_text_content = Mock(return_value="Mock response")
    provider.extract_tool_calls = Mock(return_value=[])
    return provider


@pytest.fixture
def store(tmp_path):
    """Create a temporary store."""
    return ConversationStore(tmp_path)


@pytest.fixture
def config():
    """Create a test config."""
    return Config(api_key="test-key", max_tokens=1024)


@pytest.fixture
def agent(mock_provider, store, config):
    """Create an agent for testing."""
    return Agent(mock_provider, store, config)


def test_new_conversation(agent):
    """Test creating a new conversation."""
    conv = agent.new_conversation()
    assert conv.id is not None
    assert len(conv.messages) == 0


@pytest.mark.asyncio
async def test_send_message(agent, mock_provider):
    """Test sending a message through the agent."""
    conv = agent.new_conversation()
    response = await agent.send_message(conv, "Hello")

    assert response == "Mock response"
    assert len(conv.messages) == 2
    assert conv.messages[0].role == "user"
    assert conv.messages[0].content == "Hello"
    assert conv.messages[1].role == "assistant"
    assert conv.messages[1].content == "Mock response"


@pytest.mark.asyncio
async def test_send_message_saves_conversation(agent, store):
    """Test that sending a message saves the conversation."""
    conv = agent.new_conversation()
    await agent.send_message(conv, "Test message")

    loaded = store.load(conv.id)
    assert len(loaded.messages) == 2


def test_load_conversation(agent, store):
    """Test loading an existing conversation."""
    conv = store.create_conversation()
    conv.add_message("user", "Previous message")
    store.save(conv)

    loaded = agent.load_conversation(conv.id)
    assert loaded.id == conv.id
    assert len(loaded.messages) == 1


def test_list_conversations(agent, store):
    """Test listing conversations."""
    conv1 = agent.new_conversation()
    conv2 = agent.new_conversation()

    conversations = agent.list_conversations()
    assert len(conversations) == 2
    assert all(isinstance(conv_id, str) for conv_id, _ in conversations)
    assert all(isinstance(timestamp, str) for _, timestamp in conversations)


@pytest.mark.asyncio
async def test_send_message_with_tool_calls(mock_provider, store, config):
    """Test sending a message that triggers tool calls."""
    from detective_agent.models import ToolCall
    from detective_agent.tools.registry import ToolRegistry

    # Setup tool registry
    registry = ToolRegistry()

    # Register a simple test tool
    async def test_tool(arg: str) -> dict:
        return {"result": f"processed: {arg}"}

    registry.register(
        name="test_tool",
        description="A test tool",
        input_schema={"type": "object", "properties": {"arg": {"type": "string"}}},
        handler=test_tool,
    )

    # Mock responses: first with tool call, second with final text
    tool_use_block = Mock()
    tool_use_block.type = "tool_use"
    tool_use_block.id = "tool_123"
    tool_use_block.name = "test_tool"
    tool_use_block.input = {"arg": "test"}

    text_block_1 = Mock()
    text_block_1.type = "text"
    text_block_1.text = "Let me use the tool."

    text_block_2 = Mock()
    text_block_2.type = "text"
    text_block_2.text = "Done!"

    mock_response_1 = Mock()
    mock_response_1.content = [text_block_1, tool_use_block]

    mock_response_2 = Mock()
    mock_response_2.content = [text_block_2]

    mock_provider.send_message = AsyncMock(side_effect=[mock_response_1, mock_response_2])
    mock_provider.extract_tool_calls = Mock(
        side_effect=[
            [ToolCall(id="tool_123", name="test_tool", input={"arg": "test"})],
            [],
        ]
    )
    mock_provider.get_text_content = Mock(return_value="Done!")
    mock_provider.get_tool_definitions = Mock(
        return_value=[
            {
                "name": "test_tool",
                "description": "A test tool",
                "input_schema": {"type": "object", "properties": {"arg": {"type": "string"}}},
            }
        ]
    )

    agent = Agent(mock_provider, store, config, tool_registry=registry)
    conv = agent.new_conversation()
    response = await agent.send_message(conv, "Use the test tool")

    # Should have final text response
    assert response == "Done!"

    # Verify tool was called with correct parameters
    assert mock_provider.send_message.call_count == 2
