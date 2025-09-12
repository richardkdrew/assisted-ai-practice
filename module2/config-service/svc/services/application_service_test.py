"""Tests for application service layer."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from ulid import ULID

from models.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from services.application_service import ApplicationService, application_service
from database.connection import test_db_manager
from database.migrations import migration_manager


class TestApplicationService:
    """Test cases for ApplicationService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ApplicationService()
        self.service.repository = AsyncMock()

    @pytest.mark.asyncio
    async def test_create_application_success(self):
        """Test successful application creation."""
        # Arrange
        app_id = ULID()
        now = datetime.now()

        create_data = ApplicationCreate(name="test-app", comments="Test application")

        # Mock repository responses
        self.service.repository.get_by_name.return_value = None  # No existing app
        mock_entity = MagicMock()
        mock_entity.id = app_id
        mock_entity.name = "test-app"
        mock_entity.comments = "Test application"
        mock_entity.created_at = now
        mock_entity.updated_at = now
        self.service.repository.create.return_value = mock_entity
        self.service.repository.get_configuration_ids_by_application_id.return_value = (
            []
        )

        # Act
        result = await self.service.create_application(create_data)

        # Assert
        assert isinstance(result, ApplicationResponse)
        assert result.id == app_id
        assert result.name == "test-app"
        assert result.comments == "Test application"
        assert result.configuration_ids == []

        # Verify repository calls
        self.service.repository.get_by_name.assert_called_once_with("test-app")
        self.service.repository.create.assert_called_once()
        self.service.repository.get_configuration_ids_by_application_id.assert_called_once_with(
            app_id
        )

    @pytest.mark.asyncio
    async def test_create_application_duplicate_name(self):
        """Test application creation with duplicate name."""
        # Arrange
        create_data = ApplicationCreate(name="existing-app")

        # Mock existing application
        self.service.repository.get_by_name.return_value = MagicMock(
            id=ULID(), name="existing-app"
        )

        # Act & Assert
        with pytest.raises(
            ValueError, match="Application with name 'existing-app' already exists"
        ):
            await self.service.create_application(create_data)

        # Verify repository was checked but create was not called
        self.service.repository.get_by_name.assert_called_once_with("existing-app")
        self.service.repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_application_by_id_success(self):
        """Test successful application retrieval by ID."""
        # Arrange
        app_id = ULID()
        config_ids = [ULID(), ULID()]
        now = datetime.now()

        # Mock repository responses
        mock_entity = MagicMock()
        mock_entity.id = app_id
        mock_entity.name = "test-app"
        mock_entity.comments = "Test application"
        mock_entity.created_at = now
        mock_entity.updated_at = now
        self.service.repository.get_by_id.return_value = mock_entity
        self.service.repository.get_configuration_ids_by_application_id.return_value = (
            config_ids
        )

        # Act
        result = await self.service.get_application_by_id(app_id)

        # Assert
        assert isinstance(result, ApplicationResponse)
        assert result.id == app_id
        assert result.name == "test-app"
        assert result.configuration_ids == config_ids

        # Verify repository calls
        self.service.repository.get_by_id.assert_called_once_with(app_id)
        self.service.repository.get_configuration_ids_by_application_id.assert_called_once_with(
            app_id
        )

    @pytest.mark.asyncio
    async def test_get_application_by_id_not_found(self):
        """Test application retrieval when application doesn't exist."""
        # Arrange
        app_id = ULID()
        self.service.repository.get_by_id.return_value = None

        # Act
        result = await self.service.get_application_by_id(app_id)

        # Assert
        assert result is None
        self.service.repository.get_by_id.assert_called_once_with(app_id)
        self.service.repository.get_configuration_ids_by_application_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_application_success(self):
        """Test successful application update."""
        # Arrange
        app_id = ULID()
        now = datetime.now()

        update_data = ApplicationUpdate(name="updated-app", comments="Updated comments")

        # Mock repository responses
        existing_app = MagicMock()
        existing_app.id = app_id
        existing_app.name = "original-app"
        existing_app.comments = "Original comments"
        self.service.repository.get_by_id.return_value = existing_app
        self.service.repository.get_by_name.return_value = None  # No name conflict

        updated_entity = MagicMock()
        updated_entity.id = app_id
        updated_entity.name = "updated-app"
        updated_entity.comments = "Updated comments"
        updated_entity.created_at = now
        updated_entity.updated_at = now
        self.service.repository.update.return_value = updated_entity
        self.service.repository.get_configuration_ids_by_application_id.return_value = (
            []
        )

        # Act
        result = await self.service.update_application(app_id, update_data)

        # Assert
        assert isinstance(result, ApplicationResponse)
        assert result.id == app_id
        assert result.name == "updated-app"
        assert result.comments == "Updated comments"

        # Verify repository calls
        self.service.repository.get_by_id.assert_called_once_with(app_id)
        self.service.repository.get_by_name.assert_called_once_with("updated-app")
        self.service.repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_application_not_found(self):
        """Test application update when application doesn't exist."""
        # Arrange
        app_id = ULID()
        update_data = ApplicationUpdate(name="updated-app")

        self.service.repository.get_by_id.return_value = None

        # Act
        result = await self.service.update_application(app_id, update_data)

        # Assert
        assert result is None
        self.service.repository.get_by_id.assert_called_once_with(app_id)
        self.service.repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_application_name_conflict(self):
        """Test application update with name conflict."""
        # Arrange
        app_id = ULID()
        other_app_id = ULID()

        update_data = ApplicationUpdate(name="conflicting-name")

        # Mock existing application
        existing_app = MagicMock(id=app_id, name="original-app")
        self.service.repository.get_by_id.return_value = existing_app

        # Mock conflicting application
        conflicting_app = MagicMock(id=other_app_id, name="conflicting-name")
        self.service.repository.get_by_name.return_value = conflicting_app

        # Act & Assert
        with pytest.raises(
            ValueError, match="Application with name 'conflicting-name' already exists"
        ):
            await self.service.update_application(app_id, update_data)

        # Verify repository calls
        self.service.repository.get_by_id.assert_called_once_with(app_id)
        self.service.repository.get_by_name.assert_called_once_with("conflicting-name")
        self.service.repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_application_same_name(self):
        """Test application update with same name (no conflict)."""
        # Arrange
        app_id = ULID()
        now = datetime.now()

        update_data = ApplicationUpdate(name="same-name", comments="Updated comments")

        # Mock existing application with same name
        existing_app = MagicMock()
        existing_app.id = app_id
        existing_app.name = "same-name"
        self.service.repository.get_by_id.return_value = existing_app

        updated_entity = MagicMock()
        updated_entity.id = app_id
        updated_entity.name = "same-name"
        updated_entity.comments = "Updated comments"
        updated_entity.created_at = now
        updated_entity.updated_at = now
        self.service.repository.update.return_value = updated_entity
        self.service.repository.get_configuration_ids_by_application_id.return_value = (
            []
        )

        # Act
        result = await self.service.update_application(app_id, update_data)

        # Assert
        assert isinstance(result, ApplicationResponse)
        assert result.name == "same-name"
        assert result.comments == "Updated comments"

        # Verify name conflict check was skipped
        self.service.repository.get_by_name.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_all_applications(self):
        """Test retrieving all applications."""
        # Arrange
        app1_id = ULID()
        app2_id = ULID()
        now = datetime.now()

        # Mock repository responses
        mock_entity1 = MagicMock()
        mock_entity1.id = app1_id
        mock_entity1.name = "app1"
        mock_entity1.comments = "First app"
        mock_entity1.created_at = now
        mock_entity1.updated_at = now

        mock_entity2 = MagicMock()
        mock_entity2.id = app2_id
        mock_entity2.name = "app2"
        mock_entity2.comments = "Second app"
        mock_entity2.created_at = now
        mock_entity2.updated_at = now

        mock_entities = [mock_entity1, mock_entity2]
        self.service.repository.get_all.return_value = mock_entities
        self.service.repository.get_configuration_ids_by_application_id.side_effect = [
            [ULID()],  # app1 has 1 config
            [],  # app2 has no configs
        ]

        # Act
        result = await self.service.get_all_applications(limit=10, offset=0)

        # Assert
        assert len(result) == 2
        assert all(isinstance(app, ApplicationResponse) for app in result)
        assert result[0].name == "app1"
        assert result[1].name == "app2"
        assert len(result[0].configuration_ids) == 1
        assert len(result[1].configuration_ids) == 0

        # Verify repository calls
        self.service.repository.get_all.assert_called_once_with(limit=10, offset=0)
        assert (
            self.service.repository.get_configuration_ids_by_application_id.call_count
            == 2
        )

    @pytest.mark.asyncio
    async def test_delete_application_success(self):
        """Test successful application deletion."""
        # Arrange
        app_id = ULID()
        self.service.repository.delete_by_id.return_value = True

        # Act
        result = await self.service.delete_application(app_id)

        # Assert
        assert result is True
        self.service.repository.delete_by_id.assert_called_once_with(app_id)

    @pytest.mark.asyncio
    async def test_delete_application_not_found(self):
        """Test application deletion when application doesn't exist."""
        # Arrange
        app_id = ULID()
        self.service.repository.delete_by_id.return_value = False

        # Act
        result = await self.service.delete_application(app_id)

        # Assert
        assert result is False
        self.service.repository.delete_by_id.assert_called_once_with(app_id)

    @pytest.mark.asyncio
    async def test_create_application_repository_error(self):
        """Test application creation with repository error."""
        # Arrange
        create_data = ApplicationCreate(name="test-app")

        self.service.repository.get_by_name.return_value = None
        self.service.repository.create.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await self.service.create_application(create_data)

    @pytest.mark.asyncio
    async def test_get_application_repository_error(self):
        """Test application retrieval with repository error."""
        # Arrange
        app_id = ULID()
        self.service.repository.get_by_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await self.service.get_application_by_id(app_id)


