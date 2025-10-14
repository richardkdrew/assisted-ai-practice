"""Data models for the detective agent."""

from detective_agent.models.config import DEFAULT_SYSTEM_PROMPT, Config
from detective_agent.models.message import Conversation, Message

__all__ = [
    "Config",
    "Conversation",
    "Message",
    "DEFAULT_SYSTEM_PROMPT",
]
