"""
Unit tests for users repository layer.

Tests data access and model conversions with database.
"""

from datetime import datetime

import pytest

from app.users.repository import UserRepository
from tests.fixtures.users import create_test_user


@pytest.mark.unit
class TestUserRepositoryFindAll:
    """Test UserRepository.find_all method."""

    @pytest.mark.asyncio
    async def test_find_all_with_users_returns_all_users(self, test_db_session):
        """Test finding all users when users exist."""
        # Arrange
        repo = UserRepository(test_db_session)
        user1 = create_test_user(id=None, username="user1", email="user1@example.com")
        user2 = create_test_user(id=None, username="user2", email="user2@example.com")
        await repo.create(user1)
        await repo.create(user2)
        await test_db_session.commit()

        # Act
        result = await repo.find_all()

        # Assert
        assert len(result) == 2
        assert result[0].username == "user1"
        assert result[1].username == "user2"

    @pytest.mark.asyncio
    async def test_find_all_with_empty_storage_returns_empty_list(self, test_db_session):
        """Test finding all users when storage is empty."""
        # Arrange
        repo = UserRepository(test_db_session)

        # Act
        result = await repo.find_all()

        # Assert
        assert result == []


@pytest.mark.unit
class TestUserRepositoryFindById:
    """Test UserRepository.find_by_id method."""

    @pytest.mark.asyncio
    async def test_find_by_id_when_exists_returns_user(self, test_db_session):
        """Test finding a user by ID when it exists."""
        # Arrange
        repo = UserRepository(test_db_session)
        user = create_test_user(id=None, username="testuser")
        created = await repo.create(user)
        await test_db_session.commit()

        # Act
        result = await repo.find_by_id(created.id)

        # Assert
        assert result is not None
        assert result.id == created.id
        assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_find_by_id_when_not_exists_returns_none(self, test_db_session):
        """Test finding a user by ID when it doesn't exist."""
        # Arrange
        repo = UserRepository(test_db_session)

        # Act
        result = await repo.find_by_id(999)

        # Assert
        assert result is None


@pytest.mark.unit
class TestUserRepositoryCreate:
    """Test UserRepository.create method."""

    @pytest.mark.asyncio
    async def test_create_user_assigns_id_and_returns_user(self, test_db_session):
        """Test creating a user assigns ID and returns domain model."""
        # Arrange
        repo = UserRepository(test_db_session)
        user = create_test_user(id=None, username="newuser", email="new@example.com")

        # Act
        result = await repo.create(user)
        await test_db_session.commit()

        # Assert
        assert result.id is not None
        assert result.id == 1
        assert result.username == "newuser"
        assert result.email == "new@example.com"

    @pytest.mark.asyncio
    async def test_create_multiple_users_increments_id(self, test_db_session):
        """Test creating multiple users increments ID counter."""
        # Arrange
        repo = UserRepository(test_db_session)
        user1 = create_test_user(id=None, username="user1", email="user1@example.com")
        user2 = create_test_user(id=None, username="user2", email="user2@example.com")

        # Act
        result1 = await repo.create(user1)
        await test_db_session.commit()
        result2 = await repo.create(user2)
        await test_db_session.commit()

        # Assert
        assert result1.id == 1
        assert result2.id == 2


@pytest.mark.unit
class TestUserRepositoryUpdate:
    """Test UserRepository.update method."""

    @pytest.mark.asyncio
    async def test_update_user_when_exists_returns_updated_user(self, test_db_session):
        """Test updating an existing user."""
        # Arrange
        repo = UserRepository(test_db_session)
        user = create_test_user(id=None, username="oldname", email="old@example.com")
        created = await repo.create(user)
        await test_db_session.commit()

        # Modify the user
        created.username = "newname"
        created.email = "new@example.com"

        # Act
        result = await repo.update(created.id, created)
        await test_db_session.commit()

        # Assert
        assert result is not None
        assert result.id == created.id
        assert result.username == "newname"
        assert result.email == "new@example.com"

    @pytest.mark.asyncio
    async def test_update_user_when_not_exists_returns_none(self, test_db_session):
        """Test updating a non-existent user."""
        # Arrange
        repo = UserRepository(test_db_session)
        user = create_test_user(id=999, username="test")

        # Act
        result = await repo.update(999, user)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_user_preserves_created_at(self, test_db_session):
        """Test updating a user preserves created_at timestamp."""
        # Arrange
        repo = UserRepository(test_db_session)
        original_date = datetime(2025, 1, 1, 12, 0, 0)
        user = create_test_user(id=None, username="test", created_at=original_date)
        created = await repo.create(user)
        await test_db_session.commit()

        # Modify the user
        created.username = "updated"

        # Act
        result = await repo.update(created.id, created)
        await test_db_session.commit()

        # Assert
        assert result.created_at == original_date


@pytest.mark.unit
class TestUserRepositoryDelete:
    """Test UserRepository.delete method."""

    @pytest.mark.asyncio
    async def test_delete_user_when_exists_returns_true(self, test_db_session):
        """Test deleting an existing user."""
        # Arrange
        repo = UserRepository(test_db_session)
        user = create_test_user(id=None, username="testuser")
        created = await repo.create(user)
        await test_db_session.commit()

        # Act
        result = await repo.delete(created.id)
        await test_db_session.commit()

        # Assert
        assert result is True
        # Verify user is actually deleted
        found = await repo.find_by_id(created.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_delete_user_when_not_exists_returns_false(self, test_db_session):
        """Test deleting a non-existent user."""
        # Arrange
        repo = UserRepository(test_db_session)

        # Act
        result = await repo.delete(999)

        # Assert
        assert result is False
