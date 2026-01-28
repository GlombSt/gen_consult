"""
Unit tests for users schemas/DTOs.

Tests field validation and serialization.
"""

import pytest
from pydantic import ValidationError

from app.users.schemas import UserCreateRequest, UserResponse, UserUpdateRequest


@pytest.mark.unit
class TestUserCreateRequest:
    """Test UserCreateRequest schema."""

    def test_create_request_with_valid_data_validates(self):
        """Test creating request with valid data."""
        # Arrange & Act
        request = UserCreateRequest(username="john_doe", email="john@example.com")

        # Assert
        assert request.username == "john_doe"
        assert request.email == "john@example.com"

    def test_create_request_without_username_raises_validation_error(self):
        """Test creating request without username raises error."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UserCreateRequest(email="john@example.com")

        assert "username" in str(exc_info.value)

    def test_create_request_without_email_raises_validation_error(self):
        """Test creating request without email raises error."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UserCreateRequest(username="john_doe")

        assert "email" in str(exc_info.value)


@pytest.mark.unit
class TestUserUpdateRequest:
    """Test UserUpdateRequest schema."""

    def test_update_request_with_all_fields_validates(self):
        """Test update request with all fields."""
        # Arrange & Act
        request = UserUpdateRequest(username="new_username", email="new@example.com")

        # Assert
        assert request.username == "new_username"
        assert request.email == "new@example.com"

    def test_update_request_with_no_fields_validates(self):
        """Test update request with no fields."""
        # Arrange & Act
        request = UserUpdateRequest()

        # Assert
        assert request.username is None
        assert request.email is None

    def test_update_request_with_single_field_validates(self):
        """Test update request with single field."""
        # Arrange & Act
        request = UserUpdateRequest(username="new_username")

        # Assert
        assert request.username == "new_username"
        assert request.email is None


@pytest.mark.unit
class TestUserResponse:
    """Test UserResponse schema."""

    def test_response_with_valid_data_validates(self):
        """Test response with valid data."""
        # Arrange & Act
        response = UserResponse(id=1, username="john_doe", email="john@example.com")

        # Assert
        assert response.id == 1
        assert response.username == "john_doe"
        assert response.email == "john@example.com"

    def test_response_without_id_raises_validation_error(self):
        """Test response without ID raises error."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(username="john_doe", email="john@example.com")

        assert "id" in str(exc_info.value)
