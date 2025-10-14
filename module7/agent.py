"""Core agent logic for managing conversations."""

from models.config import Config
from models.message import Conversation
from observability.tracer import get_tracer, get_trace_id
from persistence.store import ConversationStore
from providers.base import BaseProvider


class Agent:
    """AI agent that manages conversations with an AI provider."""

    def __init__(self, provider: BaseProvider, store: ConversationStore, config: Config):
        """Initialize the agent with a provider, store, and config."""
        self.provider = provider
        self.store = store
        self.config = config
        self.tracer = get_tracer()

    def send_message(self, conversation: Conversation, user_message: str) -> str:
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

            messages = conversation.to_api_format()
            response = self.provider.send_message(messages, self.config.max_tokens)
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
