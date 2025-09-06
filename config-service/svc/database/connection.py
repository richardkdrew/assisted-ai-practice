"""Database connection management with connection pooling."""

import asyncio
import logging
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncGenerator, Dict, Any

import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

from config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection manager with connection pooling."""

    def __init__(self, connection_string: str, min_conn: int = 1, max_conn: int = 20):
        """Initialize database manager with connection pool.

        Args:
            connection_string: PostgreSQL connection string
            min_conn: Minimum number of connections in pool
            max_conn: Maximum number of connections in pool
        """
        self.connection_string = connection_string
        self.min_conn = min_conn
        self.max_conn = max_conn
        self.pool: ThreadedConnectionPool = None
        self.executor = ThreadPoolExecutor(max_workers=max_conn)

    def initialize_pool(self) -> None:
        """Initialize the connection pool."""
        try:
            self.pool = ThreadedConnectionPool(
                self.min_conn,
                self.max_conn,
                self.connection_string,
                cursor_factory=psycopg2.extras.RealDictCursor,
            )
            logger.info(
                f"Database connection pool initialized with {self.min_conn}-{self.max_conn} connections"
            )
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise

    def close_pool(self) -> None:
        """Close the connection pool."""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")

        if self.executor:
            self.executor.shutdown(wait=True)
            logger.info("Thread pool executor shutdown")

    @asynccontextmanager
    async def get_connection(
        self,
    ) -> AsyncGenerator[psycopg2.extensions.connection, None]:
        """Get a database connection from the pool.

        Yields:
            Database connection with RealDictCursor factory
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        connection = None
        try:
            # Get connection from pool in thread executor
            connection = await asyncio.get_event_loop().run_in_executor(
                self.executor, self.pool.getconn
            )
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                # Return connection to pool
                await asyncio.get_event_loop().run_in_executor(
                    self.executor, self.pool.putconn, connection
                )

    async def execute_query(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """Execute a single query and return the result.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Query result as dictionary
        """
        async with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                # Commit the transaction for INSERT/UPDATE/DELETE operations
                conn.commit()
                if cursor.description:
                    return cursor.fetchone()
                return {}

    async def execute_query_many(
        self, query: str, params: tuple = None
    ) -> list[Dict[str, Any]]:
        """Execute a query and return all results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of query results as dictionaries
        """
        async with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                # Commit the transaction for INSERT/UPDATE/DELETE operations
                conn.commit()
                if cursor.description:
                    return cursor.fetchall()
                return []

    async def execute_transaction(self, queries: list[tuple[str, tuple]]) -> None:
        """Execute multiple queries in a transaction.

        Args:
            queries: List of (query, params) tuples
        """
        async with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    for query, params in queries:
                        cursor.execute(query, params)
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction failed: {e}")
                raise


# Global database manager instance
db_manager = DatabaseManager(
    connection_string=settings.database_url,
    min_conn=settings.db_min_connections,
    max_conn=settings.db_max_connections,
)

# Test database manager instance
test_db_manager = DatabaseManager(
    connection_string=settings.database_test_url, min_conn=1, max_conn=5
)
