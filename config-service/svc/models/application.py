"""Application data models."""

from typing import Optional, List
from pydantic import Field
from ulid import ULID

from models.base import BaseCreateModel, BaseUpdateModel, BaseResponseModel


class ApplicationCreate(BaseCreateModel):
    """Model for creating a new application."""

    name: str = Field(..., max_length=256, description="Unique application name")
    comments: Optional[str] = Field(
        None, max_length=1024, description="Optional comments"
    )


class ApplicationUpdate(BaseUpdateModel):
    """Model for updating an existing application."""

    name: Optional[str] = Field(
        None, max_length=256, description="Unique application name"
    )
    comments: Optional[str] = Field(
        None, max_length=1024, description="Optional comments"
    )


class ApplicationResponse(BaseResponseModel):
    """Model for application API responses."""

    name: str = Field(..., description="Application name")
    comments: Optional[str] = Field(None, description="Application comments")
    configuration_ids: List[ULID] = Field(
        default_factory=list, description="List of related configuration IDs"
    )


class ApplicationEntity(BaseResponseModel):
    """Internal application entity model for database operations."""

    name: str
    comments: Optional[str] = None
