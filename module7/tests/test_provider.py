"""Tests for provider implementations."""

from unittest.mock import Mock, patch

from providers.anthropic import AnthropicProvider


def test_anthropic_provider_init():
    """Test initializing Anthropic provider."""
    provider = AnthropicProvider("test-key", "claude-3-5-sonnet-20241022")
    assert provider.model == "claude-3-5-sonnet-20241022"


@patch("providers.anthropic.Anthropic")
def test_anthropic_provider_send_message(mock_anthropic):
    """Test sending a message through Anthropic provider."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="Hello there!")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    provider = AnthropicProvider("test-key", "claude-3-5-sonnet-20241022")
    messages = [{"role": "user", "content": "Hello"}]
    response = provider.send_message(messages, 1024)

    assert response == "Hello there!"
    mock_client.messages.create.assert_called_once_with(
        model="claude-3-5-sonnet-20241022", max_tokens=1024, messages=messages
    )


@patch("providers.anthropic.Anthropic")
def test_anthropic_provider_handles_multiple_messages(mock_anthropic):
    """Test provider handles conversation with multiple messages."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="Response")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    provider = AnthropicProvider("test-key", "claude-3-5-sonnet-20241022")
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"},
        {"role": "user", "content": "How are you?"},
    ]
    response = provider.send_message(messages, 2048)

    assert response == "Response"
    assert mock_client.messages.create.call_args[1]["messages"] == messages
