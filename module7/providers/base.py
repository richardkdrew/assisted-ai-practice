"""Base provider abstraction for AI providers."""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def send_message(self, messages: list[dict], max_tokens: int) -> str:
        """
        Send messages to the AI provider and get a response.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens for the response

        Returns:
            The assistant's response content
        """
        pass
