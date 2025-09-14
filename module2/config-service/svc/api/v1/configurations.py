"""Configuration API endpoints."""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Query, Path
from ulid import ULID
from typing import Annotated

from models.configuration import (
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationResponse,
)
from services.configuration_service import configuration_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/configurations",
    response_model=ConfigurationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new configuration",
    description="Create a new configuration for an application with a unique name per application",
)
async def create_configuration(
    configuration_data: ConfigurationCreate,
) -> ConfigurationResponse:
    """Create a new configuration.

    Args:
        configuration_data: Configuration creation data

    Returns:
        Created configuration response

    Raises:
        HTTPException: 400 if application doesn't exist or configuration name already exists
        HTTPException: 500 if creation fails
    """
    try:
        return await configuration_service.create_configuration(configuration_data)
    except ValueError as e:
        logger.warning(f"Configuration creation validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/configurations/{configuration_id}",
    response_model=ConfigurationResponse,
    summary="Get configuration by ID",
    description="Get a specific configuration by its ID",
)
async def get_configuration(
    configuration_id: Annotated[
        str, Path(description="Configuration ID (ULID format)")
    ],
) -> ConfigurationResponse:
    """Get configuration by ID.

    Args:
        configuration_id: Configuration ID

    Returns:
        Configuration response

    Raises:
        HTTPException: 404 if configuration not found
        HTTPException: 500 if retrieval fails
    """
    try:
        ulid_id = ULID.from_str(configuration_id)
        configuration = await configuration_service.get_configuration_by_id(ulid_id)
        if not configuration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuration with ID '{configuration_id}' not found",
            )
        return configuration
    except ValueError as e:
        logger.warning(f"Invalid ULID format: {configuration_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ULID format: {configuration_id}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get configuration {configuration_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put(
    "/configurations/{configuration_id}",
    response_model=ConfigurationResponse,
    summary="Update configuration",
    description="Update an existing configuration by ID",
)
async def update_configuration(
    configuration_id: Annotated[
        str, Path(description="Configuration ID (ULID format)")
    ],
    configuration_data: ConfigurationUpdate,
) -> ConfigurationResponse:
    """Update configuration by ID.

    Args:
        configuration_id: Configuration ID
        configuration_data: Configuration update data

    Returns:
        Updated configuration response

    Raises:
        HTTPException: 400 if validation fails
        HTTPException: 404 if configuration not found
        HTTPException: 500 if update fails
    """
    try:
        ulid_id = ULID.from_str(configuration_id)
        configuration = await configuration_service.update_configuration(
            ulid_id, configuration_data
        )
        if not configuration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuration with ID '{configuration_id}' not found",
            )
        return configuration
    except ValueError as e:
        # Check if it's a ULID format error or business logic error
        if "Invalid ULID" in str(e) or "ULID" in str(e):
            logger.warning(f"Invalid ULID format: {configuration_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ULID format: {configuration_id}",
            )
        else:
            logger.warning(f"Configuration update validation error: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update configuration {configuration_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/configurations",
    response_model=List[ConfigurationResponse],
    summary="List configurations",
    description="Get a list of configurations with optional filtering and pagination",
)
async def list_configurations(
    application_id: Optional[str] = Query(
        None, description="Filter configurations by application ID (ULID format)"
    ),
    limit: Optional[int] = Query(
        None, ge=1, le=1000, description="Maximum number of configurations to return"
    ),
    offset: Optional[int] = Query(
        None, ge=0, description="Number of configurations to skip"
    ),
) -> List[ConfigurationResponse]:
    """List configurations with optional filtering and pagination.

    Args:
        application_id: Optional application ID to filter configurations
        limit: Maximum number of configurations to return
        offset: Number of configurations to skip

    Returns:
        List of configuration responses

    Raises:
        HTTPException: 400 if application_id format is invalid
        HTTPException: 500 if retrieval fails
    """
    try:
        # If application_id is provided, filter by application
        if application_id:
            try:
                ulid_app_id = ULID.from_str(application_id)
                return await configuration_service.get_configurations_by_application_id(
                    ulid_app_id, limit=limit, offset=offset
                )
            except ValueError:
                logger.warning(f"Invalid ULID format for application_id: {application_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid ULID format for application_id: {application_id}",
                )
        else:
            # Return all configurations
            return await configuration_service.get_all_configurations(
                limit=limit, offset=offset
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list configurations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete(
    "/configurations/{configuration_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete configuration",
    description="Delete a configuration by ID",
)
async def delete_configuration(
    configuration_id: Annotated[
        str, Path(description="Configuration ID (ULID format)")
    ],
) -> None:
    """Delete configuration by ID.

    Args:
        configuration_id: Configuration ID

    Raises:
        HTTPException: 404 if configuration not found
        HTTPException: 500 if deletion fails
    """
    try:
        ulid_id = ULID.from_str(configuration_id)
        deleted = await configuration_service.delete_configuration(ulid_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuration with ID '{configuration_id}' not found",
            )
    except ValueError as e:
        logger.warning(f"Invalid ULID format: {configuration_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ULID format: {configuration_id}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete configuration {configuration_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
