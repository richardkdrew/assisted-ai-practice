"""Detective Agent - A foundational LLM agent for release risk assessment.

This package provides a conversational AI agent with:
- Conversation management and persistence
- OpenTelemetry-based observability
- Context window management
- Retry mechanism with exponential backoff
- Provider abstraction for AI services
"""

from detective_agent.agent import Agent
from detective_agent.context import ContextManager
from detective_agent.models import Config, Conversation, Message
from detective_agent.observability import get_trace_id, get_tracer, setup_tracer
from detective_agent.persistence import ConversationStore
from detective_agent.providers import AnthropicProvider, BaseProvider
from detective_agent.retry import RetryConfig, is_retryable_error, with_retry

__version__ = "0.1.0"

__all__ = [
    # Core
    "Agent",
    # Models
    "Config",
    "Conversation",
    "Message",
    # Providers
    "AnthropicProvider",
    "BaseProvider",
    # Persistence
    "ConversationStore",
    # Context Management
    "ContextManager",
    # Observability
    "get_trace_id",
    "get_tracer",
    "setup_tracer",
    # Retry
    "RetryConfig",
    "is_retryable_error",
    "with_retry",
    # Version
    "__version__",
]
