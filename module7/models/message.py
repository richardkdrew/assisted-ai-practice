"""Message data models for conversations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class Message:
    """A single message in a conversation."""

    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for API calls."""
        return {"role": self.role, "content": self.content}


@dataclass
class Conversation:
    """A conversation thread with messages."""

    id: str
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    trace_id: str = ""

    def add_message(self, role: Literal["user", "assistant"], content: str) -> None:
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))
        self.updated_at = datetime.now()

    def to_api_format(self) -> list[dict]:
        """Convert messages to API format."""
        return [msg.to_dict() for msg in self.messages]
