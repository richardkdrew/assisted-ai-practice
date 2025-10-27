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
class SubConversation:
    """A sub-conversation for isolated document analysis.

    Used when tool results (e.g., large documentation) exceed token thresholds.
    The sub-conversation isolates the analysis in a separate context, then
    returns a condensed summary to the main conversation.
    """

    id: str
    parent_id: str  # ID of the parent Conversation
    purpose: str  # Description of what this sub-conversation is analyzing
    system_prompt: str  # Specialized prompt for this analysis task
    messages: list[Message] = field(default_factory=list)
    summary: str = ""  # Condensed results from this sub-conversation
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None  # Set when analysis is complete
    token_count: int = 0  # Total tokens used in this sub-conversation

    def add_message(
        self, role: Literal["user", "assistant"], content: str | list[dict[str, Any]]
    ) -> None:
        """Add a message to the sub-conversation.

        Args:
            role: Message role (user or assistant)
            content: Text content or list of content blocks
        """
        self.messages.append(Message(role=role, content=content))

    def to_api_format(self) -> list[dict]:
        """Convert messages to API format."""
        return [msg.to_dict() for msg in self.messages]

    def complete(self, summary: str) -> None:
        """Mark the sub-conversation as complete with a summary.

        Args:
            summary: Condensed summary of the analysis results
        """
        self.summary = summary
        self.completed_at = datetime.now()


@dataclass
class Conversation:
    """A conversation thread with messages."""

    id: str
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    trace_id: str = ""
    trace_ids: list[str] = field(default_factory=list)  # All trace IDs for this session
    sub_conversations: list[SubConversation] = field(
        default_factory=list
    )  # Isolated analysis contexts

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
