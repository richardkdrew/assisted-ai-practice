"""Base repository classes that can work with different database pools."""

import json
import logging
from datetime import datetime, UTC
from typing import List, Optional, Dict, Any

from pydantic_extra_types.ulid import ULID
from ulid import ULID as ULIDGenerator

from .models import Application, Configuration, ApplicationCreate, ApplicationUpdate, ConfigurationCreate, ConfigurationUpdate

logger = logging.getLogger(__name__)


class ApplicationRepository:
    """Repository for Application data access."""

    def __init__(self, db_pool=None):
        self._db_pool = db_pool

    async def create(self, application_data: ApplicationCreate) -> Application:
        """Create a new application."""
        app_id = str(ULIDGenerator())
        now = datetime.now(UTC).isoformat()

        query = """
            INSERT INTO applications (id, name, comments, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id, name, comments, created_at, updated_at
        """
        params = (app_id, application_data.name, application_data.comments, now, now)

        result = await self._db_pool.execute_query(query, params)
        if not result:
            # Try SELECT for databases that don't support RETURNING
            result = await self._db_pool.execute_query(
                "SELECT id, name, comments, created_at, updated_at FROM applications WHERE id = ?",
                (app_id,)
            )

        if not result:
            raise RuntimeError("Failed to create application")

        app_data = dict(result[0])
        app_data['configuration_ids'] = []
        return Application(**app_data)

    async def get_by_id(self, app_id: ULID) -> Optional[Application]:
        """Get application by ID with related configuration IDs."""
        # Get application data
        app_query = """
            SELECT id, name, comments, created_at, updated_at
            FROM applications
            WHERE id = ?
        """
        app_result = await self._db_pool.execute_query(app_query, (str(app_id),))

        if not app_result:
            return None

        # Get related configuration IDs
        config_query = """
            SELECT id FROM configurations WHERE application_id = ?
        """
        config_result = await self._db_pool.execute_query(config_query, (str(app_id),))

        app_data = dict(app_result[0])
        app_data['configuration_ids'] = [ULID(row['id']) for row in config_result]

        return Application(**app_data)

    async def update(self, app_id: ULID, application_data: ApplicationUpdate) -> Optional[Application]:
        """Update an existing application."""
        now = datetime.now(UTC).isoformat()

        query = """
            UPDATE applications
            SET name = ?, comments = ?, updated_at = ?
            WHERE id = ?
        """
        params = (application_data.name, application_data.comments, now, str(app_id))

        affected_rows = await self._db_pool.execute_command(query, params)
        if affected_rows == 0:
            return None

        return await self.get_by_id(app_id)

    async def list_all(self, limit: int = 50, offset: int = 0) -> List[Application]:
        """List all applications with pagination."""
        query = """
            SELECT id, name, comments, created_at, updated_at
            FROM applications
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        result = await self._db_pool.execute_query(query, (limit, offset))

        applications = []
        for row in result:
            app_data = dict(row)

            # Get related configuration IDs for each application
            config_query = """
                SELECT id FROM configurations WHERE application_id = ?
            """
            config_result = await self._db_pool.execute_query(config_query, (app_data['id'],))
            app_data['configuration_ids'] = [ULID(config_row['id']) for config_row in config_result]

            applications.append(Application(**app_data))

        return applications

    async def count(self) -> int:
        """Count total number of applications."""
        query = "SELECT COUNT(*) as count FROM applications"
        result = await self._db_pool.execute_query(query)
        return result[0]['count'] if result else 0

    async def delete(self, app_id: ULID) -> bool:
        """Delete an application and its configurations."""
        query = "DELETE FROM applications WHERE id = ?"
        affected_rows = await self._db_pool.execute_command(query, (str(app_id),))
        return affected_rows > 0


class ConfigurationRepository:
    """Repository for Configuration data access."""

    def __init__(self, db_pool=None):
        self._db_pool = db_pool

    async def create(self, config_data: ConfigurationCreate) -> Configuration:
        """Create a new configuration."""
        config_id = str(ULIDGenerator())
        now = datetime.now(UTC).isoformat()

        # Check if name is unique within the application
        check_query = """
            SELECT COUNT(*) as count
            FROM configurations
            WHERE application_id = ? AND name = ?
        """
        check_result = await self._db_pool.execute_query(
            check_query,
            (str(config_data.application_id), config_data.name)
        )

        if check_result and check_result[0]['count'] > 0:
            raise ValueError(f"Configuration name '{config_data.name}' already exists for this application")

        query = """
            INSERT INTO configurations (id, application_id, name, comments, config, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            config_id,
            str(config_data.application_id),
            config_data.name,
            config_data.comments,
            json.dumps(config_data.config),
            now,
            now
        )

        await self._db_pool.execute_command(query, params)

        # Retrieve the created configuration
        result = await self._db_pool.execute_query(
            "SELECT id, application_id, name, comments, config, created_at, updated_at FROM configurations WHERE id = ?",
            (config_id,)
        )

        if not result:
            raise RuntimeError("Failed to create configuration")

        config_dict = dict(result[0])
        config_dict['config'] = json.loads(config_dict['config']) if config_dict['config'] else {}
        return Configuration(**config_dict)

    async def get_by_id(self, config_id: ULID) -> Optional[Configuration]:
        """Get configuration by ID."""
        query = """
            SELECT id, application_id, name, comments, config, created_at, updated_at
            FROM configurations
            WHERE id = ?
        """
        result = await self._db_pool.execute_query(query, (str(config_id),))

        if not result:
            return None

        config_dict = dict(result[0])
        config_dict['config'] = json.loads(config_dict['config']) if config_dict['config'] else {}
        return Configuration(**config_dict)

    async def update(self, config_id: ULID, config_data: ConfigurationUpdate) -> Optional[Configuration]:
        """Update an existing configuration."""
        now = datetime.now(UTC).isoformat()

        # Check if new name conflicts with existing configurations in the same application
        check_query = """
            SELECT COUNT(*) as count
            FROM configurations
            WHERE application_id = ? AND name = ? AND id != ?
        """
        check_result = await self._db_pool.execute_query(
            check_query,
            (str(config_data.application_id), config_data.name, str(config_id))
        )

        if check_result and check_result[0]['count'] > 0:
            raise ValueError(f"Configuration name '{config_data.name}' already exists for this application")

        query = """
            UPDATE configurations
            SET application_id = ?, name = ?, comments = ?, config = ?, updated_at = ?
            WHERE id = ?
        """
        params = (
            str(config_data.application_id),
            config_data.name,
            config_data.comments,
            json.dumps(config_data.config),
            now,
            str(config_id)
        )

        affected_rows = await self._db_pool.execute_command(query, params)
        if affected_rows == 0:
            return None

        return await self.get_by_id(config_id)

    async def delete(self, config_id: ULID) -> bool:
        """Delete a configuration."""
        query = "DELETE FROM configurations WHERE id = ?"
        affected_rows = await self._db_pool.execute_command(query, (str(config_id),))
        return affected_rows > 0