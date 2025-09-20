"""Tests for database migration system."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from .migrations import MigrationRunner


class TestMigrationRunner:
    """Test the migration runner functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create temporary directory for test migrations
        self.test_migrations_dir = Path(tempfile.mkdtemp())
        self.runner = MigrationRunner()
        # Override the migrations directory for testing
        self.runner.migrations_dir = self.test_migrations_dir

    def teardown_method(self):
        """Clean up after each test."""
        shutil.rmtree(self.test_migrations_dir)

    def test_migrations_dir_property(self):
        """Test that migrations directory is correctly set."""
        runner = MigrationRunner()
        expected_dir = Path(__file__).parent / "migrations"
        assert runner.migrations_dir == expected_dir

    def test_ensure_migrations_table(self):
        """Test creation of migrations tracking table."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        with patch.object(mock_cursor, '__enter__', return_value=mock_cursor), \
             patch.object(mock_cursor, '__exit__', return_value=None):
            self.runner.ensure_migrations_table(mock_conn)

            # Verify the SQL was executed
            mock_cursor.execute.assert_called_once()
            create_table_sql = mock_cursor.execute.call_args[0][0]
            assert "CREATE TABLE IF NOT EXISTS migrations" in create_table_sql
            mock_conn.commit.assert_called_once()

    def test_get_executed_migrations(self):
        """Test retrieval of executed migrations."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        # Mock the query result
        mock_cursor.fetchall.return_value = [
            {'filename': '001_initial.sql'},
            {'filename': '002_add_indexes.sql'}
        ]

        with patch.object(mock_cursor, '__enter__', return_value=mock_cursor), \
             patch.object(mock_cursor, '__exit__', return_value=None):
            executed = self.runner.get_executed_migrations(mock_conn)

            assert executed == ['001_initial.sql', '002_add_indexes.sql']
            mock_cursor.execute.assert_called_once_with(
                "SELECT filename FROM migrations ORDER BY executed_at"
            )

    def test_get_pending_migrations_empty_dir(self):
        """Test getting pending migrations when migrations directory is empty."""
        executed_migrations = ['001_initial.sql']
        pending = self.runner.get_pending_migrations(executed_migrations)
        assert pending == []

    def test_get_pending_migrations_with_files(self):
        """Test getting pending migrations with files present."""
        # Create test migration files
        (self.test_migrations_dir / "001_initial.sql").write_text("-- Initial migration")
        (self.test_migrations_dir / "002_add_tables.sql").write_text("-- Add tables")
        (self.test_migrations_dir / "003_add_indexes.sql").write_text("-- Add indexes")

        executed_migrations = ['001_initial.sql']
        pending = self.runner.get_pending_migrations(executed_migrations)

        # Should return the two unexecuted migrations in sorted order
        assert len(pending) == 2
        assert pending[0].name == "002_add_tables.sql"
        assert pending[1].name == "003_add_indexes.sql"

    def test_get_pending_migrations_all_executed(self):
        """Test getting pending migrations when all are executed."""
        # Create test migration files
        (self.test_migrations_dir / "001_initial.sql").write_text("-- Initial migration")
        (self.test_migrations_dir / "002_add_tables.sql").write_text("-- Add tables")

        executed_migrations = ['001_initial.sql', '002_add_tables.sql']
        pending = self.runner.get_pending_migrations(executed_migrations)

        assert pending == []

    def test_execute_migration(self):
        """Test execution of a single migration."""
        # Create test migration file
        migration_content = "CREATE TABLE test_table (id SERIAL PRIMARY KEY);"
        migration_file = self.test_migrations_dir / "001_test.sql"
        migration_file.write_text(migration_content)

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        with patch.object(mock_cursor, '__enter__', return_value=mock_cursor), \
             patch.object(mock_cursor, '__exit__', return_value=None):
            self.runner.execute_migration(mock_conn, migration_file)

            # Verify migration SQL was executed
            assert mock_cursor.execute.call_count == 2
            first_call = mock_cursor.execute.call_args_list[0][0][0]
            assert migration_content in first_call

            # Verify migration was recorded
            second_call = mock_cursor.execute.call_args_list[1]
            assert "INSERT INTO migrations" in second_call[0][0]
            assert second_call[0][1] == ('001_test.sql',)

            mock_conn.commit.assert_called_once()

    @patch('svc.migrations.MigrationRunner.get_connection')
    def test_run_migrations_no_pending(self, mock_get_conn):
        """Test running migrations when none are pending."""
        mock_conn = Mock()
        mock_get_conn.return_value = mock_conn

        # Mock methods to return no pending migrations
        with patch.object(self.runner, 'ensure_migrations_table'), \
             patch.object(self.runner, 'get_executed_migrations', return_value=['001_initial.sql']), \
             patch.object(self.runner, 'get_pending_migrations', return_value=[]):

            self.runner.run_migrations()

            # Connection should be established and closed
            mock_get_conn.assert_called_once()
            mock_conn.close.assert_called_once()

    @patch('svc.migrations.MigrationRunner.get_connection')
    def test_run_migrations_with_pending(self, mock_get_conn):
        """Test running migrations when there are pending migrations."""
        # Create test migration files
        migration1 = self.test_migrations_dir / "002_test1.sql"
        migration2 = self.test_migrations_dir / "003_test2.sql"
        migration1.write_text("-- Test migration 1")
        migration2.write_text("-- Test migration 2")

        mock_conn = Mock()
        mock_get_conn.return_value = mock_conn

        with patch.object(self.runner, 'ensure_migrations_table'), \
             patch.object(self.runner, 'get_executed_migrations', return_value=['001_initial.sql']), \
             patch.object(self.runner, 'get_pending_migrations', return_value=[migration1, migration2]), \
             patch.object(self.runner, 'execute_migration') as mock_execute:

            self.runner.run_migrations()

            # Both migrations should be executed
            assert mock_execute.call_count == 2
            mock_execute.assert_any_call(mock_conn, migration1)
            mock_execute.assert_any_call(mock_conn, migration2)

    @patch('svc.migrations.MigrationRunner.get_connection')
    def test_run_migrations_directory_not_exists(self, mock_get_conn):
        """Test running migrations when migrations directory doesn't exist."""
        # Use a non-existent directory
        self.runner.migrations_dir = Path("/nonexistent/directory")

        # Should handle gracefully without raising exception
        self.runner.run_migrations()

        # Connection should not be attempted
        mock_get_conn.assert_not_called()

    @patch('svc.migrations.MigrationRunner.get_connection')
    def test_run_migrations_database_error(self, mock_get_conn):
        """Test handling of database errors during migration."""
        mock_conn = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.side_effect = Exception("Database connection failed")

        with pytest.raises(Exception, match="Database connection failed"):
            self.runner.run_migrations()

        # Rollback should be called on error
        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()