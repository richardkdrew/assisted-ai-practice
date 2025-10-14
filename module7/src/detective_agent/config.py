"""Configuration management for the AI agent.

This module centralizes all configuration classes:
- Config: Main agent configuration
- RetryConfig: Retry mechanism configuration
"""

import os
from dataclasses import dataclass
from pathlib import Path

from detective_agent.system_prompt import DEFAULT_SYSTEM_PROMPT


@dataclass
class RetryConfig:
    """Configuration for retry behavior with exponential backoff."""

    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True


@dataclass
class Config:
    """Main configuration for the AI agent."""

    api_key: str
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    conversations_dir: Path = Path("./conversations")
    traces_dir: Path = Path("./data/traces")
    max_messages: int = 6
    system_prompt: str = DEFAULT_SYSTEM_PROMPT

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
            traces_dir=Path(os.getenv("TRACES_DIR", cls.traces_dir)),
            max_messages=int(os.getenv("MAX_MESSAGES", cls.max_messages)),
            system_prompt=os.getenv("SYSTEM_PROMPT", cls.system_prompt),
        )
