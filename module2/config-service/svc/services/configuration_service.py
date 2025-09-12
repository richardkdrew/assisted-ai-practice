"""Configuration service for business logic operations."""

import logging
from typing import List, Optional

from ulid import ULID

from models.configuration import (
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationResponse,
)
from repositories.configuration_repository import configuration_repository
from repositories.application_repository import application_repository

logger = logging.getLogger(__name__)


class ConfigurationService:
    """Service class for configuration business logic."""

    def __init__(self):
        """Initialize configuration service."""
        self.repository = configuration_repository
        self.application_repository = application_repository

    async def create_configuration(
        self, configuration_data: ConfigurationCreate
    ) -> ConfigurationResponse:
        """Create a new configuration.

        Args:
            configuration_data: Configuration creation data

        Returns:
            Created configuration response

        Raises:
            ValueError: If application doesn't exist or configuration name already exists for the application
            Exception: If creation fails
        """
        # Check if application exists
        application = await self.application_repository.get_by_id(
            configuration_data.application_id
        )
        if not application:
            raise ValueError(
                f"Application with ID '{configuration_data.application_id}' does not exist"
            )

        # Check if configuration name already exists for this application
        existing = await self.repository.get_by_application_and_name(
            configuration_data.application_id, configuration_data.name
        )
        if existing:
            raise ValueError(
                f"Configuration with name '{configuration_data.name}' already exists for application '{application.name}'"
            )

        try:
            # Create configuration
            entity = await self.repository.create(configuration_data.model_dump())

            return ConfigurationResponse(
                id=entity.id,
                application_id=entity.application_id,
                name=entity.name,
                comments=entity.comments,
                config=entity.config,
                created_at=entity.created_at,
                updated_at=entity.updated_at,
            )
        except Exception as e:
            logger.error(f"Failed to create configuration: {e}")
            raise

    async def get_configuration_by_id(
        self, configuration_id: ULID
    ) -> Optional[ConfigurationResponse]:
        """Get configuration by ID.

        Args:
            configuration_id: Configuration ID

        Returns:
            Configuration response if found, None otherwise
        """
        try:
            entity = await self.repository.get_by_id(configuration_id)
            if not entity:
                return None

            return ConfigurationResponse(
                id=entity.id,
                application_id=entity.application_id,
                name=entity.name,
                comments=entity.comments,
                config=entity.config,
                created_at=entity.created_at,
                updated_at=entity.updated_at,
            )
        except Exception as e:
            logger.error(f"Failed to get configuration {configuration_id}: {e}")
            raise

    async def update_configuration(
        self, configuration_id: ULID, configuration_data: ConfigurationUpdate
    ) -> Optional[ConfigurationResponse]:
        """Update configuration by ID.

        Args:
            configuration_id: Configuration ID
            configuration_data: Configuration update data

        Returns:
            Updated configuration response if found, None otherwise

        Raises:
            ValueError: If configuration name already exists for the application
            Exception: If update fails
        """
        # Check if configuration exists
        existing = await self.repository.get_by_id(configuration_id)
        if not existing:
            return None

        # Check if new name conflicts with existing configuration for the same application
        if configuration_data.name and configuration_data.name != existing.name:
            name_conflict = await self.repository.get_by_application_and_name(
                existing.application_id, configuration_data.name
            )
            if name_conflict and name_conflict.id != configuration_id:
                raise ValueError(
                    f"Configuration with name '{configuration_data.name}' already exists for this application"
                )

        try:
            # Update configuration
            update_data = configuration_data.model_dump(exclude_unset=True)
            entity = await self.repository.update(configuration_id, update_data)

            if not entity:
                return None

            return ConfigurationResponse(
                id=entity.id,
                application_id=entity.application_id,
                name=entity.name,
                comments=entity.comments,
                config=entity.config,
                created_at=entity.created_at,
                updated_at=entity.updated_at,
            )
        except Exception as e:
            logger.error(f"Failed to update configuration {configuration_id}: {e}")
            raise

    async def get_all_configurations(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[ConfigurationResponse]:
        """Get all configurations with optional pagination.

        Args:
            limit: Maximum number of configurations to return
            offset: Number of configurations to skip

        Returns:
            List of configuration responses
        """
        try:
            entities = await self.repository.get_all(limit=limit, offset=offset)

            return [
                ConfigurationResponse(
                    id=entity.id,
                    application_id=entity.application_id,
                    name=entity.name,
                    comments=entity.comments,
                    config=entity.config,
                    created_at=entity.created_at,
                    updated_at=entity.updated_at,
                )
                for entity in entities
            ]
        except Exception as e:
            logger.error(f"Failed to get all configurations: {e}")
            raise

    async def get_configurations_by_application_id(
        self,
        application_id: ULID,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[ConfigurationResponse]:
        """Get all configurations for a specific application.

        Args:
            application_id: Application ID
            limit: Maximum number of configurations to return
            offset: Number of configurations to skip

        Returns:
            List of configuration responses

        Raises:
            ValueError: If application doesn't exist
        """
        # Check if application exists
        application = await self.application_repository.get_by_id(application_id)
        if not application:
            raise ValueError(f"Application with ID '{application_id}' does not exist")

        try:
            entities = await self.repository.get_by_application_id(
                application_id, limit=limit, offset=offset
            )

            return [
                ConfigurationResponse(
                    id=entity.id,
                    application_id=entity.application_id,
                    name=entity.name,
                    comments=entity.comments,
                    config=entity.config,
                    created_at=entity.created_at,
                    updated_at=entity.updated_at,
                )
                for entity in entities
            ]
        except Exception as e:
            logger.error(
                f"Failed to get configurations for application {application_id}: {e}"
            )
            raise

    async def delete_configuration(self, configuration_id: ULID) -> bool:
        """Delete configuration by ID.

        Args:
            configuration_id: Configuration ID

        Returns:
            True if configuration was deleted, False if not found
        """
        try:
            return await self.repository.delete_by_id(configuration_id)
        except Exception as e:
            logger.error(f"Failed to delete configuration {configuration_id}: {e}")
            raise


# Global configuration service instance
configuration_service = ConfigurationService()
