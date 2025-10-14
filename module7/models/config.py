"""Configuration management for the AI agent."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Simple configuration for the AI agent."""

    api_key: str
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    conversations_dir: Path = Path("./conversations")

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        return cls(
            api_key=api_key,
            model=os.getenv("ANTHROPIC_MODEL", cls.model),
            max_tokens=int(os.getenv("MAX_TOKENS", cls.max_tokens)),
            conversations_dir=Path(os.getenv("CONVERSATIONS_DIR", cls.conversations_dir)),
        )
