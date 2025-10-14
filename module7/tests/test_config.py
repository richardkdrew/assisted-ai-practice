"""Tests for configuration module."""

import os
from pathlib import Path

import pytest

from models.config import Config


def test_config_from_env_with_api_key(monkeypatch):
    """Test loading config from environment variables."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    config = Config.from_env()
    assert config.api_key == "test-key"
    assert config.model == "claude-3-5-sonnet-20241022"


def test_config_from_env_missing_api_key(monkeypatch):
    """Test that missing API key raises error."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        Config.from_env()


def test_config_custom_values(monkeypatch):
    """Test loading custom configuration values."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
    monkeypatch.setenv("MAX_TOKENS", "8192")
    monkeypatch.setenv("CONVERSATIONS_DIR", "/tmp/convos")

    config = Config.from_env()
    assert config.api_key == "test-key"
    assert config.model == "claude-3-opus-20240229"
    assert config.max_tokens == 8192
    assert config.conversations_dir == Path("/tmp/convos")
