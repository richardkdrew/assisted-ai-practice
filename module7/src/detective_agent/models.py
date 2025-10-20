"""Data models for conversations and tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Literal


@dataclass
class Message:
    """A single message in a conversation.

    Content can be:
    - str: Simple text content
    - list[dict]: Complex content with tool_use or tool_result blocks
    """

    role: Literal["user", "assistant"]
    content: str | list[dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for API calls."""
        return {"role": self.role, "content": self.content}

    def get_text_content(self) -> str:
        """Extract text content from message.

        Returns:
            Text content as string. For complex content, concatenates all text blocks.
        """
        if isinstance(self.content, str):
            return self.content

        # Extract text from content blocks
        text_parts = []
        for block in self.content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    # Include tool use in text representation
                    text_parts.append(f"[Tool: {block.get('name')}]")

        return " ".join(text_parts)


@dataclass
class Conversation:
    """A conversation thread with messages."""

    id: str
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    trace_id: str = ""
    trace_ids: list[str] = field(default_factory=list)  # All trace IDs for this session

    def add_message(
        self, role: Literal["user", "assistant"], content: str | list[dict[str, Any]]
    ) -> None:
        """Add a message to the conversation.

        Args:
            role: Message role (user or assistant)
            content: Text content or list of content blocks (for tool use/results)
        """
        self.messages.append(Message(role=role, content=content))
        self.updated_at = datetime.now()

    def add_tool_result_message(self, tool_results: list[ToolResult]) -> None:
        """Add a user message containing tool results.

        Args:
            tool_results: List of tool execution results
        """
        content_blocks = []
        for result in tool_results:
            content_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": result.tool_call_id,
                    "content": result.content,
                    "is_error": not result.success,
                }
            )

        self.add_message("user", content_blocks)

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
