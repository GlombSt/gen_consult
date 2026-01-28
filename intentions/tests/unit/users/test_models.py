"""
Unit tests for users domain models.

Tests domain logic and validation rules.
"""

from datetime import datetime

import pytest

from app.users.models import User


@pytest.mark.unit
class TestUser:
    """Test User domain model."""

    def test_create_user_with_valid_data_creates_instance(self):
        """Test creating a user with valid data."""
        # Arrange & Act
        user = User(id=1, username="john_doe", email="john@example.com")

        # Assert
        assert user.id == 1
        assert user.username == "john_doe"
        assert user.email == "john@example.com"
        assert isinstance(user.created_at, datetime)

    def test_create_user_without_id_sets_none(self):
        """Test creating a user without ID sets it to None."""
        # Arrange & Act
        user = User(id=None, username="john_doe", email="john@example.com")

        # Assert
        assert user.id is None

    def test_create_user_without_created_at_sets_default(self):
        """Test creating a user without created_at sets default."""
        # Arrange & Act
        before = datetime.utcnow()
        user = User(id=1, username="john_doe", email="john@example.com")
        after = datetime.utcnow()

        # Assert
        assert before <= user.created_at <= after

    def test_create_user_with_created_at_uses_provided_value(self):
        """Test creating a user with provided created_at."""
        # Arrange
        custom_date = datetime(2025, 1, 1, 12, 0, 0)

        # Act
        user = User(id=1, username="john_doe", email="john@example.com", created_at=custom_date)

        # Assert
        assert user.created_at == custom_date
