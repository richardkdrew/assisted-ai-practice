"""Pydantic models for Configuration Service."""

from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field
from pydantic_extra_types.ulid import ULID


class ApplicationBase(BaseModel):
    """Base application model with common fields."""
    name: str = Field(..., max_length=256, description="Unique application name")
    comments: Optional[str] = Field(None, max_length=1024, description="Optional comments")


class ApplicationCreate(ApplicationBase):
    """Model for creating a new application."""
    pass


class ApplicationUpdate(ApplicationBase):
    """Model for updating an existing application."""
    pass


class Application(ApplicationBase):
    """Complete application model with all fields."""
    id: ULID = Field(..., description="Unique application identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    configuration_ids: List[ULID] = Field(default_factory=list, description="Related configuration IDs")

    model_config = {"from_attributes": True}


class ConfigurationBase(BaseModel):
    """Base configuration model with common fields."""
    application_id: ULID = Field(..., description="Associated application ID")
    name: str = Field(..., max_length=256, description="Configuration name, unique per application")
    comments: Optional[str] = Field(None, max_length=1024, description="Optional comments")
    config: Dict[str, Any] = Field(..., description="Configuration data as key-value pairs")


class ConfigurationCreate(ConfigurationBase):
    """Model for creating a new configuration."""
    pass


class ConfigurationUpdate(ConfigurationBase):
    """Model for updating an existing configuration."""
    pass


class Configuration(ConfigurationBase):
    """Complete configuration model with all fields."""
    id: ULID = Field(..., description="Unique configuration identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum number of items to return")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Number of items skipped")
    has_more: bool = Field(..., description="Whether there are more items available")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    code: Optional[str] = Field(None, description="Error code")