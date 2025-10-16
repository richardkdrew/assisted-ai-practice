"""Data models for conversations and tools."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Literal


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


# Tool Models


@dataclass
class ToolDefinition:
    """Definition of a tool that the agent can use."""

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable = field(repr=False)  # Don't show handler in repr

    def to_anthropic_format(self) -> dict[str, Any]:
        """Convert to Anthropic tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


@dataclass
class ToolCall:
    """A request to execute a tool."""

    id: str
    name: str
    input: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "input": self.input,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ToolResult:
    """Result of a tool execution."""

    tool_call_id: str
    content: str
    success: bool = True
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool_call_id": self.tool_call_id,
            "content": self.content,
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }
