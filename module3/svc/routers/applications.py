"""Applications API endpoints."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Query
from pydantic_extra_types.ulid import ULID

try:
    from ..models import Application, ApplicationCreate, ApplicationUpdate, PaginationParams, PaginatedResponse
    from ..repository import app_repository
    from ..observability import update_business_metrics
except ImportError:
    from models import Application, ApplicationCreate, ApplicationUpdate, PaginationParams, PaginatedResponse
    from repository import app_repository
    from observability import update_business_metrics

logger = logging.getLogger(__name__)
router = APIRouter()


async def _update_metrics():
    """Update business metrics with current counts."""
    try:
        app_count = await app_repository.count()
        # For now, we'll set configs and db connections to 0
        # These would need to be calculated from their respective repositories
        update_business_metrics(app_count, 0, 0)
    except Exception as e:
        logger.warning(f"Failed to update business metrics: {e}")


@router.post("/", response_model=Application, status_code=201)
async def create_application(application_data: ApplicationCreate) -> Application:
    """Create a new application."""
    try:
        application = await app_repository.create(application_data)
        await _update_metrics()  # Update metrics after creating
        return application
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{app_id}", response_model=Application)
async def get_application(app_id: str) -> Application:
    """Get application by ID, includes list of all related configuration IDs."""
    application = await app_repository.get_by_id(app_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.put("/{app_id}", response_model=Application)
async def update_application(app_id: str, application_data: ApplicationUpdate) -> Application:
    """Update an existing application."""
    try:
        application = await app_repository.update(app_id, application_data)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        return application
    except Exception as e:
        logger.error(f"Failed to update application {app_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PaginatedResponse)
async def list_applications(
    limit: int = Query(default=50, ge=1, le=1000, description="Maximum number of items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip")
) -> PaginatedResponse:
    """List all applications with pagination."""
    try:
        applications = await app_repository.list_all(limit=limit, offset=offset)
        total = await app_repository.count()

        return PaginatedResponse(
            items=applications,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )
    except Exception as e:
        logger.error(f"Failed to list applications: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{app_id}", status_code=204)
async def delete_application(app_id: str):
    """Delete an application and all its configurations."""
    success = await app_repository.delete(app_id)
    if not success:
        raise HTTPException(status_code=404, detail="Application not found")
    await _update_metrics()  # Update metrics after deletion