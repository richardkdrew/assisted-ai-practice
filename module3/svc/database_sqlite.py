"""SQLite database adapter for testing without PostgreSQL."""

import sqlite3
import contextlib
import logging
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class SQLiteDatabasePool:
    """SQLite database pool for testing."""

    def __init__(self):
        self._db_path = ":memory:"  # In-memory database
        self._executor = None
        self._connection = None

    def initialize(self):
        """Initialize the SQLite database."""
        try:
            self._connection = sqlite3.connect(self._db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row  # Dict-like rows
            self._executor = ThreadPoolExecutor(max_workers=5)

            # Create tables
            self._setup_schema()
            logger.info("SQLite database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite database: {e}")
            raise

    def _setup_schema(self):
        """Set up the database schema."""
        schema_sql = """
        -- Create applications table
        CREATE TABLE applications (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            comments TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        -- Create configurations table
        CREATE TABLE configurations (
            id TEXT PRIMARY KEY,
            application_id TEXT NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            comments TEXT,
            config TEXT NOT NULL,  -- JSON as TEXT
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(application_id, name)
        );

        -- Create indexes
        CREATE INDEX idx_configurations_application_id ON configurations(application_id);
        CREATE INDEX idx_configurations_name ON configurations(name);

        -- Create migrations table
        CREATE TABLE migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            executed_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """

        cursor = self._connection.cursor()
        cursor.executescript(schema_sql)
        self._connection.commit()

    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            logger.info("SQLite database closed")
        if self._executor:
            self._executor.shutdown(wait=True)
            logger.info("Thread pool executor shutdown")

    @contextlib.asynccontextmanager
    async def get_connection(self):
        """Get a database connection."""
        if not self._connection:
            raise RuntimeError("Database not initialized")

        try:
            yield self._connection
        except Exception as e:
            self._connection.rollback()
            logger.error(f"Database operation failed: {e}")
            raise

    async def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        async with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    async def execute_command(self, command: str, params: tuple = None) -> int:
        """Execute an INSERT/UPDATE/DELETE command."""
        async with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(command, params or ())
            conn.commit()
            return cursor.rowcount


# Global test database pool instance
test_db_pool = SQLiteDatabasePool()