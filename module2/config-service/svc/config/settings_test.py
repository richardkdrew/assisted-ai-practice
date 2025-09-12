"""Tests for application settings."""

import pytest
import os
from unittest.mock import patch

from config.settings import Settings


class TestSettings:
    """Test cases for Settings configuration."""

    def test_settings_default_values(self):
        """Test Settings with default values."""
        # Clear environment and set only required fields to test true defaults
        env_vars = {
            "DATABASE_DB": "test_db",
            "DATABASE_USER": "test_user",
            "DATABASE_PASSWORD": "test_pass",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "DATABASE_TEST_URL": "postgresql://test:test@localhost/test_db",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Mock the env_file to prevent loading .env file
            with patch(
                "config.settings.Settings.model_config",
                {"env_file": "nonexistent.env", "case_sensitive": False},
            ):
                settings = Settings()

                assert settings.log_level == "INFO"  # Default from Settings class
                assert settings.debug is False  # Default from Settings class
                assert settings.host == "0.0.0.0"
                assert settings.port == 8000  # Default from Settings class
                assert settings.db_min_connections == 1
                assert settings.db_max_connections == 20  # Default from Settings class

    def test_settings_from_environment(self):
        """Test Settings loaded from environment variables."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost/config_service",
            "DATABASE_TEST_URL": "postgresql://user:pass@localhost/config_service_test",
            "LOG_LEVEL": "DEBUG",
            "DEBUG": "True",
            "HOST": "127.0.0.1",
            "PORT": "3000",
            "DB_MIN_CONNECTIONS": "5",
            "DB_MAX_CONNECTIONS": "50",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()

            assert (
                settings.database_url
                == "postgresql://user:pass@localhost/config_service"
            )
            assert (
                settings.database_test_url
                == "postgresql://user:pass@localhost/config_service_test"
            )
            assert settings.log_level == "DEBUG"
            assert settings.debug is True
            assert settings.host == "127.0.0.1"
            assert settings.port == 3000
            assert settings.db_min_connections == 5
            assert settings.db_max_connections == 50

    def test_settings_case_insensitive(self):
        """Test Settings case insensitive configuration."""
        env_vars = {
            "database_url": "postgresql://test:test@localhost/test",
            "database_test_url": "postgresql://test:test@localhost/test_db",
            "log_level": "warning",
            "debug": "false",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()

            assert settings.database_url == "postgresql://test:test@localhost/test"
            assert settings.log_level == "warning"
            assert settings.debug is False

    def test_settings_missing_required_fields(self):
        """Test Settings validation with missing required fields."""
        with patch.dict(os.environ, {}, clear=True):
            # Mock the env_file to not exist so it doesn't load from .env
            with patch(
                "config.settings.Settings.model_config",
                {"env_file": "nonexistent.env", "case_sensitive": False},
            ):
                with pytest.raises(Exception):  # Should raise validation error
                    Settings()

    def test_settings_invalid_port(self):
        """Test Settings with invalid port value."""
        env_vars = {
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "DATABASE_TEST_URL": "postgresql://test:test@localhost/test_db",
            "PORT": "invalid_port",
        }

        with patch.dict(os.environ, env_vars):
            with pytest.raises(Exception):  # Should raise validation error
                Settings()

    def test_settings_invalid_boolean(self):
        """Test Settings with invalid boolean value."""
        env_vars = {
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "DATABASE_TEST_URL": "postgresql://test:test@localhost/test_db",
            "DEBUG": "maybe",
        }

        with patch.dict(os.environ, env_vars):
            with pytest.raises(Exception):  # Should raise validation error
                Settings()

    def test_settings_connection_pool_bounds(self):
        """Test Settings with connection pool boundary values."""
        env_vars = {
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "DATABASE_TEST_URL": "postgresql://test:test@localhost/test_db",
            "DB_MIN_CONNECTIONS": "0",
            "DB_MAX_CONNECTIONS": "1000",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()

            assert settings.db_min_connections == 0
            assert settings.db_max_connections == 1000

    def test_settings_env_file_config(self):
        """Test Settings configuration includes env_file."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://test:test@localhost/test",
                "DATABASE_TEST_URL": "postgresql://test:test@localhost/test_db",
            },
        ):
            settings = Settings()

            assert settings.model_config["env_file"] == ".env"
            assert settings.model_config["case_sensitive"] is False