class TestApplicationServiceIntegration:
    """Integration test cases for ApplicationService with real repository layer."""

    @pytest.mark.asyncio
    async def test_create_application_integration(self):
        """Integration test for create application flow.

        This test verifies that:
        1. An application can be successfully created through the service layer
        2. The application exists after creation by calling the service again
        3. The created application can be retrieved with correct data

        Note: This test uses the real service and repository layers but mocks
        the database layer to avoid requiring a running database.
        """
        # Create a real service instance (not mocked)
        service = ApplicationService()

        # Mock the repository layer to simulate database operations
        mock_repository = AsyncMock()
        service.repository = mock_repository

        # Set up mock responses
        app_id = ULID()
        now = datetime.now()

        # Mock the repository methods
        mock_repository.get_by_name.return_value = None  # No existing app

        # Mock entity returned by create
        mock_entity = MagicMock()
        mock_entity.id = app_id
        mock_entity.name = "integration-test-app"
        mock_entity.comments = "Integration test application"
        mock_entity.created_at = now
        mock_entity.updated_at = now
        mock_repository.create.return_value = mock_entity

        # Mock configuration IDs (empty for new app)
        mock_repository.get_configuration_ids_by_application_id.return_value = []

        # Mock get_by_id for verification
        mock_repository.get_by_id.return_value = mock_entity

        # Arrange
        test_app_name = "integration-test-app"
        test_comments = "Integration test application"
        create_data = ApplicationCreate(name=test_app_name, comments=test_comments)

        # Act - Create the application
        created_app = await service.create_application(create_data)

        # Assert - Verify the application was created successfully
        assert isinstance(created_app, ApplicationResponse)
        assert created_app.name == test_app_name
        assert created_app.comments == test_comments
        assert created_app.id == app_id
        assert created_app.created_at == now
        assert created_app.updated_at == now
        assert isinstance(created_app.configuration_ids, list)
        assert len(created_app.configuration_ids) == 0  # New app should have no configs

        # Verify repository was called correctly
        mock_repository.get_by_name.assert_called_once_with(test_app_name)
        mock_repository.create.assert_called_once()
        mock_repository.get_configuration_ids_by_application_id.assert_called_once_with(
            app_id
        )

        # Act - Verify the application exists by retrieving it
        retrieved_app = await service.get_application_by_id(created_app.id)

        # Assert - Verify the retrieved application matches the created one
        assert retrieved_app is not None
        assert retrieved_app.id == created_app.id
        assert retrieved_app.name == created_app.name
        assert retrieved_app.comments == created_app.comments
        assert retrieved_app.created_at == created_app.created_at
        assert retrieved_app.updated_at == created_app.updated_at

        # Verify get_by_id was called
        mock_repository.get_by_id.assert_called_once_with(app_id)

    @pytest.mark.asyncio
    async def test_create_application_duplicate_name_integration(self):
        """Integration test for duplicate application name validation."""
        # Create a real service instance
        service = ApplicationService()

        # Mock the repository layer
        mock_repository = AsyncMock()
        service.repository = mock_repository

        # Mock existing application
        existing_app = MagicMock()
        existing_app.id = ULID()
        existing_app.name = "duplicate-test-app"
        mock_repository.get_by_name.return_value = existing_app

        # Arrange
        test_app_name = "duplicate-test-app"
        create_data = ApplicationCreate(
            name=test_app_name, comments="First application"
        )

        # Act & Assert - Try to create a duplicate application
        with pytest.raises(
            ValueError,
            match=f"Application with name '{test_app_name}' already exists",
        ):
            await service.create_application(create_data)

        # Verify repository was checked but create was not called
        mock_repository.get_by_name.assert_called_once_with(test_app_name)
        mock_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_and_delete_application_integration(self):
        """Integration test for create and delete application flow."""
        # Create a real service instance
        service = ApplicationService()

        # Mock the repository layer
        mock_repository = AsyncMock()
        service.repository = mock_repository

        # Set up mock responses
        app_id = ULID()
        now = datetime.now()

        # Mock the repository methods for create flow
        mock_repository.get_by_name.return_value = None  # No existing app

        # Mock entity returned by create
        mock_entity = MagicMock()
        mock_entity.id = app_id
        mock_entity.name = "delete-test-app"
        mock_entity.comments = "Application to be deleted"
        mock_entity.created_at = now
        mock_entity.updated_at = now
        mock_repository.create.return_value = mock_entity

        # Mock configuration IDs (empty for new app)
        mock_repository.get_configuration_ids_by_application_id.return_value = []

        # Mock get_by_id for verification
        mock_repository.get_by_id.return_value = mock_entity

        # Mock delete operation
        mock_repository.delete_by_id.return_value = True

        # Arrange
        test_app_name = "delete-test-app"
        create_data = ApplicationCreate(
            name=test_app_name, comments="Application to be deleted"
        )

        # Act - Create the application
        created_app = await service.create_application(create_data)
        assert created_app is not None

        # Verify it exists
        retrieved_app = await service.get_application_by_id(created_app.id)
        assert retrieved_app is not None

        # Act - Delete the application
        delete_result = await service.delete_application(created_app.id)

        # Assert - Verify deletion was successful
        assert delete_result is True

        # Verify the delete method was called with correct ID
        mock_repository.delete_by_id.assert_called_once_with(created_app.id)
