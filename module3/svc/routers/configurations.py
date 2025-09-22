"""Configurations API endpoints."""

import logging

from fastapi import APIRouter, HTTPException
from pydantic_extra_types.ulid import ULID

try:
    from ..models import Configuration, ConfigurationCreate, ConfigurationUpdate, PaginatedResponse
    from ..repository import config_repository
except ImportError:
    from models import Configuration, ConfigurationCreate, ConfigurationUpdate, PaginatedResponse
    from repository import config_repository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=PaginatedResponse[Configuration])
async def get_configurations(application_id: str = None, limit: int = 50, offset: int = 0) -> PaginatedResponse[Configuration]:
    """Get all configurations with optional filtering by application."""
    try:
        # Get configurations from repository with pagination
        configurations = await config_repository.list_all(
            application_id=application_id,
            limit=limit,
            offset=offset
        )
        total = await config_repository.count(application_id=application_id)

        return PaginatedResponse(
            items=configurations,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )
    except Exception as e:
        logger.error(f"Failed to get configurations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Configuration, status_code=201)
async def create_configuration(config_data: ConfigurationCreate) -> Configuration:
    """Create a new configuration."""
    try:
        return await config_repository.create(config_data)
    except ValueError as e:
        # Handle duplicate name within application
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create configuration: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{config_id}", response_model=Configuration)
async def get_configuration(config_id: str) -> Configuration:
    """Get configuration by ID."""
    configuration = await config_repository.get_by_id(config_id)
    if not configuration:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return configuration


@router.put("/{config_id}", response_model=Configuration)
async def update_configuration(config_id: str, config_data: ConfigurationUpdate) -> Configuration:
    """Update an existing configuration."""
    try:
        configuration = await config_repository.update(config_id, config_data)
        if not configuration:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return configuration
    except ValueError as e:
        # Handle duplicate name within application
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update configuration {config_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{config_id}", status_code=204)
async def delete_configuration(config_id: str):
    """Delete a configuration."""
    try:
        ulid_id = ULID.from_str(config_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid configuration ID format")

    success = await config_repository.delete(ulid_id)
    if not success:
        raise HTTPException(status_code=404, detail="Configuration not found")