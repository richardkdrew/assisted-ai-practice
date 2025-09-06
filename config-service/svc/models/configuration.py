"""Configuration data models."""

from typing import Optional, Dict, Any
from pydantic import Field
from ulid import ULID

from models.base import BaseCreateModel, BaseUpdateModel, BaseResponseModel


class ConfigurationCreate(BaseCreateModel):
    """Model for creating a new configuration."""

    application_id: ULID = Field(..., description="ID of the parent application")
    name: str = Field(
        ..., max_length=256, description="Configuration name (unique per application)"
    )
    comments: Optional[str] = Field(
        None, max_length=1024, description="Optional comments"
    )
    config: Dict[str, Any] = Field(
        ..., description="Configuration data as key-value pairs"
    )


class ConfigurationUpdate(BaseUpdateModel):
    """Model for updating an existing configuration."""

    name: Optional[str] = Field(None, max_length=256, description="Configuration name")
    comments: Optional[str] = Field(
        None, max_length=1024, description="Optional comments"
    )
    config: Optional[Dict[str, Any]] = Field(
        None, description="Configuration data as key-value pairs"
    )


class ConfigurationResponse(BaseResponseModel):
    """Model for configuration API responses."""

    application_id: ULID = Field(..., description="ID of the parent application")
    name: str = Field(..., description="Configuration name")
    comments: Optional[str] = Field(None, description="Configuration comments")
    config: Dict[str, Any] = Field(
        ..., description="Configuration data as key-value pairs"
    )


class ConfigurationEntity(BaseResponseModel):
    """Internal configuration entity model for database operations."""

    application_id: ULID
    name: str
    comments: Optional[str] = None
    config: Dict[str, Any]
