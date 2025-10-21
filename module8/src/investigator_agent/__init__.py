"""Investigator Agent - A foundational LLM agent for release risk assessment.

This package provides a conversational AI agent with:
- Conversation management and persistence
- OpenTelemetry-based observability
- Context window management
- Retry mechanism with exponential backoff
- Provider abstraction for AI services
"""

from investigator_agent.agent import Agent
from investigator_agent.config import Config, RetryConfig
from investigator_agent.context import ContextManager
from investigator_agent.models import Conversation, Message, ToolCall, ToolDefinition, ToolResult
from investigator_agent.observability import get_trace_id, get_tracer, setup_tracer
from investigator_agent.persistence import ConversationStore
from investigator_agent.providers import AnthropicProvider, BaseProvider
from investigator_agent.retry import is_retryable_error, with_retry
from investigator_agent.system_prompt import DEFAULT_SYSTEM_PROMPT
from investigator_agent.tools import ToolRegistry

__version__ = "0.1.0"

__all__ = [
    # Core
    "Agent",
    # Configuration
    "Config",
    "RetryConfig",
    "DEFAULT_SYSTEM_PROMPT",
    # Models
    "Conversation",
    "Message",
    "ToolCall",
    "ToolDefinition",
    "ToolResult",
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
    "is_retryable_error",
    "with_retry",
    # Tools
    "ToolRegistry",
    # Version
    "__version__",
]
