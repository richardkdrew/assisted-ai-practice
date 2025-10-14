"""Anthropic provider implementation."""

from anthropic import Anthropic

from providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic's Claude API."""

    def __init__(self, api_key: str, model: str):
        """Initialize the Anthropic provider."""
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def send_message(self, messages: list[dict], max_tokens: int) -> str:
        """Send messages to Claude and get a response."""
        response = self.client.messages.create(
            model=self.model, max_tokens=max_tokens, messages=messages
        )
        return response.content[0].text
