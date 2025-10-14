"""Anthropic provider implementation."""

import time

from anthropic import Anthropic

from detective_agent.observability.tracer import get_tracer
from detective_agent.providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic's Claude API."""

    def __init__(self, api_key: str, model: str):
        """Initialize the Anthropic provider."""
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.tracer = get_tracer()

    def send_message(self, messages: list[dict], max_tokens: int) -> str:
        """Send messages to Claude and get a response."""
        with self.tracer.start_as_current_span("anthropic_api_call") as span:
            span.set_attribute("model", self.model)
            span.set_attribute("max_tokens", max_tokens)
            span.set_attribute("message_count", len(messages))

            start_time = time.time()
            response = self.client.messages.create(
                model=self.model, max_tokens=max_tokens, messages=messages
            )
            duration = time.time() - start_time

            span.set_attribute("input_tokens", response.usage.input_tokens)
            span.set_attribute("output_tokens", response.usage.output_tokens)
            span.set_attribute("duration_seconds", duration)

            return response.content[0].text
