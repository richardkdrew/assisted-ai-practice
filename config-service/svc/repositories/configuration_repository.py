"""Configuration repository for data access operations."""

import json
import logging
from typing import Dict, Any, List, Optional

from ulid import ULID

from database.connection import db_manager
from models.configuration import ConfigurationEntity
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ConfigurationRepository(BaseRepository[ConfigurationEntity]):
    """Repository for configuration data access operations."""

    def __init__(self):
        """Initialize configuration repository."""
        super().__init__(db_manager, "configurations")

    async def create(self, entity_data: Dict[str, Any]) -> ConfigurationEntity:
        """Create a new configuration.

        Args:
            entity_data: Configuration data dictionary

        Returns:
            Created configuration entity

        Raises:
            Exception: If configuration creation fails
        """
        configuration_id = self.generate_ulid()

        query = """
            INSERT INTO configurations (id, application_id, name, comments, config)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, application_id, name, comments, config, created_at, updated_at
        """

        params = (
            str(configuration_id),
            str(entity_data.get("application_id")),
            entity_data.get("name"),
            entity_data.get("comments"),
            json.dumps(entity_data.get("config", {})),
        )

        try:
            result = await self.db_manager.execute_query(query, params)
            if not result:
                raise Exception("Failed to create configuration")

            return ConfigurationEntity(
                id=ULID.from_str(result["id"]),
                application_id=ULID.from_str(result["application_id"]),
                name=result["name"],
                comments=result["comments"],
                config=self.deserialize_json_field(result["config"]),
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        except Exception as e:
            logger.error(f"Failed to create configuration: {e}")
            raise

    async def get_by_id(self, entity_id: ULID) -> Optional[ConfigurationEntity]:
        """Get configuration by ID.

        Args:
            entity_id: Configuration ID

        Returns:
            Configuration entity if found, None otherwise
        """
        query = """
            SELECT id, application_id, name, comments, config, created_at, updated_at
            FROM configurations
            WHERE id = %s
        """

        try:
            result = await self.db_manager.execute_query(query, (str(entity_id),))
            if not result:
                return None

            return ConfigurationEntity(
                id=ULID.from_str(result["id"]),
                application_id=ULID.from_str(result["application_id"]),
                name=result["name"],
                comments=result["comments"],
                config=self.deserialize_json_field(result["config"]),
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        except Exception as e:
            logger.error(f"Failed to get configuration by ID {entity_id}: {e}")
            raise

    async def get_by_application_and_name(
        self, application_id: ULID, name: str
    ) -> Optional[ConfigurationEntity]:
        """Get configuration by application ID and name.

        Args:
            application_id: Application ID
            name: Configuration name

        Returns:
            Configuration entity if found, None otherwise
        """
        query = """
            SELECT id, application_id, name, comments, config, created_at, updated_at
            FROM configurations
            WHERE application_id = %s AND name = %s
        """

        try:
            result = await self.db_manager.execute_query(
                query, (str(application_id), name)
            )
            if not result:
                return None

            return ConfigurationEntity(
                id=ULID.from_str(result["id"]),
                application_id=ULID.from_str(result["application_id"]),
                name=result["name"],
                comments=result["comments"],
                config=self.deserialize_json_field(result["config"]),
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        except Exception as e:
            logger.error(
                f"Failed to get configuration by application {application_id} and name {name}: {e}"
            )
            raise

    async def update(
        self, entity_id: ULID, entity_data: Dict[str, Any]
    ) -> Optional[ConfigurationEntity]:
        """Update configuration by ID.

        Args:
            entity_id: Configuration ID
            entity_data: Updated configuration data

        Returns:
            Updated configuration entity if found, None otherwise
        """
        if not await self.exists_by_id(entity_id):
            return None

        # Build dynamic update query
        update_fields = []
        params = []

        if "name" in entity_data:
            update_fields.append("name = %s")
            params.append(entity_data["name"])

        if "comments" in entity_data:
            update_fields.append("comments = %s")
            params.append(entity_data["comments"])

        if "config" in entity_data:
            update_fields.append("config = %s")
            params.append(json.dumps(entity_data["config"]))

        if not update_fields:
            # No fields to update, return current entity
            return await self.get_by_id(entity_id)

        params.append(str(entity_id))

        query = f"""
            UPDATE configurations
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, application_id, name, comments, config, created_at, updated_at
        """

        try:
            result = await self.db_manager.execute_query(query, tuple(params))
            if not result:
                return None

            return ConfigurationEntity(
                id=ULID.from_str(result["id"]),
                application_id=ULID.from_str(result["application_id"]),
                name=result["name"],
                comments=result["comments"],
                config=self.deserialize_json_field(result["config"]),
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        except Exception as e:
            logger.error(f"Failed to update configuration {entity_id}: {e}")
            raise

    async def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[ConfigurationEntity]:
        """Get all configurations with optional pagination.

        Args:
            limit: Maximum number of configurations to return
            offset: Number of configurations to skip

        Returns:
            List of configuration entities
        """
        query = """
            SELECT id, application_id, name, comments, config, created_at, updated_at
            FROM configurations
            ORDER BY created_at DESC
        """

        params = []
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        if offset is not None:
            query += " OFFSET %s"
            params.append(offset)

        try:
            results = await self.db_manager.execute_query_many(
                query, tuple(params) if params else None
            )

            return [
                ConfigurationEntity(
                    id=ULID.from_str(row["id"]),
                    application_id=ULID.from_str(row["application_id"]),
                    name=row["name"],
                    comments=row["comments"],
                    config=self.deserialize_json_field(row["config"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in results
            ]
        except Exception as e:
            logger.error(f"Failed to get all configurations: {e}")
            raise

    async def get_by_application_id(
        self,
        application_id: ULID,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[ConfigurationEntity]:
        """Get all configurations for a specific application.

        Args:
            application_id: Application ID
            limit: Maximum number of configurations to return
            offset: Number of configurations to skip

        Returns:
            List of configuration entities
        """
        query = """
            SELECT id, application_id, name, comments, config, created_at, updated_at
            FROM configurations
            WHERE application_id = %s
            ORDER BY created_at DESC
        """

        params = [str(application_id)]
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        if offset is not None:
            query += " OFFSET %s"
            params.append(offset)

        try:
            results = await self.db_manager.execute_query_many(query, tuple(params))

            return [
                ConfigurationEntity(
                    id=ULID.from_str(row["id"]),
                    application_id=ULID.from_str(row["application_id"]),
                    name=row["name"],
                    comments=row["comments"],
                    config=self.deserialize_json_field(row["config"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in results
            ]
        except Exception as e:
            logger.error(
                f"Failed to get configurations for application {application_id}: {e}"
            )
            raise


# Global configuration repository instance
configuration_repository = ConfigurationRepository()
