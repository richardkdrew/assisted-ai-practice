"""Tests for provider implementations."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from investigator_agent.providers.anthropic import AnthropicProvider


def test_anthropic_provider_init():
    """Test initializing Anthropic provider."""
    provider = AnthropicProvider("test-key", "claude-3-5-sonnet-20241022")
    assert provider.model == "claude-3-5-sonnet-20241022"


@pytest.mark.asyncio
@patch("investigator_agent.providers.anthropic.AsyncAnthropic")
async def test_anthropic_provider_send_message(mock_anthropic):
    """Test sending a message through Anthropic provider."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(type="text", text="Hello there!")]
    mock_response.usage = Mock(input_tokens=10, output_tokens=20)
    mock_response.stop_reason = "end_turn"
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    mock_anthropic.return_value = mock_client

    provider = AnthropicProvider("test-key", "claude-3-5-sonnet-20241022")
    messages = [{"role": "user", "content": "Hello"}]
    response = await provider.send_message(messages, 1024)

    # Provider now returns the full response object
    assert response == mock_response
    # Test text extraction separately
    assert provider.get_text_content(response) == "Hello there!"
    mock_client.messages.create.assert_called_once_with(
        model="claude-3-5-sonnet-20241022", max_tokens=1024, messages=messages
    )


@pytest.mark.asyncio
@patch("investigator_agent.providers.anthropic.AsyncAnthropic")
async def test_anthropic_provider_handles_multiple_messages(mock_anthropic):
    """Test provider handles conversation with multiple messages."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(type="text", text="Response")]
    mock_response.usage = Mock(input_tokens=30, output_tokens=15)
    mock_response.stop_reason = "end_turn"
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    mock_anthropic.return_value = mock_client

    provider = AnthropicProvider("test-key", "claude-3-5-sonnet-20241022")
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"},
        {"role": "user", "content": "How are you?"},
    ]
    response = await provider.send_message(messages, 2048)

    assert response == mock_response
    assert provider.get_text_content(response) == "Response"
    assert mock_client.messages.create.call_args[1]["messages"] == messages


@pytest.mark.asyncio
@patch("investigator_agent.providers.anthropic.AsyncAnthropic")
async def test_anthropic_provider_extract_tool_calls(mock_anthropic):
    """Test extracting tool calls from response."""
    mock_client = Mock()

    # Create mock blocks properly
    text_block = Mock()
    text_block.type = "text"
    text_block.text = "Let me check that for you."

    tool_block = Mock()
    tool_block.type = "tool_use"
    tool_block.id = "tool_123"
    tool_block.name = "get_weather"
    tool_block.input = {"city": "SF"}

    mock_response = Mock()
    mock_response.content = [text_block, tool_block]
    mock_response.usage = Mock(input_tokens=10, output_tokens=20)
    mock_response.stop_reason = "tool_use"
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    mock_anthropic.return_value = mock_client

    provider = AnthropicProvider("test-key", "claude-3-5-sonnet-20241022")
    messages = [{"role": "user", "content": "What's the weather in SF?"}]
    response = await provider.send_message(messages, 1024)

    # Extract tool calls
    tool_calls = provider.extract_tool_calls(response)
    assert len(tool_calls) == 1
    assert tool_calls[0].id == "tool_123"
    assert tool_calls[0].name == "get_weather"
    assert tool_calls[0].input == {"city": "SF"}


@pytest.mark.asyncio
@patch("investigator_agent.providers.anthropic.AsyncAnthropic")
async def test_anthropic_provider_get_text_content_with_tools(mock_anthropic):
    """Test extracting text content from response with tool calls."""
    mock_client = Mock()

    # Create mock blocks properly
    text_block = Mock()
    text_block.type = "text"
    text_block.text = "Let me check that for you."

    tool_block = Mock()
    tool_block.type = "tool_use"
    tool_block.id = "tool_123"
    tool_block.name = "get_weather"
    tool_block.input = {"city": "SF"}

    mock_response = Mock()
    mock_response.content = [text_block, tool_block]
    mock_response.usage = Mock(input_tokens=10, output_tokens=20)
    mock_response.stop_reason = "tool_use"
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    mock_anthropic.return_value = mock_client

    provider = AnthropicProvider("test-key", "claude-3-5-sonnet-20241022")
    messages = [{"role": "user", "content": "What's the weather?"}]
    response = await provider.send_message(messages, 1024)

    # Get text content should only extract text blocks
    text = provider.get_text_content(response)
    assert text == "Let me check that for you."


@pytest.mark.asyncio
@patch("investigator_agent.providers.anthropic.AsyncAnthropic")
async def test_anthropic_provider_with_tools_parameter(mock_anthropic):
    """Test sending message with tools parameter."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(type="text", text="I'll use that tool.")]
    mock_response.usage = Mock(input_tokens=10, output_tokens=20)
    mock_response.stop_reason = "end_turn"
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    mock_anthropic.return_value = mock_client

    provider = AnthropicProvider("test-key", "claude-3-5-sonnet-20241022")
    messages = [{"role": "user", "content": "Hello"}]
    tools = [
        {
            "name": "get_weather",
            "description": "Get weather for a city",
            "input_schema": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
            },
        }
    ]
    response = await provider.send_message(messages, 1024, tools=tools)

    assert response == mock_response
    # Verify tools were passed to API
    call_kwargs = mock_client.messages.create.call_args[1]
    assert call_kwargs["tools"] == tools
