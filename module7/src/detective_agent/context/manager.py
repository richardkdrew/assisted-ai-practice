"""Context window management for conversations."""

from detective_agent.models.message import Message


class ContextManager:
    """Manages conversation context to stay within limits."""

    def __init__(self, max_messages: int = 6):
        """
        Initialize the context manager.

        Args:
            max_messages: Maximum number of messages to keep (default: 6)
        """
        self.max_messages = max_messages

    def truncate_messages(self, messages: list[Message]) -> tuple[list[Message], bool]:
        """
        Truncate messages to keep only the most recent ones.

        Args:
            messages: List of messages in the conversation

        Returns:
            Tuple of (truncated messages, was_truncated)
        """
        if len(messages) <= self.max_messages:
            return messages, False

        # Keep only the last max_messages
        truncated = messages[-self.max_messages :]
        return truncated, True

    def get_context_info(self, messages: list[Message]) -> dict:
        """
        Get information about the current context state.

        Args:
            messages: List of messages in the conversation

        Returns:
            Dictionary with context information
        """
        return {
            "total_messages": len(messages),
            "max_messages": self.max_messages,
            "would_truncate": len(messages) > self.max_messages,
            "messages_to_drop": max(0, len(messages) - self.max_messages),
        }
