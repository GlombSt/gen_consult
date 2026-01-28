"""
Test data fixtures for users domain.
"""

from datetime import datetime

from app.users.models import User
from app.users.schemas import UserCreateRequest, UserUpdateRequest


def create_test_user(
    id: int = 1, username: str = "testuser", email: str = "test@example.com", created_at: datetime = None
) -> User:
    """Create a test user domain model."""
    return User(id=id, username=username, email=email, created_at=created_at or datetime(2025, 1, 1, 12, 0, 0))


def create_test_user_create_request(username: str = "newuser", email: str = "newuser@example.com") -> UserCreateRequest:
    """Create a test user create request."""
    return UserCreateRequest(username=username, email=email)


def create_test_user_update_request(username: str = None, email: str = None) -> UserUpdateRequest:
    """Create a test user update request."""
    return UserUpdateRequest(username=username, email=email)
