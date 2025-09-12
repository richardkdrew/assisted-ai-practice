"""Database migration system."""

import os
import logging
from pathlib import Path
from typing import List, Tuple

from database.connection import db_manager

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database migrations."""

    def __init__(self, migrations_dir: str = "database/migrations"):
        """Initialize migration manager.

        Args:
            migrations_dir: Directory containing migration files
        """
        self.migrations_dir = Path(migrations_dir)

    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions.

        Returns:
            List of applied migration versions
        """
        query = "SELECT version FROM migrations ORDER BY version"
        try:
            results = await db_manager.execute_query_many(query)
            return [row["version"] for row in results]
        except Exception as e:
            logger.warning(f"Could not get applied migrations: {e}")
            return []

    def get_available_migrations(self) -> List[Tuple[str, str, str]]:
        """Get list of available migration files.

        Returns:
            List of tuples (version, name, filepath)
        """
        migrations = []

        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory {self.migrations_dir} does not exist")
            return migrations

        for file_path in sorted(self.migrations_dir.glob("*.sql")):
            filename = file_path.stem
            parts = filename.split("_", 1)

            if len(parts) >= 2:
                version = parts[0]
                name = parts[1].replace("_", " ").title()
                migrations.append((version, name, str(file_path)))
            else:
                logger.warning(f"Invalid migration filename format: {filename}")

        return migrations

    def get_pending_migrations(
        self, applied: List[str], available: List[Tuple[str, str, str]]
    ) -> List[Tuple[str, str, str]]:
        """Get list of pending migrations.

        Args:
            applied: List of applied migration versions
            available: List of available migrations

        Returns:
            List of pending migrations
        """
        return [
            (version, name, filepath)
            for version, name, filepath in available
            if version not in applied
        ]

    async def apply_migration(self, version: str, name: str, filepath: str) -> None:
        """Apply a single migration.

        Args:
            version: Migration version
            name: Migration name
            filepath: Path to migration file
        """
        logger.info(f"Applying migration {version}: {name}")

        try:
            # Read migration file
            with open(filepath, "r") as f:
                sql_content = f.read()

            # Execute migration in transaction
            queries = [
                (sql_content, ()),
                (
                    "INSERT INTO migrations (version, name) VALUES (%s, %s)",
                    (version, name),
                ),
            ]

            await db_manager.execute_transaction(queries)
            logger.info(f"Successfully applied migration {version}")

        except Exception as e:
            logger.error(f"Failed to apply migration {version}: {e}")
            raise

    async def run_migrations(self) -> None:
        """Run all pending migrations."""
        logger.info("Starting database migrations")

        # Ensure database connection is initialized
        if not db_manager.pool:
            db_manager.initialize_pool()

        # Get applied and available migrations
        applied = await self.get_applied_migrations()
        available = self.get_available_migrations()
        pending = self.get_pending_migrations(applied, available)

        if not pending:
            logger.info("No pending migrations")
            return

        logger.info(f"Found {len(pending)} pending migrations")

        # Apply each pending migration
        for version, name, filepath in pending:
            await self.apply_migration(version, name, filepath)

        logger.info("All migrations completed successfully")

    async def get_migration_status(self) -> dict:
        """Get migration status information.

        Returns:
            Dictionary with migration status
        """
        applied = await self.get_applied_migrations()
        available = self.get_available_migrations()
        pending = self.get_pending_migrations(applied, available)

        return {
            "applied_count": len(applied),
            "available_count": len(available),
            "pending_count": len(pending),
            "applied_migrations": applied,
            "pending_migrations": [
                {"version": version, "name": name} for version, name, _ in pending
            ],
        }


# Global migration manager instance
migration_manager = MigrationManager()


async def main():
    """Main function for running migrations from command line."""
    import asyncio

    try:
        await migration_manager.run_migrations()
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        db_manager.close_pool()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
