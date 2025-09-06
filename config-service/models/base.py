"""Base model classes for the Config Service."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_extra_types.ulid import ULID


class BaseEntity(BaseModel):
    """Base entity model with common fields."""

    id: ULID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat(), ULID: lambda v: str(v)}


class BaseCreateModel(BaseModel):
    """Base model for create operations."""

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class BaseUpdateModel(BaseModel):
    """Base model for update operations."""

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class BaseResponseModel(BaseEntity):
    """Base model for API responses."""

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat(), ULID: lambda v: str(v)}
