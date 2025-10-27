"""Integration test for end-to-end conversation flow."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from investigator_agent.agent import Agent
from investigator_agent.config import Config
from investigator_agent.persistence.store import ConversationStore
from investigator_agent.providers.anthropic import AnthropicProvider


@pytest.fixture
def integration_setup(tmp_path, monkeypatch):
    """Set up components for integration testing."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    config = Config.from_env()
    config.conversations_dir = tmp_path
    store = ConversationStore(config.conversations_dir)
    return config, store


@pytest.mark.asyncio
@patch("investigator_agent.providers.anthropic.AsyncAnthropic")
async def test_full_conversation_flow(mock_anthropic, integration_setup):
    """Test a complete conversation flow from start to finish."""
    config, store = integration_setup

    mock_client = Mock()
    mock_responses = [
        Mock(
            content=[Mock(type="text", text="Hello! How can I help you?")],
            usage=Mock(input_tokens=10, output_tokens=20),
            stop_reason="end_turn",
        ),
        Mock(
            content=[Mock(type="text", text="Python is a programming language.")],
            usage=Mock(input_tokens=15, output_tokens=25),
            stop_reason="end_turn",
        ),
    ]
    mock_client.messages.create = AsyncMock(side_effect=mock_responses)
    mock_anthropic.return_value = mock_client

    provider = AnthropicProvider(config.api_key, config.model)
    agent = Agent(provider, store, config)

    conversation = agent.new_conversation()
    assert conversation.id is not None

    response1 = await agent.send_message(conversation, "Hello")
    assert response1 == "Hello! How can I help you?"
    assert len(conversation.messages) == 2

    response2 = await agent.send_message(conversation, "What is Python?")
    assert response2 == "Python is a programming language."
    assert len(conversation.messages) == 4

    loaded_conversation = agent.load_conversation(conversation.id)
    assert len(loaded_conversation.messages) == 4
    assert loaded_conversation.messages[0].content == "Hello"
    assert loaded_conversation.messages[1].content == "Hello! How can I help you?"
    assert loaded_conversation.messages[2].content == "What is Python?"
    assert loaded_conversation.messages[3].content == "Python is a programming language."


@pytest.mark.asyncio
@patch("investigator_agent.providers.anthropic.AsyncAnthropic")
async def test_multiple_conversations(mock_anthropic, integration_setup):
    """Test managing multiple conversations."""
    config, store = integration_setup

    mock_client = Mock()
    mock_response = Mock(
        content=[Mock(type="text", text="Response")],
        usage=Mock(input_tokens=10, output_tokens=20),
        stop_reason="end_turn",
    )
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    mock_anthropic.return_value = mock_client

    provider = AnthropicProvider(config.api_key, config.model)
    agent = Agent(provider, store, config)

    conv1 = agent.new_conversation()
    await agent.send_message(conv1, "Message 1")

    conv2 = agent.new_conversation()
    await agent.send_message(conv2, "Message 2")

    conversations = agent.list_conversations()
    assert len(conversations) == 2

    loaded_conv1 = agent.load_conversation(conv1.id)
    assert loaded_conv1.messages[0].content == "Message 1"

    loaded_conv2 = agent.load_conversation(conv2.id)
    assert loaded_conv2.messages[0].content == "Message 2"
