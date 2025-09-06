"""Base repository class with common database operations."""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional, TypeVar, Generic

from pydantic_extra_types.ulid import ULID
from ulid import ULID as ULIDGenerator

from database.connection import DatabaseManager

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base repository class with common CRUD operations."""

    def __init__(self, db_manager: DatabaseManager, table_name: str):
        """Initialize repository.

        Args:
            db_manager: Database manager instance
            table_name: Name of the database table
        """
        self.db_manager = db_manager
        self.table_name = table_name

    def generate_ulid(self) -> ULID:
        """Generate a new ULID.

        Returns:
            New ULID instance
        """
        return ULIDGenerator()

    def serialize_json_field(self, data: Dict[str, Any]) -> str:
        """Serialize dictionary to JSON string for database storage.

        Args:
            data: Dictionary to serialize

        Returns:
            JSON string
        """
        return json.dumps(data, default=str)

    def deserialize_json_field(self, json_str: str) -> Dict[str, Any]:
        """Deserialize JSON string from database.

        Args:
            json_str: JSON string to deserialize

        Returns:
            Deserialized dictionary
        """
        if isinstance(json_str, dict):
            return json_str
        return json.loads(json_str) if json_str else {}

    async def exists_by_id(self, entity_id: ULID) -> bool:
        """Check if entity exists by ID.

        Args:
            entity_id: Entity ID to check

        Returns:
            True if entity exists, False otherwise
        """
        query = f"SELECT 1 FROM {self.table_name} WHERE id = %s"
        result = await self.db_manager.execute_query(query, (str(entity_id),))
        return bool(result)

    async def delete_by_id(self, entity_id: ULID) -> bool:
        """Delete entity by ID.

        Args:
            entity_id: Entity ID to delete

        Returns:
            True if entity was deleted, False if not found
        """
        if not await self.exists_by_id(entity_id):
            return False

        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        await self.db_manager.execute_query(query, (str(entity_id),))
        return True

    async def count_all(self) -> int:
        """Count total number of entities.

        Returns:
            Total count of entities
        """
        query = f"SELECT COUNT(*) as count FROM {self.table_name}"
        result = await self.db_manager.execute_query(query)
        return result.get("count", 0) if result else 0

    @abstractmethod
    async def create(self, entity_data: Dict[str, Any]) -> T:
        """Create a new entity.

        Args:
            entity_data: Entity data dictionary

        Returns:
            Created entity
        """
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: ULID) -> Optional[T]:
        """Get entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def update(self, entity_id: ULID, entity_data: Dict[str, Any]) -> Optional[T]:
        """Update entity by ID.

        Args:
            entity_id: Entity ID
            entity_data: Updated entity data

        Returns:
            Updated entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[T]:
        """Get all entities with optional pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entities
        """
        pass
