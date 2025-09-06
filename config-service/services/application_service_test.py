"""Tests for application service layer."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from pydantic_extra_types.ulid import ULID
from ulid import ULID as ULIDGenerator

from models.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from services.application_service import ApplicationService


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
        app_id = ULIDGenerator()
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
            id=ULIDGenerator(), name="existing-app"
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
        app_id = ULIDGenerator()
        config_ids = [ULIDGenerator(), ULIDGenerator()]
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
        app_id = ULIDGenerator()
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
        app_id = ULIDGenerator()
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
        app_id = ULIDGenerator()
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
        app_id = ULIDGenerator()
        other_app_id = ULIDGenerator()

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
        app_id = ULIDGenerator()
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
        app1_id = ULIDGenerator()
        app2_id = ULIDGenerator()
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
            [ULIDGenerator()],  # app1 has 1 config
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
        app_id = ULIDGenerator()
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
        app_id = ULIDGenerator()
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
        app_id = ULIDGenerator()
        self.service.repository.get_by_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await self.service.get_application_by_id(app_id)
