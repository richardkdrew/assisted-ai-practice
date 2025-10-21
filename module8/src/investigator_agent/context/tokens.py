"""Token counting utilities for context management.

Uses tiktoken with cl100k_base encoding to estimate Claude token usage.
Provides ~90% accuracy for Claude models according to Anthropic documentation.
"""

import tiktoken

# Use cl100k_base encoding for Claude token estimation (~90% accurate)
_ENCODER = tiktoken.get_encoding("cl100k_base")

# Token thresholds for triggering sub-conversations
DEFAULT_TOOL_RESULT_THRESHOLD = 10000  # ~10K tokens triggers sub-conversation
DEFAULT_MAX_CONTEXT_TOKENS = 150000  # Conservative limit for Claude models


def count_tokens(text: str) -> int:
    """Count tokens in a text string.

    Uses tiktoken with cl100k_base encoding to estimate Claude token count.
    Provides approximately 90% accuracy compared to actual Claude token usage.

    Args:
        text: The text to count tokens for

    Returns:
        Estimated token count
    """
    return len(_ENCODER.encode(text))


def count_message_tokens(messages: list[dict]) -> int:
    """Count tokens in a list of messages.

    Args:
        messages: List of message dictionaries in API format

    Returns:
        Estimated total token count for all messages
    """
    total = 0

    for message in messages:
        # Count tokens in role
        total += count_tokens(message.get("role", ""))

        # Count tokens in content
        content = message.get("content", "")
        if isinstance(content, str):
            total += count_tokens(content)
        elif isinstance(content, list):
            # Handle complex content with multiple blocks
            for block in content:
                if isinstance(block, dict):
                    # Text blocks
                    if block.get("type") == "text":
                        total += count_tokens(block.get("text", ""))
                    # Tool use blocks (name + input)
                    elif block.get("type") == "tool_use":
                        total += count_tokens(block.get("name", ""))
                        total += count_tokens(str(block.get("input", {})))
                    # Tool result blocks
                    elif block.get("type") == "tool_result":
                        total += count_tokens(str(block.get("content", "")))

        # Add overhead for message formatting (~4 tokens per message)
        total += 4

    return total


def should_create_subconversation(
    tool_result_size: int, threshold: int = DEFAULT_TOOL_RESULT_THRESHOLD
) -> bool:
    """Determine if a tool result should trigger a sub-conversation.

    Args:
        tool_result_size: Token count of the tool result
        threshold: Token threshold for creating sub-conversation (default: 10K)

    Returns:
        True if sub-conversation should be created
    """
    return tool_result_size >= threshold


def estimate_context_usage(
    current_tokens: int, max_tokens: int = DEFAULT_MAX_CONTEXT_TOKENS
) -> dict:
    """Estimate current context window usage.

    Args:
        current_tokens: Current token count in conversation
        max_tokens: Maximum context window size (default: 150K)

    Returns:
        Dictionary with usage statistics
    """
    usage_percent = (current_tokens / max_tokens) * 100

    return {
        "current_tokens": current_tokens,
        "max_tokens": max_tokens,
        "usage_percent": round(usage_percent, 2),
        "remaining_tokens": max_tokens - current_tokens,
        "is_near_limit": usage_percent > 80,  # Warning threshold
    }
