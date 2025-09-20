"""Integration tests for the Configuration Service API.

These tests verify the complete flow from API endpoints through to the database.
They require a running PostgreSQL database configured per the test environment.
"""

import pytest
import asyncio
import json
from datetime import datetime, UTC
from httpx import AsyncClient, ASGITransport
from ulid import ULID

from .main import app
from .database import db_pool
from .migrations import MigrationRunner


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Set up test database with migrations before running tests."""
    # Initialize database pool
    db_pool.initialize()

    # Run migrations to ensure clean schema
    runner = MigrationRunner()
    runner.run_migrations()

    yield

    # Cleanup
    db_pool.close()


@pytest.fixture
async def clean_database():
    """Clean database before each test."""
    # Clear test data in reverse dependency order
    await db_pool.execute_command("DELETE FROM configurations")
    await db_pool.execute_command("DELETE FROM applications")
    yield


@pytest.fixture
async def client():
    """Create async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestApplicationsIntegration:
    """Integration tests for applications endpoints."""

    async def test_create_application_flow(self, client: AsyncClient, clean_database):
        """Test complete application creation flow."""
        app_data = {
            "name": "test-application",
            "comments": "Integration test application"
        }

        # Create application
        response = await client.post("/api/v1/applications/", json=app_data)
        assert response.status_code == 201

        created_app = response.json()
        assert created_app["name"] == "test-application"
        assert created_app["comments"] == "Integration test application"
        assert "id" in created_app
        assert "created_at" in created_app
        assert "updated_at" in created_app
        assert created_app["configuration_ids"] == []

        # Verify in database
        db_result = await db_pool.execute_query(
            "SELECT * FROM applications WHERE id = %s",
            (created_app["id"],)
        )
        assert len(db_result) == 1
        assert db_result[0]["name"] == "test-application"

    async def test_get_application_with_configurations(self, client: AsyncClient, clean_database):
        """Test getting application with its related configurations."""
        # Create application via API
        app_response = await client.post("/api/v1/applications/", json={
            "name": "app-with-configs",
            "comments": "App for testing configurations"
        })
        app_id = app_response.json()["id"]

        # Create configurations via API
        config1_response = await client.post("/api/v1/configurations/", json={
            "application_id": app_id,
            "name": "database-config",
            "comments": "Database settings",
            "config": {"host": "localhost", "port": 5432}
        })
        config1_id = config1_response.json()["id"]

        config2_response = await client.post("/api/v1/configurations/", json={
            "application_id": app_id,
            "name": "api-config",
            "comments": "API settings",
            "config": {"timeout": 30, "retries": 3}
        })
        config2_id = config2_response.json()["id"]

        # Get application and verify it includes configuration IDs
        get_response = await client.get(f"/api/v1/applications/{app_id}")
        assert get_response.status_code == 200

        app_data = get_response.json()
        assert app_data["name"] == "app-with-configs"
        assert len(app_data["configuration_ids"]) == 2
        assert config1_id in app_data["configuration_ids"]
        assert config2_id in app_data["configuration_ids"]

    async def test_list_applications_pagination(self, client: AsyncClient, clean_database):
        """Test application listing with pagination."""
        # Create multiple applications
        app_names = [f"test-app-{i}" for i in range(5)]
        created_apps = []

        for name in app_names:
            response = await client.post("/api/v1/applications/", json={"name": name})
            created_apps.append(response.json())

        # Test pagination
        response = await client.get("/api/v1/applications/?limit=2&offset=0")
        assert response.status_code == 200

        page_data = response.json()
        assert len(page_data["items"]) == 2
        assert page_data["total"] == 5
        assert page_data["limit"] == 2
        assert page_data["offset"] == 0
        assert page_data["has_more"] is True

        # Test second page
        response = await client.get("/api/v1/applications/?limit=2&offset=2")
        page_data = response.json()
        assert len(page_data["items"]) == 2
        assert page_data["has_more"] is True

    async def test_update_application_flow(self, client: AsyncClient, clean_database):
        """Test application update flow."""
        # Create application
        create_response = await client.post("/api/v1/applications/", json={
            "name": "original-name",
            "comments": "Original comment"
        })
        app_id = create_response.json()["id"]

        # Update application
        update_data = {
            "name": "updated-name",
            "comments": "Updated comment"
        }
        update_response = await client.put(f"/api/v1/applications/{app_id}", json=update_data)
        assert update_response.status_code == 200

        updated_app = update_response.json()
        assert updated_app["name"] == "updated-name"
        assert updated_app["comments"] == "Updated comment"
        assert updated_app["id"] == app_id

        # Verify in database
        db_result = await db_pool.execute_query(
            "SELECT * FROM applications WHERE id = %s",
            (app_id,)
        )
        assert db_result[0]["name"] == "updated-name"

    async def test_delete_application_cascade(self, client: AsyncClient, clean_database):
        """Test application deletion cascades to configurations."""
        # Create application and configuration
        app_response = await client.post("/api/v1/applications/", json={"name": "delete-test"})
        app_id = app_response.json()["id"]

        config_response = await client.post("/api/v1/configurations/", json={
            "application_id": app_id,
            "name": "test-config",
            "config": {"key": "value"}
        })
        config_id = config_response.json()["id"]

        # Delete application
        delete_response = await client.delete(f"/api/v1/applications/{app_id}")
        assert delete_response.status_code == 204

        # Verify application is deleted
        get_response = await client.get(f"/api/v1/applications/{app_id}")
        assert get_response.status_code == 404

        # Verify configuration is also deleted (cascade)
        config_get_response = await client.get(f"/api/v1/configurations/{config_id}")
        assert config_get_response.status_code == 404


