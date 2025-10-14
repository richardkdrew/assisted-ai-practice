"""Conversation persistence to filesystem."""

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from detective_agent.models import Conversation, Message
from detective_agent.observability.tracer import flush_traces


class ConversationStore:
    """Simple filesystem-based conversation storage."""

    def __init__(self, storage_dir: Path):
        """Initialize the store with a storage directory."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, conversation: Conversation) -> None:
        """Save a conversation to disk."""
        file_path = self.storage_dir / f"{conversation.id}.json"
        data = {
            "id": conversation.id,
            "trace_id": conversation.trace_id,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in conversation.messages
            ],
        }
        file_path.write_text(json.dumps(data, indent=2))

        # Flush traces to ensure they're written to disk
        flush_traces()

    def load(self, conversation_id: str) -> Conversation:
        """Load a conversation from disk."""
        file_path = self.storage_dir / f"{conversation_id}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Conversation {conversation_id} not found")

        data = json.loads(file_path.read_text())
        messages = [
            Message(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
            )
            for msg in data["messages"]
        ]

        return Conversation(
            id=data["id"],
            messages=messages,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            trace_id=data.get("trace_id", ""),
        )

    def list_conversations(self) -> list[tuple[str, datetime]]:
        """List all conversations with their IDs and last updated times."""
        conversations = []
        for file_path in self.storage_dir.glob("*.json"):
            data = json.loads(file_path.read_text())
            conversations.append(
                (data["id"], datetime.fromisoformat(data["updated_at"]))
            )
        return sorted(conversations, key=lambda x: x[1], reverse=True)

    def create_conversation(self) -> Conversation:
        """Create a new conversation with a unique ID."""
        return Conversation(id=str(uuid4()))
