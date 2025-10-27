"""Base provider abstraction for AI providers."""

from abc import ABC, abstractmethod
from typing import Any

from investigator_agent.models import ToolCall


class BaseProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    async def send_message(
        self,
        messages: list[dict],
        max_tokens: int,
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:
        """
        Send messages to the AI provider and get a response.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens for the response
            system: Optional system prompt to guide the model's behavior
            tools: Optional list of tool definitions in provider-specific format

        Returns:
            Provider-specific response object (e.g., AnthropicMessage)
        """
        pass

    @abstractmethod
    def extract_tool_calls(self, response: Any) -> list[ToolCall]:
        """
        Extract tool calls from a provider response.

        Args:
            response: Provider-specific response object

        Returns:
            List of ToolCall objects extracted from response
        """
        pass

    @abstractmethod
    def get_text_content(self, response: Any) -> str:
        """
        Extract text content from a provider response.

        Args:
            response: Provider-specific response object

        Returns:
            Concatenated text from all text blocks in response
        """
        pass
