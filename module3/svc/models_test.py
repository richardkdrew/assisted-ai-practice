"""Tests for Pydantic models."""

import pytest
from datetime import datetime, UTC
from pydantic import ValidationError
from pydantic_extra_types.ulid import ULID
from ulid import ULID as ULIDGenerator

from .models import (
    Application, ApplicationCreate, ApplicationUpdate,
    Configuration, ConfigurationCreate, ConfigurationUpdate,
    PaginationParams, PaginatedResponse, ErrorResponse
)


class TestApplicationModels:
    """Test application-related models."""

    def test_application_create_valid(self):
        """Test creating a valid ApplicationCreate instance."""
        app_data = ApplicationCreate(
            name="test-app",
            comments="A test application"
        )
        assert app_data.name == "test-app"
        assert app_data.comments == "A test application"

    def test_application_create_without_comments(self):
        """Test creating ApplicationCreate without comments."""
        app_data = ApplicationCreate(name="test-app")
        assert app_data.name == "test-app"
        assert app_data.comments is None

    def test_application_create_name_too_long(self):
        """Test that names longer than 256 chars are rejected."""
        with pytest.raises(ValidationError):
            ApplicationCreate(name="a" * 257)

    def test_application_create_comments_too_long(self):
        """Test that comments longer than 1024 chars are rejected."""
        with pytest.raises(ValidationError):
            ApplicationCreate(name="test", comments="a" * 1025)

    def test_application_full_model(self):
        """Test complete Application model."""
        ulid_id = str(ULIDGenerator())
        now = datetime.now(UTC)
        config_ids = [str(ULIDGenerator()), str(ULIDGenerator())]

        app = Application(
            id=ulid_id,
            name="test-app",
            comments="Test application",
            created_at=now,
            updated_at=now,
            configuration_ids=config_ids
        )

        assert str(app.id) == ulid_id
        assert app.name == "test-app"
        assert app.comments == "Test application"
        assert app.created_at == now
        assert app.updated_at == now
        assert len(app.configuration_ids) == 2
        assert all(isinstance(cid, ULID) for cid in app.configuration_ids)


class TestConfigurationModels:
    """Test configuration-related models."""

    def test_configuration_create_valid(self):
        """Test creating a valid ConfigurationCreate instance."""
        app_id = str(ULIDGenerator())
        config_data = ConfigurationCreate(
            application_id=app_id,
            name="database-config",
            comments="Database configuration",
            config={"host": "localhost", "port": 5432, "ssl": True}
        )

        assert str(config_data.application_id) == app_id
        assert config_data.name == "database-config"
        assert config_data.comments == "Database configuration"
        assert config_data.config["host"] == "localhost"
        assert config_data.config["port"] == 5432
        assert config_data.config["ssl"] is True

    def test_configuration_create_complex_config(self):
        """Test creating configuration with complex nested data."""
        app_id = str(ULIDGenerator())
        complex_config = {
            "database": {
                "primary": {"host": "db1", "port": 5432},
                "replica": {"host": "db2", "port": 5432}
            },
            "features": ["feature1", "feature2"],
            "limits": {"max_connections": 100, "timeout": 30.5}
        }

        config_data = ConfigurationCreate(
            application_id=app_id,
            name="complex-config",
            config=complex_config
        )

        assert config_data.config["database"]["primary"]["host"] == "db1"
        assert config_data.config["features"] == ["feature1", "feature2"]
        assert config_data.config["limits"]["timeout"] == 30.5

    def test_configuration_full_model(self):
        """Test complete Configuration model."""
        app_id = str(ULIDGenerator())
        config_id = str(ULIDGenerator())
        now = datetime.now(UTC)

        config = Configuration(
            id=config_id,
            application_id=app_id,
            name="test-config",
            comments="Test configuration",
            config={"key": "value"},
            created_at=now,
            updated_at=now
        )

        assert str(config.id) == config_id
        assert str(config.application_id) == app_id
        assert config.name == "test-config"
        assert config.comments == "Test configuration"
        assert config.config == {"key": "value"}
        assert config.created_at == now
        assert config.updated_at == now


class TestUtilityModels:
    """Test utility models."""

    def test_pagination_params_defaults(self):
        """Test PaginationParams default values."""
        params = PaginationParams()
        assert params.limit == 50
        assert params.offset == 0

    def test_pagination_params_custom(self):
        """Test PaginationParams with custom values."""
        params = PaginationParams(limit=100, offset=50)
        assert params.limit == 100
        assert params.offset == 50

    def test_pagination_params_validation(self):
        """Test PaginationParams validation rules."""
        # Test minimum limits
        with pytest.raises(ValidationError):
            PaginationParams(limit=0)

        with pytest.raises(ValidationError):
            PaginationParams(offset=-1)

        # Test maximum limits
        with pytest.raises(ValidationError):
            PaginationParams(limit=1001)

    def test_paginated_response(self):
        """Test PaginatedResponse model."""
        apps = [
            {"id": str(ULIDGenerator()), "name": "app1", "comments": None},
            {"id": str(ULIDGenerator()), "name": "app2", "comments": None}
        ]

        response = PaginatedResponse(
            items=apps,
            total=10,
            limit=2,
            offset=0,
            has_more=True
        )

        assert len(response.items) == 2
        assert response.total == 10
        assert response.limit == 2
        assert response.offset == 0
        assert response.has_more is True

    def test_error_response(self):
        """Test ErrorResponse model."""
        error = ErrorResponse(
            error="Validation failed",
            detail="Name field is required",
            code="VALIDATION_ERROR"
        )

        assert error.error == "Validation failed"
        assert error.detail == "Name field is required"
        assert error.code == "VALIDATION_ERROR"

    def test_error_response_minimal(self):
        """Test ErrorResponse with only required fields."""
        error = ErrorResponse(error="Something went wrong")
        assert error.error == "Something went wrong"
        assert error.detail is None
        assert error.code is None