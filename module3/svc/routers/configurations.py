"""Configurations API endpoints."""

import logging

from fastapi import APIRouter, HTTPException
from pydantic_extra_types.ulid import ULID

from ..models import Configuration, ConfigurationCreate, ConfigurationUpdate
from ..repository import config_repository

logger = logging.getLogger(__name__)
router = APIRouter()


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
async def get_configuration(config_id: ULID) -> Configuration:
    """Get configuration by ID."""
    configuration = await config_repository.get_by_id(config_id)
    if not configuration:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return configuration


@router.put("/{config_id}", response_model=Configuration)
async def update_configuration(config_id: ULID, config_data: ConfigurationUpdate) -> Configuration:
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
async def delete_configuration(config_id: ULID):
    """Delete a configuration."""
    success = await config_repository.delete(config_id)
    if not success:
        raise HTTPException(status_code=404, detail="Configuration not found")