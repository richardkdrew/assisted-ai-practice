"""Core agent logic for managing conversations."""

from detective_agent.config import Config
from detective_agent.context.manager import ContextManager
from detective_agent.models import Conversation
from detective_agent.observability.tracer import get_tracer, get_trace_id
from detective_agent.persistence.store import ConversationStore
from detective_agent.providers.base import BaseProvider


class Agent:
    """AI agent that manages conversations with an AI provider."""

    def __init__(self, provider: BaseProvider, store: ConversationStore, config: Config):
        """Initialize the agent with a provider, store, and config."""
        self.provider = provider
        self.store = store
        self.config = config
        self.tracer = get_tracer()
        self.context_manager = ContextManager(max_messages=config.max_messages)

    async def send_message(self, conversation: Conversation, user_message: str) -> str:
        """
        Send a user message and get an assistant response.

        Args:
            conversation: The conversation to add messages to
            user_message: The user's message

        Returns:
            The assistant's response
        """
        with self.tracer.start_as_current_span("send_message") as span:
            span.set_attribute("message_length", len(user_message))
            span.set_attribute("message_count", len(conversation.messages))

            conversation.add_message("user", user_message)

            # Store trace ID in conversation if not already set
            if not hasattr(conversation, "trace_id") or not conversation.trace_id:
                conversation.trace_id = get_trace_id()

            # Apply context window management
            truncated_messages, was_truncated = self.context_manager.truncate_messages(
                conversation.messages
            )

            # Track context information in span
            context_info = self.context_manager.get_context_info(conversation.messages)
            span.set_attribute("context.total_messages", context_info["total_messages"])
            span.set_attribute("context.was_truncated", was_truncated)
            if was_truncated:
                span.set_attribute(
                    "context.messages_dropped", context_info["messages_to_drop"]
                )

            # Convert truncated messages to API format
            messages = [msg.to_dict() for msg in truncated_messages]
            response = await self.provider.send_message(
                messages, self.config.max_tokens, system=self.config.system_prompt
            )
            conversation.add_message("assistant", response)

            span.set_attribute("response_length", len(response))
            span.set_attribute("total_messages", len(conversation.messages))

            self.store.save(conversation)
            return response

    def new_conversation(self) -> Conversation:
        """Create and save a new conversation."""
        with self.tracer.start_as_current_span("new_conversation"):
            conversation = self.store.create_conversation()
            conversation.trace_id = get_trace_id()
            self.store.save(conversation)
            return conversation

    def load_conversation(self, conversation_id: str) -> Conversation:
        """Load an existing conversation."""
        return self.store.load(conversation_id)

    def list_conversations(self) -> list[tuple[str, str]]:
        """List all conversations with formatted timestamps."""
        conversations = self.store.list_conversations()
        return [(id, dt.strftime("%Y-%m-%d %H:%M:%S")) for id, dt in conversations]
