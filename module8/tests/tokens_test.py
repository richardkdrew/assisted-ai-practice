"""Tests for token counting utilities."""

import pytest

from investigator_agent.context.tokens import (
    count_message_tokens,
    count_tokens,
    estimate_context_usage,
    should_create_subconversation,
)


def test_count_tokens_simple():
    """Test token counting for simple text."""
    text = "Hello, world!"
    tokens = count_tokens(text)

    # Should return a positive integer
    assert isinstance(tokens, int)
    assert tokens > 0
    # "Hello, world!" should be a few tokens (typically 3-4)
    assert tokens < 10


def test_count_tokens_empty():
    """Test token counting for empty string."""
    assert count_tokens("") == 0


def test_count_tokens_long_text():
    """Test token counting for longer text."""
    # Approximately 100 words
    text = " ".join(["word"] * 100)
    tokens = count_tokens(text)

    # Should be roughly 100-120 tokens
    assert 80 < tokens < 150


def test_count_tokens_unicode():
    """Test token counting with Unicode characters."""
    text = "Hello 世界 🌍"
    tokens = count_tokens(text)

    # Should handle Unicode correctly
    assert isinstance(tokens, int)
    assert tokens > 0


def test_count_message_tokens_simple():
    """Test counting tokens in simple messages."""
    messages = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there!"},
    ]

    tokens = count_message_tokens(messages)

    # Should include both messages + overhead
    assert isinstance(tokens, int)
    assert tokens > 0
    # Each message has ~4 token overhead + content
    assert tokens > 10


def test_count_message_tokens_empty():
    """Test counting tokens in empty message list."""
    assert count_message_tokens([]) == 0


def test_count_message_tokens_complex_content():
    """Test counting tokens in messages with complex content."""
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What is 2+2?"},
                {"type": "tool_use", "id": "1", "name": "calculator", "input": {"a": 2, "b": 2}},
            ],
        },
        {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "1", "content": "4"},
            ],
        },
        {"role": "assistant", "content": "The answer is 4."},
    ]

    tokens = count_message_tokens(messages)

    # Should count all content blocks
    assert isinstance(tokens, int)
    assert tokens > 20  # Should have significant token count


def test_count_message_tokens_tool_use():
    """Test counting tokens for tool use messages."""
    messages = [
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Let me check that."},
                {
                    "type": "tool_use",
                    "id": "tool_1",
                    "name": "get_jira_data",
                    "input": {},
                },
            ],
        }
    ]

    tokens = count_message_tokens(messages)
    assert tokens > 0


def test_should_create_subconversation_below_threshold():
    """Test sub-conversation check below threshold."""
    # Default threshold is 10000
    assert should_create_subconversation(5000) is False
    assert should_create_subconversation(9999) is False


def test_should_create_subconversation_above_threshold():
    """Test sub-conversation check above threshold."""
    assert should_create_subconversation(10000) is True
    assert should_create_subconversation(15000) is True
    assert should_create_subconversation(50000) is True


def test_should_create_subconversation_custom_threshold():
    """Test sub-conversation check with custom threshold."""
    assert should_create_subconversation(5000, threshold=3000) is True
    assert should_create_subconversation(5000, threshold=10000) is False


def test_estimate_context_usage_low():
    """Test context usage estimation at low usage."""
    usage = estimate_context_usage(current_tokens=10000, max_tokens=150000)

    assert usage["current_tokens"] == 10000
    assert usage["max_tokens"] == 150000
    assert usage["usage_percent"] == pytest.approx(6.67, rel=0.1)
    assert usage["remaining_tokens"] == 140000
    assert usage["is_near_limit"] is False


def test_estimate_context_usage_high():
    """Test context usage estimation at high usage (>80%)."""
    usage = estimate_context_usage(current_tokens=130000, max_tokens=150000)

    assert usage["current_tokens"] == 130000
    assert usage["max_tokens"] == 150000
    assert usage["usage_percent"] == pytest.approx(86.67, rel=0.1)
    assert usage["remaining_tokens"] == 20000
    assert usage["is_near_limit"] is True


def test_estimate_context_usage_at_threshold():
    """Test context usage estimation exactly at 80% threshold."""
    usage = estimate_context_usage(current_tokens=120000, max_tokens=150000)

    assert usage["usage_percent"] == 80.0
    assert usage["is_near_limit"] is False  # Not > 80%


def test_estimate_context_usage_custom_max():
    """Test context usage with custom max tokens."""
    usage = estimate_context_usage(current_tokens=50000, max_tokens=200000)

    assert usage["current_tokens"] == 50000
    assert usage["max_tokens"] == 200000
    assert usage["usage_percent"] == 25.0
    assert usage["remaining_tokens"] == 150000
    assert usage["is_near_limit"] is False


def test_count_tokens_realistic_doc():
    """Test token counting on realistic documentation size."""
    # Simulate a large documentation file
    doc_text = "This is documentation content. " * 500  # ~5 tokens * 500 = 2500 tokens
    tokens = count_tokens(doc_text)

    # Should be roughly 2000-3000 tokens for this test
    assert 2000 < tokens < 3500
