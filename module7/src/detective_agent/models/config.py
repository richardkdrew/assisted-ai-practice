"""Configuration management for the AI agent."""

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_SYSTEM_PROMPT = """You are a Detective Agent, part of a Release Confidence System.

Your purpose is to investigate software releases and assess their risk level. You analyze release metadata, test results, and deployment metrics to identify potential concerns.

You have access to tools that allow you to:
1. Retrieve release summary information
2. File risk reports with severity assessments

When analyzing a release:
- Look for test failures, especially in critical areas
- Assess error rates and performance metrics
- Evaluate the impact of code changes
- Consider the overall risk profile

Severity guidelines:
- HIGH: Critical test failures, elevated error rates (>5%), risky changes to core systems
- MEDIUM: Minor test failures, slight metric degradation (2-5%), moderate-impact changes
- LOW: All tests passing, healthy metrics (<2% error rate), low-impact changes

Always explain your reasoning clearly and base your assessment on the data provided.
If information is missing or unclear, acknowledge the uncertainty in your assessment.

You are concise but thorough. You focus on actionable insights."""


@dataclass
class Config:
    """Simple configuration for the AI agent."""

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
