"""Database connection pool and context management."""

import contextlib
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncContextManager, Dict, Any

import psycopg2
import psycopg2.extras
import psycopg2.pool
from psycopg2.extras import RealDictCursor

try:
    from .config import settings
except ImportError:
    from config import settings

logger = logging.getLogger(__name__)


class DatabasePool:
    """Database connection pool manager using ThreadedConnectionPool."""

    def __init__(self):
        self._pool = None
        self._executor = None

    def initialize(self):
        """Initialize the database connection pool."""
        try:
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=settings.db_pool_min_conn,
                maxconn=settings.db_pool_max_conn,
                host=settings.db_host,
                port=settings.db_port,
                database=settings.db_name,
                user=settings.db_user,
                password=settings.db_password,
                cursor_factory=RealDictCursor
            )
            self._executor = ThreadPoolExecutor(max_workers=settings.db_pool_max_conn)
            logger.info("Database pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise

    def close(self):
        """Close the database connection pool."""
        if self._pool:
            self._pool.closeall()
            logger.info("Database pool closed")
        if self._executor:
            self._executor.shutdown(wait=True)
            logger.info("Thread pool executor shutdown")

    @contextlib.asynccontextmanager
    async def get_connection(self) -> AsyncContextManager[psycopg2.extensions.connection]:
        """Get a database connection from the pool.

        Returns:
            Database connection with RealDictCursor as default cursor factory.
        """
        if not self._pool:
            raise RuntimeError("Database pool not initialized")

        connection = None
        try:
            connection = self._pool.getconn()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if connection:
                self._pool.putconn(connection)

    async def execute_query(self, query: str, params: tuple = None) -> list[Dict[str, Any]]:
        """Execute a SELECT query and return results.

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            List of dictionaries representing query results
        """
        async with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    async def execute_command(self, command: str, params: tuple = None) -> int:
        """Execute an INSERT/UPDATE/DELETE command.

        Args:
            command: SQL command string
            params: Command parameters tuple

        Returns:
            Number of affected rows
        """
        async with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(command, params)
                conn.commit()
                return cursor.rowcount

    async def execute_returning(self, command: str, params: tuple = None) -> list[Dict[str, Any]]:
        """Execute an INSERT/UPDATE/DELETE command with RETURNING clause.

        Args:
            command: SQL command string with RETURNING clause
            params: Command parameters tuple

        Returns:
            List of dictionaries representing returned results
        """
        async with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(command, params)
                conn.commit()
                return cursor.fetchall()


# Global database pool instance
db_pool = DatabasePool()