"""Tests for application model classes."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from pydantic_extra_types.ulid import ULID
from ulid import ULID as ULIDGenerator

from models.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationEntity,
)


class TestApplicationCreate:
    """Test cases for ApplicationCreate model."""

    def test_application_create_valid_data(self):
        """Test creating ApplicationCreate with valid data."""
        data = ApplicationCreate(name="test-app", comments="Test application")

        assert data.name == "test-app"
        assert data.comments == "Test application"

    def test_application_create_name_only(self):
        """Test creating ApplicationCreate with name only."""
        data = ApplicationCreate(name="test-app")

        assert data.name == "test-app"
        assert data.comments is None

    def test_application_create_missing_name(self):
        """Test ApplicationCreate validation with missing name."""
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreate()

        assert "name" in str(exc_info.value)

    def test_application_create_name_too_long(self):
        """Test ApplicationCreate validation with name too long."""
        long_name = "a" * 257  # Exceeds 256 character limit

        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreate(name=long_name)

        assert "String should have at most 256 characters" in str(exc_info.value)

    def test_application_create_comments_too_long(self):
        """Test ApplicationCreate validation with comments too long."""
        long_comments = "a" * 1025  # Exceeds 1024 character limit

        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreate(name="test-app", comments=long_comments)

        assert "String should have at most 1024 characters" in str(exc_info.value)

    def test_application_create_serialization(self):
        """Test ApplicationCreate serialization."""
        data = ApplicationCreate(name="test-app", comments="Test application")

        serialized = data.model_dump()

        assert serialized["name"] == "test-app"
        assert serialized["comments"] == "Test application"


class TestApplicationUpdate:
    """Test cases for ApplicationUpdate model."""

    def test_application_update_all_fields(self):
        """Test ApplicationUpdate with all fields."""
        data = ApplicationUpdate(name="updated-app", comments="Updated comments")

        assert data.name == "updated-app"
        assert data.comments == "Updated comments"

    def test_application_update_name_only(self):
        """Test ApplicationUpdate with name only."""
        data = ApplicationUpdate(name="updated-app")

        assert data.name == "updated-app"
        assert data.comments is None

    def test_application_update_comments_only(self):
        """Test ApplicationUpdate with comments only."""
        data = ApplicationUpdate(comments="Updated comments")

        assert data.name is None
        assert data.comments == "Updated comments"

    def test_application_update_empty(self):
        """Test ApplicationUpdate with no fields."""
        data = ApplicationUpdate()

        assert data.name is None
        assert data.comments is None

    def test_application_update_name_too_long(self):
        """Test ApplicationUpdate validation with name too long."""
        long_name = "a" * 257

        with pytest.raises(ValidationError) as exc_info:
            ApplicationUpdate(name=long_name)

        assert "String should have at most 256 characters" in str(exc_info.value)

    def test_application_update_exclude_unset(self):
        """Test ApplicationUpdate exclude_unset functionality."""
        data = ApplicationUpdate(name="updated-app")

        serialized = data.model_dump(exclude_unset=True)

        assert "name" in serialized
        assert "comments" not in serialized


class TestApplicationResponse:
    """Test cases for ApplicationResponse model."""

    def test_application_response_creation(self):
        """Test creating ApplicationResponse with valid data."""
        ulid_id = ULIDGenerator()
        config_ids = [ULIDGenerator(), ULIDGenerator()]
        now = datetime.now()

        response = ApplicationResponse(
            id=ulid_id,
            name="test-app",
            comments="Test application",
            configuration_ids=config_ids,
            created_at=now,
            updated_at=now,
        )

        assert response.id == ulid_id
        assert response.name == "test-app"
        assert response.comments == "Test application"
        assert response.configuration_ids == config_ids
        assert response.created_at == now
        assert response.updated_at == now

    def test_application_response_empty_config_ids(self):
        """Test ApplicationResponse with empty configuration_ids."""
        ulid_id = ULIDGenerator()
        now = datetime.now()

        response = ApplicationResponse(
            id=ulid_id, name="test-app", comments=None, created_at=now, updated_at=now
        )

        assert response.configuration_ids == []

    def test_application_response_serialization(self):
        """Test ApplicationResponse serialization."""
        ulid_id = ULIDGenerator()
        config_ids = [ULIDGenerator()]
        now = datetime.now()

        response = ApplicationResponse(
            id=ulid_id,
            name="test-app",
            comments="Test application",
            configuration_ids=config_ids,
            created_at=now,
            updated_at=now,
        )

        serialized = response.model_dump()

        assert serialized["id"] == ulid_id
        assert serialized["name"] == "test-app"
        assert serialized["comments"] == "Test application"
        assert serialized["configuration_ids"] == config_ids
        assert serialized["created_at"] == now
        assert serialized["updated_at"] == now


class TestApplicationEntity:
    """Test cases for ApplicationEntity model."""

    def test_application_entity_creation(self):
        """Test creating ApplicationEntity with valid data."""
        ulid_id = ULIDGenerator()
        now = datetime.now()

        entity = ApplicationEntity(
            id=ulid_id,
            name="test-app",
            comments="Test application",
            created_at=now,
            updated_at=now,
        )

        assert entity.id == ulid_id
        assert entity.name == "test-app"
        assert entity.comments == "Test application"
        assert entity.created_at == now
        assert entity.updated_at == now

    def test_application_entity_no_comments(self):
        """Test ApplicationEntity with no comments."""
        ulid_id = ULIDGenerator()
        now = datetime.now()

        entity = ApplicationEntity(
            id=ulid_id, name="test-app", created_at=now, updated_at=now
        )

        assert entity.comments is None

    def test_application_entity_from_dict(self):
        """Test creating ApplicationEntity from dictionary."""
        ulid_id = ULIDGenerator()
        now = datetime.now()

        data = {
            "id": ulid_id,
            "name": "test-app",
            "comments": "Test application",
            "created_at": now,
            "updated_at": now,
        }

        entity = ApplicationEntity(**data)

        assert entity.id == ulid_id
        assert entity.name == "test-app"
        assert entity.comments == "Test application"
