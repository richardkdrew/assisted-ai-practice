"""Tests for configuration model classes."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from pydantic_extra_types.ulid import ULID
from ulid import ULID as ULIDGenerator

from models.configuration import (
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationResponse,
    ConfigurationEntity,
)


class TestConfigurationCreate:
    """Test cases for ConfigurationCreate model."""

    def test_configuration_create_valid_data(self):
        """Test creating ConfigurationCreate with valid data."""
        app_id = ULIDGenerator()
        config_data = {"key1": "value1", "key2": 42}

        data = ConfigurationCreate(
            application_id=app_id,
            name="test-config",
            comments="Test configuration",
            config=config_data,
        )

        assert data.application_id == app_id
        assert data.name == "test-config"
        assert data.comments == "Test configuration"
        assert data.config == config_data

    def test_configuration_create_minimal_data(self):
        """Test creating ConfigurationCreate with minimal data."""
        app_id = ULIDGenerator()
        config_data = {"setting": "value"}

        data = ConfigurationCreate(
            application_id=app_id, name="test-config", config=config_data
        )

        assert data.application_id == app_id
        assert data.name == "test-config"
        assert data.comments is None
        assert data.config == config_data

    def test_configuration_create_missing_required_fields(self):
        """Test ConfigurationCreate validation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            ConfigurationCreate()

        error_str = str(exc_info.value)
        assert "application_id" in error_str
        assert "name" in error_str
        assert "config" in error_str

    def test_configuration_create_name_too_long(self):
        """Test ConfigurationCreate validation with name too long."""
        app_id = ULIDGenerator()
        long_name = "a" * 257  # Exceeds 256 character limit

        with pytest.raises(ValidationError) as exc_info:
            ConfigurationCreate(
                application_id=app_id, name=long_name, config={"key": "value"}
            )

        assert "String should have at most 256 characters" in str(exc_info.value)

    def test_configuration_create_comments_too_long(self):
        """Test ConfigurationCreate validation with comments too long."""
        app_id = ULIDGenerator()
        long_comments = "a" * 1025  # Exceeds 1024 character limit

        with pytest.raises(ValidationError) as exc_info:
            ConfigurationCreate(
                application_id=app_id,
                name="test-config",
                comments=long_comments,
                config={"key": "value"},
            )

        assert "String should have at most 1024 characters" in str(exc_info.value)

    def test_configuration_create_complex_config(self):
        """Test ConfigurationCreate with complex configuration data."""
        app_id = ULIDGenerator()
        complex_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "settings": {"pool_size": 10, "timeout": 30},
            },
            "features": ["feature1", "feature2"],
            "enabled": True,
        }

        data = ConfigurationCreate(
            application_id=app_id, name="complex-config", config=complex_config
        )

        assert data.config == complex_config


class TestConfigurationUpdate:
    """Test cases for ConfigurationUpdate model."""

    def test_configuration_update_all_fields(self):
        """Test ConfigurationUpdate with all fields."""
        config_data = {"updated": "value"}

        data = ConfigurationUpdate(
            name="updated-config", comments="Updated comments", config=config_data
        )

        assert data.name == "updated-config"
        assert data.comments == "Updated comments"
        assert data.config == config_data

    def test_configuration_update_partial_fields(self):
        """Test ConfigurationUpdate with partial fields."""
        data = ConfigurationUpdate(name="updated-config")

        assert data.name == "updated-config"
        assert data.comments is None
        assert data.config is None

    def test_configuration_update_empty(self):
        """Test ConfigurationUpdate with no fields."""
        data = ConfigurationUpdate()

        assert data.name is None
        assert data.comments is None
        assert data.config is None

    def test_configuration_update_exclude_unset(self):
        """Test ConfigurationUpdate exclude_unset functionality."""
        data = ConfigurationUpdate(name="updated-config")

        serialized = data.model_dump(exclude_unset=True)

        assert "name" in serialized
        assert "comments" not in serialized
        assert "config" not in serialized

    def test_configuration_update_name_too_long(self):
        """Test ConfigurationUpdate validation with name too long."""
        long_name = "a" * 257

        with pytest.raises(ValidationError) as exc_info:
            ConfigurationUpdate(name=long_name)

        assert "String should have at most 256 characters" in str(exc_info.value)


