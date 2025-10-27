"""Sub-conversation management for isolating large document analysis."""

import uuid
from typing import TYPE_CHECKING

from investigator_agent.context.tokens import count_message_tokens, count_tokens
from investigator_agent.models import SubConversation
from investigator_agent.observability import get_tracer

if TYPE_CHECKING:
    from investigator_agent.providers.base import BaseProvider


def _get_tracer():
    """Get tracer, handling case where it's not initialized."""
    try:
        return get_tracer()
    except RuntimeError:
        # Tracer not initialized - return a no-op tracer
        from opentelemetry import trace

        return trace.get_tracer(__name__)


class SubConversationManager:
    """Manages sub-conversations for isolated document analysis.

    When tool results exceed token thresholds, this manager creates
    isolated sub-conversations to analyze the content, then returns
    a condensed summary to the main conversation.
    """

    def __init__(self, provider: "BaseProvider"):
        """Initialize the sub-conversation manager.

        Args:
            provider: LLM provider for executing sub-conversations
        """
        self.provider = provider

    async def analyze_in_subconversation(
        self,
        parent_conversation_id: str,
        content: str,
        purpose: str,
        analysis_prompt: str,
    ) -> SubConversation:
        """Analyze content in an isolated sub-conversation.

        Creates a new sub-conversation, analyzes the content with a specialized
        prompt, and returns the sub-conversation with a summary.

        Args:
            parent_conversation_id: ID of the parent conversation
            content: Large content to analyze (e.g., documentation)
            purpose: Description of what's being analyzed
            analysis_prompt: User's analysis question/request

        Returns:
            Completed SubConversation with summary
        """
        # Create sub-conversation
        sub_conv = SubConversation(
            id=str(uuid.uuid4()),
            parent_id=parent_conversation_id,
            purpose=purpose,
            system_prompt=self._build_analysis_system_prompt(),
        )

        # Add the content and analysis request
        sub_conv.add_message(
            "user",
            f"{analysis_prompt}\n\n<document>\n{content}\n</document>",
        )

        # Execute analysis with provider
        with _get_tracer().start_as_current_span(
            "subconversation.analyze",
            attributes={
                "subconversation.id": sub_conv.id,
                "subconversation.parent_id": parent_conversation_id,
                "subconversation.purpose": purpose,
                "content.size_chars": len(content),
                "content.size_tokens": count_tokens(content),
            },
        ):
            response = await self.provider.send_message(
                messages=sub_conv.to_api_format(),
                max_tokens=4096,
                system=sub_conv.system_prompt,
                tools=None,  # No tools in sub-conversations
            )

            # Add response to sub-conversation
            response_text = self.provider.get_text_content(response)
            sub_conv.add_message("assistant", response_text)

            # Calculate token usage
            sub_conv.token_count = count_message_tokens(sub_conv.to_api_format())

            # Generate summary
            summary = await self._summarize_analysis(sub_conv)
            sub_conv.complete(summary)

        return sub_conv

    async def _summarize_analysis(self, sub_conv: SubConversation) -> str:
        """Summarize the sub-conversation analysis.

        Uses LLM to create a condensed summary (targeting 10:1 compression).

        Args:
            sub_conv: The sub-conversation to summarize

        Returns:
            Condensed summary of the analysis
        """
        # Build summarization prompt
        summarization_prompt = self._build_summarization_prompt(sub_conv)

        with _get_tracer().start_as_current_span(
            "subconversation.summarize",
            attributes={
                "subconversation.id": sub_conv.id,
                "messages.count": len(sub_conv.messages),
            },
        ):
            response = await self.provider.send_message(
                messages=[{"role": "user", "content": summarization_prompt}],
                max_tokens=2048,
                system="You are a summarization assistant. Create concise, information-dense summaries.",
                tools=None,
            )

        return self.provider.get_text_content(response)

    def _build_analysis_system_prompt(self) -> str:
        """Build system prompt for document analysis."""
        return """You are a documentation analysis assistant.

Your task is to carefully analyze the provided document and answer the user's question.

Guidelines:
- Be thorough but concise
- Focus on the specific information requested
- Extract key facts and insights
- If the document doesn't contain the requested information, say so clearly

Your response will be summarized, so be clear and well-organized."""

    def _build_summarization_prompt(self, sub_conv: SubConversation) -> str:
        """Build prompt for summarizing sub-conversation.

        Args:
            sub_conv: The sub-conversation to summarize

        Returns:
            Summarization prompt
        """
        # Extract the analysis request and response
        user_message = sub_conv.messages[0].get_text_content() if sub_conv.messages else ""
        assistant_response = (
            sub_conv.messages[1].get_text_content() if len(sub_conv.messages) > 1 else ""
        )

        return f"""Summarize the following analysis in a concise, information-dense format.

TARGET: Compress by ~10:1 ratio while retaining all key information.

Original Question:
{user_message.split('<document>')[0].strip()}

Analysis Response:
{assistant_response}

Create a summary that:
1. Captures the main findings and insights
2. Preserves specific facts and data points
3. Maintains the structure and organization
4. Is clear and actionable

SUMMARY:"""
