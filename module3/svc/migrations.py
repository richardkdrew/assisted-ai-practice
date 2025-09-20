"""Database migration system."""

import os
import logging
from pathlib import Path
from typing import List

import psycopg2
from psycopg2.extras import RealDictCursor

from .config import settings

logger = logging.getLogger(__name__)


class MigrationRunner:
    """Handles database migration execution."""

    def __init__(self):
        self.migrations_dir = Path(__file__).parent / "migrations"

    def get_connection(self):
        """Get a direct database connection for migrations."""
        return psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            cursor_factory=RealDictCursor
        )

    def ensure_migrations_table(self, conn):
        """Ensure the migrations table exists."""
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) UNIQUE NOT NULL,
                    executed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def get_executed_migrations(self, conn) -> List[str]:
        """Get list of already executed migrations."""
        with conn.cursor() as cursor:
            cursor.execute("SELECT filename FROM migrations ORDER BY executed_at")
            return [row['filename'] for row in cursor.fetchall()]

    def get_pending_migrations(self, executed_migrations: List[str]) -> List[Path]:
        """Get list of pending migration files."""
        all_migrations = sorted(self.migrations_dir.glob("*.sql"))
        pending = []

        for migration_file in all_migrations:
            if migration_file.name not in executed_migrations:
                pending.append(migration_file)

        return pending

    def execute_migration(self, conn, migration_file: Path):
        """Execute a single migration file."""
        logger.info(f"Executing migration: {migration_file.name}")

        with migration_file.open('r') as f:
            migration_sql = f.read()

        with conn.cursor() as cursor:
            # Execute the migration SQL
            cursor.execute(migration_sql)

            # Record the migration as executed (if not already recorded)
            cursor.execute(
                "INSERT INTO migrations (filename) VALUES (%s) ON CONFLICT (filename) DO NOTHING",
                (migration_file.name,)
            )

            conn.commit()
            logger.info(f"Migration {migration_file.name} executed successfully")

    def run_migrations(self):
        """Run all pending migrations."""
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory {self.migrations_dir} does not exist")
            return

        conn = None
        try:
            conn = self.get_connection()
            self.ensure_migrations_table(conn)

            executed_migrations = self.get_executed_migrations(conn)
            pending_migrations = self.get_pending_migrations(executed_migrations)

            if not pending_migrations:
                logger.info("No pending migrations to execute")
                return

            logger.info(f"Found {len(pending_migrations)} pending migrations")

            for migration_file in pending_migrations:
                self.execute_migration(conn, migration_file)

            logger.info("All migrations executed successfully")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()


def main():
    """Main entry point for running migrations."""
    logging.basicConfig(level=getattr(logging, settings.log_level))
    runner = MigrationRunner()
    runner.run_migrations()


if __name__ == "__main__":
    main()