class TestConfigurationResponse:
    """Test cases for ConfigurationResponse model."""

    def test_configuration_response_creation(self):
        """Test creating ConfigurationResponse with valid data."""
        config_id = ULIDGenerator()
        app_id = ULIDGenerator()
        config_data = {"key": "value"}
        now = datetime.now()

        response = ConfigurationResponse(
            id=config_id,
            application_id=app_id,
            name="test-config",
            comments="Test configuration",
            config=config_data,
            created_at=now,
            updated_at=now,
        )

        assert response.id == config_id
        assert response.application_id == app_id
        assert response.name == "test-config"
        assert response.comments == "Test configuration"
        assert response.config == config_data
        assert response.created_at == now
        assert response.updated_at == now

    def test_configuration_response_no_comments(self):
        """Test ConfigurationResponse with no comments."""
        config_id = ULIDGenerator()
        app_id = ULIDGenerator()
        config_data = {"key": "value"}
        now = datetime.now()

        response = ConfigurationResponse(
            id=config_id,
            application_id=app_id,
            name="test-config",
            comments=None,
            config=config_data,
            created_at=now,
            updated_at=now,
        )

        assert response.comments is None

    def test_configuration_response_serialization(self):
        """Test ConfigurationResponse serialization."""
        config_id = ULIDGenerator()
        app_id = ULIDGenerator()
        config_data = {"key": "value", "number": 42}
        now = datetime.now()

        response = ConfigurationResponse(
            id=config_id,
            application_id=app_id,
            name="test-config",
            comments="Test configuration",
            config=config_data,
            created_at=now,
            updated_at=now,
        )

        serialized = response.model_dump()

        assert serialized["id"] == config_id
        assert serialized["application_id"] == app_id
        assert serialized["name"] == "test-config"
        assert serialized["comments"] == "Test configuration"
        assert serialized["config"] == config_data
        assert serialized["created_at"] == now
        assert serialized["updated_at"] == now


class TestConfigurationEntity:
    """Test cases for ConfigurationEntity model."""

    def test_configuration_entity_creation(self):
        """Test creating ConfigurationEntity with valid data."""
        config_id = ULIDGenerator()
        app_id = ULIDGenerator()
        config_data = {"setting": "value"}
        now = datetime.now()

        entity = ConfigurationEntity(
            id=config_id,
            application_id=app_id,
            name="test-config",
            comments="Test configuration",
            config=config_data,
            created_at=now,
            updated_at=now,
        )

        assert entity.id == config_id
        assert entity.application_id == app_id
        assert entity.name == "test-config"
        assert entity.comments == "Test configuration"
        assert entity.config == config_data
        assert entity.created_at == now
        assert entity.updated_at == now

    def test_configuration_entity_no_comments(self):
        """Test ConfigurationEntity with no comments."""
        config_id = ULIDGenerator()
        app_id = ULIDGenerator()
        config_data = {"setting": "value"}
        now = datetime.now()

        entity = ConfigurationEntity(
            id=config_id,
            application_id=app_id,
            name="test-config",
            config=config_data,
            created_at=now,
            updated_at=now,
        )

        assert entity.comments is None

    def test_configuration_entity_from_dict(self):
        """Test creating ConfigurationEntity from dictionary."""
        config_id = ULIDGenerator()
        app_id = ULIDGenerator()
        config_data = {"database_url": "postgresql://localhost/test"}
        now = datetime.now()

        data = {
            "id": config_id,
            "application_id": app_id,
            "name": "db-config",
            "comments": "Database configuration",
            "config": config_data,
            "created_at": now,
            "updated_at": now,
        }

        entity = ConfigurationEntity(**data)

        assert entity.id == config_id
        assert entity.application_id == app_id
        assert entity.name == "db-config"
        assert entity.comments == "Database configuration"
        assert entity.config == config_data

    def test_configuration_entity_empty_config(self):
        """Test ConfigurationEntity with empty config dictionary."""
        config_id = ULIDGenerator()
        app_id = ULIDGenerator()
        now = datetime.now()

        entity = ConfigurationEntity(
            id=config_id,
            application_id=app_id,
            name="empty-config",
            config={},
            created_at=now,
            updated_at=now,
        )

        assert entity.config == {}
