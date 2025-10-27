"""Conversation persistence to filesystem."""

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from investigator_agent.models import Conversation, Message, SubConversation
from investigator_agent.observability.tracer import flush_traces


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
            "trace_ids": conversation.trace_ids,
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
            "sub_conversations": [
                {
                    "id": sub.id,
                    "parent_id": sub.parent_id,
                    "purpose": sub.purpose,
                    "system_prompt": sub.system_prompt,
                    "summary": sub.summary,
                    "created_at": sub.created_at.isoformat(),
                    "completed_at": sub.completed_at.isoformat() if sub.completed_at else None,
                    "token_count": sub.token_count,
                    "messages": [
                        {
                            "role": msg.role,
                            "content": msg.content,
                            "timestamp": msg.timestamp.isoformat(),
                        }
                        for msg in sub.messages
                    ],
                }
                for sub in conversation.sub_conversations
            ],
        }
        file_path.write_text(json.dumps(data, indent=2))

        # Flush traces to ensure they're written to disk
        flush_traces()

    def load(self, conversation_id: str) -> Conversation:
        """Load a conversation from disk.

        Supports partial ID matching - will match any conversation ID that starts
        with the provided string (similar to git commit SHAs).
        """
        # Strip .json extension if provided
        if conversation_id.endswith('.json'):
            conversation_id = conversation_id[:-5]

        # Try exact match first
        file_path = self.storage_dir / f"{conversation_id}.json"
        if file_path.exists():
            data = json.loads(file_path.read_text())
        else:
            # Try partial match
            matching_files = list(self.storage_dir.glob(f"{conversation_id}*.json"))
            if not matching_files:
                raise FileNotFoundError(f"Conversation {conversation_id} not found")
            if len(matching_files) > 1:
                raise ValueError(
                    f"Ambiguous conversation ID {conversation_id}: "
                    f"matches {len(matching_files)} conversations"
                )
            data = json.loads(matching_files[0].read_text())
        messages = [
            Message(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
            )
            for msg in data["messages"]
        ]

        # Load sub-conversations if present
        sub_conversations = []
        for sub_data in data.get("sub_conversations", []):
            sub_messages = [
                Message(
                    role=msg["role"],
                    content=msg["content"],
                    timestamp=datetime.fromisoformat(msg["timestamp"]),
                )
                for msg in sub_data["messages"]
            ]
            sub_conversations.append(
                SubConversation(
                    id=sub_data["id"],
                    parent_id=sub_data["parent_id"],
                    purpose=sub_data["purpose"],
                    system_prompt=sub_data["system_prompt"],
                    messages=sub_messages,
                    summary=sub_data.get("summary", ""),
                    created_at=datetime.fromisoformat(sub_data["created_at"]),
                    completed_at=(
                        datetime.fromisoformat(sub_data["completed_at"])
                        if sub_data.get("completed_at")
                        else None
                    ),
                    token_count=sub_data.get("token_count", 0),
                )
            )

        return Conversation(
            id=data["id"],
            messages=messages,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            trace_id=data.get("trace_id", ""),
            trace_ids=data.get("trace_ids", []),
            sub_conversations=sub_conversations,
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
