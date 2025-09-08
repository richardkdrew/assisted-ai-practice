"""Integration tests for configuration service layer."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from ulid import ULID

from models.configuration import ConfigurationCreate, ConfigurationResponse
from models.application import ApplicationEntity
from services.configuration_service import ConfigurationService


class TestConfigurationServiceIntegration:
    """Integration test cases for ConfigurationService with real service layer."""

    @pytest.mark.asyncio
    async def test_create_configuration_integration(self):
        """Integration test for create configuration flow.

        This test verifies that:
        1. A configuration can be successfully created through the service layer
        2. The configuration exists after creation by calling the service again
        3. The created configuration can be retrieved with correct data
        4. The application validation works correctly

        Note: This test uses the real service layer but mocks
        the repository layers to avoid requiring a running database.
        """
        # Create a real service instance (not mocked)
        service = ConfigurationService()

        # Mock the repository layers
        mock_config_repository = AsyncMock()
        mock_app_repository = AsyncMock()
        service.repository = mock_config_repository
        service.application_repository = mock_app_repository

        # Set up test data
        app_id = ULID()
        config_id = ULID()
        now = datetime.now()
        test_config_name = "integration-test-config"
        test_comments = "Integration test configuration"
        test_config_data = {
            "database": {"host": "localhost", "port": 5432, "name": "test_db"},
            "features": {"logging": True, "metrics": False},
            "timeout": 30,
        }

        # Mock application exists
        mock_application = MagicMock()
        mock_application.id = app_id
        mock_application.name = "test-application"
        mock_app_repository.get_by_id.return_value = mock_application

        # Mock no existing configuration with same name
        mock_config_repository.get_by_application_and_name.return_value = None

        # Mock entity returned by create
        mock_config_entity = MagicMock()
        mock_config_entity.id = config_id
        mock_config_entity.application_id = app_id
        mock_config_entity.name = test_config_name
        mock_config_entity.comments = test_comments
        mock_config_entity.config = test_config_data
        mock_config_entity.created_at = now
        mock_config_entity.updated_at = now
        mock_config_repository.create.return_value = mock_config_entity

        # Mock get_by_id for verification
        mock_config_repository.get_by_id.return_value = mock_config_entity

        # Arrange - Create configuration data
        create_data = ConfigurationCreate(
            application_id=app_id,
            name=test_config_name,
            comments=test_comments,
            config=test_config_data,
        )

        # Act - Create the configuration
        created_config = await service.create_configuration(create_data)

        # Assert - Verify the configuration was created successfully
        assert isinstance(created_config, ConfigurationResponse)
        assert created_config.id == config_id
        assert created_config.application_id == app_id
        assert created_config.name == test_config_name
        assert created_config.comments == test_comments
        assert created_config.config == test_config_data
        assert created_config.created_at == now
        assert created_config.updated_at == now

        # Verify repository calls for creation
        mock_app_repository.get_by_id.assert_called_once_with(app_id)
        mock_config_repository.get_by_application_and_name.assert_called_once_with(
            app_id, test_config_name
        )
        mock_config_repository.create.assert_called_once()

        # Verify the create call was made with correct data
        create_call_args = mock_config_repository.create.call_args[0][0]
        assert create_call_args["application_id"] == app_id
        assert create_call_args["name"] == test_config_name
        assert create_call_args["comments"] == test_comments
        assert create_call_args["config"] == test_config_data

        # Act - Verify the configuration exists by retrieving it
        retrieved_config = await service.get_configuration_by_id(config_id)

        # Assert - Verify the retrieved configuration matches the created one
        assert retrieved_config is not None
        assert isinstance(retrieved_config, ConfigurationResponse)
        assert retrieved_config.id == created_config.id
        assert retrieved_config.application_id == created_config.application_id
        assert retrieved_config.name == created_config.name
        assert retrieved_config.comments == created_config.comments
        assert retrieved_config.config == created_config.config
        assert retrieved_config.created_at == created_config.created_at
        assert retrieved_config.updated_at == created_config.updated_at

        # Verify get_by_id was called
        mock_config_repository.get_by_id.assert_called_once_with(config_id)

    @pytest.mark.asyncio
    async def test_create_configuration_application_not_found_integration(self):
        """Integration test for configuration creation when application doesn't exist."""
        # Create a real service instance
        service = ConfigurationService()

        # Mock the repository layers
        mock_config_repository = AsyncMock()
        mock_app_repository = AsyncMock()
        service.repository = mock_config_repository
        service.application_repository = mock_app_repository

        # Set up test data
        app_id = ULID()
        test_config_name = "test-config"
        test_config_data = {"key": "value"}

        # Mock application doesn't exist
        mock_app_repository.get_by_id.return_value = None

        # Arrange
        create_data = ConfigurationCreate(
            application_id=app_id, name=test_config_name, config=test_config_data
        )

        # Act & Assert - Try to create configuration for non-existent application
        with pytest.raises(
            ValueError, match=f"Application with ID '{app_id}' does not exist"
        ):
            await service.create_configuration(create_data)

        # Verify application was checked but configuration creation was not attempted
        mock_app_repository.get_by_id.assert_called_once_with(app_id)
        mock_config_repository.get_by_application_and_name.assert_not_called()
        mock_config_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_configuration_duplicate_name_integration(self):
        """Integration test for configuration creation with duplicate name."""
        # Create a real service instance
        service = ConfigurationService()

        # Mock the repository layers
        mock_config_repository = AsyncMock()
        mock_app_repository = AsyncMock()
        service.repository = mock_config_repository
        service.application_repository = mock_app_repository

        # Set up test data
        app_id = ULID()
        existing_config_id = ULID()
        test_config_name = "duplicate-config"
        test_config_data = {"key": "value"}

        # Mock application exists
        mock_application = MagicMock()
        mock_application.id = app_id
        mock_application.name = "test-application"
        mock_app_repository.get_by_id.return_value = mock_application

        # Mock existing configuration with same name
        mock_existing_config = MagicMock()
        mock_existing_config.id = existing_config_id
        mock_existing_config.name = test_config_name
        mock_config_repository.get_by_application_and_name.return_value = (
            mock_existing_config
        )

        # Arrange
        create_data = ConfigurationCreate(
            application_id=app_id, name=test_config_name, config=test_config_data
        )

        # Act & Assert - Try to create configuration with duplicate name
        with pytest.raises(
            ValueError,
            match=f"Configuration with name '{test_config_name}' already exists for application 'test-application'",
        ):
            await service.create_configuration(create_data)

        # Verify checks were made but creation was not attempted
        mock_app_repository.get_by_id.assert_called_once_with(app_id)
        mock_config_repository.get_by_application_and_name.assert_called_once_with(
            app_id, test_config_name
        )
        mock_config_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_configuration_minimal_data_integration(self):
        """Integration test for configuration creation with minimal data (no comments)."""
        # Create a real service instance
        service = ConfigurationService()

        # Mock the repository layers
        mock_config_repository = AsyncMock()
        mock_app_repository = AsyncMock()
        service.repository = mock_config_repository
        service.application_repository = mock_app_repository

        # Set up test data
        app_id = ULID()
        config_id = ULID()
        now = datetime.now()
        test_config_name = "minimal-config"
        test_config_data = {"setting": "value"}

        # Mock application exists
        mock_application = MagicMock()
        mock_application.id = app_id
        mock_application.name = "test-application"
        mock_app_repository.get_by_id.return_value = mock_application

        # Mock no existing configuration with same name
        mock_config_repository.get_by_application_and_name.return_value = None

        # Mock entity returned by create (no comments)
        mock_config_entity = MagicMock()
        mock_config_entity.id = config_id
        mock_config_entity.application_id = app_id
        mock_config_entity.name = test_config_name
        mock_config_entity.comments = None
        mock_config_entity.config = test_config_data
        mock_config_entity.created_at = now
        mock_config_entity.updated_at = now
        mock_config_repository.create.return_value = mock_config_entity

        # Mock get_by_id for verification
        mock_config_repository.get_by_id.return_value = mock_config_entity

        # Arrange - Create configuration data without comments
        create_data = ConfigurationCreate(
            application_id=app_id, name=test_config_name, config=test_config_data
        )

        # Act - Create the configuration
        created_config = await service.create_configuration(create_data)

        # Assert - Verify the configuration was created successfully
        assert isinstance(created_config, ConfigurationResponse)
        assert created_config.id == config_id
        assert created_config.application_id == app_id
        assert created_config.name == test_config_name
        assert created_config.comments is None  # No comments provided
        assert created_config.config == test_config_data
        assert created_config.created_at == now
        assert created_config.updated_at == now

        # Verify repository calls
        mock_app_repository.get_by_id.assert_called_once_with(app_id)
        mock_config_repository.get_by_application_and_name.assert_called_once_with(
            app_id, test_config_name
        )
        mock_config_repository.create.assert_called_once()

        # Act - Verify the configuration exists by retrieving it
        retrieved_config = await service.get_configuration_by_id(config_id)

        # Assert - Verify the retrieved configuration matches
        assert retrieved_config is not None
        assert retrieved_config.id == created_config.id
        assert retrieved_config.comments is None
        assert retrieved_config.config == test_config_data

        # Verify get_by_id was called
        mock_config_repository.get_by_id.assert_called_once_with(config_id)

    @pytest.mark.asyncio
    async def test_create_configuration_complex_config_data_integration(self):
        """Integration test for configuration creation with complex nested configuration data."""
        # Create a real service instance
        service = ConfigurationService()

        # Mock the repository layers
        mock_config_repository = AsyncMock()
        mock_app_repository = AsyncMock()
        service.repository = mock_config_repository
        service.application_repository = mock_app_repository

        # Set up test data with complex nested structure
        app_id = ULID()
        config_id = ULID()
        now = datetime.now()
        test_config_name = "complex-config"
        test_comments = "Complex configuration with nested data"
        test_config_data = {
            "database": {
                "primary": {
                    "host": "db-primary.example.com",
                    "port": 5432,
                    "database": "production",
                    "ssl": True,
                    "pool": {
                        "min_connections": 5,
                        "max_connections": 20,
                        "timeout": 30,
                    },
                },
                "replica": {
                    "host": "db-replica.example.com",
                    "port": 5432,
                    "database": "production",
                    "ssl": True,
                },
            },
            "cache": {
                "redis": {
                    "host": "redis.example.com",
                    "port": 6379,
                    "db": 0,
                    "ttl": 3600,
                }
            },
            "features": {
                "authentication": True,
                "logging": {
                    "level": "INFO",
                    "format": "json",
                    "destinations": ["console", "file"],
                },
                "metrics": {
                    "enabled": True,
                    "interval": 60,
                    "tags": ["environment:production", "service:config"],
                },
            },
            "api": {
                "rate_limiting": {
                    "enabled": True,
                    "requests_per_minute": 1000,
                    "burst": 100,
                },
                "cors": {
                    "allowed_origins": ["https://app.example.com"],
                    "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
                    "allowed_headers": ["Content-Type", "Authorization"],
                },
            },
            "environment": "production",
            "version": "1.2.3",
        }

        # Mock application exists
        mock_application = MagicMock()
        mock_application.id = app_id
        mock_application.name = "production-app"
        mock_app_repository.get_by_id.return_value = mock_application

        # Mock no existing configuration with same name
        mock_config_repository.get_by_application_and_name.return_value = None

        # Mock entity returned by create
        mock_config_entity = MagicMock()
        mock_config_entity.id = config_id
        mock_config_entity.application_id = app_id
        mock_config_entity.name = test_config_name
        mock_config_entity.comments = test_comments
        mock_config_entity.config = test_config_data
        mock_config_entity.created_at = now
        mock_config_entity.updated_at = now
        mock_config_repository.create.return_value = mock_config_entity

        # Mock get_by_id for verification
        mock_config_repository.get_by_id.return_value = mock_config_entity

        # Arrange - Create configuration data
        create_data = ConfigurationCreate(
            application_id=app_id,
            name=test_config_name,
            comments=test_comments,
            config=test_config_data,
        )

        # Act - Create the configuration
        created_config = await service.create_configuration(create_data)

        # Assert - Verify the configuration was created successfully
        assert isinstance(created_config, ConfigurationResponse)
        assert created_config.id == config_id
        assert created_config.application_id == app_id
        assert created_config.name == test_config_name
        assert created_config.comments == test_comments
        assert created_config.config == test_config_data

        # Verify complex nested data is preserved
        assert (
            created_config.config["database"]["primary"]["host"]
            == "db-primary.example.com"
        )
        assert (
            created_config.config["database"]["primary"]["pool"]["max_connections"]
            == 20
        )
        assert created_config.config["features"]["logging"]["destinations"] == [
            "console",
            "file",
        ]
        assert created_config.config["api"]["cors"]["allowed_origins"] == [
            "https://app.example.com"
        ]

        # Verify repository calls
        mock_app_repository.get_by_id.assert_called_once_with(app_id)
        mock_config_repository.get_by_application_and_name.assert_called_once_with(
            app_id, test_config_name
        )
        mock_config_repository.create.assert_called_once()

        # Act - Verify the configuration exists by retrieving it
        retrieved_config = await service.get_configuration_by_id(config_id)

        # Assert - Verify the retrieved configuration preserves complex data
        assert retrieved_config is not None
        assert retrieved_config.config == test_config_data
        assert retrieved_config.config["database"]["primary"]["pool"]["timeout"] == 30
        assert retrieved_config.config["features"]["metrics"]["tags"] == [
            "environment:production",
            "service:config",
        ]

        # Verify get_by_id was called
        mock_config_repository.get_by_id.assert_called_once_with(config_id)

    @pytest.mark.asyncio
    async def test_create_and_retrieve_multiple_configurations_integration(self):
        """Integration test for creating multiple configurations and verifying they all exist."""
        # Create a real service instance
        service = ConfigurationService()

        # Mock the repository layers
        mock_config_repository = AsyncMock()
        mock_app_repository = AsyncMock()
        service.repository = mock_config_repository
        service.application_repository = mock_app_repository

        # Set up test data for multiple configurations
        app_id = ULID()
        config1_id = ULID()
        config2_id = ULID()
        config3_id = ULID()
        now = datetime.now()

        # Mock application exists
        mock_application = MagicMock()
        mock_application.id = app_id
        mock_application.name = "multi-config-app"
        mock_app_repository.get_by_id.return_value = mock_application

        # Mock no existing configurations with same names
        mock_config_repository.get_by_application_and_name.return_value = None

        # Configuration data
        configs_data = [
            {
                "id": config1_id,
                "name": "database-config",
                "comments": "Database configuration",
                "config": {"host": "localhost", "port": 5432},
            },
            {
                "id": config2_id,
                "name": "cache-config",
                "comments": "Cache configuration",
                "config": {"redis_host": "localhost", "redis_port": 6379},
            },
            {
                "id": config3_id,
                "name": "api-config",
                "comments": None,
                "config": {"timeout": 30, "max_connections": 100},
            },
        ]

        # Mock entities returned by create
        mock_entities = []
        for config_data in configs_data:
            mock_entity = MagicMock()
            mock_entity.id = config_data["id"]
            mock_entity.application_id = app_id
            mock_entity.name = config_data["name"]
            mock_entity.comments = config_data["comments"]
            mock_entity.config = config_data["config"]
            mock_entity.created_at = now
            mock_entity.updated_at = now
            mock_entities.append(mock_entity)

        mock_config_repository.create.side_effect = mock_entities

        # Mock get_by_id for verification
        def mock_get_by_id(config_id):
            for entity in mock_entities:
                if entity.id == config_id:
                    return entity
            return None

        mock_config_repository.get_by_id.side_effect = mock_get_by_id

        created_configs = []

        # Act - Create all configurations
        for config_data in configs_data:
            create_data = ConfigurationCreate(
                application_id=app_id,
                name=config_data["name"],
                comments=config_data["comments"],
                config=config_data["config"],
            )
            created_config = await service.create_configuration(create_data)
            created_configs.append(created_config)

        # Assert - Verify all configurations were created successfully
        assert len(created_configs) == 3

        for i, created_config in enumerate(created_configs):
            expected_data = configs_data[i]
            assert isinstance(created_config, ConfigurationResponse)
            assert created_config.id == expected_data["id"]
            assert created_config.application_id == app_id
            assert created_config.name == expected_data["name"]
            assert created_config.comments == expected_data["comments"]
            assert created_config.config == expected_data["config"]

        # Verify repository calls
        assert mock_app_repository.get_by_id.call_count == 3
        assert mock_config_repository.get_by_application_and_name.call_count == 3
        assert mock_config_repository.create.call_count == 3

        # Act - Verify all configurations exist by retrieving them
        for created_config in created_configs:
            retrieved_config = await service.get_configuration_by_id(created_config.id)

            # Assert - Verify each retrieved configuration matches the created one
            assert retrieved_config is not None
            assert retrieved_config.id == created_config.id
            assert retrieved_config.name == created_config.name
            assert retrieved_config.comments == created_config.comments
            assert retrieved_config.config == created_config.config

        # Verify get_by_id was called for each configuration
        assert mock_config_repository.get_by_id.call_count == 3