class TestConfigurationsIntegration:
    """Integration tests for configurations endpoints."""

    async def test_create_configuration_flow(self, client: AsyncClient, clean_database):
        """Test complete configuration creation flow."""
        # Create parent application
        app_response = await client.post("/api/v1/applications/", json={"name": "config-parent"})
        app_id = app_response.json()["id"]

        # Create configuration
        config_data = {
            "application_id": app_id,
            "name": "test-config",
            "comments": "Test configuration",
            "config": {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "ssl": True
                },
                "features": ["feature1", "feature2"],
                "timeout": 30.5
            }
        }

        response = await client.post("/api/v1/configurations/", json=config_data)
        assert response.status_code == 201

        created_config = response.json()
        assert created_config["name"] == "test-config"
        assert created_config["application_id"] == app_id
        assert created_config["config"]["database"]["host"] == "localhost"
        assert created_config["config"]["features"] == ["feature1", "feature2"]
        assert created_config["config"]["timeout"] == 30.5

        # Verify in database
        db_result = await db_pool.execute_query(
            "SELECT * FROM configurations WHERE id = %s",
            (created_config["id"],)
        )
        assert len(db_result) == 1
        db_config = json.loads(db_result[0]["config"])
        assert db_config["database"]["port"] == 5432

    async def test_configuration_name_uniqueness_per_application(self, client: AsyncClient, clean_database):
        """Test that configuration names must be unique per application."""
        # Create two applications
        app1_response = await client.post("/api/v1/applications/", json={"name": "app1"})
        app1_id = app1_response.json()["id"]

        app2_response = await client.post("/api/v1/applications/", json={"name": "app2"})
        app2_id = app2_response.json()["id"]

        # Create configuration in app1
        config1_response = await client.post("/api/v1/configurations/", json={
            "application_id": app1_id,
            "name": "shared-name",
            "config": {"app": "1"}
        })
        assert config1_response.status_code == 201

        # Create configuration with same name in app2 (should succeed)
        config2_response = await client.post("/api/v1/configurations/", json={
            "application_id": app2_id,
            "name": "shared-name",
            "config": {"app": "2"}
        })
        assert config2_response.status_code == 201

        # Try to create duplicate name in app1 (should fail)
        duplicate_response = await client.post("/api/v1/configurations/", json={
            "application_id": app1_id,
            "name": "shared-name",
            "config": {"duplicate": "attempt"}
        })
        assert duplicate_response.status_code == 409
        assert "already exists" in duplicate_response.json()["detail"]

    async def test_update_configuration_flow(self, client: AsyncClient, clean_database):
        """Test configuration update flow."""
        # Create application and configuration
        app_response = await client.post("/api/v1/applications/", json={"name": "update-test"})
        app_id = app_response.json()["id"]

        create_response = await client.post("/api/v1/configurations/", json={
            "application_id": app_id,
            "name": "original-config",
            "config": {"version": 1, "enabled": True}
        })
        config_id = create_response.json()["id"]

        # Update configuration
        update_data = {
            "application_id": app_id,
            "name": "updated-config",
            "comments": "Updated configuration",
            "config": {"version": 2, "enabled": False, "new_feature": "active"}
        }

        update_response = await client.put(f"/api/v1/configurations/{config_id}", json=update_data)
        assert update_response.status_code == 200

        updated_config = update_response.json()
        assert updated_config["name"] == "updated-config"
        assert updated_config["comments"] == "Updated configuration"
        assert updated_config["config"]["version"] == 2
        assert updated_config["config"]["new_feature"] == "active"

        # Verify in database
        db_result = await db_pool.execute_query(
            "SELECT * FROM configurations WHERE id = %s",
            (config_id,)
        )
        db_config = json.loads(db_result[0]["config"])
        assert db_config["enabled"] is False


