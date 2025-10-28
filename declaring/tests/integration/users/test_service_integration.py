"""
Integration tests for users service with real repository.

Tests service + repository integration without mocks.
"""

from unittest.mock import patch

import pytest

from app.shared.events import EventBus
from app.users.events import UserCreatedEvent
from app.users.repository import UserRepository
from app.users.service import (
    create_user,
    delete_user,
    get_all_users,
    get_user,
    update_user,
)
from tests.fixtures.users import (
    create_test_user_create_request,
    create_test_user_update_request,
)


@pytest.mark.integration
class TestUserServiceIntegration:
    """Test users service with real repository."""

    @pytest.mark.asyncio
    async def test_create_and_get_user_integration(self):
        """Test creating and retrieving a user end-to-end."""
        # Arrange
        request = create_test_user_create_request(username="testuser", email="test@example.com")

        with patch("app.users.service.user_repository", UserRepository()), patch("app.users.service.event_bus", EventBus()):
            # Act - Create
            created_user = await create_user(request)

            # Act - Get
            retrieved_user = await get_user(created_user.id)

            # Assert
            assert retrieved_user is not None
            assert retrieved_user.id == created_user.id
            assert retrieved_user.username == "testuser"
            assert retrieved_user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_create_update_get_user_integration(self):
        """Test creating, updating, and retrieving a user."""
        # Arrange
        create_request = create_test_user_create_request(username="oldname", email="old@example.com")
        update_request = create_test_user_update_request(username="newname", email="new@example.com")

        with patch("app.users.service.user_repository", UserRepository()), patch("app.users.service.event_bus", EventBus()):
            # Act - Create
            created_user = await create_user(create_request)

            # Act - Update
            await update_user(created_user.id, update_request)

            # Act - Get
            retrieved_user = await get_user(created_user.id)

            # Assert
            assert retrieved_user is not None
            assert retrieved_user.username == "newname"
            assert retrieved_user.email == "new@example.com"

    @pytest.mark.asyncio
    async def test_create_delete_get_user_integration(self):
        """Test creating, deleting, and attempting to retrieve a user."""
        # Arrange
        request = create_test_user_create_request(username="todelete", email="delete@example.com")

        with patch("app.users.service.user_repository", UserRepository()), patch("app.users.service.event_bus", EventBus()):
            # Act - Create
            created_user = await create_user(request)

            # Act - Delete
            deleted = await delete_user(created_user.id)

            # Act - Get
            retrieved_user = await get_user(created_user.id)

            # Assert
            assert deleted is True
            assert retrieved_user is None

    @pytest.mark.asyncio
    async def test_create_multiple_and_get_all_integration(self):
        """Test creating multiple users and retrieving all."""
        # Arrange
        request1 = create_test_user_create_request(username="user1", email="user1@example.com")
        request2 = create_test_user_create_request(username="user2", email="user2@example.com")

        with patch("app.users.service.user_repository", UserRepository()), patch("app.users.service.event_bus", EventBus()):
            # Act - Create multiple
            await create_user(request1)
            await create_user(request2)

            # Act - Get all
            all_users = await get_all_users()

            # Assert
            assert len(all_users) == 2
            assert any(user.username == "user1" for user in all_users)
            assert any(user.username == "user2" for user in all_users)

    @pytest.mark.asyncio
    async def test_user_created_event_published_integration(self):
        """Test that UserCreatedEvent is published when creating user."""
        # Arrange
        request = create_test_user_create_request(username="eventtest", email="event@example.com")
        event_bus = EventBus()
        published_events = []

        async def capture_event(event):
            published_events.append(event)

        event_bus.subscribe("user.created", capture_event)

        with patch("app.users.service.user_repository", UserRepository()), patch("app.users.service.event_bus", event_bus):
            # Act
            created_user = await create_user(request)

            # Assert
            assert len(published_events) == 1
            assert isinstance(published_events[0], UserCreatedEvent)
            assert published_events[0].user_id == created_user.id
            assert published_events[0].username == "eventtest"
