"""Application API endpoints."""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Query, Path
from ulid import ULID
from typing import Annotated

from models.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from models.configuration import ConfigurationResponse
from services.application_service import application_service
from services.configuration_service import configuration_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new application",
    description="Create a new application with a unique name",
)
async def create_application(
    application_data: ApplicationCreate,
) -> ApplicationResponse:
    """Create a new application.

    Args:
        application_data: Application creation data

    Returns:
        Created application response

    Raises:
        HTTPException: 400 if application name already exists
        HTTPException: 500 if creation fails
    """
    try:
        return await application_service.create_application(application_data)
    except ValueError as e:
        logger.warning(f"Application creation validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/applications/{application_id}",
    response_model=ApplicationResponse,
    summary="Get application by ID",
    description="Get a specific application by its ID, including related configuration IDs",
)
async def get_application(
    application_id: Annotated[str, Path(description="Application ID (ULID format)")],
) -> ApplicationResponse:
    """Get application by ID.

    Args:
        application_id: Application ID

    Returns:
        Application response

    Raises:
        HTTPException: 404 if application not found
        HTTPException: 500 if retrieval fails
    """
    try:
        ulid_id = ULID.from_str(application_id)
        application = await application_service.get_application_by_id(ulid_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID '{application_id}' not found",
            )
        return application
    except ValueError as e:
        logger.warning(f"Invalid ULID format: {application_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ULID format: {application_id}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get application {application_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put(
    "/applications/{application_id}",
    response_model=ApplicationResponse,
    summary="Update application",
    description="Update an existing application by ID",
)
async def update_application(
    application_id: Annotated[str, Path(description="Application ID (ULID format)")],
    application_data: ApplicationUpdate,
) -> ApplicationResponse:
    """Update application by ID.

    Args:
        application_id: Application ID
        application_data: Application update data

    Returns:
        Updated application response

    Raises:
        HTTPException: 400 if validation fails
        HTTPException: 404 if application not found
        HTTPException: 500 if update fails
    """
    try:
        ulid_id = ULID.from_str(application_id)
        application = await application_service.update_application(
            ulid_id, application_data
        )
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID '{application_id}' not found",
            )
        return application
    except ValueError as e:
        # Check if it's a ULID format error or business logic error
        if "Invalid ULID" in str(e) or "ULID" in str(e):
            logger.warning(f"Invalid ULID format: {application_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ULID format: {application_id}",
            )
        else:
            logger.warning(f"Application update validation error: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update application {application_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/applications",
    response_model=List[ApplicationResponse],
    summary="List all applications",
    description="Get a list of all applications with optional pagination",
)
async def list_applications(
    limit: Optional[int] = Query(
        None, ge=1, le=1000, description="Maximum number of applications to return"
    ),
    offset: Optional[int] = Query(
        None, ge=0, description="Number of applications to skip"
    ),
) -> List[ApplicationResponse]:
    """List all applications with optional pagination.

    Args:
        limit: Maximum number of applications to return
        offset: Number of applications to skip

    Returns:
        List of application responses

    Raises:
        HTTPException: 500 if retrieval fails
    """
    try:
        return await application_service.get_all_applications(
            limit=limit, offset=offset
        )
    except Exception as e:
        logger.error(f"Failed to list applications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/applications/{application_id}/configurations",
    response_model=List[ConfigurationResponse],
    summary="List configurations for an application",
    description="Get all configurations for a specific application with optional pagination",
)
async def list_configurations_by_application(
    application_id: Annotated[str, Path(description="Application ID (ULID format)")],
    limit: Optional[int] = Query(
        None, ge=1, le=1000, description="Maximum number of configurations to return"
    ),
    offset: Optional[int] = Query(
        None, ge=0, description="Number of configurations to skip"
    ),
) -> List[ConfigurationResponse]:
    """List all configurations for a specific application.

    Args:
        application_id: Application ID
        limit: Maximum number of configurations to return
        offset: Number of configurations to skip

    Returns:
        List of configuration responses

    Raises:
        HTTPException: 400 if application doesn't exist
        HTTPException: 500 if retrieval fails
    """
    try:
        ulid_id = ULID.from_str(application_id)
        return await configuration_service.get_configurations_by_application_id(
            ulid_id, limit=limit, offset=offset
        )
    except ValueError as e:
        # Check if it's a ULID format error or business logic error
        if "Invalid ULID" in str(e) or "ULID" in str(e):
            logger.warning(f"Invalid ULID format: {application_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ULID format: {application_id}",
            )
        else:
            logger.warning(f"Configuration listing validation error: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(
            f"Failed to list configurations for application {application_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete(
    "/applications/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete application",
    description="Delete an application by ID (this will also delete all related configurations)",
)
async def delete_application(
    application_id: Annotated[str, Path(description="Application ID (ULID format)")],
) -> None:
    """Delete application by ID.

    Args:
        application_id: Application ID

    Raises:
        HTTPException: 404 if application not found
        HTTPException: 500 if deletion fails
    """
    try:
        ulid_id = ULID.from_str(application_id)
        deleted = await application_service.delete_application(ulid_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID '{application_id}' not found",
            )
    except ValueError as e:
        logger.warning(f"Invalid ULID format: {application_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ULID format: {application_id}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete application {application_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
