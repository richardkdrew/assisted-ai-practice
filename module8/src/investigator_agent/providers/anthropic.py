"""Anthropic provider implementation."""

import time
from typing import Any

from anthropic import AsyncAnthropic
from anthropic.types import Message as AnthropicMessage

from investigator_agent.config import RetryConfig
from investigator_agent.models import ToolCall
from investigator_agent.observability.tracer import get_tracer
from investigator_agent.providers.base import BaseProvider
from investigator_agent.retry.strategy import with_retry


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic's Claude API."""

    def __init__(self, api_key: str, model: str, retry_config: RetryConfig = None):
        """Initialize the Anthropic provider."""
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.tracer = get_tracer()
        self.retry_config = retry_config or RetryConfig()

    async def send_message(
        self,
        messages: list[dict],
        max_tokens: int,
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> AnthropicMessage:
        """Send messages to Claude and get a response with retry logic.

        Args:
            messages: List of message dicts
            max_tokens: Maximum tokens for response
            system: Optional system prompt
            tools: Optional list of tool definitions in Anthropic format

        Returns:
            Full Anthropic Message object (contains content blocks, tool calls, etc.)
        """
        with self.tracer.start_as_current_span("anthropic_api_call") as span:
            span.set_attribute("model", self.model)
            span.set_attribute("max_tokens", max_tokens)
            span.set_attribute("message_count", len(messages))
            span.set_attribute("has_system_prompt", system is not None)
            span.set_attribute("has_tools", tools is not None)
            if tools:
                span.set_attribute("tool_count", len(tools))

            async def _make_api_call():
                """Inner function to make the API call."""
                start_time = time.time()

                # Build API call parameters
                api_params = {
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "messages": messages,
                }
                if system:
                    api_params["system"] = system
                if tools:
                    api_params["tools"] = tools

                response = await self.client.messages.create(**api_params)
                duration = time.time() - start_time

                span.set_attribute("input_tokens", response.usage.input_tokens)
                span.set_attribute("output_tokens", response.usage.output_tokens)
                span.set_attribute("duration_seconds", duration)
                span.set_attribute("stop_reason", response.stop_reason)

                # Track if response contains tool calls
                has_tool_use = any(
                    block.type == "tool_use" for block in response.content
                )
                span.set_attribute("has_tool_use", has_tool_use)

                return response

            # Wrap the API call with retry logic
            return await with_retry(
                _make_api_call, self.retry_config, operation_name="anthropic_api_call"
            )

    def extract_tool_calls(self, response: AnthropicMessage) -> list[ToolCall]:
        """Extract tool calls from an Anthropic response.

        Args:
            response: Anthropic Message object

        Returns:
            List of ToolCall objects extracted from response
        """
        tool_calls = []

        for block in response.content:
            if block.type == "tool_use":
                tool_call = ToolCall(
                    id=block.id,
                    name=block.name,
                    input=block.input,
                )
                tool_calls.append(tool_call)

        return tool_calls

    def get_text_content(self, response: AnthropicMessage) -> str:
        """Extract text content from response.

        Args:
            response: Anthropic Message object

        Returns:
            Concatenated text from all text blocks
        """
        text_parts = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)

        return "".join(text_parts)
