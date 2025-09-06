"""Tests for base model classes."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from pydantic_extra_types.ulid import ULID
from ulid import ULID as ULIDGenerator

from models.base import BaseEntity, BaseCreateModel, BaseUpdateModel, BaseResponseModel


class TestBaseEntity:
    """Test cases for BaseEntity model."""

    def test_base_entity_creation(self):
        """Test creating a BaseEntity with valid data."""
        ulid_id = ULIDGenerator()
        now = datetime.now()

        entity = BaseEntity(id=ulid_id, created_at=now, updated_at=now)

        assert entity.id == ulid_id
        assert entity.created_at == now
        assert entity.updated_at == now

    def test_base_entity_json_serialization(self):
        """Test JSON serialization of BaseEntity."""
        ulid_id = ULIDGenerator()
        now = datetime.now()

        entity = BaseEntity(id=ulid_id, created_at=now, updated_at=now)

        json_data = entity.model_dump()

        assert json_data["id"] == ulid_id
        assert json_data["created_at"] == now
        assert json_data["updated_at"] == now

    def test_base_entity_invalid_id(self):
        """Test BaseEntity with invalid ULID."""
        now = datetime.now()

        with pytest.raises(ValidationError):
            BaseEntity(id="invalid-ulid", created_at=now, updated_at=now)

    def test_base_entity_missing_required_fields(self):
        """Test BaseEntity with missing required fields."""
        with pytest.raises(ValidationError):
            BaseEntity()


class TestBaseCreateModel:
    """Test cases for BaseCreateModel."""

    def test_base_create_model_creation(self):
        """Test creating a BaseCreateModel."""
        model = BaseCreateModel()
        assert isinstance(model, BaseCreateModel)

    def test_base_create_model_config(self):
        """Test BaseCreateModel configuration."""
        model = BaseCreateModel()
        assert model.model_config["from_attributes"] is True


class TestBaseUpdateModel:
    """Test cases for BaseUpdateModel."""

    def test_base_update_model_creation(self):
        """Test creating a BaseUpdateModel."""
        model = BaseUpdateModel()
        assert isinstance(model, BaseUpdateModel)

    def test_base_update_model_config(self):
        """Test BaseUpdateModel configuration."""
        model = BaseUpdateModel()
        assert model.model_config["from_attributes"] is True


class TestBaseResponseModel:
    """Test cases for BaseResponseModel."""

    def test_base_response_model_creation(self):
        """Test creating a BaseResponseModel with valid data."""
        ulid_id = ULIDGenerator()
        now = datetime.now()

        model = BaseResponseModel(id=ulid_id, created_at=now, updated_at=now)

        assert model.id == ulid_id
        assert model.created_at == now
        assert model.updated_at == now

    def test_base_response_model_config(self):
        """Test BaseResponseModel configuration."""
        ulid_id = ULIDGenerator()
        now = datetime.now()

        model = BaseResponseModel(id=ulid_id, created_at=now, updated_at=now)

        assert model.model_config["from_attributes"] is True
        assert "json_encoders" in model.model_config
