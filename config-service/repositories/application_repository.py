"""Application repository for data access operations."""

import logging
from typing import Dict, Any, List, Optional

from pydantic_extra_types.ulid import ULID

from database.connection import db_manager
from models.application import ApplicationEntity
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ApplicationRepository(BaseRepository[ApplicationEntity]):
    """Repository for application data access operations."""

    def __init__(self):
        """Initialize application repository."""
        super().__init__(db_manager, "applications")

    async def create(self, entity_data: Dict[str, Any]) -> ApplicationEntity:
        """Create a new application.

        Args:
            entity_data: Application data dictionary

        Returns:
            Created application entity

        Raises:
            Exception: If application creation fails
        """
        application_id = self.generate_ulid()

        query = """
            INSERT INTO applications (id, name, comments)
            VALUES (%s, %s, %s)
            RETURNING id, name, comments, created_at, updated_at
        """

        params = (
            str(application_id),
            entity_data.get("name"),
            entity_data.get("comments"),
        )

        try:
            result = await self.db_manager.execute_query(query, params)
            if not result:
                raise Exception("Failed to create application")

            return ApplicationEntity(
                id=ULID.from_str(result["id"]),
                name=result["name"],
                comments=result["comments"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        except Exception as e:
            logger.error(f"Failed to create application: {e}")
            raise

    async def get_by_id(self, entity_id: ULID) -> Optional[ApplicationEntity]:
        """Get application by ID.

        Args:
            entity_id: Application ID

        Returns:
            Application entity if found, None otherwise
        """
        query = """
            SELECT id, name, comments, created_at, updated_at
            FROM applications
            WHERE id = %s
        """

        try:
            result = await self.db_manager.execute_query(query, (str(entity_id),))
            if not result:
                return None

            return ApplicationEntity(
                id=ULID.from_str(result["id"]),
                name=result["name"],
                comments=result["comments"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        except Exception as e:
            logger.error(f"Failed to get application by ID {entity_id}: {e}")
            raise

    async def get_by_name(self, name: str) -> Optional[ApplicationEntity]:
        """Get application by name.

        Args:
            name: Application name

        Returns:
            Application entity if found, None otherwise
        """
        query = """
            SELECT id, name, comments, created_at, updated_at
            FROM applications
            WHERE name = %s
        """

        try:
            result = await self.db_manager.execute_query(query, (name,))
            if not result:
                return None

            return ApplicationEntity(
                id=ULID.from_str(result["id"]),
                name=result["name"],
                comments=result["comments"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        except Exception as e:
            logger.error(f"Failed to get application by name {name}: {e}")
            raise

    async def update(
        self, entity_id: ULID, entity_data: Dict[str, Any]
    ) -> Optional[ApplicationEntity]:
        """Update application by ID.

        Args:
            entity_id: Application ID
            entity_data: Updated application data

        Returns:
            Updated application entity if found, None otherwise
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

        if not update_fields:
            # No fields to update, return current entity
            return await self.get_by_id(entity_id)

        params.append(str(entity_id))

        query = f"""
            UPDATE applications
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, name, comments, created_at, updated_at
        """

        try:
            result = await self.db_manager.execute_query(query, tuple(params))
            if not result:
                return None

            return ApplicationEntity(
                id=ULID.from_str(result["id"]),
                name=result["name"],
                comments=result["comments"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        except Exception as e:
            logger.error(f"Failed to update application {entity_id}: {e}")
            raise

    async def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[ApplicationEntity]:
        """Get all applications with optional pagination.

        Args:
            limit: Maximum number of applications to return
            offset: Number of applications to skip

        Returns:
            List of application entities
        """
        query = """
            SELECT id, name, comments, created_at, updated_at
            FROM applications
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
                ApplicationEntity(
                    id=ULID.from_str(row["id"]),
                    name=row["name"],
                    comments=row["comments"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in results
            ]
        except Exception as e:
            logger.error(f"Failed to get all applications: {e}")
            raise

    async def get_configuration_ids_by_application_id(
        self, application_id: ULID
    ) -> List[ULID]:
        """Get all configuration IDs for a specific application.

        Args:
            application_id: Application ID

        Returns:
            List of configuration IDs
        """
        query = """
            SELECT id
            FROM configurations
            WHERE application_id = %s
            ORDER BY created_at DESC
        """

        try:
            results = await self.db_manager.execute_query_many(
                query, (str(application_id),)
            )
            return [ULID.from_str(row["id"]) for row in results]
        except Exception as e:
            logger.error(
                f"Failed to get configuration IDs for application {application_id}: {e}"
            )
            raise


# Global application repository instance
application_repository = ApplicationRepository()
