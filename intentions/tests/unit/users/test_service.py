"""
Unit tests for users service layer.

Tests business logic with mocked dependencies.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.users.events import UserCreatedEvent, UserDeletedEvent, UserUpdatedEvent
from app.users.service import create_user, delete_user, get_all_users, get_user, update_user
from tests.fixtures.users import create_test_user, create_test_user_create_request, create_test_user_update_request


@pytest.mark.unit
class TestGetAllUsers:
    """Test get_all_users service function."""

    @pytest.mark.asyncio
    async def test_get_all_users_returns_all_users(self):
        """Test getting all users returns repository results."""
        # Arrange
        mock_users = [create_test_user(id=1, username="user1"), create_test_user(id=2, username="user2")]

        mock_repo = MagicMock()
        mock_repo.find_all = AsyncMock(return_value=mock_users)

        # Act
        result = await get_all_users(mock_repo)

        # Assert
        assert len(result) == 2
        assert result[0].username == "user1"
        assert result[1].username == "user2"
        mock_repo.find_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_users_with_empty_repository_returns_empty_list(self):
        """Test getting all users from empty repository."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.find_all = AsyncMock(return_value=[])

        # Act
        result = await get_all_users(mock_repo)

        # Assert
        assert result == []
        mock_repo.find_all.assert_called_once()


@pytest.mark.unit
class TestGetUser:
    """Test get_user service function."""

    @pytest.mark.asyncio
    async def test_get_user_when_exists_returns_user(self):
        """Test getting a user that exists."""
        # Arrange
        mock_user = create_test_user(id=1, username="testuser")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=mock_user)

        # Act
        result = await get_user(1, mock_repo)

        # Assert
        assert result is not None
        assert result.id == 1
        assert result.username == "testuser"
        mock_repo.find_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_when_not_found_returns_none(self):
        """Test getting a user that doesn't exist."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        # Act
        result = await get_user(999, mock_repo)

        # Assert
        assert result is None
        mock_repo.find_by_id.assert_called_once_with(999)


@pytest.mark.unit
class TestCreateUser:
    """Test create_user service function."""

    @pytest.mark.asyncio
    async def test_create_user_with_valid_data_returns_created_user(self):
        """Test creating a user with valid data."""
        # Arrange
        request = create_test_user_create_request(username="newuser", email="new@example.com")
        created_user = create_test_user(id=1, username="newuser", email="new@example.com")

        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(return_value=created_user)

        with patch("app.users.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await create_user(request, mock_repo)

            # Assert
            assert result.id == 1
            assert result.username == "newuser"
            assert result.email == "new@example.com"
            mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_publishes_user_created_event(self):
        """Test creating a user publishes UserCreatedEvent."""
        # Arrange
        request = create_test_user_create_request(username="newuser", email="new@example.com")
        created_user = create_test_user(id=1, username="newuser", email="new@example.com")

        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(return_value=created_user)

        with patch("app.users.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            await create_user(request, mock_repo)

            # Assert
            mock_bus.publish.assert_called_once()
            published_event = mock_bus.publish.call_args[0][0]
            assert isinstance(published_event, UserCreatedEvent)
            assert published_event.user_id == 1
            assert published_event.username == "newuser"
            assert published_event.email == "new@example.com"
            assert published_event.event_type == "user.created"


@pytest.mark.unit
class TestUpdateUser:
    """Test update_user service function."""

    @pytest.mark.asyncio
    async def test_update_user_when_exists_returns_updated_user(self):
        """Test updating an existing user."""
        # Arrange
        existing_user = create_test_user(id=1, username="oldname")
        updated_user = create_test_user(id=1, username="newname")
        request = create_test_user_update_request(username="newname")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_user)
        mock_repo.update = AsyncMock(return_value=updated_user)

        with patch("app.users.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await update_user(1, request, mock_repo)

            # Assert
            assert result is not None
            assert result.username == "newname"
            mock_repo.find_by_id.assert_called_once_with(1)
            mock_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_when_not_found_returns_none(self):
        """Test updating a non-existent user."""
        # Arrange
        request = create_test_user_update_request(username="newname")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        with patch("app.users.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await update_user(999, request, mock_repo)

            # Assert
            assert result is None
            mock_repo.find_by_id.assert_called_once_with(999)
            mock_bus.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_publishes_user_updated_event(self):
        """Test updating a user publishes UserUpdatedEvent."""
        # Arrange
        existing_user = create_test_user(id=1, username="oldname")
        updated_user = create_test_user(id=1, username="newname")
        request = create_test_user_update_request(username="newname")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_user)
        mock_repo.update = AsyncMock(return_value=updated_user)

        with patch("app.users.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            await update_user(1, request, mock_repo)

            # Assert
            mock_bus.publish.assert_called_once()
            published_event = mock_bus.publish.call_args[0][0]
            assert isinstance(published_event, UserUpdatedEvent)
            assert published_event.user_id == 1
            assert published_event.event_type == "user.updated"


@pytest.mark.unit
class TestDeleteUser:
    """Test delete_user service function."""

    @pytest.mark.asyncio
    async def test_delete_user_when_exists_returns_true(self):
        """Test deleting an existing user."""
        # Arrange
        existing_user = create_test_user(id=1)

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_user)
        mock_repo.delete = AsyncMock(return_value=True)

        with patch("app.users.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await delete_user(1, mock_repo)

            # Assert
            assert result is True
            mock_repo.find_by_id.assert_called_once_with(1)
            mock_repo.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_user_when_not_found_returns_false(self):
        """Test deleting a non-existent user."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        with patch("app.users.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await delete_user(999, mock_repo)

            # Assert
            assert result is False
            mock_repo.find_by_id.assert_called_once_with(999)
            mock_bus.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_user_publishes_user_deleted_event(self):
        """Test deleting a user publishes UserDeletedEvent."""
        # Arrange
        existing_user = create_test_user(id=1)

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_user)
        mock_repo.delete = AsyncMock(return_value=True)

        with patch("app.users.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            await delete_user(1, mock_repo)

            # Assert
            mock_bus.publish.assert_called_once()
            published_event = mock_bus.publish.call_args[0][0]
            assert isinstance(published_event, UserDeletedEvent)
            assert published_event.user_id == 1
            assert published_event.event_type == "user.deleted"
