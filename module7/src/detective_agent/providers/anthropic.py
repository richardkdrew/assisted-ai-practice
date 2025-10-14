"""Anthropic provider implementation."""

import time

from anthropic import AsyncAnthropic

from detective_agent.observability.tracer import get_tracer
from detective_agent.providers.base import BaseProvider
from detective_agent.retry.strategy import RetryConfig, with_retry


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic's Claude API."""

    def __init__(self, api_key: str, model: str, retry_config: RetryConfig = None):
        """Initialize the Anthropic provider."""
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.tracer = get_tracer()
        self.retry_config = retry_config or RetryConfig()

    async def send_message(self, messages: list[dict], max_tokens: int) -> str:
        """Send messages to Claude and get a response with retry logic."""
        with self.tracer.start_as_current_span("anthropic_api_call") as span:
            span.set_attribute("model", self.model)
            span.set_attribute("max_tokens", max_tokens)
            span.set_attribute("message_count", len(messages))

            async def _make_api_call():
                """Inner function to make the API call."""
                start_time = time.time()
                response = await self.client.messages.create(
                    model=self.model, max_tokens=max_tokens, messages=messages
                )
                duration = time.time() - start_time

                span.set_attribute("input_tokens", response.usage.input_tokens)
                span.set_attribute("output_tokens", response.usage.output_tokens)
                span.set_attribute("duration_seconds", duration)

                return response.content[0].text

            # Wrap the API call with retry logic
            return await with_retry(
                _make_api_call, self.retry_config, operation_name="anthropic_api_call"
            )