class TestErrorHandlingIntegration:
    """Integration tests for error scenarios."""

    async def test_create_configuration_with_invalid_application_id(self, client: AsyncClient, clean_database):
        """Test creating configuration with non-existent application ID."""
        fake_app_id = str(ULID())

        response = await client.post("/api/v1/configurations/", json={
            "application_id": fake_app_id,
            "name": "orphan-config",
            "config": {"key": "value"}
        })

        # Should fail due to foreign key constraint
        assert response.status_code == 400

    async def test_get_nonexistent_resources(self, client: AsyncClient, clean_database):
        """Test getting non-existent applications and configurations."""
        fake_id = str(ULID())

        # Non-existent application
        app_response = await client.get(f"/api/v1/applications/{fake_id}")
        assert app_response.status_code == 404

        # Non-existent configuration
        config_response = await client.get(f"/api/v1/configurations/{fake_id}")
        assert config_response.status_code == 404

    async def test_invalid_ulid_format(self, client: AsyncClient, clean_database):
        """Test API response to invalid ULID formats."""
        invalid_id = "not-a-valid-ulid"

        response = await client.get(f"/api/v1/applications/{invalid_id}")
        assert response.status_code == 422  # Pydantic validation error


class TestDatabaseConsistency:
    """Integration tests for database consistency and constraints."""

    async def test_timestamp_handling(self, client: AsyncClient, clean_database):
        """Test that timestamps are properly handled."""
        before_create = datetime.now(UTC)

        # Create application
        response = await client.post("/api/v1/applications/", json={"name": "timestamp-test"})
        app_data = response.json()

        after_create = datetime.now(UTC)

        # Parse timestamps
        created_at = datetime.fromisoformat(app_data["created_at"].replace('Z', '+00:00'))
        updated_at = datetime.fromisoformat(app_data["updated_at"].replace('Z', '+00:00'))

        # Verify timestamps are reasonable
        assert before_create <= created_at <= after_create
        assert before_create <= updated_at <= after_create
        assert created_at == updated_at  # Should be same on creation

    async def test_json_config_storage(self, client: AsyncClient, clean_database):
        """Test that complex JSON configurations are stored and retrieved correctly."""
        app_response = await client.post("/api/v1/applications/", json={"name": "json-test"})
        app_id = app_response.json()["id"]

        complex_config = {
            "database": {
                "primary": {
                    "host": "primary-db.example.com",
                    "port": 5432,
                    "ssl": True,
                    "connection_pool": {
                        "min": 5,
                        "max": 20,
                        "timeout": 30.0
                    }
                },
                "replicas": [
                    {"host": "replica1.example.com", "port": 5432},
                    {"host": "replica2.example.com", "port": 5432}
                ]
            },
            "features": ["analytics", "caching", "monitoring"],
            "limits": {
                "max_requests_per_minute": 1000,
                "max_file_size_mb": 50
            },
            "metadata": {
                "environment": "production",
                "version": "1.2.3",
                "deployed_at": "2023-01-01T00:00:00Z"
            }
        }

        # Create configuration with complex JSON
        create_response = await client.post("/api/v1/configurations/", json={
            "application_id": app_id,
            "name": "complex-config",
            "config": complex_config
        })
        config_id = create_response.json()["id"]

        # Retrieve and verify structure is preserved
        get_response = await client.get(f"/api/v1/configurations/{config_id}")
        retrieved_config = get_response.json()["config"]

        assert retrieved_config["database"]["primary"]["host"] == "primary-db.example.com"
        assert len(retrieved_config["database"]["replicas"]) == 2
        assert retrieved_config["features"] == ["analytics", "caching", "monitoring"]
        assert retrieved_config["limits"]["max_requests_per_minute"] == 1000
        assert retrieved_config["metadata"]["version"] == "1.2.3"