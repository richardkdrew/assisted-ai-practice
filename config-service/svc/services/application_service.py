"""Application service for business logic operations."""

import logging
from typing import List, Optional

from ulid import ULID

from models.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from repositories.application_repository import application_repository

logger = logging.getLogger(__name__)


class ApplicationService:
    """Service class for application business logic."""

    def __init__(self):
        """Initialize application service."""
        self.repository = application_repository

    async def create_application(
        self, application_data: ApplicationCreate
    ) -> ApplicationResponse:
        """Create a new application.

        Args:
            application_data: Application creation data

        Returns:
            Created application response

        Raises:
            ValueError: If application name already exists
            Exception: If creation fails
        """
        # Check if application name already exists
        existing = await self.repository.get_by_name(application_data.name)
        if existing:
            raise ValueError(
                f"Application with name '{application_data.name}' already exists"
            )

        try:
            # Create application
            entity = await self.repository.create(application_data.model_dump())

            # Get configuration IDs for the response
            config_ids = await self.repository.get_configuration_ids_by_application_id(
                entity.id
            )

            return ApplicationResponse(
                id=entity.id,
                name=entity.name,
                comments=entity.comments,
                configuration_ids=config_ids,
                created_at=entity.created_at,
                updated_at=entity.updated_at,
            )
        except Exception as e:
            logger.error(f"Failed to create application: {e}")
            raise

    async def get_application_by_id(
        self, application_id: ULID
    ) -> Optional[ApplicationResponse]:
        """Get application by ID.

        Args:
            application_id: Application ID

        Returns:
            Application response if found, None otherwise
        """
        try:
            entity = await self.repository.get_by_id(application_id)
            if not entity:
                return None

            # Get configuration IDs for the response
            config_ids = await self.repository.get_configuration_ids_by_application_id(
                entity.id
            )

            return ApplicationResponse(
                id=entity.id,
                name=entity.name,
                comments=entity.comments,
                configuration_ids=config_ids,
                created_at=entity.created_at,
                updated_at=entity.updated_at,
            )
        except Exception as e:
            logger.error(f"Failed to get application {application_id}: {e}")
            raise

    async def update_application(
        self, application_id: ULID, application_data: ApplicationUpdate
    ) -> Optional[ApplicationResponse]:
        """Update application by ID.

        Args:
            application_id: Application ID
            application_data: Application update data

        Returns:
            Updated application response if found, None otherwise

        Raises:
            ValueError: If application name already exists for another application
            Exception: If update fails
        """
        # Check if application exists
        existing = await self.repository.get_by_id(application_id)
        if not existing:
            return None

        # Check if new name conflicts with existing application
        if application_data.name and application_data.name != existing.name:
            name_conflict = await self.repository.get_by_name(application_data.name)
            if name_conflict and name_conflict.id != application_id:
                raise ValueError(
                    f"Application with name '{application_data.name}' already exists"
                )

        try:
            # Update application
            update_data = application_data.model_dump(exclude_unset=True)
            entity = await self.repository.update(application_id, update_data)

            if not entity:
                return None

            # Get configuration IDs for the response
            config_ids = await self.repository.get_configuration_ids_by_application_id(
                entity.id
            )

            return ApplicationResponse(
                id=entity.id,
                name=entity.name,
                comments=entity.comments,
                configuration_ids=config_ids,
                created_at=entity.created_at,
                updated_at=entity.updated_at,
            )
        except Exception as e:
            logger.error(f"Failed to update application {application_id}: {e}")
            raise

    async def get_all_applications(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[ApplicationResponse]:
        """Get all applications with optional pagination.

        Args:
            limit: Maximum number of applications to return
            offset: Number of applications to skip

        Returns:
            List of application responses
        """
        try:
            entities = await self.repository.get_all(limit=limit, offset=offset)

            # Build response list with configuration IDs
            responses = []
            for entity in entities:
                config_ids = (
                    await self.repository.get_configuration_ids_by_application_id(
                        entity.id
                    )
                )
                responses.append(
                    ApplicationResponse(
                        id=entity.id,
                        name=entity.name,
                        comments=entity.comments,
                        configuration_ids=config_ids,
                        created_at=entity.created_at,
                        updated_at=entity.updated_at,
                    )
                )

            return responses
        except Exception as e:
            logger.error(f"Failed to get all applications: {e}")
            raise

    async def delete_application(self, application_id: ULID) -> bool:
        """Delete application by ID.

        Args:
            application_id: Application ID

        Returns:
            True if application was deleted, False if not found
        """
        try:
            return await self.repository.delete_by_id(application_id)
        except Exception as e:
            logger.error(f"Failed to delete application {application_id}: {e}")
            raise


# Global application service instance
application_service = ApplicationService()
