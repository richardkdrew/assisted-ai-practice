"""Tests for configuration management."""

import pytest
from unittest.mock import patch
from pydantic import ValidationError

from .config import Settings


def test_settings_default_values():
    """Test that settings have appropriate default values."""
    settings = Settings()

    # Database defaults
    assert settings.db_host == "localhost"
    assert settings.db_port == 5432
    assert settings.db_name == "configservice"
    assert settings.db_user == "user"
    assert settings.db_password == "password"
    assert settings.db_pool_min_conn == 1
    assert settings.db_pool_max_conn == 20

    # Application defaults
    assert settings.log_level == "INFO"
    assert settings.api_prefix == "/api/v1"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000


def test_settings_from_environment():
    """Test that settings can be loaded from environment variables."""
    env_vars = {
        "DATABASE_URL": "postgresql://testuser:testpass@testhost:5433/testdb",
        "DB_HOST": "testhost",
        "DB_PORT": "5433",
        "DB_NAME": "testdb",
        "DB_USER": "testuser",
        "DB_PASSWORD": "testpass",
        "LOG_LEVEL": "DEBUG",
        "API_PREFIX": "/api/v2",
        "HOST": "127.0.0.1",
        "PORT": "9000"
    }

    with patch.dict("os.environ", env_vars):
        settings = Settings()

        assert settings.database_url == "postgresql://testuser:testpass@testhost:5433/testdb"
        assert settings.db_host == "testhost"
        assert settings.db_port == 5433
        assert settings.db_name == "testdb"
        assert settings.db_user == "testuser"
        assert settings.db_password == "testpass"
        assert settings.log_level == "DEBUG"
        assert settings.api_prefix == "/api/v2"
        assert settings.host == "127.0.0.1"
        assert settings.port == 9000


def test_settings_port_validation():
    """Test that port validation works correctly."""
    with patch.dict("os.environ", {"PORT": "0"}):
        settings = Settings()
        assert settings.port == 0

    with patch.dict("os.environ", {"PORT": "65535"}):
        settings = Settings()
        assert settings.port == 65535


def test_settings_pool_connection_bounds():
    """Test database pool connection boundaries."""
    with patch.dict("os.environ", {"DB_POOL_MIN_CONN": "5", "DB_POOL_MAX_CONN": "100"}):
        settings = Settings()
        assert settings.db_pool_min_conn == 5
        assert settings.db_pool_max_conn == 100